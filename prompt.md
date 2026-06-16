# Copilot Agent – POST Endpoint Implementation

You are an AI coding agent. Your task is to implement a POST (create) REST API endpoint.

These instructions are generic and apply to ANY repository and ANY resource.

---

## Step 1 – Read the Jira Ticket

Use the Jira tool to fetch the ticket provided.

Extract:
- The resource name (e.g. "appointment", "user", "order")
- The endpoint to implement (e.g. POST /appointments)
- Any specific business logic called out
- The Confluence page reference for the API spec

---

## Step 2 – Fetch API Specification from Confluence

Use the Confluence tool to fetch the page referenced in the Jira ticket.

Find the section for the POST endpoint of the resource.

Extract:
- The exact endpoint path
- The exact request body JSON format
- The exact response JSON format
- Any validation rules

---

## Step 3 – Read Existing Code

Use the GitHub tool to read the existing implementation files in the repository.

Understand:
- How existing endpoints are structured
- How new records are created and saved
- How responses are returned
- What imports are already present

DO NOT modify any already implemented endpoints.

---

## Step 4 – Implement the POST Endpoint

A POST endpoint must:
- Accept the request body matching the Confluence spec
- Validate required fields
- Create a new resource record
- Save and return the created resource
- Return appropriate HTTP status (201 Created where possible)
- Follow the exact same code style as existing endpoints
- Use dependency injection for sessions or clients
- Return a JSON-serializable response

---

## Step 5 – Create a Branch

Use the GitHub tool to create a new branch:
- Branch name: feature/{jira-ticket-id}-post-{resource-name}
- Base branch: main

---

## Step 6 – Push the Code

Push only the minimal necessary changes to the feature branch.

Commit message format:
"[{jira-ticket-id}] Implement POST /{resource} endpoint"

---

## Step 7 – Raise a Pull Request

Create a PR with:
- Title: [{jira-ticket-id}] Implement POST /{resource}
- Body: what was implemented, files changed, Jira and Confluence references
- Head: feature branch
- Base: main

---

## Rules

- Never modify already working endpoints
- Always validate request body against Confluence spec
- Always follow existing code style
- Always follow the Confluence spec for request/response format
- Minimal changes only — do not refactor unrelated code


---

## Live Context for This Ticket

### Jira Ticket: KAN-23
**Summary:** Create appointment booking API
**Status:** To Do
**Priority:** Medium
**Labels:** ai-pipeline
**URL:** https://hpe-team2.atlassian.net/browse/KAN-23

**Description:**
Implement POST endpoint for appointment booking. Trigger pipeline.

---

### API Specification (from Confluence: API-Based Automation Platform)
**Source:** https://hpe-team2-cpp.atlassian.net/wiki/spaces/~71202046a5693ef7834f62afe3bad6ad83fef8/pages/360449/API-Based+Automation+Platform

API-Based Automation Platform - Engineering Guidelines Overview The API-Based Automation Platform automates backend workflows through REST APIs. Services must be modular, reusable, testable, and easy to integrate with other enterprise systems. This page defines generic implementation standards for any Jira ticket handled by the automation pipeline. The Jira ticket is the source of truth for the specific feature, endpoint, request body, response body, validation rules, and acceptance criteria. Core Rule Always implement the Jira ticket requirements first. If this Confluence page conflicts with the Jira ticket, follow the Jira ticket. If the Jira ticket is ambiguous, make the safest minimal implementation and document assumptions in the generated solution. Tech Stack Backend framework: FastAPI for Python services Express.js only if the target repository is already Node.js API architecture: REST Data format: JSON Database: Use the existing repository database pattern. Do not introduce a new database unless the Jira ticket explicitly asks for it. Prefer SQLite only for local/simple service skeletons. Service Design Principles Every implementation should follow these principles: Keep changes scoped to the Jira ticket. Reuse existing repository structure and patterns. Do not rename unrelated files, routes, models, or services. Do not change public API behavior unrelated to the ticket. Keep code modular. Add validation at API boundaries. Return consistent JSON responses. Handle errors cleanly. Avoid hardcoded credentials, tokens, secrets, or environment-specific values. Standard REST Behavior Use these conventions unless the Jira ticket specifies otherwise. Create POST /&lt;resource&gt; Success status: 201 Created Read list GET /&lt;resource&gt; Success status: 200 OK Read one GET /&lt;resource&gt;/{id} Success status: 200 OK Not found: 404 Not Found Update PUT /&lt;resource&gt;/{id} PATCH /&lt;resource&gt;/{id} Success status: 200 OK Not found: 404 Not Found Delete DELETE /&lt;resource&gt;/{id} Success status: 204 No Content Not found: 404 Not Found Request Validation Standards Validate: Required fields Field types Empty strings where invalid Invalid enum values Invalid IDs Invalid pagination parameters Invalid date/time formats Invalid request body shape For invalid client input, return HTTP 400 or HTTP 422 depending on the framework's existing convention. Standard Error Response Use the repository's existing error format if available. If no format exists, use: json wide 760
