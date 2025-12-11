# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI project with a minimal structure. The application is defined in `main.py` as a single-file FastAPI application with basic REST endpoints.

## Development Commands

### Running the Application

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run the development server
uvicorn main:app --reload

# Run on specific host/port
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The application runs on `http://127.0.0.1:8000` by default with hot-reloading enabled.

### Testing Endpoints

Use the `test_main.http` file with an HTTP client (like PyCharm's HTTP Client or VS Code REST Client extension) to test endpoints.

Manual testing with curl:
```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/hello/YourName
```

### View API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Architecture

### Application Structure

The application follows a single-file pattern:
- `main.py`: Contains the FastAPI application instance (`app = FastAPI()`) and all route handlers
- All endpoints are defined as async functions decorated with FastAPI route decorators (`@app.get()`, `@app.post()`, etc.)

### Dependencies

Core dependencies installed in `.venv`:
- `fastapi`: Web framework
- `uvicorn`: ASGI server for running the application
- `pydantic`: Data validation (FastAPI dependency)

### Expanding the Application

When adding new functionality:
- For small applications, continue adding routes to `main.py`
- For larger applications, consider refactoring into a package structure with separate modules for routes, models, services, etc.
