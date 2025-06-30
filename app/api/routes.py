from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import product as crud_product
from app.schemas import product as schema_product
from app.services.image_service import image_service
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List

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

@router.post("/upload-image/{product_type}/{product_id}")
async def upload_product_image(
    product_type: str,
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload an image for a product (bicycle or accessory)"""
    
    # Validate product type
    if product_type not in ['bicycle', 'accessory']:
        raise HTTPException(status_code=400, detail="Invalid product type")
    
    # Verify product exists
    if product_type == 'bicycle':
        product = crud_product.get_bicycle(db, product_id)
    else:
        product = crud_product.get_accessory(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        # Save the image using the image service
        result = await image_service.save_image(file, product_id, product_type)
        
        # Update the product's primary image if it doesn't have one
        if not product.image and result['success']:
            update_data = {"image": result['primary_path']}
            if product_type == 'bicycle':
                crud_product.update_bicycle(db, product_id, update_data)
            else:
                crud_product.update_accessory(db, product_id, update_data)
        
        return JSONResponse(content={
            "success": True,
            "message": "Image uploaded successfully",
            "image_url": result['primary_path'],
            "paths": result['paths']
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/product-images/{product_type}/{product_id}")
async def get_product_images(product_type: str, product_id: int):
    """Get all images for a product"""
    
    if product_type not in ['bicycle', 'accessory']:
        raise HTTPException(status_code=400, detail="Invalid product type")
    
    images = image_service.get_product_images(product_id, product_type)
    defaults = image_service.get_default_images()
    
    # If no images found, return default
    if not images:
        default_key = product_type if product_type in defaults else 'no_image'
        images = [defaults[default_key]]
    
    return JSONResponse(content={
        "images": images,
        "count": len(images)
    })

@router.delete("/product-images/{product_type}/{product_id}")
async def delete_product_images(product_type: str, product_id: int, db: Session = Depends(get_db)):
    """Delete all images for a product"""
    
    if product_type not in ['bicycle', 'accessory']:
        raise HTTPException(status_code=400, detail="Invalid product type")
    
    # Delete physical files
    image_service.delete_product_images(product_id, product_type)
    
    # Clear the image field in the database
    update_data = {"image": None}
    if product_type == 'bicycle':
        crud_product.update_bicycle(db, product_id, update_data)
    else:
        crud_product.update_accessory(db, product_id, update_data)
    
    return JSONResponse(content={"success": True, "message": "Images deleted successfully"})

@router.get("/admin/products", response_class=HTMLResponse)
async def admin_products(request: Request, db: Session = Depends(get_db)):
    """Simple admin page for managing products and images"""
    bicycles = crud_product.get_bicycles(db)
    accessories = crud_product.get_accessories(db)
    
    return templates.TemplateResponse("admin/products.html", {
        "request": request,
        "bicycles": bicycles,
        "accessories": accessories
    })
