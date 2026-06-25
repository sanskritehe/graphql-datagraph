### FILE: app/graphql_schema.py
```python
import strawberry
from typing import Optional
from app.database import SessionLocal
from app.models import AppointmentDB
from app.services.booking_service import get_appointment_by_id as get_appointment_by_id_service

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
            appointment = db.query(AppointmentDB).filter(AppointmentDB.id == id).first()
            if appointment:
                return AppointmentStorage(
                    id=appointment.id,
                    user=appointment.user,
                    time=appointment.time,
                    status=appointment.status
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
            status=appointment["status"]
        )

schema = strawberry.Schema(query=Query)
```

### FILE: app/routes/appointments.py
```python
from fastapi import APIRouter, HTTPException, Path, Depends
from typing import List
from app.models import AppointmentResponse
from app.graphql_client import run_query

router = APIRouter(prefix="/appointments", tags=["Appointment"])

def get_list_service():
    import app.services.booking_service as booking_service
    return booking_service.list_appointments

def get_delete_service():
    import app.services.booking_service as booking_service
    return booking_service.delete_appointment_service

@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(list_service=Depends(get_list_service)):
    try:
        appointments = list_service()
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve appointments: {str(e)}")

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int = Path(..., title="The ID of the appointment to fetch", gt=0)
):
    """
    GET /appointments/{appointment_id}
    Fetches an appointment by ID using the GraphQL Datagraph.

    Path Parameters:
    - appointment_id (int): Positive integer representing the appointment ID.

    Responses:
    - 200: Successful retrieval.
    - 404: Appointment not found.
    - 500: Internal server error.
    """
    query = """
    query GetAppointment($id: Int!) {
        appointment(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    try:
        res = run_query(query, {"id": appointment_id})
        if "errors" in res and res["errors"]:
            error_msg = res["errors"][0].get("message", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Appointment not found")
            raise HTTPException(status_code=500, detail=error_msg)
        
        data = res.get("data")
        if not data or not data.get("appointment"):
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return data["appointment"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve appointment: {str(e)}")

@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(
    appointment_id: int = Path(..., title="The ID of the appointment to delete", gt=0),
    delete_service=Depends(get_delete_service),
):
    """
    DELETE /appointments/{appointment_id}
    Performs a hard delete of an appointment by ID.

    Path Parameters:
    - appointment_id (int): Positive integer representing the appointment ID.

    Responses:
    - 204: No Content on successful deletion.
    - 404: Appointment not found.
    - 500: Internal server error.
    """
    try:
        deleted = delete_service(appointment_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail={"message": "Appointment not found", "code": "not_found"},
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete appointment: {str(e)}")
```

### FILE: tests/test_graphql.py
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_appointment():
    response = client.get("/appointments/1")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "user" in response.json()
    assert "time" in response.json()
    assert "status" in response.json()

def test_read_non_existent_appointment():
    response = client.get("/appointments/999")
    assert response.status_code == 404

def test_read_appointment_invalid_id():
    response = client.get("/appointments/0")
    assert response.status_code == 422  # Unprocessable Entity for invalid input
```