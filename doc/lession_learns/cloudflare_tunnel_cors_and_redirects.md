# Lesson Learned: Cloudflare Tunnel, CORS, and Redirects

## Problem Identification
When deploying a FastAPI + Vite application behind a Cloudflare Tunnel (or any reverse proxy), two major issues often occur:
1.  **Mixed Content / SSL Issues**: Hardcoded `http://localhost:8000` URLs break when the frontend is accessed via `https://your-tunnel.com`.
2.  **Redirect Origin Leak**: FastAPI routes defined without a trailing slash (e.g., `/api/login`) will 307/308 redirect to the slashed version (`/api/login/`). During this redirect, the server may provide an absolute URL in the `Location` header that points to the internal address (`http://localhost:8000`), causing the browser to try and connect to a local port that isn't accessible remotely.

## The "Trailing Slash" Rule
To prevent origin-leaking redirects, always define and call endpoints with a trailing slash for collection-level routes and actions.

### ✅ Do (Consistent)
**Backend:**
```python
@router.post("/login/")
async def login(...): ...
```
**Frontend:**
```typescript
api.post('/auth/login/', data)
```

### ❌ Don't (Causes Redirect)
**Backend:**
```python
@router.post("/login") # Missing slash
```
**Frontend:**
```typescript
api.post('/auth/login', data) # Missing slash
```

## Relative Path Strategy
Centralize API calls using relative paths and a Vite proxy.
- **Vite Config**: Proxy `/api` to `http://localhost:8000`.
- **Axios BaseURL**: Set to `/api/v1` (relative).
- **Result**: The browser only ever talks to the tunnel domain, and the proxy handles the internal routing.

## Image Handling
Avoid hardcoding full URLs for images in the database or frontend.
- **Use a utility**: `const getImageUrl = (path) => path.startsWith('/') ? path : `/${path}`;`
- **Result**: Images load via the same proxy as the API, inheriting the HTTPS tunnel session correctly.

---
*Last Updated: 2026-05-09*
