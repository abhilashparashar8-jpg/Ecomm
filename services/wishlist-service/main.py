import os
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor for Application Insights
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if connection_string:
    configure_azure_monitor(connection_string=connection_string)

from prometheus_fastapi_instrumentator import Instrumentator

from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db
from security import verify_token

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wishlist Service")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"service": "Wishlist Service", "status": "online"}

@app.get("/wishlist", response_model=List[schemas.WishlistItemResponse])
def get_wishlist(request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    items = db.query(models.WishlistItem).filter(models.WishlistItem.user_id == user_id).all()
    return items

@app.post("/wishlist", response_model=schemas.WishlistItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(item_in: schemas.WishlistItemCreate, request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    existing = db.query(models.WishlistItem).filter(
        models.WishlistItem.user_id == user_id,
        models.WishlistItem.product_id == item_in.product_id
    ).first()
    
    if existing:
        return existing
        
    item = models.WishlistItem(user_id=user_id, **item_in.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.delete("/wishlist/{product_id}")
def remove_from_wishlist(product_id: int, request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    item = db.query(models.WishlistItem).filter(
        models.WishlistItem.user_id == user_id,
        models.WishlistItem.product_id == product_id
    ).first()
    
    if item:
        db.delete(item)
        db.commit()
    return {"detail": "Removed from wishlist"}

# Expose metrics for Prometheus
Instrumentator().instrument(app).expose(app)
