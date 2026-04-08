import os
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor for Application Insights
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if connection_string:
    configure_azure_monitor(connection_string=connection_string)

from fastapi import FastAPI, HTTPException, Depends, Request, status
from sqlalchemy import create_engine, Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship
from prometheus_fastapi_instrumentator import Instrumentator
from typing import List

# ---------------------------
# Database setup
# ---------------------------
DATABASE_URL = "sqlite:///./orderservice.db"  # self-contained local DB

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Models
# ---------------------------
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    total_amount = Column(Float)
    status = Column(String, default="pending")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer)
    quantity = Column(Integer)
    price = Column(Float)
    order = relationship("Order", back_populates="items")

# ---------------------------
# Schemas
# ---------------------------
from pydantic import BaseModel

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    total_amount: float
    items: List[OrderItemCreate]

class OrderItemResponse(OrderItemCreate):
    id: int
    class Config:
        orm_mode = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    items: List[OrderItemResponse]
    class Config:
        orm_mode = True

# ---------------------------
# Auto-create tables
# ---------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------
# FastAPI App
# ---------------------------
app = FastAPI(title="Order Service")

# Simple simulation: assume all requests come from user_id=1
def get_user_id():
    return 1

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"service": "Order Service", "status": "online"}

# ---------------------------
# CRUD endpoints
# ---------------------------
@app.get("/orders", response_model=List[OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    user_id = get_user_id()
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    user_id = get_user_id()
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    user_id = get_user_id()
    new_order = Order(user_id=user_id, total_amount=order_in.total_amount)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    for item in order_in.items:
        new_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(new_item)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status_in: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status_in
    db.commit()
    return {"detail": "Order status updated", "new_status": order.status}

@app.get("/admin/orders", response_model=List[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return orders

# ---------------------------
# Prometheus metrics
# ---------------------------
Instrumentator().instrument(app).expose(app)