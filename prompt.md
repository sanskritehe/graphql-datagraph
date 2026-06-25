# AI Coding Agent – GraphQL Query Implementation

You are an AI coding agent. Your task is to implement a federated GraphQL Query resolver and its corresponding REST API Gateway mapping.

Since this is a multi-repo federated GraphQL microservice architecture, you must write changes scoped to the correct files under the respective repository layouts:

## 1. Appointment Database Service (role: "database")
- File: `app/graphql_schema.py`
  - Add the database-level Query field (e.g. `appointment_record(self, id: int) -> Optional[AppointmentStorage]`).
  - Query the database using SQLAlchemy Session from `app.database.SessionLocal`.
- File: `app/models.py` (if needed)
  - Define or verify the SQLAlchemy DB model.
- File: `app/main.py` (if needed)
  - Ensure the `/appointments` HTTP endpoints or GraphQL router routes correctly.

## 2. Appointment Service (role: "api")
- File: `app/graphql_schema.py`
  - Add the business-level Query field (e.g. `appointment(self, id: int) -> Optional[Appointment]`).
  - The resolver must communicate with the Database Service by calling functions in `app.services.booking_service`.
- File: `app/services/booking_service.py`
  - Delegate the lookup/operation to `app.db_client`.
- File: `app/db_client.py`
  - Fetch the data from the Database Service using GraphQL or REST (e.g. POST to Database Service's `/graphql` endpoint or HTTP GET/POST to `/appointments`).

## 3. GraphQL Datagraph Gateway (role: "graphql")
- Files: `appointment-service.graphql`, `appointment-db-service.graphql`, `supergraph.graphql`
  - Update the subgraphs and regenerate the composed schema.
  - **Important**: You MUST run `python compose.py` in the `graphql-datagraph` directory to dynamically export the schemas from both subgraphs and compile them into `supergraph.graphql`.

## 4. REST API Gateway (role: "gateway")
- File: `app/routes/appointments.py`
  - Add the REST endpoint route mapping (e.g. `GET /appointments/{appointment_id}`).
  - Call the GraphQL Datagraph (`http://localhost:4000`) using the `run_query` utility in `app.graphql_client` with the required query/mutation string and variables.
  - Map errors correctly (e.g. return HTTP 404 if the response is null).

## 5. Implement Automated Tests
- You MUST update or generate `tests/test_graphql.py` under the target directories.
- Run tests via pytest to verify the endpoints.


---

## Live Context for This Ticket

### Jira Ticket: KAN-28
**Summary:** Implement a new GraphQL Query to retrieve an appointment record by its integer ID.
**Status:** In Progress
**Priority:** Medium
**Labels:** none
**URL:** https://hpe-team2.atlassian.net/browse/KAN-28

**Description:**
Implement a federated GraphQL Query for appointment lookup, and expose it via a REST API Gateway endpoint. Requirements: GraphQL Subgraph Schema: Add the query "appointment(id: Int!): Appointment" to the schema in the Appointment Service (api) and Appointment Database Service (database). GraphQL Resolvers:  In the database service, implement the query resolver to fetch from the database using SQLAlchemy. In the api service, implement the resolver to call the database service via db_client. REST API Gateway Mapping:  In the gateway service, implement the route "GET /appointments/{appointment_id}" in 'app/routes/appointments.py'. Validate that 'appointment_id' is a positive integer (greater than 0) using FastAPI Path(..., gt=0). Use the 'run_query' utility in 'app.graphql_client' to fetch the appointment data from the Apollo Router ( http://localhost:4000). Return the data validated against a Pydantic model named 'AppointmentResponse' (fields: id, user, time, status). Return 404 if the datagraph returns null.

---

### API Specification (from Confluence: API-Based Automation Platform)
**Source:** https://hpe-team2-cpp.atlassian.net/wiki/spaces/~71202046a5693ef7834f62afe3bad6ad83fef8/pages/360449/API-Based+Automation+Platform

API-Based Automation Platform - Engineering Guidelines Overview The API-Based Automation Platform automates backend workflows through REST APIs. Services must be modular, reusable, testable, and easy to integrate with other enterprise systems. This page defines generic implementation standards for any Jira ticket handled by the automation pipeline. The Jira ticket is the source of truth for the specific feature, endpoint, request body, response body, validation rules, and acceptance criteria. Core Rule Always implement the Jira ticket requirements first. If this Confluence page conflicts with the Jira ticket, follow the Jira ticket. If the Jira ticket is ambiguous, make the safest minimal implementation and document assumptions in the generated solution. Tech Stack Backend framework: FastAPI for Python services Express.js only if the target repository is already Node.js API architecture: REST Data format: JSON Database: Use the existing repository database pattern. Do not introduce a new database unless the Jira ticket explicitly asks for it. Prefer SQLite only for local/simple service skeletons. Service Design Principles Every implementation should follow these principles: Keep changes scoped to the Jira ticket. Reuse existing repository structure and patterns. Do not rename unrelated files, routes, models, or services. Do not change public API behavior unrelated to the ticket. Keep code modular. Add validation at API boundaries. Return consistent JSON responses. Handle errors cleanly. Avoid hardcoded credentials, tokens, secrets, or environment-specific values. Standard REST Behavior Use these conventions unless the Jira ticket specifies otherwise. Create POST /&lt;resource&gt; Success status: 201 Created Read list GET /&lt;resource&gt; Success status: 200 OK Read one GET /&lt;resource&gt;/{id} Success status: 200 OK Not found: 404 Not Found Update PUT /&lt;resource&gt;/{id} PATCH /&lt;resource&gt;/{id} Success status: 200 OK Not found: 404 Not Found Delete DELETE /&lt;resource&gt;/{id} Success status: 204 No Content Not found: 404 Not Found Request Validation Standards Validate: Required fields Field types Empty strings where invalid Invalid enum values Invalid IDs Invalid pagination parameters Invalid date/time formats Invalid request body shape For invalid client input, return HTTP 400 or HTTP 422 depending on the framework's existing convention. Standard Error Response Use the repository's existing error format if available. If no format exists, use: json wide 760
