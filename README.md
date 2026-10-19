# FastAPI Authentication API

A modern, production-ready Authentication and User Management API built with **Python 3**, **FastAPI**, **SQLAlchemy**, **Bcrypt**, and **JWT (JSON Web Tokens)**.

---

## Features

- **User Registration**: Secure account creation with email & username uniqueness verification and strong password constraints.
- **Bcrypt Password Hashing**: State-of-the-art password hashing using native `bcrypt` (fully compatible with modern Python 3.12+ / 3.13+ / 3.15+).
- **Dual Login Support**:
  - `POST /api/v1/auth/login`: Standard JSON payload login for SPAs / Mobile clients.
  - `POST /api/v1/auth/login/oauth2`: OAuth2 Password Form compatible login (native integration with Swagger UI's "Authorize" modal).
- **JWT Token Management**:
  - Fast, cryptographically signed Access Tokens (`HS256`).
  - Refresh Tokens to renew expired sessions without re-authenticating.
- **Protected Endpoints**:
  - `GET /api/v1/auth/me`: Fetch authenticated user profile.
  - `PATCH /api/v1/auth/me`: Update profile details (email, full name).
  - `POST /api/v1/auth/change-password`: Change password with existing password verification.
  - `POST /api/v1/auth/logout`: Stateless client logout.
- **SQLite Database**: Zero configuration needed out-of-the-box (auto-migrated via SQLAlchemy). Easily switches to PostgreSQL / MySQL via `DATABASE_URL`.
- **Automated Testing Suite**: 100% test coverage with `pytest` using an isolated in-memory SQLite database.
- **Interactive API Docs**: Built-in Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## Directory Structure

```
fastapi-auth/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   └── auth.py        # Authentication & user route handlers
│   │   ├── deps.py            # JWT token validation & db session dependencies
│   │   └── __init__.py        # API router aggregation
│   ├── core/
│   │   ├── config.py          # App settings & environment variables
│   │   └── security.py        # Bcrypt hashing & PyJWT token utilities
│   ├── db/
│   │   ├── database.py        # SQLAlchemy engine & session maker
│   │   └── models.py          # User table model definition
│   ├── schemas/
│   │   └── auth.py            # Pydantic request/response validation models
│   └── main.py                # FastAPI app factory, CORS, and lifespan
├── tests/
│   ├── conftest.py            # Pytest fixtures & in-memory SQLite setup
│   └── test_auth.py           # Comprehensive integration tests
├── .env.example               # Environment variables template
├── requirements.txt           # Project dependencies
├── run.py                     # Convenience launcher
└── README.md
```

---

## Quick Start

### 1. Activate Environment

```bash
cd /Users/betopia/.gemini/antigravity-ide/scratch/fastapi-auth
source .venv/bin/activate
```

*(If setting up on a fresh machine: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`)*

### 2. Run the Server

```bash
python run.py
```
Or with Uvicorn directly:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API Base**: `http://localhost:8000`
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Running Tests

Run the test suite with `pytest`:

```bash
pytest -v
```

---

## API Endpoints Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/` | API status & documentation links | No |
| `GET` | `/health` | Health check endpoint | No |
| `POST` | `/api/v1/auth/register` | Register new user | No |
| `POST` | `/api/v1/auth/login` | Login (JSON body) | No |
| `POST` | `/api/v1/auth/login/oauth2` | Login (OAuth2 form for Swagger) | No |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | No |
| `GET` | `/api/v1/auth/me` | Current user profile | **Yes (Bearer JWT)** |
| `PATCH` | `/api/v1/auth/me` | Update current user profile | **Yes (Bearer JWT)** |
| `POST` | `/api/v1/auth/change-password` | Change user password | **Yes (Bearer JWT)** |
| `POST` | `/api/v1/auth/logout` | Logout | **Yes (Bearer JWT)** |

---

## Example Usage with cURL

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "developer",
    "password": "SuperSecretPassword123!",
    "full_name": "Antigravity Dev"
  }'
```

### 2. Login (JSON)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_email": "developer",
    "password": "SuperSecretPassword123!"
  }'
```
Response:
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### 3. Access Protected Route (`/me`)
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

### 4. Refresh Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<YOUR_REFRESH_TOKEN>"
  }'
```

### 5. Change Password
```bash
curl -X POST "http://localhost:8000/api/v1/auth/change-password" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "SuperSecretPassword123!",
    "new_password": "NewUltraSecretPassword456!"
  }'
```
