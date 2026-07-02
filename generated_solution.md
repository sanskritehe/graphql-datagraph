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

### FILE: app/graphql/schema.py
```python
import strawberry
from app.graphql.resolvers import resolve_appointment_record
from typing import Optional


@strawberry.type
class AppointmentStorage:
    id: int
    user: str
    time: str
    status: str


@strawberry.type
class Query:
    @strawberry.field
    def appointment_record(self, id: int) -> Optional[AppointmentStorage]:
        appointment = resolve_appointment_record(id=id)
        if not appointment:
            return None
        return AppointmentStorage(
            id=appointment.id,
            user=appointment.user,
            time=appointment.time,
            status=appointment.status,
        )

    @strawberry.field
    def getAppointment(self, id: int) -> Optional[AppointmentStorage]:
        appointment = resolve_appointment_record(id=id)
        if not appointment:
            return None
        return AppointmentStorage(
            id=appointment.id,
            user=appointment.user,
            time=appointment.time,
            status=appointment.status,
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

### FILE: app/services/booking_service.py
```python
from typing import List, Optional
from app.db_client import (
    get_all_appointments,
    get_appointment_by_id as db_get_appointment_by_id,
    delete_appointment_by_id as db_delete_appointment_by_id,
)


def list_appointments() -> List[dict]:
    return get_all_appointments()


def get_appointment_by_id(appointment_id: int) -> Optional[dict]:
    return db_get_appointment_by_id(appointment_id)


def delete_appointment_by_id(appointment_id: int) -> Optional[dict]:
    return db_delete_appointment_by_id(appointment_id)
```

### FILE: tests/test_graphql.py
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_appointment_success():
    response = client.get("/appointments/1")
    assert response.status_code == 200
    assert "id" in response.json()


def test_get_appointment_not_found():
    response = client.get("/appointments/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Appointment not found"}

```