from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime, ForeignKey, func
from app.db.session import Base
import os
from typing import List, Optional

class ProductImage(Base):
    """Separate table for product images to support multiple images per product"""
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, nullable=False)  # Foreign key to bicycle/accessory
    product_type = Column(String, nullable=False)  # 'bicycle' or 'accessory'
    image_path = Column(String, nullable=False)  # Relative path to image
    image_name = Column(String, nullable=False)  # Original filename
    image_alt = Column(String)  # Alt text for accessibility
    is_primary = Column(Boolean, default=False)  # Primary product image
    display_order = Column(Integer, default=0)  # Order for image gallery
    created_at = Column(DateTime, server_default=func.now())
    
    @property
    def full_path(self) -> str:
        """Get full URL path for the image"""
        return f"/static/images/{self.image_path}"
    
    @property
    def absolute_path(self) -> str:
        """Get absolute file system path"""
        return os.path.join("app/static/images", self.image_path)

class Bicycle(Base):
    __tablename__ = "bicycles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    
    # Keep legacy image field for backward compatibility
    image = Column(String)  # Primary image path
    
    # Basic product fields
    brand = Column(String)
    description = Column(Text)
    size = Column(String)  # Legacy field for compatibility
    
    # Extended bicycle-specific fields
    frame_size = Column(String)  # S, M, L, XL, or specific measurements
    wheel_size = Column(String)  # 26", 27.5", 29", etc.
    gear_count = Column(Integer)  # Number of gears
    brake_type = Column(String)  # Disc, Rim, Hydraulic, etc.
    suspension = Column(String)  # None, Front, Full, etc.
    
    # Admin/inventory fields
    stock_quantity = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    
    features = Column(JSON)  # Store as JSON array - for compatibility
    in_stock = Column(Boolean, default=True)  # Legacy field
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def get_primary_image(self) -> str:
        """Get primary image URL"""
        # First try to get from image service
        from app.services.image_service import image_service
        product_id = getattr(self, 'id', None)
        if product_id:
            service_images = image_service.get_product_images(product_id, 'bicycle')
            if service_images:
                return service_images[0]
        
        # Fallback to database image field
        image_field = getattr(self, 'image', None)
        if image_field:
            # Ensure image path starts with /static/
            if not image_field.startswith('/static/'):
                return f"/static/{image_field.lstrip('/')}"
            return image_field
        
        # Default fallback
        return "/static/images/default-bicycle.svg"
    
    def get_image_gallery(self) -> List[str]:
        """Get all images for this bicycle"""
        from app.services.image_service import image_service
        product_id = getattr(self, 'id', None)
        if product_id:
            service_images = image_service.get_product_images(product_id, 'bicycle')
            if service_images:
                return service_images
        
        # Fallback to primary image
        primary = self.get_primary_image()
        return [primary] if primary else []

class Accessory(Base):
    __tablename__ = "accessories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    
    # Keep legacy image field for backward compatibility
    image = Column(String)  # Primary image path
    
    # Basic product fields
    brand = Column(String)
    description = Column(Text)
    size = Column(String)
    
    # Accessory-specific fields
    accessory_type = Column(String)  # Helmet, Light, Lock, etc.
    compatibility = Column(String)  # Compatible bike types or universal
    
    # Admin/inventory fields
    stock_quantity = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    
    features = Column(JSON)  # Store as JSON array - for compatibility
    in_stock = Column(Boolean, default=True)  # Legacy field
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def get_primary_image(self) -> str:
        """Get primary image URL"""
        # First try to get from image service
        from app.services.image_service import image_service
        product_id = getattr(self, 'id', None)
        if product_id:
            service_images = image_service.get_product_images(product_id, 'accessory')
            if service_images:
                return service_images[0]
        
        # Fallback to database image field
        image_field = getattr(self, 'image', None)
        if image_field:
            # Ensure image path starts with /static/
            if not image_field.startswith('/static/'):
                return f"/static/{image_field.lstrip('/')}"
            return image_field
        
        # Default fallback
        return "/static/images/default-accessory.svg"
    
    def get_image_gallery(self) -> List[str]:
        """Get all images for this accessory"""
        from app.services.image_service import image_service
        product_id = getattr(self, 'id', None)
        if product_id:
            service_images = image_service.get_product_images(product_id, 'accessory')
            if service_images:
                return service_images
        
        # Fallback to primary image
        primary = self.get_primary_image()
        return [primary] if primary else []
