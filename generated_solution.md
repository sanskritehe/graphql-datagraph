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
    def appointment(self, id: int) -> Optional[Appointment]:
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

### FILE: app/graphql/resolvers.py
```python
import strawberry
from strawberry.exceptions import GraphQLError
from app.database import SessionLocal
from app.models import AppointmentDB


@strawberry.type
class GraphQLErrorType(Exception):
    message: str


def resolve_appointment_record(id: int):
    db = SessionLocal()
    try:
        appointment = db.query(AppointmentDB).filter(AppointmentDB.id == id).first()  # type: ignore
        if not appointment:
            return None
        return appointment
    finally:
        db.close()

```