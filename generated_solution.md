### FILE: app/graphql_schema.py
```python
import strawberry
from typing import Optional
from app.database import SessionLocal
from app.models import AppointmentDB
from app.services.booking_service import (
    get_appointment_by_id as get_appointment_by_id_service,
)


@strawberry.type
class AppointmentStorage:
    id: int
    user: str
    time: str
    status: str


@strawberry.type
class Appointment:
    id: int
    patientName: str
    doctorName: str
    date: str
    status: str


@strawberry.type
class Query:
    @strawberry.field
    def appointment_record(self, id: int) -> Optional[AppointmentStorage]:
        db = SessionLocal()
        try:
            appointment = db.query(AppointmentDB).filter(AppointmentDB.id == id).first()  # type: ignore
            if appointment:
                return AppointmentStorage(
                    id=appointment.id,
                    user=appointment.user,
                    time=appointment.time,
                    status=appointment.status,
                )
            return None
        finally:
            db.close()

    @strawberry.field
    def appointment(self, id: int) -> Optional[Appointment]:
        appointment = get_appointment_by_id_service(appointment_id=id)
        if not appointment:
            return None
        return Appointment(
            id=appointment["id"],
            patientName=appointment["user"],
            doctorName=appointment["time"],
            date=appointment["status"],
            status=appointment["status"],
        )


schema = strawberry.Schema(query=Query)

```

### FILE: app/routes/appointments.py
```python
from fastapi import APIRouter, HTTPException, Path
from app.models import AppointmentResponse
from app.db_client import delete_appointment
from app.graphql_client import run_query

router = APIRouter(prefix="/appointments", tags=["Appointment"])


# Existing GET endpoint
@router.get("/{appointment_id}", response_model=AppointmentResponse)
def read_appointment(
    appointment_id: int = Path(..., title="The ID of the appointment", gt=0),
):
    existing_appointment = run_query(
        """
    query ($id: Int!) {
        appointment(id: $id) {
            id
            user
            time
            status
        }
    }
    """,
        {"id": appointment_id},
    )

    if existing_appointment.get("data", {}).get("appointment") is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return AppointmentResponse(**existing_appointment["data"]["appointment"])


# Updated DELETE endpoint
@router.delete("/{appointment_id}")
def delete_appointment_endpoint(
    appointment_id: int = Path(..., title="The ID of the appointment", gt=0),
):
    appointment = run_query(
        """
    query ($id: Int!) {
        appointment(id: $id) {
            id
        }
    }
    """,
        {"id": appointment_id},
    )

    if appointment.get("data", {}).get("appointment") is None:
        raise HTTPException(status_code=404, detail={"detail": "Appointment not found"})

    delete_appointment(appointment_id)

    return {
        "message": "Appointment deleted successfully",
        "appointment_id": appointment_id,
    }

```

### FILE: tests/test_graphql.py
```python
import pytest
from app.graphql_client import run_query

def test_get_appointment_success():
    query = """
    query ($id: Int!) {
        appointment(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    variables = {"id": 1}
    response = run_query(query, variables)
    assert response['data']['appointment'] is not None
    assert response['data']['appointment']['id'] == 1

def test_get_appointment_not_found():
    query = """
    query ($id: Int!) {
        appointment(id: $id) {
            id
        }
    }
    """
    variables = {"id": 9999}
    response = run_query(query, variables)
    assert response['data']['appointment'] is None

```