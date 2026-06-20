### FILE: appointment-service.graphql
```graphql
type Query {
  appointmentById(id: Int!): Appointment
  appointment(id: Int!): Appointment
  microsoftRepos: [Repository!]!
}

type Appointment {
  id: Int!
  user: String!
  time: String!
  status: String!
}

type Repository {
  id: Int!
  name: String!
  html_url: String!
  description: String!
  language: String!
}
```

### FILE: appointment-db-service.graphql
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

### FILE: supergraph.graphql
```graphql
schema
  @link(url: "https://specs.apollo.dev/link/v1.0")
  @link(url: "https://specs.apollo.dev/join/v0.3", import: ["@join__graph", "@join__field"])
{
  query: Query
}

directive @join__graph(name: String!, url: String!) on SCHEMA
directive @join__field(graph: join__Graph!, requires: String, provides: String, type: String) on FIELD_DEFINITION

enum join__Graph {
  APPOINTMENT @join__graph(name: "appointment", url: "http://localhost:8000/graphql")
  APPOINTMENT_DB @join__graph(name: "appointment-db", url: "http://localhost:8001/graphql")
}

type Query {
  appointmentById(id: Int!): Appointment @join__field(graph: APPOINTMENT)
  appointment(id: Int!): Appointment @join__field(graph: APPOINTMENT)
  appointment_record(id: Int!): AppointmentStorage @join__field(graph: APPOINTMENT_DB)
}

type Appointment {
  id: Int! @join__field(graph: APPOINTMENT)
  user: String! @join__field(graph: APPOINTMENT)
  time: String! @join__field(graph: APPOINTMENT)
  status: String! @join__field(graph: APPOINTMENT)
}

type AppointmentStorage {
  id: Int! @join__field(graph: APPOINTMENT_DB)
  user: String! @join__field(graph: APPOINTMENT_DB)
  time: String! @join__field(graph: APPOINTMENT_DB)
  status: String! @join__field(graph: APPOINTMENT_DB)
}
```

### FILE: graphql-datagraph/appointment-service.graphql
```graphql
type Query {
  appointmentById(id: Int!): Appointment
  appointment(id: Int!): Appointment
  microsoftRepos: [Repository!]!
}

type Appointment {
  id: Int!
  user: String!
  time: String!
  status: String!
}

type Repository {
  id: Int!
  name: String!
  html_url: String!
  description: String!
  language: String!
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

### FILE: graphql-datagraph/supergraph.graphql
```graphql
schema
  @link(url: "https://specs.apollo.dev/link/v1.0")
  @link(url: "https://specs.apollo.dev/join/v0.3", import: ["@join__graph", "@join__field"])
{
  query: Query
}

directive @join__graph(name: String!, url: String!) on SCHEMA
directive @join__field(graph: join__Graph!, requires: String, provides: String, type: String) on FIELD_DEFINITION

enum join__Graph {
  APPOINTMENT @join__graph(name: "appointment", url: "http://localhost:8000/graphql")
  APPOINTMENT_DB @join__graph(name: "appointment-db", url: "http://localhost:8001/graphql")
}

type Query {
  appointmentById(id: Int!): Appointment @join__field(graph: APPOINTMENT)
  appointment(id: Int!): Appointment @join__field(graph: APPOINTMENT)
  appointment_record(id: Int!): AppointmentStorage @join__field(graph: APPOINTMENT_DB)
}

type Appointment {
  id: Int! @join__field(graph: APPOINTMENT)
  user: String! @join__field(graph: APPOINTMENT)
  time: String! @join__field(graph: APPOINTMENT)
  status: String! @join__field(graph: APPOINTMENT)
}

type AppointmentStorage {
  id: Int! @join__field(graph: APPOINTMENT_DB)
  user: String! @join__field(graph: APPOINTMENT_DB)
  time: String! @join__field(graph: APPOINTMENT_DB)
  status: String! @join__field(graph: APPOINTMENT_DB)
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