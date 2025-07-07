from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.crud import product as crud_product
from app.crud import user as crud_user
from app.schemas import product as schema_product
from app.services.image_service import image_service
from app.services.auth_service import auth_service
from app.models.user import User
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Authentication dependency
async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get current logged-in user from session"""
    session_token = request.cookies.get("session_token")
    if session_token:
        return auth_service.get_current_user(db, session_token)
    return None

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    featured_bikes = crud_product.get_bicycles(db)[:3]
    featured_accessories = crud_product.get_accessories(db)[:3]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "featured_bikes": featured_bikes,
        "featured_accessories": featured_accessories,
        "user": current_user
    })

@router.get("/bicycles", response_class=HTMLResponse)
async def bicycles(
    request: Request,
    category: Optional[str] = None,
    size: Optional[str] = None,
    min_price: Optional[str] = None,
    max_price: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Convert price strings to integers, handling empty strings
    min_price_int = None
    max_price_int = None
    
    if min_price and min_price.strip():
        try:
            min_price_int = int(min_price)
        except ValueError:
            min_price_int = None
    
    if max_price and max_price.strip():
        try:
            max_price_int = int(max_price)
        except ValueError:
            max_price_int = None
    
    filtered_bikes = crud_product.get_bicycles(db, category, size, min_price_int, max_price_int)
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
        "current_max_price": max_price,
        "user": current_user
    })

@router.get("/bicycle/{bicycle_id}", response_class=HTMLResponse)
async def bicycle_detail(bicycle_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bicycle = crud_product.get_bicycle(db, bicycle_id)
    if not bicycle:
        return templates.TemplateResponse("404.html", {"request": request, "user": current_user})
    
    related_bikes = crud_product.get_bicycles(db, category=bicycle.category)
    related_bikes = [bike for bike in related_bikes if bike.id != bicycle_id][:3]
    
    return templates.TemplateResponse("bicycle_detail.html", {
        "request": request,
        "bicycle": bicycle,
        "related_bikes": related_bikes,
        "user": current_user
    })

@router.get("/accessories", response_class=HTMLResponse)
async def accessories(
    request: Request,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filtered_accessories = crud_product.get_accessories(db, category)
    categories = crud_product.get_categories(db, "accessory")
    
    return templates.TemplateResponse("accessories.html", {
        "request": request,
        "accessories": filtered_accessories,
        "categories": categories,
        "current_category": category,
        "user": current_user
    })

@router.get("/about", response_class=HTMLResponse)
async def about(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("about.html", {"request": request, "user": current_user})

@router.get("/contact", response_class=HTMLResponse)
async def contact(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("contact.html", {"request": request, "user": current_user})

@router.post("/contact", response_class=HTMLResponse)
async def contact_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    # In a real app, you would save this to a database or send an email
    return templates.TemplateResponse("contact.html", {
        "request": request,
        "success": True,
        "message": "Thank you for your message! We'll get back to you soon.",
        "user": current_user
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
async def admin_products(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Simple admin page for managing products and images"""
    bicycles = crud_product.get_bicycles(db)
    accessories = crud_product.get_accessories(db)
    
    return templates.TemplateResponse("admin/products.html", {
        "request": request,
        "bicycles": bicycles,
        "accessories": accessories,
        "user": current_user
    })

# Authentication Routes
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Display registration form"""
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Handle user registration"""
    
    # Validate passwords match
    if password != confirm_password:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "Passwords do not match",
            "form_data": {
                "email": email,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone or "",
                "address": address or "",
                "city": city or "",
                "state": state or "",
                "pincode": pincode or ""
            }
        })
    
    # Validate password strength
    if len(password) < 6:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": "Password must be at least 6 characters long",
            "form_data": {
                "email": email,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone or "",
                "address": address or "",
                "city": city or "",
                "state": state or "",
                "pincode": pincode or ""
            }
        })
    
    try:
        user_data = {
            "email": email,
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode
        }
        
        user = auth_service.register_user(db, user_data)
        
        # Auto-login after registration
        session_token = auth_service.create_session(db, user, request)
        
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            secure=False  # Set to True in production with HTTPS
        )
        
        return response
        
    except HTTPException as e:
        return templates.TemplateResponse("auth/register.html", {
            "request": request,
            "error": e.detail,
            "form_data": request.__dict__
        })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login form"""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    remember_me: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Handle user login"""
    
    try:
        user = auth_service.authenticate_user(db, email, password)
        
        if not user:
            return templates.TemplateResponse("auth/login.html", {
                "request": request,
                "error": "Invalid email or password",
                "email": email
            })
        
        # Create session
        session_token = auth_service.create_session(db, user, request)
        
        # Set session duration based on remember_me
        max_age = 30 * 24 * 60 * 60 if remember_me else 24 * 60 * 60  # 30 days or 1 day
        
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=max_age,
            httponly=True,
            secure=False  # Set to True in production with HTTPS
        )
        
        return response
        
    except HTTPException as e:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": e.detail,
            "email": email
        })

@router.get("/logout")
async def logout_user(request: Request, db: Session = Depends(get_db)):
    """Handle user logout"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        auth_service.logout_user(db, session_token)
    
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session_token")
    
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User dashboard page"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get user's recent activity, orders, etc.
    # For now, we'll show basic user info and some featured products
    featured_bikes = crud_product.get_bicycles(db)[:3]
    featured_accessories = crud_product.get_accessories(db)[:3]
    
    return templates.TemplateResponse("dashboard/index.html", {
        "request": request,
        "user": current_user,
        "featured_bikes": featured_bikes,
        "featured_accessories": featured_accessories
    })

@router.get("/profile", response_class=HTMLResponse)
async def user_profile(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """User profile page"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("dashboard/profile.html", {
        "request": request,
        "user": current_user
    })

@router.post("/profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    pincode: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Update user information using CRUD
    user_data = {
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "address": address,
        "city": city,
        "state": state,
        "pincode": pincode
    }
    
    updated_user = crud_user.update_user(db, int(current_user.id), user_data)
    
    return templates.TemplateResponse("dashboard/profile.html", {
        "request": request,
        "user": updated_user,
        "success": "Profile updated successfully!"
    })
