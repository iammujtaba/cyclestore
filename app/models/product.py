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
    
    size = Column(String)
    brand = Column(String)
    description = Column(Text)
    features = Column(JSON)  # Store as JSON array
    in_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def get_primary_image(self) -> str:
        """Get primary image URL"""
        return getattr(self, 'image', None) or "/static/images/default-bicycle.svg"
    
    def get_image_gallery(self) -> List[str]:
        """Get all images for this bicycle"""
        # For now, return the primary image. Can be enhanced with ProductImage relationship
        return [self.get_primary_image()]

class Accessory(Base):
    __tablename__ = "accessories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    
    # Keep legacy image field for backward compatibility
    image = Column(String)  # Primary image path
    
    description = Column(Text)
    size = Column(String)
    in_stock = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def get_primary_image(self) -> str:
        """Get primary image URL"""
        return getattr(self, 'image', None) or "/static/images/default-accessory.svg"
    
    def get_image_gallery(self) -> List[str]:
        """Get all images for this accessory"""
        return [self.get_primary_image()]
