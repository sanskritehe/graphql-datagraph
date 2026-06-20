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

### FILE: app/services/booking_service.py
```python
from typing import List, Optional
from app.db_client import (
    get_all_appointments,
    get_appointment_by_id as db_get_appointment_by_id,
    delete_appointment,
)


def list_appointments() -> List[dict]:
    return get_all_appointments()


def get_appointment_by_id(appointment_id: int) -> Optional[dict]:
    return db_get_appointment_by_id(appointment_id)


def delete_appointment_service(appointment_id: int) -> bool:
    """
    Deletes an appointment by its ID. First checks if the appointment exists, and
    then calls the database client to perform a hard delete operation.

    Args:
        appointment_id (int): The ID of the appointment to delete.

    Returns:
        bool: True if the appointment was successfully deleted, False if not found.
    """
    existing_appointment = get_appointment_by_id(appointment_id)
    if not existing_appointment:
        return False
    return delete_appointment(appointment_id)
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