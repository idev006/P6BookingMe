from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.router import api_router
from app.events.booking_handlers import register_booking_handlers
from app.events.user_handlers import register_user_handlers
from app.core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.context import set_request_id

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Set context variable for global access (Sprint 5.1 Improvement)
        set_request_id(request_id)
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Inject into response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        return response

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    register_booking_handlers()
    register_user_handlers()
    
    # Start Background Task
    import asyncio
    from app.services.booking import BookingService
    from app.services.config_service import ConfigService
    from app.core.database import AsyncSessionLocal

    async def cleanup_task():
        while True:
            try:
                async with AsyncSessionLocal() as db:
                    config_service = ConfigService(db)
                    expire_mins = await config_service.get_value("GHOST_BOOKING_EXPIRE_MINS", 30)
                    interval_mins = await config_service.get_value("GHOST_CLEANUP_INTERVAL_MINS", 10)
                    
                    service = BookingService(db)
                    count = await service.cleanup_expired_bookings(minutes=expire_mins)
                    if count > 0:
                        logger.info(f"Ghost Booking Prevention: Auto-cancelled {count} bookings")
                    
                    await asyncio.sleep(60 * interval_mins)
            except Exception as e:
                logger.error(f"Cleanup task failed: {e}")
                await asyncio.sleep(60) # Wait a bit before retry if failed

    cleanup_job = asyncio.create_task(cleanup_task())
    
    yield
    
    # --- SHUTDOWN ---
    cleanup_job.cancel()
    try:
        await cleanup_job
    except asyncio.CancelledError:
        logger.info("Background cleanup task cancelled gracefully")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global Exception Handler for consistent error responses
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    # ดึง X-Error-Code จาก headers ถ้ามี (ส่งมาจาก deps.py)
    error_code = exc.headers.get("X-Error-Code") if exc.headers else None
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": error_code,
            "path": request.url.path
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "ข้อมูลที่ส่งมาไม่ถูกต้อง (Validation Error)",
            "errors": exc.errors(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def universal_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "เกิดข้อผิดพลาดภายในระบบ (Internal Server Error)",
            "path": request.url.path
        }
    )

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount Uploads directory for static serving
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")


@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
