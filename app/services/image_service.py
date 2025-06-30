"""
Image Management Service for Supreme Cycle & Rickshaw Company
Handles upload, storage, optimization, and serving of product images
"""

import os
import uuid
import shutil
from typing import List, Optional, Tuple
from pathlib import Path
from PIL import Image, ImageOps
import aiofiles
from fastapi import UploadFile, HTTPException

class ImageService:
    """Service for handling product image operations"""
    
    def __init__(self):
        self.base_path = Path("app/static/images")
        self.products_path = self.base_path / "products"
        self.accessories_path = self.base_path / "accessories"
        self.thumbnails_path = self.base_path / "thumbnails"
        
        # Create directories if they don't exist
        self.base_path.mkdir(exist_ok=True)
        self.products_path.mkdir(exist_ok=True)
        self.accessories_path.mkdir(exist_ok=True)
        self.thumbnails_path.mkdir(exist_ok=True)
        
        # Supported image formats
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.webp'}
        
        # Image size configurations
        self.image_sizes = {
            'original': None,  # Keep original size
            'large': (1200, 1200),
            'medium': (600, 600),
            'small': (300, 300),
            'thumbnail': (150, 150)
        }
    
    def generate_filename(self, original_filename: str, product_id: int, size: str = 'original') -> str:
        """Generate a unique filename for the image"""
        ext = Path(original_filename).suffix.lower()
        if size == 'original':
            return f"product_{product_id}_{uuid.uuid4().hex[:8]}{ext}"
        return f"product_{product_id}_{uuid.uuid4().hex[:8]}_{size}{ext}"
    
    async def save_image(
        self, 
        file: UploadFile, 
        product_id: int, 
        product_type: str = 'bicycle',
        generate_thumbnails: bool = True
    ) -> dict:
        """
        Save uploaded image and generate different sizes
        Returns dict with paths to different image sizes
        """
        
        # Validate file type
        if not self._is_valid_image(file.filename):
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Determine save directory
        save_dir = self.products_path if product_type == 'bicycle' else self.accessories_path
        
        # Generate filename
        original_filename = self.generate_filename(file.filename, product_id)
        
        # Save original file
        file_path = save_dir / original_filename
        
        try:
            # Save uploaded file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Generate different sizes if requested
            image_paths = {'original': str(file_path.relative_to(self.base_path))}
            
            if generate_thumbnails:
                thumbnail_paths = await self._generate_thumbnails(file_path, product_id)
                image_paths.update(thumbnail_paths)
            
            return {
                'success': True,
                'paths': image_paths,
                'primary_path': f"/static/images/{image_paths['medium'] or image_paths['original']}"
            }
            
        except Exception as e:
            # Clean up on error
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")
    
    async def _generate_thumbnails(self, original_path: Path, product_id: int) -> dict:
        """Generate thumbnail versions of the image"""
        thumbnail_paths = {}
        
        try:
            with Image.open(original_path) as img:
                # Convert to RGB if necessary (for transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                for size_name, dimensions in self.image_sizes.items():
                    if size_name == 'original' or dimensions is None:
                        continue
                    
                    # Create resized image
                    resized = ImageOps.fit(img, dimensions, Image.Resampling.LANCZOS)
                    
                    # Generate filename for this size
                    size_filename = self.generate_filename(original_path.name, product_id, size_name)
                    size_path = self.thumbnails_path / size_filename
                    
                    # Save resized image
                    resized.save(size_path, optimize=True, quality=85)
                    
                    thumbnail_paths[size_name] = str(size_path.relative_to(self.base_path))
        
        except Exception as e:
            print(f"Error generating thumbnails: {e}")
        
        return thumbnail_paths
    
    def _is_valid_image(self, filename: str) -> bool:
        """Check if file has valid image extension"""
        return Path(filename).suffix.lower() in self.supported_formats
    
    def delete_product_images(self, product_id: int, product_type: str = 'bicycle'):
        """Delete all images for a product"""
        search_dirs = [self.products_path, self.accessories_path, self.thumbnails_path]
        
        for directory in search_dirs:
            if directory.exists():
                for file_path in directory.glob(f"product_{product_id}_*"):
                    try:
                        file_path.unlink()
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")
    
    def get_product_images(self, product_id: int, product_type: str = 'bicycle') -> List[str]:
        """Get all image paths for a product"""
        search_dirs = [self.products_path, self.accessories_path]
        image_paths = []
        
        for directory in search_dirs:
            if directory.exists():
                for file_path in directory.glob(f"product_{product_id}_*"):
                    rel_path = file_path.relative_to(self.base_path)
                    image_paths.append(f"/static/images/{rel_path}")
        
        return sorted(image_paths)
    
    def get_default_images(self) -> dict:
        """Get default placeholder images"""
        return {
            'bicycle': '/static/images/default-bicycle.svg',
            'accessory': '/static/images/default-accessory.svg',
            'no_image': '/static/images/no-image.svg'
        }

# Create global instance
image_service = ImageService()
