# Supreme Cycle and Rickshaw Company - Online Store

A beautiful, modern e-commerce website for Supreme Cycle and Rickshaw Company located at Mehdawal Road, Khalilabad. Built with FastAPI backend, Jinja2 templates, and Tailwind CSS for a stunning user experience.

## Features

### 🎨 Beautiful Design
- Modern, responsive design with Tailwind CSS
- Smooth animations and hover effects
- Mobile-first approach
- Beautiful gradient backgrounds and card designs

### 🚲 Product Catalog
- Comprehensive bicycle collection (Mountain, City, Racing, Kids, Electric, Hybrid)
- Detailed product pages with specifications
- Advanced filtering by category, size, and price
- High-quality product displays

### 🛠️ Accessories Store
- Wide range of bicycle accessories (Tyres, Tubes, Rims, Chains, Forks, Lights)
- Category-based browsing
- Quick add-to-cart functionality

### 📱 User Experience
- Fully responsive design
- Fast loading times
- Intuitive navigation
- Search functionality
- Shopping cart and wishlist features

### 🏪 Business Information
- Complete store information
- Contact forms
- Store location and hours
- About us page with team information

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, Jinja2 Templates
- **Styling**: Tailwind CSS
- **JavaScript**: jQuery
- **Icons**: Font Awesome 6
- **Server**: Uvicorn

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### 1. Clone or Download the Project
```bash
cd cyclestore
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

Or alternatively:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Website
Open your browser and navigate to:
```
http://localhost:8000
```

## Project Structure

```
cyclestore/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── bicycles.html     # Bicycles listing
│   ├── bicycle_detail.html # Individual bicycle page
│   ├── accessories.html  # Accessories listing
│   ├── about.html        # About us page
│   ├── contact.html      # Contact page
│   └── 404.html          # Error page
├── static/               # Static files
│   ├── css/
│   │   └── custom.css    # Custom CSS styles
│   ├── js/
│   │   └── main.js       # Custom JavaScript
│   └── images/           # Image assets
└── README.md            # This file
```

## Features Explained

### Homepage
- Hero section with call-to-action buttons
- Featured bicycles and accessories
- Company statistics and testimonials
- Responsive design with smooth animations

### Bicycle Catalog
- Filter by category (Mountain, City, Racing, Kids, Electric, Hybrid)
- Filter by size (Small, Medium, Large)
- Price range filtering
- Sorting by name and price
- Detailed product cards with specifications

### Product Detail Pages
- High-quality product images
- Comprehensive specifications
- Feature highlights
- Related products
- Add to cart functionality

### Accessories Store
- Category-wise organization
- Quick view product cards
- Easy add-to-cart functionality
- Responsive grid layout

### Contact & About Pages
- Complete business information
- Contact form with validation
- FAQ section
- Team information
- Store location and hours

## Customization

### Adding New Products
Edit the `BICYCLES` and `ACCESSORIES` lists in `main.py` to add new products:

```python
BICYCLES.append({
    "id": 7,
    "name": "Your New Bike",
    "category": "mountain",
    "price": 30000,
    "image": "/static/images/new-bike.jpg",
    "size": "large",
    "brand": "Supreme",
    "description": "Description here...",
    "features": ["Feature 1", "Feature 2"],
    "in_stock": True
})
```

### Styling Changes
- Modify `static/css/custom.css` for custom styles
- Update Tailwind classes in templates
- Change color scheme in the CSS variables

### Adding New Pages
1. Create new template in `templates/`
2. Add route in `main.py`
3. Update navigation in `base.html`

## Deployment

### For Production
1. Set up a proper database (PostgreSQL/MySQL)
2. Configure environment variables
3. Use a production ASGI server like Gunicorn
4. Set up reverse proxy with Nginx
5. Configure SSL certificates

### Environment Variables
```bash
export DATABASE_URL="your_database_url"
export SECRET_KEY="your_secret_key"
export EMAIL_HOST="your_email_host"
export EMAIL_PORT="your_email_port"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For support and questions:
- Email: info@supremecycle.com
- Phone: +91 98765 43210
- Address: Mehdawal Road, Khalilabad

## License

This project is created for Supreme Cycle and Rickshaw Company. All rights reserved.

---

**Supreme Cycle and Rickshaw Company** - Your trusted partner for all cycling needs since 2020.
