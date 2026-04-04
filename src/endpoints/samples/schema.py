from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class SampleCreate(BaseModel):
  code: str
  created_by: int
  collected_at: datetime

class SampleResponse(BaseModel):
  id: int
  code: str
  created_by: int
  analyzed_by: Optional[int] = None
  tier: Optional[int] = None
  tier_label: Optional[str] = None
  status: str
  collected_at: datetime
  analyzed_at: Optional[datetime] = None
  created_at: datetime

  model_config = {"from_attributes": True}
