from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth, database

router = APIRouter(prefix="/payments", tags=["Pagos"])

@router.get("/", response_model=List[schemas.Payment])
async def get_payments(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Payment).all()

@router.post("/", response_model=schemas.Payment)
async def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verificar que el paciente exista
    db_patient = db.query(models.Patient).filter(models.Patient.id == payment.patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@router.get("/patient/{patient_id}", response_model=List[schemas.Payment])
async def get_payments_by_patient(
    patient_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Payment).filter(models.Payment.patient_id == patient_id).all()
