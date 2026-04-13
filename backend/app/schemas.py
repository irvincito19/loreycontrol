from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# User Schemas
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

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
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Appointment Schemas
class AppointmentBase(BaseModel):
    patient_id: int
    date_time: datetime
    description: Optional[str] = None
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
    active: bool = True

class AvailabilityCreate(AvailabilityBase):
    pass

class Availability(AvailabilityBase):
    id: int

    class Config:
        from_attributes = True

class AvailabilityOverrideBase(BaseModel):
    date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_blocked: bool = False

class AvailabilityOverrideCreate(AvailabilityOverrideBase):
    pass

class AvailabilityOverride(AvailabilityOverrideBase):
    id: int

    class Config:
        from_attributes = True

class Slot(BaseModel):
    time: str
    available: bool
