# AI Agent Instructions for Equipment Lending System

## Project Overview
This is a Flask-based Equipment Lending and Return System for SIET. The system manages equipment lending, tracking, and returns with role-based access control.

## Architecture and Structure

### Key Components
- **Blueprints** (`app/blueprints/`): Modular route handlers
  - `admin/`: Administrative functions and user management
  - `auth/`: Authentication and authorization
  - `inventory/`: Equipment management
  - `tracking/`: Equipment tracking
  - `pages/`: Static pages

### Data Layer
- **Models** (`app/models/`): SQLAlchemy models for core entities
  - Key entities: User, Equipment, Borrow, Return
- **Repositories** (`app/repositories/`): Data access layer implementing repository pattern
- **Services** (`app/services/`): Business logic layer

## Development Workflow

### Database Setup
```bash
# Initialize database
python3 -m app.db.init_db

# Populate with initial data
python3 -m app.db.insert
```

### File Upload Handling
- Equipment images are stored in `app/static/uploads/equipment/`
- Supported formats: jpg, jpeg, png, gif, webp
- Access images through Flask's static file handling

## Project-Specific Patterns

### Service Layer Pattern
- Business logic is isolated in service classes (`app/services/`)
- Services handle validation, business rules, and coordinate repositories
- Example: `equipment_service.py` for equipment management operations

### Authentication Flow
- Uses Flask session-based authentication
- Role-based access control (member, admin)
- Protected routes use `@login_required` decorator from `app/utils/decorators.py`

### Repository Pattern
- Each entity has a corresponding repository extending `BaseRepository`
- Repositories handle all database operations
- Example: `equipment_repository.py` for equipment CRUD operations

## Integration Points
- Database: SQLite (configured in `app/db/db.py`)
- File Storage: Local filesystem (configured in `app/config.py`)
- Frontend: Flask templates with Bootstrap CSS
- Session Management: Flask Session

## Common Operations
- Equipment management (CRUD) through `/inventory` routes
- User management through `/admin` routes
- Lending workflow through `/tracking` routes
- Authentication through `/auth` routes