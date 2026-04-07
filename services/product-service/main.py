from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db
from security import verify_token
import random

from sqlalchemy import text
models.Base.metadata.create_all(bind=engine)

# Auto-migration for missing columns
try:
    with engine.begin() as conn:
        columns_to_add = {
            "video_url": "NVARCHAR(500) NULL",
            "youtube_id": "NVARCHAR(100) NULL",
            "category": "NVARCHAR(100) NULL",
            "stock": "INT DEFAULT 0"
        }
        for col, type_info in columns_to_add.items():
            result = conn.execute(text(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'products' AND COLUMN_NAME = '{col}'"))
            if not result.fetchone():
                print(f"Adding missing column '{col}' to 'products' table")
                conn.execute(text(f"ALTER TABLE products ADD {col} {type_info}"))
except Exception as e:
    print(f"Migration failed for product-service: {e}")

app = FastAPI(title="Product Service")

# PUNEET'S STABLE MASTER CATALOG - ABSOLUTELY FIXED TO PREVENT 'GADBAD'
MASTER_CATALOG = [
    { "id": 201, "name": "Shararat (Dhurandhar)", "category": "Action & Adventure", "youtube_id": "YyepU5ztLf4", "image_url": "https://img.youtube.com/vi/YyepU5ztLf4/hqdefault.jpg", "description": "High-octane action featuring Ranveer Singh.", "price": 19.99, "stock": 100 },
    { "id": 202, "name": "Jaiye Sajana (Dhurandhar)", "category": "Action & Adventure", "youtube_id": "F2m4HPLvj-4", "image_url": "https://img.youtube.com/vi/F2m4HPLvj-4/hqdefault.jpg", "description": "Dhurandhar The Revenge - Musical High.", "price": 14.99, "stock": 100 },
    { "id": 203, "name": "Jaan Se Guzarte Hain", "category": "Action & Adventure", "youtube_id": "IAONd2d_PDU", "image_url": "https://img.youtube.com/vi/IAONd2d_PDU/hqdefault.jpg", "description": "Lyrical saga of Dhurandhar The Revenge.", "price": 9.99, "stock": 100 },
    { "id": 204, "name": "Dhurandhar (Full Album)", "category": "Action & Adventure", "youtube_id": "jo3p7O8n6is", "image_url": "https://img.youtube.com/vi/jo3p7O8n6is/hqdefault.jpg", "description": "The complete musical journey of a hero.", "price": 24.99, "stock": 100 },
    { "id": 205, "name": "Mohe Mor Banaiyo Radha", "category": "Devotional & Soulful", "youtube_id": "IzC6Cgqcup0", "image_url": "https://img.youtube.com/vi/IzC6Cgqcup0/hqdefault.jpg", "description": "Peaceful Radha Krishna Bhajan.", "price": 4.99, "stock": 100 },
    { "id": 206, "name": "Radhe Tere Charno Ki", "category": "Devotional & Soulful", "youtube_id": "lZQ5XzKrUFM", "image_url": "https://img.youtube.com/vi/lZQ5XzKrUFM/hqdefault.jpg", "description": "Soulful Radha Bhajan for inner peace.", "price": 4.99, "stock": 100 },
    { "id": 207, "name": "Samay Samjhayega (Sad)", "category": "Devotional & Soulful", "youtube_id": "6ZwwapPikyQ", "image_url": "https://img.youtube.com/vi/6ZwwapPikyQ/hqdefault.jpg", "description": "Tum Prem Ho Sad Version - Radha Krishn.", "price": 0.99, "stock": 100 },
    { "id": 208, "name": "Radha Apne Vrindavan Ko", "category": "Devotional & Soulful", "youtube_id": "zdVpB9m9GqI", "image_url": "https://img.youtube.com/vi/zdVpB9m9GqI/hqdefault.jpg", "description": "Another peaceful rendition of the Radha Bhajan.", "price": 4.99, "stock": 100 }
]

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"service": "Product Service", "status": "online"}

@app.get("/products", response_model=List[schemas.ProductResponse])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Always return User's Stable Catalog for the Puneet/Adult profile 'WOW' experience
    # Randomly shuffle the LIST of objects, but the mapping inside them is FIXED
    pool = list(MASTER_CATALOG)
    random.shuffle(pool)
    return pool[skip : skip + limit]

@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    # Match against MASTER_CATALOG first for identity sync
    product = next((p for p in MASTER_CATALOG if p["id"] == product_id), None)
    
    if not product:
        # Fallback to database
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: schemas.ProductCreate, request: Request, db: Session = Depends(get_db)):
    verify_token(request)
    product = models.Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

Instrumentator().instrument(app).expose(app)
