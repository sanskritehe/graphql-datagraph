from app.db_client import create_patient, get_all_patients, get_patient_by_id, delete_patient


def register_patient(data):
    return create_patient(data)


def list_patients():
    return get_all_patients()


def get_patient(patient_id: int):
    return get_patient_by_id(patient_id)


def remove_patient(patient_id: int):
    return delete_patient(patient_id)
