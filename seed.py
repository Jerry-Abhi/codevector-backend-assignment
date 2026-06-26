import sys
import time
import random
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from sqlalchemy import insert
from database import SessionLocal, engine, Base
from models import Product

# Data dictionaries for generating realistic, diverse product catalogs
ADJECTIVES = ["Aero", "Alpha", "Apex", "Bold", "Core", "Drift", "Eco", "Flux", "Giga", "Hyper", "Ion", "Nova", "Omni", "Prime", "Quantum", "Solar", "Titan", "Ultra", "Vortex", "Zenith"]
NOUNS = ["Beacon", "Catalyst", "Device", "Engine", "Fusion", "Grid", "Hub", "Instrument", "Link", "Matrix", "Node", "Orbit", "Pulse", "Radar", "Sensor", "Tracker", "Unit", "Vector", "Wave", "Zone"]
CATEGORIES = ["Electronics", "Home & Kitchen", "Apparel", "Sports & Outdoors", "Books", "Beauty & Personal Care", "Automotive", "Toys & Games", "Office Products", "Tools"]

def seed_database():
    db = SessionLocal()
    print("Connecting to database and verifying tables exist...")
    # Ensure tables and indexes are created in the database before seeding
    Base.metadata.create_all(bind=engine)
    
    # Check if database is already seeded to avoid accidental duplicate data
    total_existing = db.query(Product).count()
    if total_existing > 0:
        print(f"Database already contains {total_existing} products. Skipping seeding.")
        db.close()
        return

    print("Seeding database with exactly 200,000 products...")
    start_time = time.time()
    
    total_records = 200000
    batch_size = 10000  # 10k is optimal to balance memory limits and database packet sizes
    num_batches = total_records // batch_size
    
    # Base timestamp: starting 30 days ago
    # We will incrementally spread products over the 30-day window.
    # 30 days = 2,592,000 seconds
    # Spacing interval: 2,592,000s / 200,000 items = 12.96 seconds per item.
    base_time = datetime.now(timezone.utc) - timedelta(days=30)
    
    for b in range(num_batches):
        batch_start_time = time.time()
        products_batch = []
        
        for i in range(batch_size):
            global_idx = b * batch_size + i
            
            # Deterministic, unique names combined with randomized lists
            name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} {global_idx}"
            category = random.choice(CATEGORIES)
            price = Decimal(f"{random.randint(5, 1000)}.{random.randint(0, 99)}")
            
            # Spread timestamps sequentially to mock real historical data
            item_time = base_time + timedelta(seconds=global_idx * 12.96)
            
            products_batch.append({
                "name": name,
                "category": category,
                "price": price,
                "created_at": item_time,
                "updated_at": item_time
            })
            
        # Bulk Insert via SQLAlchemy Core
        # Calling db.execute(insert(Product), list_of_dicts) compiles to a single parameterized 
        # INSERT statement containing multi-row values (e.g. INSERT INTO products (...) VALUES (...), (...)).
        # This bypasses SQLAlchemy ORM object instantiation overhead, saving CPU and memory.
        db.execute(insert(Product), products_batch)
        db.commit()
        
        batch_duration = time.time() - batch_start_time
        print(f"Batch {b+1}/{num_batches} ({batch_size} records) inserted in {batch_duration:.2f}s")
        
    total_duration = time.time() - start_time
    print(f"Successfully seeded 200,000 products in {total_duration:.2f} seconds!")
    db.close()

if __name__ == "__main__":
    seed_database()
