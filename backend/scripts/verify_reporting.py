import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from app.core.database import AsyncSessionLocal
from app.services.reporting import ReportingService
from app.models.booking import BookingStatus

async def verify_reporting():
    async with AsyncSessionLocal() as db:
        service = ReportingService(db)
        
        print("--- Testing Summary Stats ---")
        stats = await service.get_summary_stats()
        print(f"Stats: {stats}")
        
        print("\n--- Testing Frequent Rooms ---")
        rooms = await service.get_frequent_rooms()
        print(f"Frequent Rooms: {rooms}")
        
        print("\n--- Testing Usage Trends ---")
        trends = await service.get_usage_trends()
        print(f"Trends (last 7 days): {trends}")
        
        print("\n--- Testing CSV Export ---")
        csv_data = await service.export_bookings_csv()
        print(f"CSV Header: {csv_data.splitlines()[0] if csv_data else 'Empty'}")
        print(f"CSV Rows: {len(csv_data.splitlines()) - 1}")

if __name__ == "__main__":
    asyncio.run(verify_reporting())
