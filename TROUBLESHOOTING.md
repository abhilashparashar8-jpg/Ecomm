# Microservices Troubleshooting & Fix Log

This document tracks the persistent issues encountered during deployment and the specific fixes applied to resolve them.

## 1. Authentication Service - HTTP 500 (Internal Server Error)
**Status:** Under Investigation / Partially Fixed

### Symptom:
User registration or login returns a `500 Internal Server Error`.

### Identified Causes & Fixes:
1. **Azure SQL SSL Handshake Failure**:
   - **Problem**: Kubernetes pods could not verify the Azure SQL SSL certificate.
   - **Fix**: Added `TrustServerCertificate=yes` to the `DATABASE_URL` in `k8s/deployments-fixed.yaml` and standardized `database.py` fallbacks.
2. **Silent Background Crashes**:
   - **Problem**: Registration logic was failing silently, returning a generic 500.
   - **Fix**: Added `try...except` block with `traceback.format_exc()` in `auth-service/main.py`. The API now returns the actual error message in the response body.

---

## 2. API Gateway - CORS Blockage
**Status:** Fix Applied in `api:v4`

### Symptom:
`Access-Control-Allow-Origin` header is missing in browser console; preflight requests fail.

### Identified Causes & Fixes:
1. **Credential/Wildcard Conflict**:
   - **Problem**: `allow_origins=["*"]` used with `allow_credentials=True` is prohibited by browsers.
   - **Fix**: Explicitly listed the frontend domain (`https://jpshop.puneetdevops.online`) in `api-gateway/main.py`.
2. **Preflight Interception**:
   - **Problem**: The catch-all proxy route `/{service_name}/{path}` was handling `OPTIONS` requests, preventing the CORS middleware from injecting headers.
   - **Fix**: Removed `OPTIONS` from the supported methods in `route_request`. Now, the `CORSMiddleware` handles all preflight requests automatically.

---

## 3. Product Service - HTTP 503 (Service Unavailable)
**Status:** Pending Deployment

### Symptom:
Gateway fails to proxy requests to `http://product-service:8003/products`.

### Identified Causes & Fixes:
1. **Service Connectivity**:
   - **Problem**: Gateway times out or fails to resolve the service name.
   - **Fix**: Ensure the `product-service` deployment is using the updated `DATABASE_URL` with `TrustServerCertificate=yes`. If the service crashes on start due to DB failure, the gateway returns 503.

---

## 4. Frontend - 404 Assets
**Status:** Fixed

### Symptom:
Background images on the login page failed to load.

### Fix:
- Generated a local cinematic background image.
- Placed it in `frontend/public/background.png`.
- Updated `Login.jsx` to use the relative path `/background.png`.

---

## 5. Slow Docker Builds
**Status:** Optimized Dockerfiles, Action Required from User

### Symptom:
Docker builds take an extremely long time (e.g., 500s+).

### Identified Causes:
1. **CPU Emulation**: Building `linux/amd64` images on Apple Silicon (ARM) requires QEMU emulation, which significantly slows down package installation and compilation.
2. **Disabling Cache**: Using the `--no-cache` flag forces Docker to re-download and re-compile everything (like ODBC drivers and `pyodbc`) every time, even if only a small line of code changed.

### Fixes & Recommendations:
- **Enable Caching**: **DO NOT** use `--no-cache` unless absolutely necessary. Docker is smart enough to only rebuild layers that have changed.
- **Dockerfile Optimization**: I have optimized the `Dockerfile` for `auth-service` and `api-gateway` to consolidate heavy `apt-get` operations into fewer layers, which helps the cache work more effectively.
- **Recommended Build Command**:
  ```bash
  docker buildx build --platform linux/amd64 -t <tag> --push .
  ```
  (Removed `--no-cache`)

---

## Debugging Commands

### Check Gateway Logs (Real-time)
```bash
kubectl logs -f deployment/api-gateway
```

### Check Auth Service Logs
```bash
kubectl logs -f deployment/auth-service
```
