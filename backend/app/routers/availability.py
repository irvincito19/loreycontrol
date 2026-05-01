from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, time, timedelta
from .. import models, schemas, auth, database

router = APIRouter(prefix="/availability", tags=["Disponibilidad"])

@router.get("/config", response_model=List[schemas.Availability])
async def get_availability_config(
    location: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.Availability)
    if location:
        query = query.filter(models.Availability.location == location)
    return query.all()

@router.post("/config", response_model=schemas.Availability)
async def update_availability_config(
    availability: schemas.AvailabilityCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Buscar si ya existe configuración para ese día y lugar
    db_avail = db.query(models.Availability).filter(
        models.Availability.day_of_week == availability.day_of_week,
        models.Availability.location == availability.location
    ).first()

    # Validar traslapes con OTRAS ubicaciones para el mismo día
    if availability.active:
        other_locations_config = db.query(models.Availability).filter(
            models.Availability.day_of_week == availability.day_of_week,
            models.Availability.location != availability.location,
            models.Availability.active == True
        ).all()

        for other in other_locations_config:
            # Comprobar traslape de horas
            # (Start1 < End2) AND (Start2 < End1)
            if max(availability.start_time, other.start_time) < min(availability.end_time, other.end_time):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Conflicto de horario: El día {availability.day_of_week} ya tiene un horario activo en {other.location} ({other.start_time}-{other.end_time}) que se traslapa con este."
                )

    if db_avail:
        for key, value in availability.dict().items():
            setattr(db_avail, key, value)
    else:
        db_avail = models.Availability(**availability.dict())
        db.add(db_avail)
    
    db.commit()
    db.refresh(db_avail)
    return db_avail

@router.get("/slots", response_model=List[schemas.Slot])
async def get_available_slots(
    date: str, # YYYY-MM-DD
    location: str, # "Oaxaca" o "Miahuatlán"
    db: Session = Depends(database.get_db)
):
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

    day_of_week = dt.weekday() # 0 = Lunes

    # 1. Obtener configuración base para ese día
    config = db.query(models.Availability).filter(
        models.Availability.day_of_week == day_of_week,
        models.Availability.location == location,
        models.Availability.active == True
    ).first()

    # 2. Verificar overrides (bloqueos o cambios de horario específicos)
    overrides = db.query(models.AvailabilityOverride).filter(
        models.AvailabilityOverride.date == date,
        models.AvailabilityOverride.location == location
    ).all()

    intervals = []
    if overrides:
      if any(o.is_blocked for o in overrides):
          return []
      for o in overrides:
          if o.start_time and o.end_time:
              intervals.append({
                  "start": o.start_time,
                  "end": o.end_time,
                  "duration": o.slot_duration
              })
    elif config:
      intervals.append({
          "start": config.start_time,
          "end": config.end_time,
          "duration": config.slot_duration
      })
    
    if not intervals:
        return []

    # 3. Obtener citas existentes para ese día (de cualquier ubicación)
    day_start = datetime.strptime(f"{date} 00:00", "%Y-%m-%d %H:%M")
    day_end = datetime.strptime(f"{date} 23:59", "%Y-%m-%d %H:%M")
    
    existing_appointments = db.query(models.Appointment).filter(
        models.Appointment.date_time >= day_start,
        models.Appointment.date_time <= day_end,
        models.Appointment.status != "cancelado"
    ).all()
    
    # Definimos que cada cita ocupa un bloque de 30 minutos por defecto
    occupied_intervals = [
        (appt.date_time, appt.date_time + timedelta(minutes=30))
        for appt in existing_appointments
    ]

    # 4. Generar slots para cada intervalo
    slots = []
    for interval in intervals:
        start_str = interval["start"]
        end_str = interval["end"]
        duration = interval["duration"]
        
        current_dt = datetime.strptime(f"{date} {start_str}", "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(f"{date} {end_str}", "%Y-%m-%d %H:%M")
        
        while current_dt < end_dt:
            slot_start = current_dt
            slot_end = current_dt + timedelta(minutes=duration)
            
            # Verificar si este slot se traslapa con alguna cita existente
            is_available = True
            for occ_start, occ_end in occupied_intervals:
                # Hay traslape si el inicio de uno es antes del fin del otro
                if max(slot_start, occ_start) < min(slot_end, occ_end):
                    is_available = False
                    break
            
            slots.append(schemas.Slot(
                time=current_dt.strftime("%H:%M"),
                available=is_available
            ))
            current_dt += timedelta(minutes=duration)

    # Ordenar slots por tiempo
    slots.sort(key=lambda x: x.time)
    return slots

@router.post("/overrides/bulk")
async def update_day_availability(
    update: schemas.DayAvailabilityUpdate,
    location: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Validar traslapes con OTRAS ubicaciones para esta FECHA específica
    if not update.is_blocked:
        # 1. Buscar overrides en otras ubicaciones para la misma fecha
        other_overrides = db.query(models.AvailabilityOverride).filter(
            models.AvailabilityOverride.date == update.date,
            models.AvailabilityOverride.location != location,
            models.AvailabilityOverride.is_blocked == False
        ).all()

        for new_int in update.intervals:
            # Check against other overrides
            for other in other_overrides:
                if max(new_int.start_time, other.start_time) < min(new_int.end_time, other.end_time):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Conflicto: Ya existe un horario activo en {other.location} ({other.start_time}-{other.end_time}) para esta fecha."
                    )
            
            # Check against base config if no override exists for other locations (optional but safer)
            # Para simplificar, priorizamos los overrides.

    # 1. Eliminar overrides existentes para esa fecha y lugar
    db.query(models.AvailabilityOverride).filter(
        models.AvailabilityOverride.date == update.date,
        models.AvailabilityOverride.location == location
    ).delete()

    # 2. Si está bloqueado, solo añadir un registro de bloqueo
    if update.is_blocked:
        db_override = models.AvailabilityOverride(
            date=update.date,
            location=location,
            is_blocked=True
        )
        db.add(db_override)
    else:
        # 3. Añadir los nuevos intervalos
        for interval in update.intervals:
            db_override = models.AvailabilityOverride(
                date=update.date,
                location=location,
                start_time=interval.start_time,
                end_time=interval.end_time,
                slot_duration=interval.slot_duration,
                is_blocked=False
            )
            db.add(db_override)
    
    db.commit()
    return {"message": "Disponibilidad actualizada exitosamente"}

@router.get("/overrides/{date}", response_model=List[schemas.AvailabilityOverride])
async def get_day_overrides(
    date: str,
    location: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.AvailabilityOverride).filter(
        models.AvailabilityOverride.date == date,
        models.AvailabilityOverride.location == location
    ).all()
