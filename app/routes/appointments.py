from fastapi import APIRouter, status, HTTPException
from app.models import (
    AppointmentUpdate, AppointmentBookingCreate, AppointmentSimpleCreate, 
    AppointmentResponse, ErrorResponse, AppointmentDeleteResponse
)
from app.services.booking_service import (
    list_appointments,
    get_appointment,
    update_booking,
    cancel_booking,
    validate_and_book_appointment,
    create_simple_appointment,
    patch_booking_status
)

router = APIRouter(prefix="/appointments", tags=["Appointment"])


# Book an appointment with simple request format (KAN-17)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AppointmentResponse)
def create_appointment_simple(req: AppointmentSimpleCreate):
    """Create a new appointment with user and time information. Returns 201 Created."""
    return create_simple_appointment(req.dict())


# Book an appointment with full details (KAN-23)
@router.post("/appointments", status_code=status.HTTP_201_CREATED, response_model=AppointmentResponse)
def book_appointment(req: AppointmentBookingCreate):
    """Create a new appointment with full details (patient, doctor, date, time slot). Returns 201 Created."""
    try:
        return validate_and_book_appointment(req.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get all appointments
@router.get("/", response_model=list)
def get_appointments():
    """Retrieve all appointments."""
    return list_appointments()


# Get a single appointment by ID
@router.get("/{appointment_id}", response_model=AppointmentResponse, status_code=status.HTTP_200_OK,
            responses={404: {"model": ErrorResponse, "description": "Appointment not found"}})
def get_appointment_by_id(appointment_id: int):
    """
    Retrieve a single appointment by ID.
    
    - **appointment_id**: The appointment ID (path parameter)
    - Returns: Appointment object with id, user, time, status
    - Returns 404 if appointment not found
    """
    return get_appointment(appointment_id)


# Update an appointment by ID (KAN-17 - PUT endpoint per Confluence spec)
@router.put("/{appointment_id}", response_model=AppointmentResponse, status_code=status.HTTP_200_OK,
            responses={404: {"model": ErrorResponse, "description": "Appointment not found"}})
def update_appointment_by_id(appointment_id: int, req: AppointmentUpdate):
    """
    Update an appointment by ID per Confluence API spec.
    
    - **appointment_id**: The appointment ID (path parameter)
    - **Request body**: {time, status} fields to update
    - Returns: Updated appointment object with id, user, time, status
    - Returns 404 if appointment not found
    """
    return update_booking(appointment_id, req.dict())


# Patch an appointment by ID (KAN-22 - PATCH endpoint per Confluence spec)
@router.patch("/{appointment_id}/status", response_model=AppointmentResponse, status_code=status.HTTP_200_OK,
               responses={404: {"model": ErrorResponse, "description": "Appointment not found"},
                          400: {"model": ErrorResponse, "description": "Invalid status transition or request body"}})
def patch_appointment_status(appointment_id: int, req: dict):
    """
    Patch an appointment by ID per Confluence API spec.
    
    - **appointment_id**: The appointment ID (path parameter)
    - **Request body**: {status} field to update
    - Returns: Updated appointment object with id, user, time, status
    - Returns 404 if appointment not found
    - Returns 400 with {"detail": "Invalid status transition"} if transition is not allowed
    - Returns 400 with {"detail": "Invalid request body"} if request body is invalid
    """
    if not req or "status" not in req or len(req) > 1:
        raise HTTPException(status_code=400, detail="Invalid request body")
    return patch_booking_status(appointment_id, req)


# Delete an appointment by ID (KAN-18 - DELETE endpoint per Confluence spec)
@router.delete("/{appointment_id}", response_model=AppointmentDeleteResponse, status_code=status.HTTP_200_OK,
            responses={404: {"model": ErrorResponse, "description": "Appointment not found"}})
def cancel_appointment_by_id(appointment_id: int):
    """
    Delete an appointment by ID per Confluence API spec.
    
    - **appointment_id**: The appointment ID (path parameter)
    - Returns: {"message": "Appointment deleted successfully", "appointment_id": <id>}
    - Returns 404 with {"detail": "Appointment not found"} if appointment does not exist
    """
    return cancel_booking(appointment_id)

