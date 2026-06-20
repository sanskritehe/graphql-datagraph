### FILE: app/database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### FILE: app/models.py
```python
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from app.database import Base, engine

class AppointmentDB(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    time = Column(String)
    status = Column(String, default="Scheduled")

# Ensure table exists in SQLite database
Base.metadata.create_all(bind=engine)

class AppointmentCreate(BaseModel):
    user: str
    time: str

class AppointmentUpdate(BaseModel):
    time: str

class AppointmentResponse(BaseModel):
    id: int
    user: str
    time: str
    status: str
```

### FILE: app/graphql_schema.py
```python
import strawberry
from typing import Optional
from app.services.booking_service import get_appointment_by_id as get_appointment_by_id_service
from app.database import SessionLocal
from app.models import AppointmentDB

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
    
    @strawberry.field
    def appointmentById(self, id: int) -> Optional[Appointment]:
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

### FILE: app/graphql/resolvers.py
```python
import strawberry
from app.services.booking_service import get_appointment_by_id as get_appointment_by_id_service
from app.services.github_service import list_microsoft_repos_service
from strawberry.exceptions import GraphQLError


@strawberry.type
class GraphQLErrorType(Exception):
    message: str


def resolve_appointment_by_id(id: int):
    appointment = get_appointment_by_id_service(appointment_id=id)
    if not appointment:
        raise GraphQLError("Appointment not found")
    return appointment


def resolve_microsoft_repos():
    return list_microsoft_repos_service()
```

### FILE: app/graphql/schema.py
```python
import strawberry
from app.graphql.resolvers import resolve_appointment_by_id, resolve_microsoft_repos
from typing import Optional

@strawberry.type
class Appointment:
    id: int
    user: str
    time: str
    status: str

@strawberry.type
class Repository:
    id: int
    name: str
    html_url: str = strawberry.field(name="html_url")
    description: str
    language: str

@strawberry.type
class Query:
    @strawberry.field
    def appointmentById(self, id: int) -> Optional[Appointment]:
        appointment = resolve_appointment_by_id(id=id)
        return Appointment(
            id=appointment["id"],
            user=appointment["user"],
            time=appointment["time"],
            status=appointment["status"]
        )
    
    @strawberry.field
    def appointment(self, id: int) -> Optional[Appointment]:
        appointment = resolve_appointment_by_id(id=id)
        return Appointment(
            id=appointment["id"],
            user=appointment["user"],
            time=appointment["time"],
            status=appointment["status"]
        )
    
    @strawberry.field
    def microsoftRepos(self) -> list[Repository]:
        repos = resolve_microsoft_repos()
        return [
            Repository(
                id=repo["id"],
                name=repo["name"],
                html_url=repo["html_url"],
                description=repo["description"],
                language=repo["language"]
            )
            for repo in repos
        ]

schema = strawberry.Schema(query=Query)
```

### FILE: app/db_client.py
```python
from typing import List, Optional
import requests
from app.config import settings


def get_all_appointments() -> List[dict]:
    try:
        response = requests.get(f"{settings.DB_SERVICE_URL}/appointments")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch appointments from DB service: {str(e)}") from e


def get_appointment_by_id(appointment_id: int) -> Optional[dict]:
    try:
        response = requests.get(f"{settings.DB_SERVICE_URL}/appointments/{appointment_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch appointment from DB service: {str(e)}") from e


def delete_appointment(appointment_id: int) -> bool:
    """
    Perform a hard delete of the appointment record from the database.

    Args:
        appointment_id (int): ID of the appointment to be deleted.

    Returns:
        bool: True if the record was successfully deleted, False if not found.
    """
    try:
        response = requests.delete(f"{settings.DB_SERVICE_URL}/appointments/{appointment_id}")
        if response.status_code == 404:
            return False
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to delete appointment from DB service: {str(e)}") from e


def get_microsoft_repos() -> List[dict]:
    """
    Fetch the public repositories from Microsoft's GitHub organization.

    Returns:
        List[dict]: A list of repositories.
    """
    try:
        response = requests.get("https://api.github.com/orgs/microsoft/repos")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch Microsoft repositories: {str(e)}") from e
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


@router.get("/{id}", response_model=AppointmentResponse)
def get_appointment(
    id: int = Path(..., title="The ID of the appointment to fetch", ge=1)
):
    """
    GET /appointments/{id}
    Fetches an appointment by ID using the GraphQL Datagraph.

    Path Parameters:
    - id (int): Positive integer representing the appointment ID.

    Responses:
    - 200: Successful retrieval.
    - 404: Appointment not found.
    - 500: Internal server error.
    """
    query = """
    query GetAppointment($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    try:
        res = run_query(query, {"id": id})
        if "errors" in res and res["errors"]:
            error_msg = res["errors"][0].get("message", "")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail="Appointment not found")
            raise HTTPException(status_code=500, detail=error_msg)
        
        data = res.get("data")
        if not data or not data.get("appointmentById"):
            raise HTTPException(status_code=404, detail="Appointment not found")
            
        return data["appointmentById"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve appointment: {str(e)}")


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(
    appointment_id: int = Path(..., title="The ID of the appointment to delete", ge=1),
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

### FILE: graphql-datagraph/appointment-service.graphql
```graphql
type Query {
  appointmentById(id: Int!): Appointment
  appointment(id: Int!): Appointment
}

type Appointment {
  id: Int!
  user: String!
  time: String!
  status: String!
}
```

### FILE: graphql-datagraph/appointment-db-service.graphql
```graphql
type Query {
  appointment_record(id: Int!): AppointmentStorage
}

type AppointmentStorage {
  id: Int!
  user: String!
  time: String!
  status: String!
}
```

### FILE: tests/test_graphql.py
```python
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app as fastapi_app
from strawberry.exceptions import GraphQLError

client = TestClient(fastapi_app)


def test_appointment_by_id_success():
    query = """
    query($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = 1
    test_response = {
        "id": 1,
        "user": "John Doe",
        "time": "2023-10-25T10:00:00",
        "status": "Scheduled"
    }
    with patch("app.graphql.schema.resolve_appointment_by_id", return_value=test_response):
        response = client.post("/graphql", json={"query": query, "variables": {"id": test_id}})
        assert response.status_code == 200
        assert "errors" not in response.json()
        data = response.json()["data"]["appointmentById"]
        assert data == {
            "id": test_response["id"],
            "user": test_response["user"],
            "time": test_response["time"],
            "status": test_response["status"]
        }


def test_appointment_by_id_not_found():
    query = """
    query($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = 999
    with patch("app.graphql.schema.resolve_appointment_by_id", side_effect=GraphQLError("Appointment not found")):
        response = client.post("/graphql", json={"query": query, "variables": {"id": test_id}})
        assert response.status_code == 200
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Appointment not found"


def test_appointment_by_id_success_integration():
    query = """
    query($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = 1
    test_response = {
        "id": 1,
        "user": "John Doe",
        "time": "2023-10-25T10:00:00",
        "status": "Scheduled"
    }
    with patch("app.graphql.resolvers.get_appointment_by_id_service", return_value=test_response):
        response = client.post("/graphql", json={"query": query, "variables": {"id": test_id}})
        assert response.status_code == 200
        assert "errors" not in response.json()
        data = response.json()["data"]["appointmentById"]
        assert data == {
            "id": test_response["id"],
            "user": test_response["user"],
            "time": test_response["time"],
            "status": test_response["status"]
        }


def test_appointment_by_id_not_found_integration():
    query = """
    query($id: Int!) {
        appointmentById(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = 999
    with patch("app.graphql.resolvers.get_appointment_by_id_service", return_value=None):
        response = client.post("/graphql", json={"query": query, "variables": {"id": test_id}})
        assert response.status_code == 200
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Appointment not found"


def test_appointment_field_success():
    query = """
    query($id: Int!) {
        appointment(id: $id) {
            id
            user
            time
            status
        }
    }
    """
    test_id = 1
    test_response = {
        "id": 1,
        "user": "Jane Doe",
        "time": "2023-10-26T11:00:00",
        "status": "Scheduled"
    }
    with patch("app.graphql.schema.resolve_appointment_by_id", return_value=test_response):
        response = client.post("/graphql", json={"query": query, "variables": {"id": test_id}})
        assert response.status_code == 200
        assert "errors" not in response.json()
        data = response.json()["data"]["appointment"]
        assert data == {
            "id": test_response["id"],
            "user": test_response["user"],
            "time": test_response["time"],
            "status": test_response["status"]
        }


def test_microsoft_repos_success():
    query = """
    query {
        microsoftRepos {
            id
            name
            html_url
            description
            language
        }
    }
    """
    test_response = [
        {
            "id": 1,
            "name": "repo1",
            "html_url": "https://github.com/microsoft/repo1",
            "description": "Test repository 1",
            "language": "Python"
        }
    ]
    with patch("app.graphql.schema.resolve_microsoft_repos", return_value=test_response):
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        assert "errors" not in response.json()
        data = response.json()["data"]["microsoftRepos"]
        assert data[0]["name"] == "repo1"
```