from pydantic import BaseModel, Field
from enum import Enum


class AppointmentStatus(str, Enum):
    """Appointment status enumeration per Confluence spec"""
    booked = "booked"
    cancelled = "cancelled"
    completed = "completed"


class AppointmentCreate(BaseModel):
    user: str
    time: str


class AppointmentSimpleCreate(BaseModel):
    """Request model for POST /appointments endpoint (KAN-17)"""
    user: str
    time: str

    class Config:
        schema_extra = {
            "example": {
                "user": "John Doe",
                "time": "2024-04-07T10:00:00Z"
            }
        }


class AppointmentBookingCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: str
    time_slot: str

class AppointmentUpdate(BaseModel):
    """Request model for PUT /appointments/{id} endpoint (KAN-17)"""
    time: str = Field(..., description="Appointment time in ISO format")
    status: AppointmentStatus = Field(..., description="Appointment status")

    class Config:
        schema_extra = {
            "example": {
                "time": "2024-04-07T11:00:00Z",
                "status": "booked"
            }
        }

class AppointmentResponse(BaseModel):
    """Response model for appointment endpoints per Confluence spec"""
    id: int
    user: str
    time: str
    status: AppointmentStatus

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "user": "John Doe",
                "time": "2024-04-07T10:00:00Z",
                "status": "booked"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model per Confluence spec"""
    detail: str

    class Config:
        schema_extra = {
            "example": {
                "detail": "Appointment not found"
            }
        }


class AppointmentDeleteResponse(BaseModel):
    """Response model for DELETE /appointments/{id} endpoint per Confluence spec"""
    message: str
    appointment_id: int

    class Config:
        schema_extra = {
            "example": {
                "message": "Appointment deleted successfully",
                "appointment_id": 1
            }
        }


class PatientCreate(BaseModel):
    name: str
    age: int
    blood_group: str
    contact: str


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    blood_group: str
    contact: str