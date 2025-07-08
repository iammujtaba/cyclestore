from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models.product import Bicycle, Accessory

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def seed_database():
    """Populate database with sample data"""
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(Bicycle).first() or db.query(Accessory).first():
        db.close()
        return
    
    # Sample bicycles
    bicycles = [
        Bicycle(
            id=1,
            name="Mountain Explorer Pro",
            category="mountain",
            price=25000,
            image="/static/images/products/product_1_0f5931cd.png",
            size="large",
            brand="Supreme",
            description="Professional mountain bike with advanced suspension and durable frame. BSA quality since 1999.",
            features=["21-speed gear", "Shock absorber", "Disc brakes", "Aluminum frame"],
            in_stock=True
        ),
        Bicycle(
            id=2,
            name="City Cruiser Deluxe",
            category="city",
            price=15000,
            image="/static/images/default-bicycle.svg",
            size="medium",
            brand="Supreme",
            description="Comfortable city bike perfect for daily commuting and leisure rides.",
            features=["7-speed gear", "Comfortable seat", "LED lights", "Basket included"],
            in_stock=True
        ),
        Bicycle(
            id=3,
            name="Speed Demon Racing",
            category="racing",
            price=35000,
            image="/static/images/default-bicycle.svg",
            size="large",
            brand="Supreme",
            description="High-performance racing bike designed for speed and agility.",
            features=["18-speed gear", "Carbon fiber frame", "Drop handlebars", "Racing tires"],
            in_stock=True
        ),
        Bicycle(
            id=4,
            name="Kids Adventure",
            category="kids",
            price=8000,
            image="/static/images/default-bicycle.svg",
            size="small",
            brand="Supreme",
            description="Safe and fun bicycle designed specially for children.",
            features=["Training wheels", "Colorful design", "Safety reflectors", "Adjustable seat"],
            in_stock=True
        ),
        Bicycle(
            id=5,
            name="Electric Power Bike",
            category="electric",
            price=45000,
            image="/static/images/default-bicycle.svg",
            size="large",
            brand="Supreme",
            description="Modern electric bike with long battery life and smart features.",
            features=["Electric motor", "60km range", "USB charging", "Digital display"],
            in_stock=True
        ),
        Bicycle(
            id=6,
            name="Hybrid Comfort",
            category="hybrid",
            price=20000,
            image="/static/images/default-bicycle.svg",
            size="medium",
            brand="Supreme",
            description="Perfect blend of mountain and city bike features.",
            features=["14-speed gear", "Suspension fork", "Wide tires", "Ergonomic design"],
            in_stock=True
        )
    ]
    
    # Sample accessories
    accessories = [
        Accessory(
            id=101,
            name="Premium Bicycle Tyre",
            category="tyres",
            price=800,
            image="/static/images/default-accessory.svg",
            description="High-quality rubber tyre with excellent grip and durability.",
            size="26 inch",
            in_stock=True
        ),
        Accessory(
            id=102,
            name="Inner Tube Set",
            category="tubes",
            price=150,
            image="/static/images/default-accessory.svg",
            description="Durable inner tubes compatible with most bicycle tyres.",
            size="Multiple sizes",
            in_stock=True
        ),
        Accessory(
            id=103,
            name="Alloy Rim 26\"",
            category="rims",
            price=1200,
            image="/static/images/default-accessory.svg",
            description="Lightweight aluminum alloy rim for better performance.",
            size="26 inch",
            in_stock=True
        ),
        Accessory(
            id=104,
            name="Heavy Duty Chain",
            category="chains",
            price=400,
            image="/static/images/default-accessory.svg",
            description="Strong and durable bicycle chain for smooth gear shifting.",
            size="Universal",
            in_stock=True
        ),
        Accessory(
            id=105,
            name="Suspension Fork",
            category="forks",
            price=2500,
            image="/static/images/default-accessory.svg",
            description="Advanced suspension fork for mountain bikes.",
            size="26/27.5 inch",
            in_stock=True
        ),
        Accessory(
            id=106,
            name="LED Headlight",
            category="lights",
            price=600,
            image="/static/images/default-accessory.svg",
            description="Bright LED headlight with rechargeable battery.",
            size="Universal",
            in_stock=True
        )
    ]
    
    # Add all bicycles and accessories to database
    for bicycle in bicycles:
        db.add(bicycle)
    
    for accessory in accessories:
        db.add(accessory)
    
    try:
        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    seed_database()
