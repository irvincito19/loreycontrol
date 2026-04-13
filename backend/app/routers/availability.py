from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, time, timedelta
from .. import models, schemas, auth, database

router = APIRouter(prefix="/availability", tags=["Disponibilidad"])

@router.get("/config", response_model=List[schemas.Availability])
async def get_availability_config(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Availability).all()

@router.post("/config", response_model=schemas.Availability)
async def update_availability_config(
    availability: schemas.AvailabilityCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Buscar si ya existe configuración para ese día
    db_avail = db.query(models.Availability).filter(
        models.Availability.day_of_week == availability.day_of_week
    ).first()

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
        models.Availability.active == True
    ).first()

    if not config:
        return []

    # 2. Verificar overrides (bloqueos o cambios de horario específicos)
    override = db.query(models.AvailabilityOverride).filter(
        models.AvailabilityOverride.date == date
    ).first()

    if override and override.is_blocked:
        return []

    start_str = override.start_time if (override and override.start_time) else config.start_time
    end_str = override.end_time if (override and override.end_time) else config.end_time
    duration = config.slot_duration

    # 3. Generar slots
    slots = []
    current_dt = datetime.strptime(f"{date} {start_str}", "%Y-%m-%d %H:%M")
    end_dt = datetime.strptime(f"{date} {end_str}", "%Y-%m-%d %H:%M")

    # 4. Obtener citas existentes para ese día
    existing_appointments = db.query(models.Appointment).filter(
        models.Appointment.date_time >= current_dt,
        models.Appointment.date_time < end_dt,
        models.Appointment.status != "cancelado"
    ).all()
    
    occupied_times = {appt.date_time.strftime("%H:%M") for appt in existing_appointments}

    while current_dt < end_dt:
        time_str = current_dt.strftime("%H:%M")
        slots.append(schemas.Slot(
            time=time_str,
            available=(time_str not in occupied_times)
        ))
        current_dt += timedelta(minutes=duration)

    return slots

@router.post("/overrides", response_model=schemas.AvailabilityOverride)
async def create_override(
    override: schemas.AvailabilityOverrideCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_override = db.query(models.AvailabilityOverride).filter(
        models.AvailabilityOverride.date == override.date
    ).first()

    if db_override:
        for key, value in override.dict().items():
            setattr(db_override, key, value)
    else:
        db_override = models.AvailabilityOverride(**override.dict())
        db.add(db_override)
    
    db.commit()
    db.refresh(db_override)
    return db_override
