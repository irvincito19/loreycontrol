from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# User Schemas
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# Reminder Config Schemas
class ReminderConfigBase(BaseModel):
    twilio_sid: Optional[str] = None
    twilio_token: Optional[str] = None
    twilio_phone: Optional[str] = None
    dentist_reminder_time: str = "07:00"
    patient_reminder_day_before_time: str = "19:00"
    patient_reminder_day_of_time: str = "08:00"
    is_active: bool = True

class ReminderConfigCreate(ReminderConfigBase):
    pass

class ReminderConfig(ReminderConfigBase):
    id: int
    last_run_dentist: Optional[datetime] = None
    last_run_patient_before: Optional[datetime] = None
    last_run_patient_today: Optional[datetime] = None

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Patient Schemas
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    reference: Optional[str] = None
    
    # Datos Personales
    age: Optional[int] = None
    sex: Optional[str] = None
    ethnic_group: Optional[str] = None
    occupation: Optional[str] = None
    birth_date: Optional[str] = None
    school_grade: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    marital_status: Optional[str] = None
    religion: Optional[str] = None
    entry_date: Optional[str] = None
    nationality: Optional[str] = None
    locality: Optional[str] = None
    consultation_reason: Optional[str] = None
    last_dental_consultation: Optional[str] = None
    
    # Menor de edad
    minor_father_name: Optional[str] = None
    minor_father_occupation: Optional[str] = None
    minor_mother_name: Optional[str] = None
    minor_mother_occupation: Optional[str] = None
    minor_parents_marital_status: Optional[str] = None
    minor_pediatrician: Optional[str] = None
    
    # Signos Vitales
    weight: Optional[float] = None
    height: Optional[float] = None
    temperature: Optional[float] = None
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    blood_pressure: Optional[str] = None
    oxygen_saturation: Optional[int] = None
    glucose: Optional[int] = None
    
    # Examen Facial
    facial_profile: Optional[str] = None
    facial_front: Optional[str] = None
    facial_particular_signs: Optional[str] = None
    
    # Antecedentes (JSON)
    family_history_json: Optional[str] = None
    non_pathological_history_json: Optional[str] = None
    pathological_history_json: Optional[str] = None
    
    # Association
    doctor_id: Optional[int] = None
    initial_budget: Optional[float] = 0.0
    
    # Odontograma y Notas
    odontogram_json: Optional[str] = None
    notes: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: datetime
    doctor: Optional[User] = None

    class Config:
        from_attributes = True

# Appointment Schemas
class AppointmentBase(BaseModel):
    patient_id: int
    date_time: datetime
    description: Optional[str] = None
    treatment_details: Optional[str] = None
    cost: Optional[float] = 0.0
    location: Optional[str] = None
    status: Optional[str] = "pendiente"

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    patient: Optional[Patient] = None

    class Config:
        from_attributes = True


# Payment Schemas
class PaymentBase(BaseModel):
    patient_id: int
    amount: float
    method: str
    description: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True

# Aggregate Schemas
class PatientDetail(Patient):
    appointments: List[Appointment] = []
    payments: List[Payment] = []

    class Config:
        from_attributes = True

# Availability Schemas
class AvailabilityBase(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    slot_duration: int = 30
    location: str
    active: bool = True

class AvailabilityCreate(AvailabilityBase):
    pass

class Availability(AvailabilityBase):
    id: int

    class Config:
        from_attributes = True

class IntervalBase(BaseModel):
    start_time: str
    end_time: str
    slot_duration: int = 30

class AvailabilityOverrideBase(BaseModel):
    date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    slot_duration: int = 30
    location: str
    is_blocked: bool = False

class AvailabilityOverrideCreate(AvailabilityOverrideBase):
    pass

class AvailabilityOverride(AvailabilityOverrideBase):
    id: int

    class Config:
        from_attributes = True

class DayAvailabilityUpdate(BaseModel):
    date: str
    intervals: List[IntervalBase]
    is_blocked: bool = False

class Slot(BaseModel):
    time: str
    available: bool
