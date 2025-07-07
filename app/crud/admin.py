from sqlalchemy.orm import Session
from app.models.product import Bicycle, Accessory, ProductImage
from app.models.admin import Admin
from typing import Optional, Dict, Any, List
import os
import uuid
import shutil
from datetime import datetime
from fastapi import UploadFile

def create_bicycle(db: Session, bicycle_data: Dict[str, Any]) -> Bicycle:
    """Create a new bicycle"""
    bicycle = Bicycle(**bicycle_data)
    db.add(bicycle)
    db.commit()
    db.refresh(bicycle)
    return bicycle

def update_bicycle(db: Session, bicycle_id: int, bicycle_data: Dict[str, Any]) -> Optional[Bicycle]:
    """Update bicycle information"""
    bicycle = db.query(Bicycle).filter(Bicycle.id == bicycle_id).first()
    if not bicycle:
        return None
    
    for field, value in bicycle_data.items():
        if hasattr(bicycle, field):
            setattr(bicycle, field, value)
    
    db.commit()
    db.refresh(bicycle)
    return bicycle

def delete_bicycle(db: Session, bicycle_id: int) -> bool:
    """Delete a bicycle"""
    bicycle = db.query(Bicycle).filter(Bicycle.id == bicycle_id).first()
    if not bicycle:
        return False
    
    # Delete associated images
    images = db.query(ProductImage).filter(
        ProductImage.product_id == bicycle_id,
        ProductImage.product_type == "bicycle"
    ).all()
    
    for image in images:
        # Delete physical file
        try:
            if os.path.exists(image.absolute_path):
                os.remove(image.absolute_path)
        except:
            pass
        db.delete(image)
    
    db.delete(bicycle)
    db.commit()
    return True

def create_accessory(db: Session, accessory_data: Dict[str, Any]) -> Accessory:
    """Create a new accessory"""
    accessory = Accessory(**accessory_data)
    db.add(accessory)
    db.commit()
    db.refresh(accessory)
    return accessory

def update_accessory(db: Session, accessory_id: int, accessory_data: Dict[str, Any]) -> Optional[Accessory]:
    """Update accessory information"""
    accessory = db.query(Accessory).filter(Accessory.id == accessory_id).first()
    if not accessory:
        return None
    
    for field, value in accessory_data.items():
        if hasattr(accessory, field):
            setattr(accessory, field, value)
    
    db.commit()
    db.refresh(accessory)
    return accessory

def delete_accessory(db: Session, accessory_id: int) -> bool:
    """Delete an accessory"""
    accessory = db.query(Accessory).filter(Accessory.id == accessory_id).first()
    if not accessory:
        return False
    
    # Delete associated images
    images = db.query(ProductImage).filter(
        ProductImage.product_id == accessory_id,
        ProductImage.product_type == "accessory"
    ).all()
    
    for image in images:
        # Delete physical file
        try:
            if os.path.exists(image.absolute_path):
                os.remove(image.absolute_path)
        except:
            pass
        db.delete(image)
    
    db.delete(accessory)
    db.commit()
    return True

def get_all_bicycles(db: Session, skip: int = 0, limit: int = 100) -> List[Bicycle]:
    """Get all bicycles for admin"""
    return db.query(Bicycle).offset(skip).limit(limit).all()

def get_all_accessories(db: Session, skip: int = 0, limit: int = 100) -> List[Accessory]:
    """Get all accessories for admin"""
    return db.query(Accessory).offset(skip).limit(limit).all()

def get_product_images(db: Session, product_id: int, product_type: str) -> List[ProductImage]:
    """Get all images for a product"""
    return db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
        ProductImage.product_type == product_type
    ).order_by(ProductImage.display_order).all()

def add_product_image(db: Session, image_data: Dict[str, Any]) -> ProductImage:
    """Add a new product image"""
    image = ProductImage(**image_data)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

def delete_product_image(db: Session, image_id: int) -> bool:
    """Delete a product image"""
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not image:
        return False
    
    # Delete physical file
    try:
        if os.path.exists(image.absolute_path):
            os.remove(image.absolute_path)
    except:
        pass
    
    db.delete(image)
    db.commit()
    return True

def set_primary_image(db: Session, product_id: int, product_type: str, image_id: int) -> bool:
    """Set an image as primary for a product"""
    # Remove primary flag from all images of this product
    db.query(ProductImage).filter(
        ProductImage.product_id == product_id,
        ProductImage.product_type == product_type
    ).update({"is_primary": False})
    
    # Set the selected image as primary
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if image:
        image.is_primary = True
        db.commit()
        return True
    
    return False

async def save_product_image(
    db: Session, 
    product_id: int, 
    product_type: str, 
    file: UploadFile
) -> str:
    """Save uploaded product image and create database record"""
    
    # Create upload directory if it doesn't exist
    upload_dir = "app/static/images/products"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    unique_filename = f"{product_type}_{product_id}_{uuid.uuid4().hex[:8]}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create database record
    relative_path = f"products/{unique_filename}"
    image_data = {
        "product_id": product_id,
        "product_type": product_type,
        "image_path": relative_path,
        "image_name": file.filename or unique_filename,
        "image_alt": f"{product_type} image",
        "is_primary": False,
        "display_order": 0
    }
    
    image = add_product_image(db, image_data)
    return image.full_path
