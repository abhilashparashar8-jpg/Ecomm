import os
import urllib
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -----------------------------
# DATABASE URL CONFIGURATION
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback local SQLite (for local development)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./local.db"

# If using Azure SQL, convert ODBC string to proper SQLAlchemy URL
if DATABASE_URL.startswith("Driver={") or DATABASE_URL.startswith("mssql://") is False:
    # Replace these with your actual Azure SQL credentials
    server = os.getenv("DB_SERVER", "ecommserveraks.database.windows.net")
    database = os.getenv("DB_NAME", "ecommdb")
    username = os.getenv("DB_USER", "ecommadmin")
    password = os.getenv("DB_PASSWORD", "admin@123@")  # special chars need encoding

    # URL encode username/password
    password_encoded = urllib.parse.quote_plus(password)

    # Build SQLAlchemy connection string for ODBC
    DATABASE_URL = (
        f"mssql+pyodbc://{username}:{password_encoded}@{server}:1433/{database}"
        f"?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
    )

# -----------------------------
# CREATE ENGINE
# -----------------------------
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# -----------------------------
# SESSION & BASE
# -----------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -----------------------------
# FASTAPI DEPENDENCY
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()