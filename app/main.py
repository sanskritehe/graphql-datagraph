from fastapi import FastAPI
from app.routes import appointments, patients

app = FastAPI(title="Appointment Service")

app.include_router(appointments.router)
app.include_router(patients.router)