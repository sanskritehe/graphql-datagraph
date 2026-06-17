from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_get_all_appointments_success():
    test_response = [
        {"id": 1, "user": "John Doe", "time": "2023-10-25T10:00:00", "status": "Scheduled"},
        {"id": 2, "user": "Jane Doe", "time": "2023-10-26T11:00:00", "status": "Scheduled"}
    ]
    with patch("app.services.booking_service.list_appointments", return_value=test_response):
        response = client.get("/appointments/")
        assert response.status_code == 200
        assert response.json() == test_response


def test_get_all_appointments_empty():
    with patch("app.services.booking_service.list_appointments", return_value=[]):
        response = client.get("/appointments/")
        assert response.status_code == 200
        assert response.json() == []


def test_delete_appointment_success():
    test_id = 1
    with patch("app.services.booking_service.delete_appointment_service", return_value=True):
        response = client.delete(f"/appointments/{test_id}")
        assert response.status_code == 204
        assert response.content == b""  # 204 No Content response should have an empty body


def test_delete_appointment_not_found():
    test_id = 999
    with patch("app.services.booking_service.delete_appointment_service", return_value=False):
        response = client.delete(f"/appointments/{test_id}")
        assert response.status_code == 404
        assert response.json() == {"detail": {"message": "Appointment not found", "code": "not_found"}}


