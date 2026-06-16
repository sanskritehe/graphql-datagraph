# Copilot Agent – GET Endpoint Implementation

You are an AI coding agent. Your task is to implement a GET (read) REST API endpoint.

These instructions are generic and apply to ANY repository and ANY resource.

---

## Step 1 – Read the Jira Ticket

Use the Jira tool to fetch the ticket provided.

Extract:
- The resource name (e.g. "appointment", "user", "order")
- The endpoint to implement (e.g. GET /appointments or GET /appointments/{id})
- Any specific business logic called out (e.g. filtering, pagination)
- The Confluence page reference for the API spec

---

## Step 2 – Fetch API Specification from Confluence

Use the Confluence tool to fetch the page referenced in the Jira ticket.

Find the section for the GET endpoint of the resource.

Extract:
- The exact endpoint path
- Whether it returns a single resource or a list
- Any query parameters (filters, pagination)
- The exact response JSON format
- The error response format (especially 404 for single resource)

---

## Step 3 – Read Existing Code

Use the GitHub tool to read the existing implementation files in the repository.

Understand:
- How existing GET endpoints are structured
- How queries are made
- How lists vs single records are returned
- What imports are already present

DO NOT modify any already implemented endpoints.

---

## Step 4 – Implement the GET Endpoint

A GET endpoint must:
- Accept path parameters if fetching a single resource
- Accept query parameters if filtering or paginating
- Query the resource correctly
- Return 404 if a single resource is not found
- Return an empty list (not 404) if a collection has no results
- Follow the exact same code style as existing endpoints
- Use dependency injection for sessions or clients
- Return a JSON-serializable response matching the Confluence spec

---

## Step 5 – Create a Branch

Use the GitHub tool to create a new branch:
- Branch name: feature/{jira-ticket-id}-get-{resource-name}
- Base branch: main

---

## Step 6 – Push the Code

Push only the minimal necessary changes to the feature branch.

Commit message format:
"[{jira-ticket-id}] Implement GET /{resource} endpoint"

---

## Step 7 – Raise a Pull Request

Create a PR with:
- Title: [{jira-ticket-id}] Implement GET /{resource}
- Body: what was implemented, files changed, Jira and Confluence references
- Head: feature branch
- Base: main

---

## Rules

- Never modify already working endpoints
- Always return 404 for missing single resources
- Always return empty list for empty collections
- Always follow existing code style
- Always follow the Confluence spec for response format
- Minimal changes only — do not refactor unrelated code


---

## Live Context for This Ticket

### Jira Ticket: KAN-24
**Summary:** We need to implement a new GraphQL query to fetch an appointment by its ID. 
**Status:** In Progress
**Priority:** Medium
**Labels:** none
**URL:** https://hpe-team2.atlassian.net/browse/KAN-24

**Description:**
We need to implement a new GraphQL query to fetch an appointment by its ID. Service: appointment Format: GraphQL query Please define the following types and query: type Query {   appointmentById(id: Int!): Appointment } type Appointment {   id: Int!   user: String!   time: String!   status: String! } Requirements: Implement the resolver function in  app/graphql/resolvers.py  or equivalent schema files. The resolver should query the database layer using  db_client . Create a unit test file at  tests/test_graphql.py  using pytest and  fastapi.testclient.TestClient . The test must send a POST request to  /graphql  with the  appointmentById  query, and verify: Success: Returns data matching the requested ID. Error: If the ID does not exist, returns an error message "Appointment not found".

---

### API Specification (from Confluence: API-Based Automation Platform)
**Source:** https://hpe-team2-cpp.atlassian.net/wiki/spaces/~71202046a5693ef7834f62afe3bad6ad83fef8/pages/360449/API-Based+Automation+Platform

API-Based Automation Platform - Engineering Guidelines Overview The API-Based Automation Platform automates backend workflows through REST APIs. Services must be modular, reusable, testable, and easy to integrate with other enterprise systems. This page defines generic implementation standards for any Jira ticket handled by the automation pipeline. The Jira ticket is the source of truth for the specific feature, endpoint, request body, response body, validation rules, and acceptance criteria. Core Rule Always implement the Jira ticket requirements first. If this Confluence page conflicts with the Jira ticket, follow the Jira ticket. If the Jira ticket is ambiguous, make the safest minimal implementation and document assumptions in the generated solution. Tech Stack Backend framework: FastAPI for Python services Express.js only if the target repository is already Node.js API architecture: REST Data format: JSON Database: Use the existing repository database pattern. Do not introduce a new database unless the Jira ticket explicitly asks for it. Prefer SQLite only for local/simple service skeletons. Service Design Principles Every implementation should follow these principles: Keep changes scoped to the Jira ticket. Reuse existing repository structure and patterns. Do not rename unrelated files, routes, models, or services. Do not change public API behavior unrelated to the ticket. Keep code modular. Add validation at API boundaries. Return consistent JSON responses. Handle errors cleanly. Avoid hardcoded credentials, tokens, secrets, or environment-specific values. Standard REST Behavior Use these conventions unless the Jira ticket specifies otherwise. Create POST /&lt;resource&gt; Success status: 201 Created Read list GET /&lt;resource&gt; Success status: 200 OK Read one GET /&lt;resource&gt;/{id} Success status: 200 OK Not found: 404 Not Found Update PUT /&lt;resource&gt;/{id} PATCH /&lt;resource&gt;/{id} Success status: 200 OK Not found: 404 Not Found Delete DELETE /&lt;resource&gt;/{id} Success status: 204 No Content Not found: 404 Not Found Request Validation Standards Validate: Required fields Field types Empty strings where invalid Invalid enum values Invalid IDs Invalid pagination parameters Invalid date/time formats Invalid request body shape For invalid client input, return HTTP 400 or HTTP 422 depending on the framework's existing convention. Standard Error Response Use the repository's existing error format if available. If no format exists, use: json wide 760
