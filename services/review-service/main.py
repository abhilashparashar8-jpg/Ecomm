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

app = FastAPI(title="Review Service")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"service": "Review Service", "status": "online"}

@app.get("/reviews/product/{product_id}", response_model=List[schemas.ReviewResponse])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(models.Review.product_id == product_id).all()
    return reviews

@app.post("/reviews", response_model=schemas.ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(review_in: schemas.ReviewCreate, request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    if review_in.rating < 1 or review_in.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
    review = models.Review(user_id=user_id, **review_in.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

# Expose metrics for Prometheus
Instrumentator().instrument(app).expose(app)
