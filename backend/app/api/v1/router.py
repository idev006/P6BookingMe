from fastapi import APIRouter

api_router = APIRouter()

# Routers will be added here as features are built
from app.api.v1.endpoints import auth, users, notifications, rooms, bookings, approvals, admin_config, admin_audit, admin_reporting, calendar, admin_users, admin_bookings
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(admin_config.router, prefix="/admin/configs", tags=["admin-config"])
api_router.include_router(admin_audit.router, prefix="/admin/audit-logs", tags=["admin-audit"])
api_router.include_router(admin_reporting.router, prefix="/admin/reporting", tags=["admin-reporting"])
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin-users"])
api_router.include_router(admin_bookings.router, prefix="/admin/bookings", tags=["admin-bookings"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
