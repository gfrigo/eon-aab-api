from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class SampleCreate(BaseModel):
  code: str
  created_by: int
  collected_at: datetime
  tier_label: Optional[str] = None

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

class SampleWithFileResponse(BaseModel):
  id: int
  code: str
  status: str
  tier: Optional[int] = None
  tier_label: Optional[str] = None
  created_by: int
  analyzed_by: Optional[int] = None
  collected_at: datetime
  analyzed_at: Optional[datetime] = None
  created_at: datetime
  file_url: Optional[str] = None       # URL servida pelo /uploads/
  file_name: Optional[str] = None

class DashboardStatsResponse(BaseModel):
  processed_samples: int
  confidence_score: float
  anomalies_detected: int
  avg_processing_time: float
  daily_reads: int
  daily_rejections: int

class DashboardSampleItem(BaseModel):
  id: str
  type: str
  typeClass: str
  patient: str
  prediction: str
  confidence: int
  status: str
  statusClass: str

class DashboardResponse(BaseModel):
  stats: DashboardStatsResponse
  recent_samples: List[DashboardSampleItem]
