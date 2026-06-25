### FILE: app/graphql_schema.py
```python
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models import AppointmentStorage

class Query:
    def appointment_record(self, id: int, db: Session) -> Optional[AppointmentStorage]:
        return db.query(AppointmentStorage).filter(AppointmentStorage.id == id).first()

class AppointmentStorage(BaseModel):
    id: int
    user: str
    time: str
    status: str
```

### FILE: app/models.py
```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class AppointmentStorage(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    time = Column(String)
    status = Column(String)
```

### FILE: app/main.py
```python
from fastapi import FastAPI
from app.routes import appointments
from app.database import SessionLocal

app = FastAPI()

app.include_router(appointments.router)
```

### FILE: app/graphql_schema.py
```python
from typing import Optional
from app.services.booking_service import get_appointment

class Query:
    def appointment(self, id: int) -> Optional[Appointment]:
        return get_appointment(id)
```

### FILE: app/services/booking_service.py
```python
from app.db_client import fetch_appointment

def get_appointment(id: int):
    return fetch_appointment(id)
```

### FILE: app/db_client.py
```python
import requests

def fetch_appointment(id: int):
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
    response = requests.post("http://database-service/graphql", json={'query': query, 'variables': {'id': id}})
    response_data = response.json()
    return response_data.get("data", {}).get("appointment", None)
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
```

### FILE: appointment-service.graphql
```graphql
type Query {
    appointment(id: Int!): Appointment
}

type Appointment {
    id: ID!
    user: String!
    time: String!
    status: String!
}
```

### FILE: appointment-db-service.graphql
```graphql
type Query {
    appointment_record(id: Int!): AppointmentStorage
}

type AppointmentStorage {
    id: ID!
    user: String!
    time: String!
    status: String!
}
```

### FILE: supergraph.graphql
```graphql
# This is the composed schema from the appointment and appointment-db services
schema {
    query: Query
}

# Other types and queries from subgraphs will be included here...
```