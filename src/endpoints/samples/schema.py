from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class SampleCreate(BaseModel):
  batch_id: int
  code: str
  created_by: int
  collected_at: datetime
  tier_label: Optional[str] = None

class RaspSampleCreate(BaseModel):
  photo_id: str
  tier: str          # "bom" | "ruim" | "pessimo"
  gcp_url: str
  collected_at: datetime
  doctor_name: Optional[str] = None

class RecentSampleResponse(BaseModel):
  code: str
  tier_label: Optional[str] = None
  tier: Optional[int] = None
  image_url: Optional[str] = None
  collected_at: datetime

class SampleResponse(BaseModel):
  id: int
  batch_id: int
  code: str
  created_by: int
  tier: Optional[int] = None
  tier_label: Optional[str] = None
  status: str
  collected_at: datetime
  analyzed_at: Optional[datetime] = None
  created_at: datetime

  model_config = {"from_attributes": True}

class SampleWithImageResponse(BaseModel):
  id: int
  batch_id: int
  code: str
  status: str
  tier: Optional[int] = None
  tier_label: Optional[str] = None
  created_by: int
  collected_at: datetime
  analyzed_at: Optional[datetime] = None
  created_at: datetime
  image_url: Optional[str] = None
  confidence_score: Optional[float] = None
  prediction: Optional[str] = None
  model_version: Optional[str] = None

class GalleryItemResponse(BaseModel):
  id: int
  code: str
  tier: Optional[int] = None
  tier_label: Optional[str] = None
  status: str
  confidence_score: Optional[float] = None
  prediction: Optional[str] = None
  image_url: str
  processed_at: datetime

class RaspStatusResponse(BaseModel):
  is_online: bool
  last_seen: Optional[datetime] = None
  minutes_ago: Optional[int] = None

class PendingCountResponse(BaseModel):
  processing: int
  pending: int
  total: int

class TimeSeriesItem(BaseModel):
  date: str
  total: int
  bom: int
  ruim: int
  pessimo: int

class RaspLogItem(BaseModel):
  code: str
  tier: Optional[int] = None
  tier_label: Optional[str] = None
  doctor: Optional[str] = None
  image_url: Optional[str] = None
  collected_at: datetime
  created_at: datetime

class DashboardStatsResponse(BaseModel):
  processed_samples: int
  confidence_score: float
  anomalies_detected: int
  avg_processing_time: float
  daily_reads: int
  daily_rejections: int
  tier_bom: int = 0
  tier_ruim: int = 0
  tier_pessimo: int = 0
  yesterday_reads: int = 0
  current_batch: Optional[str] = None
  current_shift: Optional[str] = None

class DashboardSampleItem(BaseModel):
  id: str
  type: str
  typeClass: str
  patient: str
  prediction: str
  doctor: Optional[str] = None
  confidence: int
  status: str
  statusClass: str

class DoctorStatItem(BaseModel):
  doctor: str
  count: int

class DashboardResponse(BaseModel):
  stats: DashboardStatsResponse
  recent_samples: List[DashboardSampleItem]
