from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.config import settings
from app.db.session import get_db, engine, Base
from app.models.product import Bicycle, Accessory, ProductImage
from app.models.user import User, UserSession
from app.api.routes import router as api_router
from app.services.auth_service import auth_service

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Include API routes
app.include_router(api_router)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

@app.on_event("startup")
async def startup_event():
    """Seed database with sample data on startup"""
    try:
        from app.db.init_db import seed_database
        seed_database()
        print("Database seeded successfully")
    except Exception as e:
        print(f"Database seeding failed: {e}")
        # Continue startup even if seeding fails

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    featured_bikes = db.query(Bicycle).limit(3).all()
    featured_accessories = db.query(Accessory).limit(3).all()
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
    max_price: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Bicycle)
    
    if category:
        query = query.filter(Bicycle.category == category)
    if size:
        query = query.filter(Bicycle.size == size)
    if min_price:
        query = query.filter(Bicycle.price >= min_price)
    if max_price:
        query = query.filter(Bicycle.price <= max_price)
    
    filtered_bikes = query.all()
    
    # Get unique categories and sizes for filters
    categories = db.query(Bicycle.category).distinct().all()
    categories = [cat[0] for cat in categories]
    sizes = db.query(Bicycle.size).distinct().all()
    sizes = [size[0] for size in sizes if size[0]]
    
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
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Accessory)
    
    if category:
        query = query.filter(Accessory.category == category)
    
    filtered_accessories = query.all()
    
    categories = db.query(Accessory.category).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return templates.TemplateResponse("accessories.html", {
        "request": request,
        "accessories": filtered_accessories,
        "categories": categories,
        "current_category": category
    })

@app.get("/bicycle/{bicycle_id}", response_class=HTMLResponse)
async def bicycle_detail(request: Request, bicycle_id: int, db: Session = Depends(get_db)):
    bicycle = db.query(Bicycle).filter(Bicycle.id == bicycle_id).first()
    if not bicycle:
        return templates.TemplateResponse("404.html", {"request": request})
    
    related_bikes = db.query(Bicycle).filter(
        Bicycle.category == bicycle.category,
        Bicycle.id != bicycle_id
    ).limit(3).all()
    
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
