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

app = FastAPI(title="Cart Service")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"service": "Cart Service", "status": "online"}

@app.get("/cart", response_model=List[schemas.CartItemResponse])
def get_cart(request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    items = db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()
    return items

@app.post("/cart", response_model=schemas.CartItemResponse)
def add_to_cart(item_in: schemas.CartItemCreate, request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    # Check if item exists in cart
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id, 
        models.CartItem.product_id == item_in.product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item_in.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
        
    new_item = models.CartItem(user_id=user_id, **item_in.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.delete("/cart/{item_id}")
def remove_from_cart(item_id: int, request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.user_id == user_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    db.delete(item)
    db.commit()
    return {"detail": "Item removed"}

@app.delete("/cart")
def clear_cart(request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()
    return {"detail": "Cart cleared"}

# Expose metrics for Prometheus
Instrumentator().instrument(app).expose(app)
