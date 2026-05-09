from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.system_config import SystemConfig
from typing import List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ConfigRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[SystemConfig]:
        stmt = select(SystemConfig).order_by(SystemConfig.key)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_key(self, key: str) -> Optional[SystemConfig]:
        stmt = select(SystemConfig).where(SystemConfig.key == key)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_value(self, key: str, value_str: str, user_id: int) -> Optional[SystemConfig]:
        config = await self.get_by_key(key)
        if config:
            config.value = value_str
            config.updated_by = user_id
            await self.db.commit()
            await self.db.refresh(config)
            return config
        return None

# Simple In-Memory Cache for Settings
_CONFIG_CACHE = {}

class ConfigService:
    def __init__(self, db: AsyncSession):
        self.repo = ConfigRepository(db)

    async def get_value(self, key: str, default: Any = None) -> Any:
        # 1. Check Cache
        if key in _CONFIG_CACHE:
            return _CONFIG_CACHE[key]
        
        # 2. Check DB
        config = await self.repo.get_by_key(key)
        if config:
            val = config.value
            # Basic type conversion heuristic (since we lost config_type in the new schema)
            # If we want to be more sophisticated, we'd need to re-add config_type to the model
            # For now, let's just return as is (string) or try basic conversion
            try:
                if val.lower() == 'true': return True
                if val.lower() == 'false': return False
                if val.isdigit(): return int(val)
            except:
                pass
                
            _CONFIG_CACHE[key] = val
            return val
        
        return default

    async def set_value(self, key: str, value: Any, user_id: int):
        config = await self.repo.get_by_key(key)
        if not config:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="ไม่พบการตั้งค่าที่ระบุ")

        # Convert everything to string for storage
        value_str = str(value)

        # 1. Update DB
        updated = await self.repo.update_value(key, value_str, user_id)
        
        # 2. Update Cache
        if updated:
            _CONFIG_CACHE[key] = value
        return updated

    async def list_all_configs(self) -> List[SystemConfig]:
        return await self.repo.get_all()

    async def refresh_cache(self):
        configs = await self.repo.get_all()
        for c in configs:
            _CONFIG_CACHE[c.key] = c.value
        logger.info("System Config Cache Refreshed")
