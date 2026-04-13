from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="patient", cascade="all, delete-orphan")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    date_time = Column(DateTime, index=True)
    description = Column(String)
    status = Column(String, default="pendiente") # pendiente, atendido, cancelado

    patient = relationship("Patient", back_populates="appointments")

    # Índice único para evitar citas en el mismo horario
    __table_args__ = (
        Index("idx_appointment_datetime_unique", "date_time", unique=True),
    )

class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer) # 0=Lunes, 6=Domingo
    start_time = Column(String) # "HH:MM"
    end_time = Column(String) # "HH:MM"
    slot_duration = Column(Integer, default=30) # minutos
    active = Column(Boolean, default=True)

class AvailabilityOverride(Base):
    __tablename__ = "availability_overrides"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String) # "YYYY-MM-DD"
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)
    is_blocked = Column(Boolean, default=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    amount = Column(Float)
    date = Column(DateTime(timezone=True), server_default=func.now())
    method = Column(String) # efectivo, tarjeta, transferencia
    description = Column(String)

    patient = relationship("Patient", back_populates="payments")
