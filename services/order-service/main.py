from sqlalchemy import text
models.Base.metadata.create_all(bind=engine)

# Auto-migration for missing columns
try:
    with engine.begin() as conn:
        # Check standard columns if any were added recently
        pass 
except Exception as e:
    print(f"Migration failed for order-service: {e}")

app = FastAPI(title="Order Service")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"service": "Order Service", "status": "online"}

@app.get("/orders", response_model=List[schemas.OrderResponse])
def get_orders(request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
    # Populate items
    for order in orders:
        order.items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
    return orders

@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
    return order

@app.post("/orders", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: schemas.OrderCreate, request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    user_id = user_payload.get("id")
    
    new_order = models.Order(user_id=user_id, total_amount=order_in.total_amount)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    for item in order_in.items:
        new_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(new_item)
    
    db.commit()
    
    new_order.items = db.query(models.OrderItem).filter(models.OrderItem.order_id == new_order.id).all()
    return new_order

@app.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status_in: str, request: Request, db: Session = Depends(get_db)):
    user_payload = verify_token(request)
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.status = status_in
    db.commit()
    return {"detail": "Order status updated", "new_status": order.status}

@app.get("/admin/orders", response_model=List[schemas.OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    for order in orders:
        order.items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
    return orders


# Expose metrics for Prometheus
Instrumentator().instrument(app).expose(app)
