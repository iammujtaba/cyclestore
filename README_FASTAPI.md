# Supreme Cycle and Rickshaw Company - FastAPI Application

A modern, production-ready web application for a bicycle shop built with FastAPI, SQLAlchemy, and Tailwind CSS.

## Features

- **FastAPI Backend**: High-performance, modern Python web framework
- **SQLAlchemy ORM**: Database abstraction and relationship management
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS
- **Product Catalog**: Browse bicycles and accessories with filtering
- **Database Seeding**: Automatic sample data population
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Migration Support**: Alembic for database schema versioning

## Project Structure

```
cyclestore/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application configuration
│   ├── models/
│   │   └── product.py       # SQLAlchemy models
│   ├── schemas/
│   │   └── product.py       # Pydantic schemas
│   ├── crud/
│   │   └── product.py       # Database operations
│   ├── api/
│   │   └── routes.py        # API routes (for future API endpoints)
│   ├── db/
│   │   ├── session.py       # Database session management
│   │   └── init_db.py       # Database initialization and seeding
│   ├── templates/           # Jinja2 HTML templates
│   └── static/             # CSS, JS, and image files
├── alembic/                # Database migration files
├── requirements.txt        # Python dependencies
├── start.py               # Development server script
├── deploy.py              # Production deployment script
└── README.md              # This file
```

## Setup and Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cyclestore
   ```

2. **Create and activate virtual environment**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python -c "from app.db.init_db import create_tables, seed_database; create_tables(); seed_database()"
   ```

## Running the Application

### Development Mode

```bash
# Using the start script
python start.py

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload
```

The application will be available at:
- **Website**: http://localhost:8081
- **API Documentation**: http://localhost:8081/docs
- **Alternative API Docs**: http://localhost:8081/redoc

### Production Mode

```bash
python deploy.py
```

Or with environment variables:
```bash
PORT=8080 WORKERS=4 python deploy.py
```

## Database Management

### Using Alembic for Migrations

1. **Create a new migration**
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations**
   ```bash
   alembic upgrade head
   ```

3. **Downgrade migration**
   ```bash
   alembic downgrade -1
   ```

### Manual Database Operations

```bash
# Seed database with sample data
python -c "from app.db.init_db import seed_database; seed_database()"

# Create all tables
python -c "from app.db.init_db import create_tables; create_tables()"
```

## API Endpoints

### Web Routes
- `GET /` - Homepage with featured products
- `GET /bicycles` - Bicycle catalog with filtering
- `GET /accessories` - Accessory catalog
- `GET /bicycle/{id}` - Individual bicycle details
- `GET /about` - About page
- `GET /contact` - Contact form
- `POST /contact` - Submit contact form

### API Routes (Future Development)
API routes can be added in `app/api/routes.py` for:
- Product CRUD operations
- User management
- Order processing
- Inventory management

## Configuration

Application settings are managed in `app/config.py`:

```python
# Database URL
DATABASE_URL = "sqlite:///./cyclestore.db"

# Application settings
PROJECT_NAME = "Supreme Cycle and Rickshaw Company"
```

## Development

### Adding New Models

1. Create model in `app/models/`
2. Add Pydantic schema in `app/schemas/`
3. Create CRUD operations in `app/crud/`
4. Generate migration: `alembic revision --autogenerate -m "Add new model"`
5. Apply migration: `alembic upgrade head`

### Styling

The application uses Tailwind CSS for styling. Templates are located in `app/templates/` and can be customized as needed.

## Deployment

### Docker (Recommended for Production)

Create a `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "deploy.py"]
```

### Traditional Server

1. Install dependencies on the server
2. Set environment variables (PORT, WORKERS)
3. Run with a process manager like systemd or supervisor
4. Use a reverse proxy (nginx) for SSL and static files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please contact the development team or create an issue in the repository.
