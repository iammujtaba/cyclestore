from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import product as crud_product
from app.schemas import product as schema_product
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    featured_bikes = crud_product.get_bicycles(db)[:3]
    featured_accessories = crud_product.get_accessories(db)[:3]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_bikes": featured_bikes,
        "featured_accessories": featured_accessories
    })

@router.get("/bicycles", response_class=HTMLResponse)
async def bicycles(
    request: Request,
    category: Optional[str] = None,
    size: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    db: Session = Depends(get_db)
):
    filtered_bikes = crud_product.get_bicycles(db, category, size, min_price, max_price)
    categories = crud_product.get_categories(db, "bicycle")
    sizes = crud_product.get_sizes(db)
    
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

@router.get("/bicycle/{bicycle_id}", response_class=HTMLResponse)
async def bicycle_detail(bicycle_id: int, request: Request, db: Session = Depends(get_db)):
    bicycle = crud_product.get_bicycle(db, bicycle_id)
    if not bicycle:
        return templates.TemplateResponse("404.html", {"request": request})
    
    related_bikes = crud_product.get_bicycles(db, category=bicycle.category)
    related_bikes = [bike for bike in related_bikes if bike.id != bicycle_id][:3]
    
    return templates.TemplateResponse("bicycle_detail.html", {
        "request": request,
        "bicycle": bicycle,
        "related_bikes": related_bikes
    })

@router.get("/accessories", response_class=HTMLResponse)
async def accessories(
    request: Request,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    filtered_accessories = crud_product.get_accessories(db, category)
    categories = crud_product.get_categories(db, "accessory")
    
    return templates.TemplateResponse("accessories.html", {
        "request": request,
        "accessories": filtered_accessories,
        "categories": categories,
        "current_category": category
    })

@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@router.post("/contact", response_class=HTMLResponse)
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
