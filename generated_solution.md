### FILE: app/graphql_schema.py
```python
from typing import Optional
from app.models import AppointmentStorage
from app.services.booking_service import get_appointment
from sqlalchemy.orm import Session
from app.database import SessionLocal

class Query:
    def appointment_record(self, id: int) -> Optional[AppointmentStorage]:
        db: Session = SessionLocal()
        appointment = db.query(AppointmentStorage).filter(AppointmentStorage.id == id).first()
        return appointment
        
    def appointment(self, id: int) -> Optional[Appointment]:
        return get_appointment(id)

```

### FILE: app/routes/appointments.py
```python
from fastapi import APIRouter, HTTPException, Path
from app.graphql_client import run_query
from pydantic import BaseModel

router = APIRouter()

class AppointmentResponse(BaseModel):
    id: int
    user: str
    time: str
    status: str

@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def read_appointment(appointment_id: int = Path(..., gt=0)):
    query = """
    query getAppointment($id: Int!) {
        appointment(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    appointment = await run_query(query, {'id': appointment_id})
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

```