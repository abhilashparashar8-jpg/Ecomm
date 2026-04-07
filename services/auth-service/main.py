from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import models, schemas, auth, traceback
from database import engine, get_db
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create DB tables
from sqlalchemy import text
models.Base.metadata.create_all(bind=engine)

# Auto-migration for missing columns
try:
    with engine.begin() as conn:
        # Check if full_name exists in auth_users
        result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'auth_users' AND COLUMN_NAME = 'full_name'"))
        if not result.fetchone():
            logger.info("Adding missing column 'full_name' to 'auth_users' table")
            conn.execute(text("ALTER TABLE auth_users ADD full_name NVARCHAR(255) NULL"))
except Exception as e:
    logger.error(f"Migration failed: {e}")

app = FastAPI(title="Auth Service")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"service": "Auth Service", "status": "online"}

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = auth.get_password_hash(user.password)
        new_user = models.User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "id": user.id, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/admin/users", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


# Expose metrics for Prometheus
Instrumentator().instrument(app).expose(app)
