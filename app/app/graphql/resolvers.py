import strawberry
from app.services.booking_service import get_appointment_by_id as get_appointment_by_id_service
from strawberry.exceptions import GraphQLError


@strawberry.type
class GraphQLErrorType(Exception):
    message: str


def resolve_appointment_by_id(id: int):
    appointment = get_appointment_by_id_service(appointment_id=id)
    if not appointment:
        raise GraphQLError("Appointment not found")
    return appointment
