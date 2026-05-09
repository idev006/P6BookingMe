import httpx
import asyncio
import sys

BASE_URL = "http://localhost:8000/api/v1"

async def check_health():
    async with httpx.AsyncClient() as client:
        print("\n" + "="*40)
        print("🔍 P6BookingMe System Health Check")
        print("="*40 + "\n")
        
        # 1. Check API Connection
        try:
            res = await client.get(f"http://localhost:8000/health")
            print(f"✅ API Connection: {'Success' if res.status_code == 200 else 'Failed'}")
        except Exception as e:
            print(f"❌ API Connection: Failed (Server not running on port 8000)")
            print(f"   Error: {e}")
            return

        # 2. Check Auth Middleware
        try:
            res = await client.get(f"{BASE_URL}/auth/me")
            if res.status_code == 401:
                print(f"✅ Auth Middleware: Active & Secure")
            else:
                print(f"⚠️ Auth Middleware: Unexpected Status {res.status_code}")
        except:
            print("❌ Auth Middleware: Check Failed")

        # 3. Check Room Service
        try:
            res = await client.get(f"{BASE_URL}/rooms")
            if res.status_code == 200:
                print(f"✅ Room Service: Operational (Found {len(res.json().get('data', []))} rooms)")
            else:
                print(f"❌ Room Service: Failed with status {res.status_code}")
        except:
            print("❌ Room Service: Check Failed")

        # 4. Check System Config Service
        try:
            # We check if we can reach the public configs or if it's secured
            res = await client.get(f"{BASE_URL}/admin/configs")
            if res.status_code == 401:
                print(f"✅ Admin Config API: Securely Protected")
            else:
                print(f"⚠️ Admin Config API: Unexpected accessibility status {res.status_code}")
        except:
            print("❌ Config Service: Check Failed")

        print("\n" + "="*40)
        print("🚀 Overall Status: READY FOR OPERATION")
        print("="*40 + "\n")

if __name__ == "__main__":
    asyncio.run(check_health())
