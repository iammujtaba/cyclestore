from sqlalchemy.orm import Session
from app.models.product import Bicycle, Accessory
from app.schemas.product import BicycleCreate, AccessoryCreate
from typing import Optional, List
import json

def get_bicycles(db: Session, category: Optional[str] = None, size: Optional[str] = None, 
                min_price: Optional[int] = None, max_price: Optional[int] = None):
    query = db.query(Bicycle)
    
    if category:
        query = query.filter(Bicycle.category == category)
    if size:
        query = query.filter(Bicycle.size == size)
    if min_price:
        query = query.filter(Bicycle.price >= min_price)
    if max_price:
        query = query.filter(Bicycle.price <= max_price)
    
    return query.all()

def get_bicycle(db: Session, bicycle_id: int):
    return db.query(Bicycle).filter(Bicycle.id == bicycle_id).first()

def create_bicycle(db: Session, bicycle: BicycleCreate):
    bicycle_data = bicycle.dict()
    if bicycle_data.get('features'):
        bicycle_data['features'] = json.dumps(bicycle_data['features'])
    db_bike = Bicycle(**bicycle_data)
    db.add(db_bike)
    db.commit()
    db.refresh(db_bike)
    return db_bike

def get_accessories(db: Session, category: Optional[str] = None):
    query = db.query(Accessory)
    if category:
        query = query.filter(Accessory.category == category)
    return query.all()

def get_accessory(db: Session, accessory_id: int):
    return db.query(Accessory).filter(Accessory.id == accessory_id).first()

def create_accessory(db: Session, accessory: AccessoryCreate):
    db_acc = Accessory(**accessory.dict())
    db.add(db_acc)
    db.commit()
    db.refresh(db_acc)
    return db_acc

def get_categories(db: Session, product_type: str = "bicycle"):
    if product_type == "bicycle":
        result = db.query(Bicycle.category).distinct().all()
    else:
        result = db.query(Accessory.category).distinct().all()
    return [row[0] for row in result]

def get_sizes(db: Session):
    result = db.query(Bicycle.size).distinct().all()
    return [row[0] for row in result if row[0]]

def update_bicycle(db: Session, bicycle_id: int, bicycle_data: dict):
    """Update a bicycle record"""
    db_bike = db.query(Bicycle).filter(Bicycle.id == bicycle_id).first()
    if db_bike:
        for key, value in bicycle_data.items():
            if hasattr(db_bike, key):
                setattr(db_bike, key, value)
        db.commit()
        db.refresh(db_bike)
    return db_bike

def update_accessory(db: Session, accessory_id: int, accessory_data: dict):
    """Update an accessory record"""
    db_accessory = db.query(Accessory).filter(Accessory.id == accessory_id).first()
    if db_accessory:
        for key, value in accessory_data.items():
            if hasattr(db_accessory, key):
                setattr(db_accessory, key, value)
        db.commit()
        db.refresh(db_accessory)
    return db_accessory
