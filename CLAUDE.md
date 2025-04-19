# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Setup: `pip install -r requirements.txt`
- Run server: `uvicorn app.main:app --reload`
- Lint: `flake8 . && black --check .`
- Type check: `mypy .`
- Tests: `pytest`
- Single test: `pytest tests/path_to_test.py::test_function_name -v`

## Style Guidelines
- Imports: Group standard library, FastAPI, SQLAlchemy, pgvector, then local imports
- Formatting: Black with default 88 character line length
- Types: Use Pydantic models for API schemas; type hints for all functions
- FastAPI: Use dependency injection for DB connections and shared resources
- Database: Use SQLAlchemy async ORM with pgvector for vector operations
- Error handling: Return appropriate HTTP status codes with detailed error responses
- Naming: snake_case for variables/functions, CamelCase for classes/Pydantic models
- API endpoints: RESTful structure with consistent URL patterns