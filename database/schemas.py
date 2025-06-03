from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WaterQualityMeasurementBase(BaseModel):
    location: str
    latitude: float
    longitude: float
    temperature: float
    dissolved_oxygen: float
    ph: float
    conductivity: float
    bod: float
    nitrate: float
    fecal_coliform: float
    total_coliform: float

class WaterQualityMeasurementCreate(WaterQualityMeasurementBase):
    pass

class WaterQualityMeasurement(WaterQualityMeasurementBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class WaterQualityPredictionBase(BaseModel):
    is_potable: bool
    confidence: float
    wqi_value: float
    quality_category: str

class WaterQualityPredictionCreate(WaterQualityPredictionBase):
    measurement_id: int

class WaterQualityPrediction(WaterQualityPredictionBase):
    id: int
    measurement_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class RecommendationBase(BaseModel):
    parameter: str
    severity: str
    priority: str
    description: str
    estimated_cost: Optional[float] = None
    implementation_timeframe: Optional[str] = None

class RecommendationCreate(RecommendationBase):
    measurement_id: int

class Recommendation(RecommendationBase):
    id: int
    measurement_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class WaterQualityResponse(BaseModel):
    measurement: WaterQualityMeasurement
    prediction: WaterQualityPrediction
    recommendations: List[Recommendation] 