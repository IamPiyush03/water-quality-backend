from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.config import Base

class WaterQualityMeasurement(Base):
    __tablename__ = "water_quality_measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    temperature = Column(Float)
    dissolved_oxygen = Column(Float)
    ph = Column(Float)
    conductivity = Column(Float)
    bod = Column(Float)
    nitrate = Column(Float)
    fecal_coliform = Column(Float)
    total_coliform = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    predictions = relationship("WaterQualityPrediction", back_populates="measurement")
    recommendations = relationship("Recommendation", back_populates="measurement")
    user = relationship("User", back_populates="measurements")

class WaterQualityPrediction(Base):
    __tablename__ = "water_quality_predictions"

    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(Integer, ForeignKey("water_quality_measurements.id"))
    is_potable = Column(Boolean)
    confidence = Column(Float)
    wqi_value = Column(Float)
    quality_category = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    measurement = relationship("WaterQualityMeasurement", back_populates="predictions")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(Integer, ForeignKey("water_quality_measurements.id"))
    parameter = Column(String)
    severity = Column(String)
    priority = Column(String)
    description = Column(String)
    estimated_cost = Column(Float, nullable=True)
    implementation_timeframe = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    measurement = relationship("WaterQualityMeasurement", back_populates="recommendations")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    measurements = relationship("WaterQualityMeasurement", back_populates="user") 