from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_water_quality_measurement(
    db: Session,
    user_id: int,
    latitude: float,
    longitude: float,
    temperature: float,
    dissolved_oxygen: float,
    ph: float,
    conductivity: float,
    bod: float,
    nitrate: float,
    fecal_coliform: float,
    total_coliform: float,
) -> models.WaterQualityMeasurement:
    db_measurement = models.WaterQualityMeasurement(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        temperature=temperature,
        dissolved_oxygen=dissolved_oxygen,
        ph=ph,
        conductivity=conductivity,
        bod=bod,
        nitrate=nitrate,
        fecal_coliform=fecal_coliform,
        total_coliform=total_coliform,
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def create_prediction(
    db: Session,
    measurement_id: int,
    is_potable: bool,
    confidence: float,
    wqi_value: float,
    quality_category: str,
) -> models.WaterQualityPrediction:
    db_prediction = models.WaterQualityPrediction(
        measurement_id=measurement_id,
        is_potable=is_potable,
        confidence=confidence,
        wqi_value=wqi_value,
        quality_category=quality_category,
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def create_recommendation(
    db: Session,
    measurement_id: int,
    parameter: str,
    severity: str,
    priority: str,
    description: str,
    estimated_cost: Optional[float] = None,
    implementation_timeframe: Optional[str] = None,
) -> models.Recommendation:
    db_recommendation = models.Recommendation(
        measurement_id=measurement_id,
        parameter=parameter,
        severity=severity,
        priority=priority,
        description=description,
        estimated_cost=estimated_cost,
        implementation_timeframe=implementation_timeframe,
    )
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

def get_measurement(db: Session, measurement_id: int) -> Optional[models.WaterQualityMeasurement]:
    return db.query(models.WaterQualityMeasurement).filter(models.WaterQualityMeasurement.id == measurement_id).first()

def get_measurements(
    db: Session,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.WaterQualityMeasurement]:
    query = db.query(models.WaterQualityMeasurement).filter(models.WaterQualityMeasurement.user_id == user_id)
    
    if start_date:
        query = query.filter(models.WaterQualityMeasurement.timestamp >= start_date)
    if end_date:
        query = query.filter(models.WaterQualityMeasurement.timestamp <= end_date)
    
    return query.order_by(models.WaterQualityMeasurement.timestamp.desc()).offset(skip).limit(limit).all()

def get_predictions_by_measurement(
    db: Session,
    measurement_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[models.WaterQualityPrediction]:
    return (
        db.query(models.WaterQualityPrediction)
        .filter(models.WaterQualityPrediction.measurement_id == measurement_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_recommendations_by_measurement(
    db: Session,
    measurement_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Recommendation]:
    return (
        db.query(models.Recommendation)
        .filter(models.Recommendation.measurement_id == measurement_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_recent_measurements(
    db: Session,
    hours: int = 24,
    limit: int = 100,
) -> List[models.WaterQualityMeasurement]:
    start_date = datetime.utcnow() - timedelta(hours=hours)
    return get_measurements(db, start_date=start_date, limit=limit)

def update_recommendation(
    db: Session,
    recommendation_id: int,
    estimated_cost: Optional[float] = None,
    implementation_timeframe: Optional[str] = None,
) -> Optional[models.Recommendation]:
    db_recommendation = db.query(models.Recommendation).filter(models.Recommendation.id == recommendation_id).first()
    if db_recommendation:
        if estimated_cost is not None:
            db_recommendation.estimated_cost = estimated_cost
        if implementation_timeframe is not None:
            db_recommendation.implementation_timeframe = implementation_timeframe
        db.commit()
        db.refresh(db_recommendation)
    return db_recommendation

# User CRUD operations
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, username: str, email: str, hashed_password: str):
    db_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user 