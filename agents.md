# AGENTS.md — AI Context Manager (Phase 1)

## 1. Project Objective

Build a minimal, production-conscious AI Context Manager that enables two independent AI coding agents (Codex Account A and Codex Account B) to share and retrieve task context through a centralized backend.

**Core experiment:**

Prove that Agent B can understand and continue Agent A's unfinished development task without:
- Reading Agent A's conversation history.
- Receiving manually copied conversation transcripts.
- Depending on project-specific `AGENTS.md` files for task progress.
- Sharing the same LLM context window.

The Context Manager must be the source of truth for shared task state.

## 2. Scope — Phase 1 Only

Implement:

1. Agent registration and identity.
2. Task creation and retrieval.
3. Structured task context updates.
4. Persistent context event history.
5. Context retrieval and assembly.
6. Optimistic concurrency control using task versions.
7. Automated API and integration tests.
8. Real-world Codex A/B handoff experiment.

Do NOT implement:
- MCP integration.
- RAG or Vector Database.
- LLM summarization or embeddings.
- Redis, Kafka, WebSockets or SSE.
- Automatic agent orchestration.
- Simultaneous agent execution or complex distributed locking.
- Frontend or dashboard.

Use HTTP REST for Agent communication.

## 3. Technology Stack

- Python 3.13+
- FastAPI
- Pydantic v2
- pydantic-settings
- SQLAlchemy 2.x
- PostgreSQL
- Alembic
- Docker Compose
- HTTPX
- pytest

Use modern, stable, mutually compatible dependency versions.

Use asynchronous database operations where appropriate.

## 4. Architecture

Follow a simple layered architecture:

app/
├── main.py
├── core/
│   └── config.py
├── api/
│   └── routes/
│       ├── agents.py
│       ├── tasks.py
│       └── contexts.py
├── schemas/
│   ├── agent.py
│   ├── task.py
│   ├── context.py
│   └── event.py
├── models/
│   ├── agent.py
│   ├── task.py
│   └── context_event.py
├── services/
│   ├── agent_manager.py
│   ├── task_state_manager.py
│   ├── event_manager.py
│   └── context_manager.py
├── repositories/
│   ├── agent_repository.py
│   ├── task_repository.py
│   └── event_repository.py
└── db/
    ├── base.py
    ├── session.py
    └── dependencies.py

tests/
alembic/
.env.example
docker-compose.yml
pyproject.toml
README.md

Responsibilities:

- API: HTTP request and response handling.
- Schemas: Pydantic validation.
- Services: Business logic.
- Repositories: Database operations.
- Models: SQLAlchemy database models.
- DB: Engine, sessions and database dependencies.

Avoid unnecessary abstractions, generic frameworks and over-engineering.

## 5. Database Design

Implement three core tables.

### Agents
- id: UUID primary key
- name: string
- created_at: timestamp

### Tasks
- id: UUID primary key
- title: string
- description: text
- status: string
- completed_steps: JSONB
- current_step: text
- next_step: text
- updated_by: UUID foreign key
- version: integer
- created_at: timestamp
- updated_at: timestamp

### ContextEvents
- id: UUID primary key
- task_id: UUID foreign key
- agent_id: UUID foreign key
- event_type: string
- payload: JSONB
- created_at: timestamp

Use appropriate indexes, foreign keys and database constraints.

Tasks represent the latest state.

ContextEvents represent historical changes.

This is a lightweight append-only event log, NOT a full Event Sourcing implementation.

## 6. REST API

Implement:

POST /agents
- Register an agent.

POST /tasks
- Create a task.

GET /tasks/{task_id}
- Retrieve task information.

PUT /tasks/{task_id}/context
- Update task state.
- Require agent_id and expected_version.
- Increment version after successful update.
- Record a ContextEvent in the same database transaction.

GET /tasks/{task_id}/context
- Return current task state and recent event history.
- Assemble a structured context response.

GET /tasks/{task_id}/events
- Retrieve task event history.

Use appropriate HTTP status codes.

Return HTTP 409 when the expected task version is stale.

## 7. Core Context Manager Logic

The ContextManager must expose two primary operations:

### update_context()

1. Validate task and agent existence.
2. Validate expected_version.
3. Update the task's current state.
4. Increment the task version.
5. Record a ContextEvent.
6. Commit all changes atomically in one database transaction.
7. Return the updated state.

### get_context()

1. Retrieve the task.
2. Retrieve recent context events.
3. Assemble structured context.
4. Return a validated response.

The Context Manager must not depend on a particular LLM provider.

Do not introduce LLM summarization in Phase 1.

## 8. Agent Interaction Protocol

Agent A:

1. Register with Context Manager.
2. Create a task.
3. Execute development work.
4. After meaningful progress, update task context.
5. Record completed_steps, current_step and next_step.
6. Publish the latest state before stopping.

Agent B:

1. Register with Context Manager.
2. Retrieve the same task_id.
3. Read current task state and recent events.
4. Inspect actual project files before modifying them.
5. Continue from the recorded progress.
6. Update Context Manager after meaningful progress.

Use HTTP requests through curl initially. MCP is outside Phase 1 scope.

Context Manager records agent-reported progress; it must not be treated as proof that code changes are correct.

## 9. Engineering Requirements

- Use Pydantic v2 models.
- Use SQLAlchemy 2.x typed ORM mappings.
- Use pydantic-settings for configuration.
- Keep secrets in .env.
- Never commit .env.
- Provide .env.example.
- Use Alembic for all schema migrations.
- Use dependency injection through FastAPI Depends().
- Use proper transaction management.
- Use UUID identifiers.
- Use timezone-aware timestamps.
- Use clear type hints.
- Handle expected errors explicitly.
- Add tests for critical business logic and API behavior.
- Never hardcode credentials.
- Never silently overwrite stale task versions.

Keep the implementation simple and maintainable.

## 10. Development Workflow

Implement the project incrementally in the following order:

1. Configuration and PostgreSQL connection.
2. SQLAlchemy models.
3. Alembic migrations.
4. Agent API.
5. Task API.
6. Event management.
7. Context Manager.
8. Optimistic concurrency control.
9. Automated integration tests.
10. Codex A/B experiment.

Do not implement future phases prematurely.

Before modifying existing files:
- Inspect the current repository.
- Understand the existing implementation.
- Reuse working code where appropriate.
- Avoid replacing working components unnecessarily.

After each step:
- Explain the implementation.
- Run relevant tests.
- Report modified files.
- Report any remaining issues.
- Wait for approval before proceeding to the next step.

## 11. Phase 1 Acceptance Criteria

The experiment is successful when:

1. Two independent Codex accounts can use the same Context Manager.
2. Agent A can create and update a task.
3. Agent B can retrieve Agent A's latest context.
4. Agent B can identify completed work and the next step without conversation transcripts.
5. Context survives application and agent restarts.
6. Stale version updates are rejected.
7. The backend works independently of the LLM provider.
8. Agent B can continue the actual development task using retrieved context.

**Final experiment objective:**

Demonstrate that an agent can enter an existing project without a project-specific AGENTS.md and still recover the necessary working context from the external Context Manager.

The shared context infrastructure, not a static instruction file, must provide task continuity.

## 12. First Action

Start with Step 1: Configuration and PostgreSQL connection.

Inspect the existing repository before making changes.

Do not generate the entire project at once.

Explain the design decisions, implement only Step 1, run the relevant tests, and report the result before proceeding.