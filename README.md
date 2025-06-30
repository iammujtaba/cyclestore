# Supreme Cycle & Rickshaw Company - FastAPI Web Application

A modern, production-ready web application for **Supreme Cycle & Rickshaw Company**, a well-established bicycle business serving the community since 1999. Built with FastAPI, SQLAlchemy, and featuring a responsive design with Tailwind CSS.

## 🏪 About the Business

**Supreme Cycle & Rickshaw Company** has been serving customers from Mehdawal Road, Khalilabad-272175, Sant Kabir Nagar, Uttar Pradesh for over **26 years**. With a **4.0-star rating** and established reputation, we specialize in:

- **Traditional Bicycles** - Mountain, City, Racing, Kids bikes
- **Electric Bicycles** - Modern e-bikes with latest technology
- **Cycle Rickshaws** - Commercial transportation solutions
- **BSA Authorized Dealer** - Official dealer for BSA brand products
- **Wholesale Services** - Bulk supplies for retailers
- **Same Day Delivery** - Quick delivery across Khalilabad and surrounding areas

## ✨ Features

### 🎨 Modern Web Application
- **FastAPI Backend** - High-performance Python web framework
- **SQLAlchemy ORM** - Robust database management
- **Responsive Design** - Mobile-first approach with Tailwind CSS
- **Interactive UI** - Smooth animations and modern components
- **WhatsApp Integration** - Direct customer communication

### 🚲 Product Management
- **Dynamic Product Catalog** - Database-driven bicycle and accessory listings
- **Advanced Filtering** - Filter by category, size, price range
- **Product Details** - Comprehensive specifications and features
- **Image Management** - High-quality product galleries
- **Inventory Tracking** - Stock status and availability

### 📱 Customer Experience
- **Responsive Design** - Works perfectly on all devices
- **Fast Loading** - Optimized performance
- **Easy Navigation** - Intuitive user interface
- **Contact Integration** - Multiple contact methods
- **WhatsApp Support** - Instant customer service

### 🛠️ Technical Features
- **Database Migrations** - Alembic for schema management
- **API Documentation** - Auto-generated Swagger/OpenAPI docs
- **Error Handling** - Comprehensive error management
- **Security** - Production-ready security features
- **Deployment Ready** - Docker and traditional deployment support

## 📞 Contact Information

- **📍 Address**: Mehdawal Road, Khalilabad-272175, Sant Kabir Nagar, Uttar Pradesh
- **📱 Phone & WhatsApp**: +91 98398 50588
- **📧 Email**: mujtaba.aamir1@gmail.com
- **🗺️ Google Maps**: [Get Directions](https://maps.app.goo.gl/vV7coEa9f3iZxrze9)
- **🕒 Hours**: Mon-Sat: 9AM-7PM, Sun: 10AM-6PM

## 🚀 Technology Stack

- **Backend**: FastAPI 0.104.1 (Python)
- **Database**: SQLAlchemy 2.0.23 with SQLite/PostgreSQL
- **Templates**: Jinja2 3.1.2
- **Styling**: Tailwind CSS
- **Server**: Uvicorn 0.24.0
- **Migrations**: Alembic 1.12.1
- **File Handling**: Aiofiles, Python-multipart
- **Image Processing**: Pillow 10.0.1

## 📁 Project Structure

```
cyclestore/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Application configuration
│   ├── models/            # SQLAlchemy models
│   │   └── product.py     # Bicycle and Accessory models
│   ├── schemas/           # Pydantic schemas
│   │   └── product.py     # Data validation schemas
│   ├── crud/              # Database operations
│   │   └── product.py     # CRUD operations
│   ├── db/                # Database configuration
│   │   ├── session.py     # Database session management
│   │   └── init_db.py     # Database initialization & seeding
│   ├── api/               # API routes (future expansion)
│   │   └── routes.py      # Additional API endpoints
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── base.html      # Base template
│   │   ├── index.html     # Homepage
│   │   ├── bicycles.html  # Bicycle catalog
│   │   ├── bicycle_detail.html # Product details
│   │   ├── accessories.html # Accessories catalog
│   │   ├── about.html     # About us page
│   │   └── contact.html   # Contact page
│   └── static/            # Static files
│       ├── css/           # Custom CSS
│       ├── js/            # JavaScript files
│       └── images/        # Image assets
├── alembic/               # Database migrations
├── requirements.txt       # Python dependencies
├── start.py              # Development server script
├── deploy.py             # Production deployment script
├── alembic.ini           # Alembic configuration
└── README.md             # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.12+** (recommended)
- **pip** (Python package manager)
- **Git** (for version control)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd cyclestore
```

### 2. Create Virtual Environment
```bash
python3.12 -m venv .venv

# On macOS/Linux
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize Database
```bash
# Create tables and seed with sample data
python -c "from app.db.init_db import create_tables, seed_database; create_tables(); seed_database()"
```

### 5. Run the Application

#### Development Mode
```bash
# Using the start script
python start.py

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload
```

#### Production Mode
```bash
python deploy.py
```

### 6. Access the Application
- **Website**: http://localhost:8081
- **API Documentation**: http://localhost:8081/docs
- **Alternative API Docs**: http://localhost:8081/redoc

## 📖 API Documentation

The application includes auto-generated API documentation:

- **Swagger UI**: `/docs` - Interactive API documentation
- **ReDoc**: `/redoc` - Alternative API documentation
- **OpenAPI JSON**: `/openapi.json` - Raw OpenAPI specification

## 🗄️ Database Management

### Using Alembic for Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1
```

### Manual Database Operations

```bash
# Seed database with sample data
python -c "from app.db.init_db import seed_database; seed_database()"

# Create all tables
python -c "from app.db.init_db import create_tables; create_tables()"
```

## 🎯 Available Routes

### Web Routes
- `GET /` - Homepage with featured products
- `GET /bicycles` - Bicycle catalog with filtering
- `GET /accessories` - Accessory catalog
- `GET /bicycle/{id}` - Individual bicycle details
- `GET /about` - About us page
- `GET /contact` - Contact form
- `POST /contact` - Submit contact form

### API Routes (Future Development)
- RESTful API endpoints for product management
- User authentication and management
- Order processing system
- Inventory management

## 🎨 Customization

### Adding New Products
Products are stored in the database. Use the seeding script in `app/db/init_db.py` or create new products through the admin interface (future feature).

### Styling Changes
- Modify templates in `app/templates/`
- Update custom CSS in `app/static/css/`
- Customize Tailwind classes
- Add new JavaScript in `app/static/js/`

### Business Information
Update business details in:
- `app/config.py` - Application configuration
- Templates - Contact information, about page
- Database seeding script - Sample products

## 🚀 Deployment

### Environment Variables
```bash
export DATABASE_URL="postgresql://user:password@localhost/cyclestore"
export PORT="8080"
export WORKERS="4"
```

### Docker Deployment
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "deploy.py"]
```

### Traditional Server Deployment
1. Set up Python environment on server
2. Install dependencies
3. Configure reverse proxy (Nginx)
4. Set up SSL certificates
5. Use process manager (systemd/supervisor)

## 🔧 Development

### Adding New Features
1. Create models in `app/models/`
2. Add Pydantic schemas in `app/schemas/`
3. Implement CRUD operations in `app/crud/`
4. Create API routes in `app/api/`
5. Add templates in `app/templates/`
6. Generate and apply migrations

### Testing
```bash
# Run tests (when implemented)
pytest

# Check code quality
flake8 app/
black app/
mypy app/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is created for **Supreme Cycle & Rickshaw Company**. All rights reserved.

## 📞 Support

For technical support or business inquiries:

- **Email**: mujtaba.aamir1@gmail.com
- **WhatsApp**: +91 98398 50588
- **Visit Store**: Mehdawal Road, Khalilabad-272175, Sant Kabir Nagar, UP

---

**Supreme Cycle & Rickshaw Company** - Your trusted partner for all cycling needs since 1999 🚲
