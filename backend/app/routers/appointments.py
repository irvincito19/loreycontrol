from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from .. import models, schemas, auth, database

router = APIRouter(prefix="/appointments", tags=["Citas"])

@router.get("/", response_model=List[schemas.Appointment])
async def get_appointments(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    location: Optional[str] = None
):
    query = db.query(models.Appointment)
    if start_date:
        query = query.filter(models.Appointment.date_time >= start_date)
    if end_date:
        query = query.filter(models.Appointment.date_time <= end_date)
    if location:
        query = query.filter(models.Appointment.location == location)
    return query.order_by(models.Appointment.date_time.asc()).all()

@router.post("/", response_model=schemas.Appointment)
async def create_appointment(
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verificar que el paciente exista
    db_patient = db.query(models.Patient).filter(models.Patient.id == appointment.patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Verificar disponibilidad (concurrencia y traslapes)
    # Cada cita se asume de 30 minutos
    new_start = appointment.date_time
    new_end = new_start + timedelta(minutes=30)
    
    # Buscar cualquier cita que se traslape
    # (Existing_Start < New_End) AND (New_Start < Existing_End)
    
    day_start = new_start.replace(hour=0, minute=0, second=0)
    day_end = new_start.replace(hour=23, minute=59, second=59)
    
    existing_appointments = db.query(models.Appointment).filter(
        models.Appointment.date_time >= day_start - timedelta(minutes=60), # Margen amplio
        models.Appointment.date_time <= day_end,
        models.Appointment.status != "cancelado"
    ).all()
    
    for existing in existing_appointments:
        ex_start = existing.date_time
        ex_end = ex_start + timedelta(minutes=30)
        
        if max(new_start, ex_start) < min(new_end, ex_end):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Conflicto de horario: Ya existe una cita en {existing.location} que se traslapa con este horario."
            )
        
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al guardar la cita: Posible conflicto de horario")
        
    db.refresh(db_appointment)
    return db_appointment

@router.put("/{appointment_id}", response_model=schemas.Appointment)
async def update_appointment(
    appointment_id: int,
    appointment_update: schemas.AppointmentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    for key, value in appointment_update.dict().items():
        setattr(db_appointment, key, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    
    db.delete(db_appointment)
    db.commit()
    return None
