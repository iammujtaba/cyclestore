"""
Admin routes for Supreme Cycle & Rickshaw Company
Handles admin authentication, product management, and admin panel
"""

from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List
import os
import shutil
from datetime import datetime

from app.db.session import get_db
from app.models.admin import Admin
from app.models.product import Bicycle, Accessory, ProductImage
from app.services.admin_auth_service import AdminAuthService
from app.crud import admin as admin_crud

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")
admin_auth_service = AdminAuthService()

# Admin authentication dependency
async def get_current_admin(request: Request, db: Session = Depends(get_db)) -> Optional[Admin]:
    """Get current logged-in admin from session"""
    session_token = request.cookies.get("admin_session_token")
    if session_token:
        return admin_auth_service.get_current_admin(db, session_token)
    return None

async def require_admin(request: Request, db: Session = Depends(get_db)) -> Admin:
    """Require admin authentication"""
    admin = await get_current_admin(request, db)
    if not admin:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    return admin

# Admin Login Routes
@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin/login.html", {"request": request})

@router.post("/login")
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle admin login"""
    admin = admin_auth_service.authenticate_admin(db, username, password)
    if not admin:
        return templates.TemplateResponse("admin/login.html", {
            "request": request,
            "error": "Invalid username or password"
        })
    
    # Create session
    session_token = admin_auth_service.create_session(db, admin, request)
    
    # Redirect to dashboard with session cookie
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(
        key="admin_session_token",
        value=session_token,
        max_age=24*60*60,  # 24 hours
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        path="/"  # Available for entire site
    )
    return response

@router.post("/logout")
async def admin_logout(request: Request, db: Session = Depends(get_db)):
    """Handle admin logout"""
    session_token = request.cookies.get("admin_session_token")
    if session_token:
        admin_auth_service.logout_admin(db, session_token)
    
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_session_token")
    return response

# Admin Dashboard
@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Admin dashboard with stats and quick actions"""
    
    # Get stats
    bicycle_count = db.query(Bicycle).count()
    accessory_count = db.query(Accessory).count()
    total_products = bicycle_count + accessory_count
    
    # Get low stock items (stock < 10)
    low_stock_bicycles = db.query(Bicycle).filter(Bicycle.stock_quantity < 10).count()
    low_stock_accessories = db.query(Accessory).filter(Accessory.stock_quantity < 10).count()
    low_stock_items = low_stock_bicycles + low_stock_accessories
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "admin": admin,
        "stats": {
            "total_bicycles": bicycle_count,
            "total_accessories": accessory_count,
            "total_products": total_products,
            "total_users": 0,  # Placeholder for future user management
            "low_stock_items": low_stock_items
        }
    })

# Product Management Routes
@router.get("/products", response_class=HTMLResponse)
async def admin_products(
    request: Request,
    product_type: Optional[str] = "all",
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Admin products management page"""
    
    bicycles = []
    accessories = []
    
    if product_type in ["all", "bicycle"]:
        bicycles = db.query(Bicycle).all()
    
    if product_type in ["all", "accessory"]:
        accessories = db.query(Accessory).all()
    
    return templates.TemplateResponse("admin/products_new.html", {
        "request": request,
        "admin": admin,
        "bicycles": bicycles,
        "accessories": accessories,
        "current_filter": product_type
    })

@router.get("/products/new", response_class=HTMLResponse)
async def admin_new_product(
    request: Request,
    product_type: str = "bicycle",
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Add new product form"""
    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "admin": admin,
        "product_type": product_type,
        "action": "create",
        "product": None
    })

@router.get("/products/{product_type}/{product_id}/edit", response_class=HTMLResponse)
async def admin_edit_product(
    request: Request,
    product_type: str,
    product_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Edit product form"""
    
    product = None
    if product_type == "bicycle":
        product = db.query(Bicycle).filter(Bicycle.id == product_id).first()
    elif product_type == "accessory":
        product = db.query(Accessory).filter(Accessory.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get product images
    images = db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
        ProductImage.product_type == product_type
    ).all()
    
    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "admin": admin,
        "product": product,
        "product_type": product_type,
        "product_id": product_id,
        "images": images,
        "action": "edit"
    })

@router.post("/products/create")
async def admin_create_product(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Create new product with enhanced features"""
    
    # Parse form data manually to handle features[] properly
    form_data = await request.form()
    
    # Extract basic fields with proper type handling
    product_type = str(form_data.get("product_type", ""))
    name = str(form_data.get("name", ""))
    description = str(form_data.get("description", ""))
    price_str = form_data.get("price", "0")
    price = float(price_str) if isinstance(price_str, str) else 0.0
    brand = str(form_data.get("brand", ""))
    category = str(form_data.get("category", ""))
    
    # Extract features[] as a list
    features = form_data.getlist("features[]")
    processed_features = [str(f).strip() for f in features if f and str(f).strip()]
    
    # Extract other fields
    frame_size = str(form_data.get("frame_size", "")) if form_data.get("frame_size") else None
    wheel_size = str(form_data.get("wheel_size", "")) if form_data.get("wheel_size") else None
    gear_count_str = form_data.get("gear_count")
    gear_count = int(gear_count_str) if gear_count_str and isinstance(gear_count_str, str) and gear_count_str.isdigit() else None
    brake_type = str(form_data.get("brake_type", "")) if form_data.get("brake_type") else None
    suspension = str(form_data.get("suspension", "")) if form_data.get("suspension") else None
    size = str(form_data.get("size", "")) if form_data.get("size") else None
    accessory_type = str(form_data.get("accessory_type", "")) if form_data.get("accessory_type") else None
    compatibility = str(form_data.get("compatibility", "")) if form_data.get("compatibility") else None
    stock_quantity_str = form_data.get("stock_quantity", "10")
    stock_quantity = int(stock_quantity_str) if isinstance(stock_quantity_str, str) and stock_quantity_str.isdigit() else 10
    is_featured = form_data.get("is_featured") == "true"
    in_stock = form_data.get("in_stock") == "true"
    
    # Handle image uploads
    images = []
    for key, value in form_data.items():
        if key == "images" and hasattr(value, 'filename') and hasattr(value, 'content_type'):
            images.append(value)
    
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "brand": brand,
        "category": category,
        "size": size,
        "stock_quantity": stock_quantity,
        "is_featured": is_featured,
        "in_stock": in_stock,
        "features": processed_features
    }
    
    try:
        if product_type == "bicycle":
            product_data.update({
                "frame_size": frame_size,
                "wheel_size": wheel_size,
                "gear_count": gear_count,
                "brake_type": brake_type,
                "suspension": suspension
            })
            product = admin_crud.create_bicycle(db, product_data)
        elif product_type == "accessory":
            product_data.update({
                "accessory_type": accessory_type,
                "compatibility": compatibility
            })
            product = admin_crud.create_accessory(db, product_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid product type")
        
        # Handle image uploads
        if images and product:
            from app.services.image_service import image_service
            
            for image in images:
                if hasattr(image, 'filename') and hasattr(image, 'content_type') and image.filename and image.content_type and image.content_type.startswith('image/'):
                    try:
                        result = await image_service.save_image(image, int(product.id), product_type)
                        if result['success'] and not product.image:
                            # Set first uploaded image as primary
                            if product_type == "bicycle":
                                admin_crud.update_bicycle(db, int(product.id), {"image": result['primary_path']})
                            else:
                                admin_crud.update_accessory(db, int(product.id), {"image": result['primary_path']})
                    except Exception as img_error:
                        print(f"Error uploading image {image.filename}: {img_error}")
        
        return RedirectResponse(url="/admin/products", status_code=302)
    
    except Exception as e:
        return templates.TemplateResponse("admin/product_form.html", {
            "request": request,
            "admin": admin,
            "product_type": product_type,
            "action": "create",
            "product": None,
            "error": f"Error creating product: {str(e)}"
        })

@router.post("/products/{product_type}/{product_id}/update")
async def admin_update_product(
    request: Request,
    product_type: str,
    product_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Update existing product with enhanced features"""
    
    # Parse form data manually to handle features[] properly
    form_data = await request.form()
    
    # Extract basic fields with proper type handling
    name = str(form_data.get("name", ""))
    description = str(form_data.get("description", ""))
    price_str = form_data.get("price", "0")
    price = float(price_str) if isinstance(price_str, str) else 0.0
    brand = str(form_data.get("brand", ""))
    category = str(form_data.get("category", ""))
    
    # Extract features[] as a list
    features = form_data.getlist("features[]")
    processed_features = [str(f).strip() for f in features if f and str(f).strip()]
    
    # Extract other fields
    frame_size = str(form_data.get("frame_size", "")) if form_data.get("frame_size") else None
    wheel_size = str(form_data.get("wheel_size", "")) if form_data.get("wheel_size") else None
    gear_count_str = form_data.get("gear_count")
    gear_count = int(gear_count_str) if gear_count_str and isinstance(gear_count_str, str) and gear_count_str.isdigit() else None
    brake_type = str(form_data.get("brake_type", "")) if form_data.get("brake_type") else None
    suspension = str(form_data.get("suspension", "")) if form_data.get("suspension") else None
    size = str(form_data.get("size", "")) if form_data.get("size") else None
    accessory_type = str(form_data.get("accessory_type", "")) if form_data.get("accessory_type") else None
    compatibility = str(form_data.get("compatibility", "")) if form_data.get("compatibility") else None
    stock_quantity_str = form_data.get("stock_quantity", "10")
    stock_quantity = int(stock_quantity_str) if isinstance(stock_quantity_str, str) and stock_quantity_str.isdigit() else 10
    is_featured = form_data.get("is_featured") == "true"
    in_stock = form_data.get("in_stock") == "true"
    
    # Handle image uploads
    images = []
    for key, value in form_data.items():
        if key == "images" and hasattr(value, 'filename') and hasattr(value, 'content_type'):
            images.append(value)
    
    product_data = {
        "name": name,
        "description": description,
        "price": price,
        "brand": brand,
        "category": category,
        "size": size,
        "stock_quantity": stock_quantity,
        "is_featured": is_featured,
        "in_stock": in_stock,
        "features": processed_features
    }
    
    try:
        if product_type == "bicycle":
            product_data.update({
                "frame_size": frame_size,
                "wheel_size": wheel_size,
                "gear_count": gear_count,
                "brake_type": brake_type,
                "suspension": suspension
            })
            product = admin_crud.update_bicycle(db, product_id, product_data)
        elif product_type == "accessory":
            product_data.update({
                "accessory_type": accessory_type,
                "compatibility": compatibility
            })
            product = admin_crud.update_accessory(db, product_id, product_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid product type")
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Handle image uploads
        if images:
            from app.services.image_service import image_service
            
            for image in images:
                if hasattr(image, 'filename') and hasattr(image, 'content_type') and image.filename and image.content_type and image.content_type.startswith('image/'):
                    try:
                        result = await image_service.save_image(image, product_id, product_type)
                        if result['success'] and not product.image:
                            # Set first uploaded image as primary
                            if product_type == "bicycle":
                                admin_crud.update_bicycle(db, product_id, {"image": result['primary_path']})
                            else:
                                admin_crud.update_accessory(db, product_id, {"image": result['primary_path']})
                    except Exception as img_error:
                        print(f"Error uploading image {image.filename}: {img_error}")
        
        return RedirectResponse(url="/admin/products", status_code=302)
    
    except Exception as e:
        return templates.TemplateResponse("admin/product_form.html", {
            "request": request,
            "admin": admin,
            "product_type": product_type,
            "product_id": product_id,
            "action": "edit",
            "error": f"Error updating product: {str(e)}"
        })

@router.post("/products/{product_type}/{product_id}/delete")
async def admin_delete_product(
    product_type: str,
    product_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Delete product"""
    
    try:
        if product_type == "bicycle":
            success = admin_crud.delete_bicycle(db, product_id)
        elif product_type == "accessory":
            success = admin_crud.delete_accessory(db, product_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid product type")
        
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return JSONResponse({"success": True, "message": "Product deleted successfully"})
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# Bulk Actions Routes
@router.post("/products/bulk-delete")
async def admin_bulk_delete_products(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Bulk delete products"""
    try:
        data = await request.json()
        products = data.get('products', [])
        
        deleted_count = 0
        for product in products:
            product_type = product.get('type')
            product_id = int(product.get('id'))
            
            if product_type == 'bicycle':
                success = admin_crud.delete_bicycle(db, product_id)
            elif product_type == 'accessory':
                success = admin_crud.delete_accessory(db, product_id)
            else:
                continue
                
            if success:
                deleted_count += 1
        
        return JSONResponse({
            "success": True, 
            "message": f"Deleted {deleted_count} products successfully"
        })
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.post("/products/bulk-update-stock")
async def admin_bulk_update_stock(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Bulk update stock quantities"""
    try:
        data = await request.json()
        products = data.get('products', [])
        stock_quantity = data.get('stock_quantity', 0)
        
        updated_count = 0
        for product in products:
            product_type = product.get('type')
            product_id = int(product.get('id'))
            
            update_data = {'stock_quantity': stock_quantity}
            
            if product_type == 'bicycle':
                success = admin_crud.update_bicycle(db, product_id, update_data)
            elif product_type == 'accessory':
                success = admin_crud.update_accessory(db, product_id, update_data)
            else:
                continue
                
            if success:
                updated_count += 1
        
        return JSONResponse({
            "success": True, 
            "message": f"Updated stock for {updated_count} products"
        })
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.post("/products/bulk-toggle-featured")
async def admin_bulk_toggle_featured(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Bulk toggle featured status"""
    try:
        data = await request.json()
        products = data.get('products', [])
        
        updated_count = 0
        for product in products:
            product_type = product.get('type')
            product_id = int(product.get('id'))
            
            # Get current product to toggle featured status
            if product_type == 'bicycle':
                current_product = db.query(Bicycle).filter(Bicycle.id == product_id).first()
                if current_product:
                    new_featured = not current_product.is_featured
                    success = admin_crud.update_bicycle(db, product_id, {'is_featured': new_featured})
            elif product_type == 'accessory':
                current_product = db.query(Accessory).filter(Accessory.id == product_id).first()
                if current_product:
                    new_featured = not current_product.is_featured
                    success = admin_crud.update_accessory(db, product_id, {'is_featured': new_featured})
            else:
                continue
                
            if success:
                updated_count += 1
        
        return JSONResponse({
            "success": True, 
            "message": f"Updated featured status for {updated_count} products"
        })
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.get("/products/export")
async def admin_export_products(
    request: Request,
    products: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Export products to CSV"""
    try:
        import csv
        from io import StringIO
        from fastapi.responses import StreamingResponse
        
        # Get products to export
        bicycles = []
        accessories = []
        
        if products:
            # Export selected products
            product_list = products.split(',')
            for product_spec in product_list:
                if '-' in product_spec:
                    product_type, product_id = product_spec.split('-', 1)
                    product_id = int(product_id)
                    
                    if product_type == 'bicycle':
                        bicycle = db.query(Bicycle).filter(Bicycle.id == product_id).first()
                        if bicycle:
                            bicycles.append(bicycle)
                    elif product_type == 'accessory':
                        accessory = db.query(Accessory).filter(Accessory.id == product_id).first()
                        if accessory:
                            accessories.append(accessory)
        else:
            # Export all products
            bicycles = db.query(Bicycle).all()
            accessories = db.query(Accessory).all()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'Type', 'ID', 'Name', 'Category', 'Price', 'Brand', 'Stock', 'Featured',
            'Frame Size', 'Wheel Size', 'Gear Count', 'Brake Type', 'Suspension',
            'Accessory Type', 'Compatibility', 'Created At'
        ])
        
        # Write bicycle data
        for bicycle in bicycles:
            writer.writerow([
                'Bicycle', bicycle.id, bicycle.name, bicycle.category, bicycle.price,
                bicycle.brand or '', bicycle.stock_quantity or 0, bicycle.is_featured or False,
                bicycle.frame_size or '', bicycle.wheel_size or '', bicycle.gear_count or '',
                bicycle.brake_type or '', bicycle.suspension or '', '', '', bicycle.created_at
            ])
        
        # Write accessory data
        for accessory in accessories:
            writer.writerow([
                'Accessory', accessory.id, accessory.name, accessory.category, accessory.price,
                accessory.brand or '', accessory.stock_quantity or 0, accessory.is_featured or False,
                '', '', '', '', '', accessory.accessory_type or '', 
                accessory.compatibility or '', accessory.created_at
            ])
        
        output.seek(0)
        
        # Return CSV file
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=products_export.csv"}
        )
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.get("/products/import", response_class=HTMLResponse)
async def admin_import_page(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Product import page"""
    return templates.TemplateResponse("admin/import_products.html", {
        "request": request,
        "admin": admin
    })

@router.post("/products/import")
async def admin_import_products(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Import products from CSV"""
    try:
        import csv
        from io import StringIO
        
        if not file.filename.endswith('.csv'):
            return JSONResponse({"success": False, "error": "Please upload a CSV file"}, status_code=400)
        
        contents = await file.read()
        csv_data = StringIO(contents.decode('utf-8'))
        reader = csv.DictReader(csv_data)
        
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                product_type = row.get('Type', '').lower()
                
                if product_type == 'bicycle':
                    bicycle_data = {
                        'name': row.get('Name', ''),
                        'category': row.get('Category', ''),
                        'price': float(row.get('Price', 0)),
                        'brand': row.get('Brand', ''),
                        'stock_quantity': int(row.get('Stock', 0)),
                        'is_featured': row.get('Featured', '').lower() in ['true', '1', 'yes'],
                        'frame_size': row.get('Frame Size', ''),
                        'wheel_size': row.get('Wheel Size', ''),
                        'gear_count': int(row.get('Gear Count', 0)) if row.get('Gear Count') else None,
                        'brake_type': row.get('Brake Type', ''),
                        'suspension': row.get('Suspension', ''),
                    }
                    admin_crud.create_bicycle(db, bicycle_data)
                    imported_count += 1
                    
                elif product_type == 'accessory':
                    accessory_data = {
                        'name': row.get('Name', ''),
                        'category': row.get('Category', ''),
                        'price': float(row.get('Price', 0)),
                        'brand': row.get('Brand', ''),
                        'stock_quantity': int(row.get('Stock', 0)),
                        'is_featured': row.get('Featured', '').lower() in ['true', '1', 'yes'],
                        'accessory_type': row.get('Accessory Type', ''),
                        'compatibility': row.get('Compatibility', ''),
                    }
                    admin_crud.create_accessory(db, accessory_data)
                    imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        result = {
            "success": True,
            "message": f"Imported {imported_count} products successfully"
        }
        
        if errors:
            result["warnings"] = errors[:10]  # Show first 10 errors
            
        return JSONResponse(result)
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# Enhanced Image Management Routes
@router.post("/products/{product_type}/{product_id}/images/upload")
async def admin_upload_product_images(
    product_type: str,
    product_id: int,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Upload multiple images for a product"""
    
    if product_type not in ['bicycle', 'accessory']:
        raise HTTPException(status_code=400, detail="Invalid product type")
    
    # Verify product exists
    if product_type == 'bicycle':
        product = db.query(Bicycle).filter(Bicycle.id == product_id).first()
    else:
        product = db.query(Accessory).filter(Accessory.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    uploaded_images = []
    errors = []
    
    for image in images:
        try:
            # Validate file type
            if not image.content_type.startswith('image/'):
                errors.append(f"Invalid file type for {image.filename}")
                continue
            
            # Validate file size (5MB limit)
            content = await image.read()
            if len(content) > 5 * 1024 * 1024:  # 5MB
                errors.append(f"File too large: {image.filename}")
                continue
            
            # Reset file position
            await image.seek(0)
            
            # Save using image service
            from app.services.image_service import image_service
            result = await image_service.save_image(image, product_id, product_type)
            
            if result['success']:
                uploaded_images.append(result['primary_path'])
                
                # Update product's primary image if it doesn't have one
                if not product.image:
                    product.image = result['primary_path']
                    db.commit()
            else:
                errors.append(f"Failed to save {image.filename}")
        
        except Exception as e:
            errors.append(f"Error processing {image.filename}: {str(e)}")
    
    return JSONResponse({
        "success": True,
        "uploaded_count": len(uploaded_images),
        "uploaded_images": uploaded_images,
        "errors": errors
    })

@router.delete("/products/{product_type}/{product_id}/images/{image_name}")
async def admin_delete_product_image(
    product_type: str,
    product_id: int,
    image_name: str,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Delete a specific product image"""
    
    try:
        # Find and delete the image record
        image_record = db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.product_type == product_type,
            ProductImage.image_name == image_name
        ).first()
        
        if image_record:
            # Delete physical file
            if os.path.exists(image_record.absolute_path):
                os.remove(image_record.absolute_path)
            
            # Delete database record
            db.delete(image_record)
            db.commit()
        
        return JSONResponse({"success": True, "message": "Image deleted successfully"})
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@router.post("/products/{product_type}/{product_id}/images/set-primary")
async def admin_set_primary_image(
    product_type: str,
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Set an image as the primary product image"""
    
    data = await request.json()
    image_path = data.get('image_path')
    
    if not image_path:
        raise HTTPException(status_code=400, detail="Image path required")
    
    try:
        # Update product's primary image
        if product_type == 'bicycle':
            product = db.query(Bicycle).filter(Bicycle.id == product_id).first()
        else:
            product = db.query(Accessory).filter(Accessory.id == product_id).first()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product.image = image_path
        db.commit()
        
        # Update image records to set primary flag
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.product_type == product_type
        ).update({"is_primary": False})
        
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.product_type == product_type,
            ProductImage.image_path.contains(image_path.split('/')[-1])
        ).update({"is_primary": True})
        
        db.commit()
        
        return JSONResponse({"success": True, "message": "Primary image updated"})
    
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# Create global instance
admin_auth_service = AdminAuthService()

@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    db: Session = Depends(get_db),
    admin: Admin = Depends(require_admin)
):
    """Admin users management page (placeholder)"""
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "admin": admin,
        "users": []  # Placeholder for future user management
    })
