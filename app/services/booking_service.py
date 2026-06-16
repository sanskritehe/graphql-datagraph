from app.db_client import create_appointment, get_all_appointments, get_appointment_by_id, update_appointment, cancel_appointment, check_slot_availability
from fastapi import HTTPException
from requests.exceptions import HTTPError
from app.models import AppointmentUpdate


def create_simple_appointment(data):
    """Create appointment with simple format (user, time) - KAN-17"""
    if not data.get("user") or not data.get("time"):
        raise HTTPException(status_code=400, detail="Missing required fields: user, time")
    return create_appointment(data)

def validate_and_book_appointment(data):
    doctor_id = data.get("doctor_id")
    appointment_date = data.get("appointment_date")
    time_slot = data.get("time_slot")
    
    # Check if time slot is available
    if not check_slot_availability(doctor_id, appointment_date, time_slot):
        raise HTTPException(status_code=409, detail="Time slot already booked")
    
    # Create appointment if slot is available
    return create_appointment(data)

def list_appointments():
    return get_all_appointments()

def get_appointment(appointment_id: int):
    try:
        return get_appointment_by_id(appointment_id)
    except HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Appointment not found")
        raise

def update_booking(appointment_id: int, data: dict):
    try:
        appointment = get_appointment_by_id(appointment_id)
    except HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Appointment not found")
        raise

    if appointment["status"] == "booked" and data.get("status") not in ["confirmed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status transition from booked")
    elif appointment["status"] == "confirmed" and data.get("status") not in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status transition from confirmed")
    elif appointment["status"] == "cancelled" and data.get("status") not in ["booked", "confirmed", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status transition from cancelled")
    elif appointment["status"] == "completed" and data.get("status") not in ["completed"]:
        raise HTTPException(status_code=400, detail="Invalid status transition from completed")

    return update_appointment(appointment_id, data)

def cancel_booking(appointment_id: int):
    try:
        cancel_appointment(appointment_id)
        return {
            "message": "Appointment deleted successfully",
            "appointment_id": appointment_id
        }
    except HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Appointment not found")
        raise

def patch_booking_status(appointment_id: int, data: dict):
    try:
        appointment = get_appointment_by_id(appointment_id)
    except HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Appointment not found")
        raise

    if appointment["status"] == "booked" and data.get("status") not in ["confirmed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status transition from booked")
    elif appointment["status"] == "confirmed" and data.get("status") not in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status transition from confirmed")
    elif appointment["status"] == "cancelled" and data.get("status") not in ["booked", "confirmed", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status transition from cancelled")
    elif appointment["status"] == "completed" and data.get("status") not in ["completed"]:
        raise HTTPException(status_code=400, detail="Invalid status transition from completed")

    data = AppointmentUpdate(status=data.get("status")).dict(exclude_unset=True)
    return update_appointment(appointment_id, data)

