from fastapi import APIRouter
from app.models import PatientCreate
from app.services.patient_service import (
    register_patient,
    list_patients,
    get_patient,
    remove_patient
)

router = APIRouter(prefix="/patients", tags=["Patient"])


# Register a new patient
@router.post("/")
def create_patient(req: PatientCreate):
    return register_patient(req.dict())


# Get all patients
@router.get("/")
def get_all_patients():
    return list_patients()


# Get a specific patient by ID
@router.get("/{patient_id}")
def get_patient_by_id(patient_id: int):
    return get_patient(patient_id)


# Delete a patient by ID
@router.delete("/{patient_id}")
def delete_patient_by_id(patient_id: int):
    return remove_patient(patient_id)
