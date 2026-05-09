from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.services.reporting import ReportingService
from app.schemas.common import StandardResponse
from datetime import date
import io

router = APIRouter()

@router.get("/summary", response_model=StandardResponse)
async def get_reporting_summary(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = ReportingService(db)
    stats = await service.get_summary_stats()
    return StandardResponse(data=stats)

@router.get("/frequent-rooms", response_model=StandardResponse)
async def get_frequent_rooms(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = ReportingService(db)
    rooms = await service.get_frequent_rooms(limit)
    return StandardResponse(data=rooms)

@router.get("/usage-trends", response_model=StandardResponse)
async def get_usage_trends(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = ReportingService(db)
    trends = await service.get_usage_trends(days)
    return StandardResponse(data=trends)

@router.get("/export/bookings")
async def export_bookings(
    start_date: date = Query(None),
    end_date: date = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = ReportingService(db)
    csv_data = await service.export_bookings_csv(start_date, end_date)
    
    # Create streaming response
    buf = io.BytesIO(csv_data.encode("utf-8-sig")) # Use utf-8-sig for Excel compatibility (BOM)
    
    filename = f"bookings_export_{date.today().isoformat()}.csv"
    
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
