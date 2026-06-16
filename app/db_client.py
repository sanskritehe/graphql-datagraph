import requests
from app.config import DB_SERVICE_URL

def create_appointment(data: dict):
    response = requests.post(
        f"{DB_SERVICE_URL}/appointments",
        json=data
    )
    response.raise_for_status()
    return response.json()

def check_slot_availability(doctor_id: int, appointment_date: str, time_slot: str):
    response = requests.get(
        f"{DB_SERVICE_URL}/appointments",
        params={"doctor_id": doctor_id, "appointment_date": appointment_date, "time_slot": time_slot}
    )
    response.raise_for_status()
    appointments = response.json()
    return len(appointments) == 0

def get_all_appointments():
    response = requests.get(f"{DB_SERVICE_URL}/appointments")
    response.raise_for_status()
    return response.json()

def get_appointment_by_id(appointment_id: int):
    response = requests.get(f"{DB_SERVICE_URL}/appointments/{appointment_id}")
    response.raise_for_status()
    return response.json()

def update_appointment(appointment_id: int, data: dict):
    response = requests.put(
        f"{DB_SERVICE_URL}/appointments/{appointment_id}",
        json=data
    )
    response.raise_for_status()
    return response.json()

def cancel_appointment(appointment_id: int):
    response = requests.delete(
        f"{DB_SERVICE_URL}/appointments/{appointment_id}"
    )
    response.raise_for_status()
    return response.json()


def create_patient(data: dict):
    response = requests.post(
        f"{DB_SERVICE_URL}/patients",
        json=data
    )
    response.raise_for_status()
    return response.json()


def get_all_patients():
    response = requests.get(f"{DB_SERVICE_URL}/patients")
    response.raise_for_status()
    return response.json()


def get_patient_by_id(patient_id: int):
    response = requests.get(f"{DB_SERVICE_URL}/patients/{patient_id}")
    response.raise_for_status()
    return response.json()


def delete_patient(patient_id: int):
    response = requests.delete(f"{DB_SERVICE_URL}/patients/{patient_id}")
    response.raise_for_status()
    return response.json()