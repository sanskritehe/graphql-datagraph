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
    user: str
    time: str
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
            user=appointment["user"],
            time=appointment["time"],
            status=appointment["status"],
        )


schema = strawberry.Schema(query=Query)

```

### FILE: app/routes/appointments.py
```python
from fastapi import APIRouter, HTTPException, Path
from app.models import AppointmentResponse
from app.graphql_client import run_query

router = APIRouter(prefix="/appointments", tags=["Appointment"])


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def read_appointment(
    appointment_id: int = Path(..., title="The ID of the appointment to fetch", gt=0),
):
    """
    GET /appointments/{appointment_id}
    Fetches an appointment by ID.

    Path Parameters:
    - appointment_id (int): Positive integer representing the appointment ID.

    Responses:
    - 200: Successful retrieval of the appointment.
    - 404: Appointment not found.
    """
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
    variables = {"id": appointment_id}
    appointment_data = run_query(query, variables)

    if appointment_data.get("data", {}).get("appointment") is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return AppointmentResponse(**appointment_data["data"]["appointment"])

```

### FILE: tests/test_graphql.py
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_appointment_success():
    response = client.get("/appointments/1")
    assert response.status_code == 200
    assert "id" in response.json()


def test_read_appointment_not_found():
    response = client.get("/appointments/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Appointment not found"}

```