from fastapi import FastAPI
from app.routes.appointments import router as appointments_router

app = FastAPI(title="Appointment Service")

# Include Appointments routes
app.include_router(appointments_router)
