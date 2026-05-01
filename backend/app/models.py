from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100))
    phone = Column(String(20))

# ... (Patient, Appointment, Availability, AvailabilityOverride, Payment models) ...

class ReminderConfig(Base):
    __tablename__ = "reminder_configs"
    id = Column(Integer, primary_key=True, index=True)
    twilio_sid = Column(String(100))
    twilio_token = Column(String(100))
    twilio_phone = Column(String(20))
    dentist_reminder_time = Column(String(5), default="07:00") # HH:MM
    patient_reminder_day_before_time = Column(String(5), default="19:00") # HH:MM
    patient_reminder_day_of_time = Column(String(5), default="08:00") # HH:MM
    is_active = Column(Boolean, default=True)
    last_run_dentist = Column(DateTime, nullable=True)
    last_run_patient_before = Column(DateTime, nullable=True)
    last_run_patient_today = Column(DateTime, nullable=True)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    reference = Column(String(255)) # "el señor de la esquina"
    
    # Datos Personales
    age = Column(Integer)
    sex = Column(String(20))
    ethnic_group = Column(String(50))
    occupation = Column(String(100))
    birth_date = Column(String(10)) # YYYY-MM-DD
    school_grade = Column(String(50))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(String(255))
    marital_status = Column(String(50))
    religion = Column(String(50))
    entry_date = Column(String(10)) # YYYY-MM-DD
    nationality = Column(String(50))
    locality = Column(String(100))
    consultation_reason = Column(Text)
    last_dental_consultation = Column(String(100))
    
    # Association
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    initial_budget = Column(Float, default=0.0)
    
    # Menor de edad
    minor_father_name = Column(String(150))
    minor_father_occupation = Column(String(100))
    minor_mother_name = Column(String(150))
    minor_mother_occupation = Column(String(100))
    minor_parents_marital_status = Column(String(50))
    minor_pediatrician = Column(String(150))
    
    # Signos Vitales
    weight = Column(Float)
    height = Column(Float)
    temperature = Column(Float)
    heart_rate = Column(Integer)
    respiratory_rate = Column(Integer)
    blood_pressure = Column(String(20))
    oxygen_saturation = Column(Integer)
    glucose = Column(Integer)
    
    # Examen Facial
    facial_profile = Column(String(50)) # Recto, Cóncavo, Convexo
    facial_front = Column(String(50)) # Braquifacial, Normofacial, Dolicofacial
    facial_particular_signs = Column(String(255))
    
    # Antecedentes (Almacenados como JSON para flexibilidad)
    family_history_json = Column(Text)
    non_pathological_history_json = Column(Text)
    pathological_history_json = Column(Text)
    
    # Odontograma y Notas
    odontogram_json = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="patient", cascade="all, delete-orphan")
    doctor = relationship("User")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    date_time = Column(DateTime, index=True)
    description = Column(String(255))
    treatment_details = Column(Text)
    cost = Column(Float, default=0.0)
    location = Column(String(100)) # "Oaxaca" o "Miahuatlán"
    status = Column(String(20), default="pendiente") # pendiente, atendido, cancelado

    patient = relationship("Patient", back_populates="appointments")

    # Índice único para evitar citas en el mismo horario
    __table_args__ = (
        Index("idx_appointment_datetime_unique", "date_time", unique=True),
    )

class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer) # 0=Lunes, 6=Domingo
    start_time = Column(String(5)) # "HH:MM"
    end_time = Column(String(5)) # "HH:MM"
    slot_duration = Column(Integer, default=30) # minutos
    location = Column(String(100)) # "Oaxaca" o "Miahuatlán"
    active = Column(Boolean, default=True)

class AvailabilityOverride(Base):
    __tablename__ = "availability_overrides"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10)) # "YYYY-MM-DD"
    start_time = Column(String(5), nullable=True)
    end_time = Column(String(5), nullable=True)
    slot_duration = Column(Integer, default=30)
    location = Column(String(100)) # "Oaxaca" o "Miahuatlán"
    is_blocked = Column(Boolean, default=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    amount = Column(Float)
    date = Column(DateTime(timezone=True), server_default=func.now())
    method = Column(String(50)) # efectivo, tarjeta, transferencia
    description = Column(String(255))

    patient = relationship("Patient", back_populates="payments")
