from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/db")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define the database models
class WaterQualityMeasurement(Base):
    __tablename__ = "water_quality_measurements"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    Lat = Column(Float)
    Lon = Column(Float)
    Temperature = Column(Float)
    D_O = Column(Float)  # Use D_O to avoid issues with SQL keywords
    pH = Column(Float)
    Conductivity = Column(Float)
    B_O_D = Column(Float) # Use B_O_D
    Nitrate = Column(Float)
    Fecalcaliform = Column(Float)
    Totalcaliform = Column(Float)

    prediction = relationship("WaterQualityPrediction", back_populates="measurement", uselist=False)
    recommendations = relationship("Recommendation", back_populates="measurement")

class WaterQualityPrediction(Base):
    __tablename__ = "water_quality_predictions"

    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(Integer, ForeignKey("water_quality_measurements.id"))
    is_potable = Column(Integer)
    confidence = Column(Float)
    model_version = Column(String, default="v1.0.0")
    timestamp = Column(DateTime, default=datetime.utcnow)

    measurement = relationship("WaterQualityMeasurement", back_populates="prediction")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(Integer, ForeignKey("water_quality_measurements.id"))
    parameter = Column(String)
    severity = Column(String)
    priority = Column(String)
    recommendation = Column(String)
    estimated_cost = Column(Float, nullable=True)
    implementation_timeframe = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    measurement = relationship("WaterQualityMeasurement", back_populates="recommendations")

# Add User model for authentication
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Create database tables
def create_db_tables():
    Base.metadata.create_all(bind=engine)

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# CRUD operations for WaterQualityMeasurement
class WaterQualityMeasurementCreate(Base):
    location: str
    Lat: float
    Lon: float
    Temperature: float
    D_O: float
    pH: float
    Conductivity: float
    B_O_D: float
    Nitrate: float
    Fecalcaliform: float
    Totalcaliform: float

class WaterQualityResponse(Base):
    measurement: WaterQualityMeasurement
    prediction: WaterQualityPrediction
    recommendations: list[Recommendation] = []

class WaterQualityPredictionCreate(Base):
    measurement_id: int
    is_potable: int
    confidence: float
    model_version: str

class RecommendationCreate(Base):
    measurement_id: int
    parameter: str
    severity: str
    priority: str
    recommendation: str
    estimated_cost: float | None = None
    implementation_timeframe: str | None = None

def create_water_quality_measurement(db: Session, measurement: WaterQualityMeasurementCreate):
    # Map Pydantic model to SQLAlchemy model, handling alias if necessary
    db_measurement = WaterQualityMeasurement(
        location=measurement.location,
        Lat=measurement.Lat,
        Lon=measurement.Lon,
        Temperature=measurement.Temperature,
        D_O=measurement.D_O,
        pH=measurement.pH,
        Conductivity=measurement.Conductivity,
        B_O_D=measurement.B_O_D,
        Nitrate=measurement.Nitrate,
        Fecalcaliform=measurement.Fecalcaliform,
        Totalcaliform=measurement.Totalcaliform
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def get_measurement(db: Session, measurement_id: int):
    return db.query(WaterQualityMeasurement).filter(WaterQualityMeasurement.id == measurement_id).first()

def create_prediction(db: Session, prediction: WaterQualityPredictionCreate):
    db_prediction = WaterQualityPrediction(**prediction.model_dump())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_predictions_by_measurement(db: Session, measurement_id: int):
    return db.query(WaterQualityPrediction).filter(WaterQualityPrediction.measurement_id == measurement_id).all()

def create_recommendation(db: Session, recommendation: RecommendationCreate):
    db_recommendation = Recommendation(**recommendation.model_dump())
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

def get_recommendations_by_measurement(db: Session, measurement_id: int):
    return db.query(Recommendation).filter(Recommendation.measurement_id == measurement_id).all()

# CRUD operations for User
class UserCreate(Base):
    email: str
    password: str

class UserInDB(Base):
    email: str
    hashed_password: str

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    # In a real application, you would hash the password here
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user 