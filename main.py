from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from typing import Optional, List
import json

app = FastAPI(title="Supreme Cycle and Rickshaw Company")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Sample data - In real app, this would come from a database
BICYCLES = [
    {
        "id": 1,
        "name": "Mountain Explorer Pro",
        "category": "mountain",
        "price": 25000,
        "image": "/static/images/mountain-bike-1.jpg",
        "size": "large",
        "brand": "Supreme",
        "description": "Professional mountain bike with advanced suspension and durable frame.",
        "features": ["21-speed gear", "Shock absorber", "Disc brakes", "Aluminum frame"],
        "in_stock": True
    },
    {
        "id": 2,
        "name": "City Cruiser Deluxe",
        "category": "city",
        "price": 15000,
        "image": "/static/images/city-bike-1.jpg",
        "size": "medium",
        "brand": "Supreme",
        "description": "Comfortable city bike perfect for daily commuting and leisure rides.",
        "features": ["7-speed gear", "Comfortable seat", "LED lights", "Basket included"],
        "in_stock": True
    },
    {
        "id": 3,
        "name": "Speed Demon Racing",
        "category": "racing",
        "price": 35000,
        "image": "/static/images/racing-bike-1.jpg",
        "size": "large",
        "brand": "Supreme",
        "description": "High-performance racing bike designed for speed and agility.",
        "features": ["18-speed gear", "Carbon fiber frame", "Drop handlebars", "Racing tires"],
        "in_stock": True
    },
    {
        "id": 4,
        "name": "Kids Adventure",
        "category": "kids",
        "price": 8000,
        "image": "/static/images/kids-bike-1.jpg",
        "size": "small",
        "brand": "Supreme",
        "description": "Safe and fun bicycle designed specially for children.",
        "features": ["Training wheels", "Colorful design", "Safety reflectors", "Adjustable seat"],
        "in_stock": True
    },
    {
        "id": 5,
        "name": "Electric Power Bike",
        "category": "electric",
        "price": 45000,
        "image": "/static/images/electric-bike-1.jpg",
        "size": "large",
        "brand": "Supreme",
        "description": "Modern electric bike with long battery life and smart features.",
        "features": ["Electric motor", "60km range", "USB charging", "Digital display"],
        "in_stock": True
    },
    {
        "id": 6,
        "name": "Hybrid Comfort",
        "category": "hybrid",
        "price": 20000,
        "image": "/static/images/hybrid-bike-1.jpg",
        "size": "medium",
        "brand": "Supreme",
        "description": "Perfect blend of mountain and city bike features.",
        "features": ["14-speed gear", "Suspension fork", "Wide tires", "Ergonomic design"],
        "in_stock": True
    }
]

ACCESSORIES = [
    {
        "id": 101,
        "name": "Premium Bicycle Tyre",
        "category": "tyres",
        "price": 800,
        "image": "/static/images/tyre-1.jpg",
        "description": "High-quality rubber tyre with excellent grip and durability.",
        "size": "26 inch",
        "in_stock": True
    },
    {
        "id": 102,
        "name": "Inner Tube Set",
        "category": "tubes",
        "price": 150,
        "image": "/static/images/tube-1.jpg",
        "description": "Durable inner tubes compatible with most bicycle tyres.",
        "size": "Multiple sizes",
        "in_stock": True
    },
    {
        "id": 103,
        "name": "Alloy Rim 26\"",
        "category": "rims",
        "price": 1200,
        "image": "/static/images/rim-1.jpg",
        "description": "Lightweight aluminum alloy rim for better performance.",
        "size": "26 inch",
        "in_stock": True
    },
    {
        "id": 104,
        "name": "Heavy Duty Chain",
        "category": "chains",
        "price": 400,
        "image": "/static/images/chain-1.jpg",
        "description": "Strong and durable bicycle chain for smooth gear shifting.",
        "size": "Universal",
        "in_stock": True
    },
    {
        "id": 105,
        "name": "Suspension Fork",
        "category": "forks",
        "price": 2500,
        "image": "/static/images/fork-1.jpg",
        "description": "Advanced suspension fork for mountain bikes.",
        "size": "26/27.5 inch",
        "in_stock": True
    },
    {
        "id": 106,
        "name": "LED Headlight",
        "category": "lights",
        "price": 600,
        "image": "/static/images/light-1.jpg",
        "description": "Bright LED headlight with rechargeable battery.",
        "size": "Universal",
        "in_stock": True
    }
]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    featured_bikes = BICYCLES[:3]
    featured_accessories = ACCESSORIES[:3]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_bikes": featured_bikes,
        "featured_accessories": featured_accessories
    })

@app.get("/bicycles", response_class=HTMLResponse)
async def bicycles(
    request: Request,
    category: Optional[str] = None,
    size: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None
):
    filtered_bikes = BICYCLES.copy()
    
    if category:
        filtered_bikes = [bike for bike in filtered_bikes if bike["category"] == category]
    if size:
        filtered_bikes = [bike for bike in filtered_bikes if bike["size"] == size]
    if min_price:
        filtered_bikes = [bike for bike in filtered_bikes if bike["price"] >= min_price]
    if max_price:
        filtered_bikes = [bike for bike in filtered_bikes if bike["price"] <= max_price]
    
    categories = list(set([bike["category"] for bike in BICYCLES]))
    sizes = list(set([bike["size"] for bike in BICYCLES]))
    
    return templates.TemplateResponse("bicycles.html", {
        "request": request,
        "bicycles": filtered_bikes,
        "categories": categories,
        "sizes": sizes,
        "current_category": category,
        "current_size": size,
        "current_min_price": min_price,
        "current_max_price": max_price
    })

@app.get("/accessories", response_class=HTMLResponse)
async def accessories(
    request: Request,
    category: Optional[str] = None
):
    filtered_accessories = ACCESSORIES.copy()
    
    if category:
        filtered_accessories = [acc for acc in filtered_accessories if acc["category"] == category]
    
    categories = list(set([acc["category"] for acc in ACCESSORIES]))
    
    return templates.TemplateResponse("accessories.html", {
        "request": request,
        "accessories": filtered_accessories,
        "categories": categories,
        "current_category": category
    })

@app.get("/bicycle/{bicycle_id}", response_class=HTMLResponse)
async def bicycle_detail(request: Request, bicycle_id: int):
    bicycle = next((bike for bike in BICYCLES if bike["id"] == bicycle_id), None)
    if not bicycle:
        return templates.TemplateResponse("404.html", {"request": request})
    
    related_bikes = [bike for bike in BICYCLES if bike["category"] == bicycle["category"] and bike["id"] != bicycle_id][:3]
    
    return templates.TemplateResponse("bicycle_detail.html", {
        "request": request,
        "bicycle": bicycle,
        "related_bikes": related_bikes
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact", response_class=HTMLResponse)
async def contact_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    # In a real app, you would save this to a database or send an email
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "success": True,
        "message": "Thank you for your message! We'll get back to you soon."
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
