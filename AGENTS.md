# Developer Guidelines (AGENTS.md)

This document serves as a guide for AI agents and developers working on the `SistemaRAG` repository.

## 1. Environment & Build

The project is a **FastAPI** application with **Supabase**, **Redis**, and **RQ**, primarily designed to run via Docker.

### Local Setup
- **Python Version**: 3.12+
- **Dependency Management**: `pip` with `requirements.txt`.
- **Environment Variables**: Create a `.env` file in the root directory (see `README.md` for required keys).

### Commands
| Action | Command | Notes |
| :--- | :--- | :--- |
| **Install Dependencies** | `pip install -r requirements.txt` | Run in virtual environment |
| **Start Dev Server** | `uvicorn backend.main:app --reload` | Run from project root |
| **Run via Docker** | `docker-compose up --build` | Orchestrates API, Worker, Redis |
| **Run Tests** | `pytest` | *Note: No tests currently exist. Create in `backend/tests/`.* |
| **Run Single Test** | `pytest path/to/test_file.py::test_function_name` | |
| **Linting** | `ruff check backend/` | Recommended (not currently enforced) |
| **Formatting** | `ruff format backend/` | Recommended (not currently enforced) |

---

## 2. Code Style & Conventions

### General Python
- **Style**: Follow **PEP 8**.
- **Formatting**: Use standard formatting (black-compatible).
- **Type Hinting**: Strongly encouraged. Use Python's `typing` module and Pydantic models.
  - *Example*: `async def get_user(user_id: str) -> dict:`
- **Imports**: Use **absolute imports** relative to the `backend/` directory.
  - *Good*: `from config.app import app`, `from routers import auth`
  - *Bad*: `from ..config import app` (avoid excessive relative imports where absolute is clearer)

### FastAPI & Pydantic
- **Router**: Use `APIRouter` in `backend/routers/` and include them in `backend/main.py`.
- **Schemas**: Define Pydantic models in `backend/schemas/`.
  - **Naming**: Use **PascalCase** for Schema classes (e.g., `UserSignupSchema`).
  - *Note*: Existing code may use mixed case (e.g., `signupSchema`); refactor to PascalCase when touching those files, but ensure consistency in new files.
- **Validation**: Rely on Pydantic `v2` for request body validation.

### Database & Auth (Supabase)
- Use the singleton `supabase` client from `backend/config/supabase_client.py`.
- Handle Supabase errors explicitly.

### Error Handling
- Use `try...except` blocks for external service calls (Supabase, OpenAI, Redis).
- Raise `fastapi.HTTPException` with appropriate status codes (400, 401, 404, 500) and clear detail messages.
- Avoid exposing raw stack traces to the client in production.

### Logging
- **Preferred**: Use Python's standard `logging` module.
- **Discouraged**: Avoid `print()` statements for production logs.

## 3. Repository Structure

```text
backend/
├── config/         # Configuration (DB, App, Redis)
├── routers/        # API Route definitions
├── schemas/        # Pydantic models (Data Transfer Objects)
├── utils/          # Business logic, helpers, AI services
├── worker/         # RQ Worker scripts
└── main.py         # Application entry point
```

## 4. AI & Agent Instructions
- **Modifying Code**: When editing existing files, match the indentation (4 spaces) and existing import style.
- **New Features**: Place business logic in `backend/utils/` and expose it via `backend/routers/`.
- **Safety**: Do not commit `.env` files or hardcoded credentials.
- **Verification**: Since tests are scarce, verify logic by creating a small reproduction script or minimal test case if possible.
