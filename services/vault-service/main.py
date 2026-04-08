import os
from azure.monitor.opentelemetry import configure_azure_monitor

# Configure Azure Monitor for Application Insights
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if connection_string:
    configure_azure_monitor(connection_string=connection_string)

import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator

import models, database
from database import engine, get_db

# Storage path (This should be the PVC mount point)
STORAGE_PATH = os.getenv("STORAGE_PATH", "/mnt/personal-vault")

# Ensure the storage directory exists
if not os.path.exists(STORAGE_PATH):
    os.makedirs(STORAGE_PATH, exist_ok=True)

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vault Service")

@app.get("/health")
def health_check():
    return {"status": "vault is ready"}

@app.get("/")
async def root():
    return {"service": "Vault Service", "storage": STORAGE_PATH}

@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # In a real app, extract user_email from JWT. For now, using a header or default.
    user_email = request.headers.get("X-User-Email", "puneet@example.com")
    
    # Create user-specific directory in the vault
    user_dir = os.path.join(STORAGE_PATH, user_email)
    os.makedirs(user_dir, exist_ok=True)
    
    file_location = os.path.join(user_dir, file.filename)
    
    # Save file to PVC
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Determine file type
    content_type = file.content_type
    file_type = "doc"
    if content_type.startswith("video"):
        file_type = "video"
    elif content_type.startswith("image"):
        file_type = "image"
        
    # Get file size in MB
    file_size = os.path.getsize(file_location) / (1024 * 1024)
    
    # Save metadata to DB
    db_file = models.VaultFile(
        user_email=user_email,
        filename=file.filename,
        file_type=file_type,
        file_size=round(file_size, 2),
        storage_path=file_location
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return {"message": "Upload successful", "file_id": db_file.id}

@app.get("/files", response_model=List[dict])
def list_files(request: Request, db: Session = Depends(get_db)):
    user_email = request.headers.get("X-User-Email", "puneet@example.com")
    files = db.query(models.VaultFile).filter(models.VaultFile.user_email == user_email).all()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "file_type": f.file_type,
            "file_size": f.file_size,
            "upload_time": f.upload_time
        } for f in files
    ]

@app.get("/view/{file_id}")
def view_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(models.VaultFile).filter(models.VaultFile.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if file exists on disk
    if not os.path.exists(db_file.storage_path):
        raise HTTPException(status_code=404, detail="File missing on storage")
        
    return FileResponse(db_file.storage_path)

# Expose metrics for Prometheus
Instrumentator().instrument(app).expose(app)
