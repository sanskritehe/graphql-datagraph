### FILE: app/graphql_schema.py
```python
import strawberry
from typing import Optional
from app.services.booking_service import (
    get_appointment_by_id as get_appointment_by_id_service,
)


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
    def getAppointment(self, id: int) -> Optional[Appointment]:
        appointment = get_appointment_by_id_service(appointment_id=id)
        if not appointment:
            raise Exception("Appointment not found")
        return Appointment(
            id=appointment["id"],
            patientName=appointment["patientName"],
            doctorName=appointment["doctorName"],
            date=appointment["date"],
            status=appointment["status"],
        )

```

### FILE: app/routes/appointments.py
```python
from fastapi import APIRouter, HTTPException, Path
from app.models import AppointmentResponse
from app.graphql_client import run_query

router = APIRouter(prefix="/appointments", tags=["Appointment"])


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def read_appointment(
    appointment_id: int = Path(..., title="The ID of the appointment", gt=0),
):
    """
    GET /appointments/{appointment_id}
    Retrieves an appointment by ID.

    Path Parameters:
    - appointment_id (int): Positive integer representing the appointment ID.

    Responses:
    - 200: Successful retrieval of the appointment.
    - 404: Appointment not found.
    """
    existing_appointment = run_query(
        """
    query ($id: Int!) {
        getAppointment(id: $id) {
            id
            patientName
            doctorName
            date
            status
        }
    }
    """,
        {"id": appointment_id},
    )

    if existing_appointment.get("data", {}).get("getAppointment") is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return AppointmentResponse(**existing_appointment["data"]["getAppointment"])

```

### FILE: tests/test_graphql.py
```python
import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_appointment_success():
    response = client.get("/appointments/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "patientName" in data
    assert "doctorName" in data
    assert "date" in data
    assert "status" in data


def test_get_appointment_not_found():
    response = client.get("/appointments/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Appointment not found"}

```