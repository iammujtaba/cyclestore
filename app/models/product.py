from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON
from app.db.session import Base

class Bicycle(Base):
    __tablename__ = "bicycles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String)
    size = Column(String)
    brand = Column(String)
    description = Column(Text)
    features = Column(JSON)  # Store as JSON array
    in_stock = Column(Boolean, default=True)

class Accessory(Base):
    __tablename__ = "accessories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String)
    description = Column(Text)
    size = Column(String)
    in_stock = Column(Boolean, default=True)
