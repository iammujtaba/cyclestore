from pydantic import BaseModel
from typing import Optional, List

class BicycleBase(BaseModel):
    name: str
    category: str
    price: float
    image: Optional[str] = None
    size: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = []
    in_stock: Optional[bool] = True

class BicycleCreate(BicycleBase):
    pass

class Bicycle(BicycleBase):
    id: int
    class Config:
        from_attributes = True

class AccessoryBase(BaseModel):
    name: str
    category: str
    price: float
    image: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    in_stock: Optional[bool] = True

class AccessoryCreate(AccessoryBase):
    pass

class Accessory(AccessoryBase):
    id: int
    class Config:
        from_attributes = True
