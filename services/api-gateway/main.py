import os
from fastapi import FastAPI, Request, Response, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import httpx
import jwt  # For decoding user info
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator

from database import engine, Base, SessionLocal, get_db
from models import AuditLog

# Create DB tables if they don't exist
Base.metadata.create_all(bind=engine)

# Getting service URLs and hosts from env
API_HOST = os.getenv("API_HOST", "api.puneetdevops.online")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8002")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8003")
CART_SERVICE_URL = os.getenv("CART_SERVICE_URL", "http://cart-service:8004")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8005")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8006")
REVIEW_SERVICE_URL = os.getenv("REVIEW_SERVICE_URL", "http://review-service:8007")
WISHLIST_SERVICE_URL = os.getenv("WISHLIST_SERVICE_URL", "http://wishlist-service:8008")
VAULT_SERVICE_URL = os.getenv("VAULT_SERVICE_URL", "http://vault-service:8009")

app = FastAPI(title="API Gateway")

# Force HTTPS for all redirects and proxies when behind a proxy
@app.middleware("http")
async def force_https_middleware(request: Request, call_next):
    # Trusting X-Forwarded-Proto for HTTPS
    if request.headers.get("x-forwarded-proto") == "https" or request.headers.get("x-forwarded-scheme") == "https":
        request.scope["scheme"] = "https"
    
    response = await call_next(request)
    
    # Ensure redirects produced by FastAPI also use HTTPS
    if response.status_code in (301, 302, 307, 308) and "location" in response.headers:
        loc = response.headers["location"]
        if loc.startswith(f"http://{API_HOST}"):
            response.headers["location"] = loc.replace("http://", "https://", 1)
            
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jpshop.puneetdevops.online",
        "http://jpshop.puneetdevops.online",
        "https://api.puneetdevops.online",
        "http://localhost:5173",  # Local Vite dev server
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SERVICES = {
    "auth": AUTH_SERVICE_URL,
    "user": USER_SERVICE_URL,
    "product": PRODUCT_SERVICE_URL,
    "cart": CART_SERVICE_URL,
    "order": ORDER_SERVICE_URL,
    "payment": PAYMENT_SERVICE_URL,
    "review": REVIEW_SERVICE_URL,
    "wishlist": WISHLIST_SERVICE_URL,
    "vault": VAULT_SERVICE_URL,
}

def save_audit_log(ip_address: str, method: str, service_name: str, path: str, status_code: int, user_email: str = None):
    """Background task to safely save request logs without blocking the proxy"""
    db = SessionLocal()
    try:
        log_entry = AuditLog(
            ip_address=ip_address,
            method=method,
            user_email=user_email,
            service_name=service_name,
            path=path,
            status_code=status_code
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"Failed to save audit log: {e}")
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "gateway is live"}

@app.get("/")
async def root():
    return {
        "message": "Welcome to StreamShop API Gateway",
        "status": "online",
        "services": list(SERVICES.keys())
    }

@app.get("/admin/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    # Returns last 100 logs for admin view
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return logs

# Example simple proxy logic
@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_request(service_name: str, path: str, request: Request, background_tasks: BackgroundTasks):
    if service_name not in SERVICES:
        return Response(status_code=404, content="Service not found")
        
    url = f"{SERVICES[service_name]}/{path}"
    if not path:
        url = SERVICES[service_name]
    
    # Exclude specific headers that can cause issues when proxying
    excluded_headers = ["host", "content-length"]
    headers = {k: v for k, v in request.headers.items() if k.lower() not in excluded_headers}
    
    body = await request.body()
    client_ip = request.client.host if request.client else "unknown"
    
    # Extract user from JWT if available
    user_email = "Anonymous"
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            # We only decode, not verify here (verification happens in services)
            payload = jwt.decode(token, options={"verify_signature": False})
            user_email = payload.get("sub", "Unknown")
        except:
            pass

    # Forward the user identity to microservices
    headers["X-User-Email"] = user_email

    async with httpx.AsyncClient() as client:
        try:
            proxy_response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            # Queue the background task to log the audit record
            background_tasks.add_task(
                save_audit_log,
                ip_address=client_ip,
                method=request.method,
                user_email=user_email,
                service_name=service_name,
                path=path,
                status_code=proxy_response.status_code
            )
            
            return Response(
                content=proxy_response.content,
                status_code=proxy_response.status_code,
                headers={k: v for k, v in proxy_response.headers.items() if k.lower() not in excluded_headers}
            )
        except httpx.RequestError as e:
            # Log the failure
            background_tasks.add_task(
                save_audit_log,
                ip_address=client_ip,
                method=request.method,
                user_email=user_email,
                service_name=service_name,
                path=path,
                status_code=503
            )
            return Response(status_code=503, content=f"Service unavailable: {str(e)}")

# Expose metrics for Prometheus
Instrumentator().instrument(app).expose(app)
