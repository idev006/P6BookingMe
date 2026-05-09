from pydantic import BaseModel, ConfigDict
from typing import Any, Optional
from datetime import datetime

class ConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    key: str
    value: Any
    description: Optional[str] = None
    updated_at: datetime

class ConfigUpdate(BaseModel):
    value: Any
