from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from database.config import get_db, SessionLocal
from database import crud, models
from sqlalchemy.orm import Session
import numpy as np
import joblib
import pandas as pd
from models.predict import WaterQualityPredictor
from recommender.rules import WaterQualityRecommender
from utils.visualization import WaterQualityVisualizer
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from utils.pdf_generator import generate_water_quality_report

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Authentication Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True

# Authentication Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class WaterQualityData(BaseModel):
    temperature: float
    dissolved_oxygen: float
    ph: float
    conductivity: float
    bod: float
    nitrate: float
    fecal_coliform: float
    total_coliform: float
    Lat: Optional[float] = None
    Lon: Optional[float] = None

class WaterQualityPrediction(BaseModel):
    is_potable: bool
    confidence: float
    wqi_value: float
    quality_category: str
    parameters: Dict[str, float]
    recommendations: Dict[str, List[Dict]]

class DashboardData(BaseModel):
    current_wqi: float
    quality_category: str
    parameter_summary: Dict[str, Dict[str, float]]
    recent_measurements: List[Dict]

app = FastAPI(
    title="Water Quality Analysis API",
    description="API for analyzing water quality and providing recommendations",
    version="1.0.0"
)

# Enable CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Frontend URL from environment variable
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize components
predictor = WaterQualityPredictor()
recommender = WaterQualityRecommender()

# Initialize visualizer with a database session
@app.on_event("startup")
async def startup_event():
    # Create database tables if they don't exist
    from database.config import Base, engine
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        app.state.visualizer = WaterQualityVisualizer(session=db)
    finally:
        db.close()

# Load the trained model
try:
    model = joblib.load('models/water_quality_model.joblib')
    predictor.train("data/aquaattributes.xlsx")
    print("Model loaded successfully")
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    print("Model will be trained during first request")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/register", response_model=User)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = crud.create_user(
        db,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    return db_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/api/predict")
async def predict_water_quality(
    data: WaterQualityData, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Validate input data
        if not all([
            isinstance(data.temperature, (int, float)) and 0 <= data.temperature <= 40,
            isinstance(data.dissolved_oxygen, (int, float)) and 0 <= data.dissolved_oxygen <= 14,
            isinstance(data.ph, (int, float)) and 0 <= data.ph <= 14,
            isinstance(data.conductivity, (int, float)) and 0 <= data.conductivity <= 2000,
            isinstance(data.bod, (int, float)) and 0 <= data.bod <= 30,
            isinstance(data.nitrate, (int, float)) and 0 <= data.nitrate <= 50,
            isinstance(data.fecal_coliform, (int, float)) and 0 <= data.fecal_coliform <= 500,
            isinstance(data.total_coliform, (int, float)) and 0 <= data.total_coliform <= 1000,
        ]):
            raise HTTPException(
                status_code=422,
                detail="Invalid parameter values. Please check the input ranges."
            )

        # Create measurement record with user_id
        measurement = crud.create_water_quality_measurement(
            db,
            user_id=current_user.id,
            latitude=data.Lat if data.Lat is not None else 0,
            longitude=data.Lon if data.Lon is not None else 0,
            temperature=data.temperature,
            dissolved_oxygen=data.dissolved_oxygen,
            ph=data.ph,
            conductivity=data.conductivity,
            bod=data.bod,
            nitrate=data.nitrate,
            fecal_coliform=data.fecal_coliform,
            total_coliform=data.total_coliform
        )

        # Calculate WQI (simplified version)
        wqi = calculate_wqi(data)
        quality_category = get_quality_category(wqi)

        # Create prediction record
        prediction = crud.create_prediction(
            db,
            measurement_id=measurement.id,
            is_potable=wqi >= 50,
            confidence=0.95,  # This should come from your ML model
            wqi_value=wqi,
            quality_category=quality_category
        )

        # Generate recommendations
        input_values = {
            "temperature": data.temperature,
            "dissolved_oxygen": data.dissolved_oxygen,
            "ph": data.ph,
            "conductivity": data.conductivity,
            "bod": data.bod,
            "nitrate": data.nitrate,
            "fecal_coliform": data.fecal_coliform,
            "total_coliform": data.total_coliform
        }
        recommendations = recommender.generate_recommendations(input_values)

        return WaterQualityPrediction(
            is_potable=prediction.is_potable,
            confidence=prediction.confidence,
            wqi_value=prediction.wqi_value,
            quality_category=prediction.quality_category,
            parameters={
                "temperature": data.temperature,
                "dissolved_oxygen": data.dissolved_oxygen,
                "ph": data.ph,
                "conductivity": data.conductivity,
                "bod": data.bod,
                "nitrate": data.nitrate,
                "fecal_coliform": data.fecal_coliform,
                "total_coliform": data.total_coliform
            },
            recommendations=recommendations
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process prediction: {str(e)}")

@app.get("/api/dashboard")
async def get_dashboard_data(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get recent measurements for current user (last 7 days)
        recent_measurements = crud.get_measurements(
            db,
            user_id=current_user.id,
            start_date=datetime.utcnow() - timedelta(days=7)
        )

        # If no measurements exist, return default values
        if not recent_measurements:
            return {
                "current_wqi": 0,
                "quality_category": "No Data",
                "parameter_summary": {
                    "temperature": {"current": 0, "min": 0, "max": 0, "avg": 0},
                    "dissolved_oxygen": {"current": 0, "min": 0, "max": 0, "avg": 0},
                    "ph": {"current": 0, "min": 0, "max": 0, "avg": 0},
                    "conductivity": {"current": 0, "min": 0, "max": 0, "avg": 0},
                    "bod": {"current": 0, "min": 0, "max": 0, "avg": 0},
                    "nitrate": {"current": 0, "min": 0, "max": 0, "avg": 0},
                    "fecal_coliform": {"current": 0, "min": 0, "max": 0, "avg": 0},
                    "total_coliform": {"current": 0, "min": 0, "max": 0, "avg": 0}
                },
                "recent_measurements": [],
                "alerts": [],
                "recommendations": []
            }

        # Get current WQI from the most recent measurement
        current_measurement = recent_measurements[0]
        current_wqi = 0
        quality_category = "Unknown"
        
        # Get the most recent prediction
        latest_prediction = db.query(models.WaterQualityPrediction)\
            .filter(models.WaterQualityPrediction.measurement_id == current_measurement.id)\
            .order_by(models.WaterQualityPrediction.timestamp.desc())\
            .first()
            
        if latest_prediction:
            current_wqi = latest_prediction.wqi_value
            quality_category = latest_prediction.quality_category

        # Calculate parameter summaries and check for alerts
        parameter_summary = {}
        alerts = []
        recommendations = []

        parameters = [
            "temperature", "dissolved_oxygen", "ph", "conductivity",
            "bod", "nitrate", "fecal_coliform", "total_coliform"
        ]

        # Define thresholds for each parameter
        thresholds = {
            "temperature": {"min": 20, "max": 30},
            "dissolved_oxygen": {"min": 4, "max": 8},
            "ph": {"min": 6.5, "max": 8.5},
            "conductivity": {"min": 200, "max": 800},
            "bod": {"min": 1, "max": 5},
            "nitrate": {"min": 0, "max": 10},
            "fecal_coliform": {"min": 0, "max": 500},
            "total_coliform": {"min": 0, "max": 1000}
        }

        # Create input values for recommender
        input_values = {}

        for param in parameters:
            values = [getattr(m, param) for m in recent_measurements]
            current_value = values[0]
            min_value = min(values)
            max_value = max(values)
            avg_value = sum(values) / len(values)

            parameter_summary[param] = {
                "current": current_value,
                "min": min_value,
                "max": max_value,
                "avg": avg_value
            }

            # Add current value to input values for recommender
            input_values[param] = current_value

            # Check for alerts
            threshold = thresholds.get(param, {"min": 0, "max": 0})
            if current_value < threshold["min"]:
                alerts.append({
                    "parameter": param,
                    "severity": "low",
                    "message": f"{param.replace('_', ' ').title()} is below acceptable range"
                })
            elif current_value > threshold["max"]:
                alerts.append({
                    "parameter": param,
                    "severity": "high",
                    "message": f"{param.replace('_', ' ').title()} is above acceptable range"
                })

        # Generate recommendations
        recommendations = recommender.generate_recommendations(input_values)

        # Format recent measurements
        formatted_measurements = []
        for measurement in recent_measurements[:5]:  # Limit to 5 most recent
            prediction = db.query(models.WaterQualityPrediction)\
                .filter(models.WaterQualityPrediction.measurement_id == measurement.id)\
                .order_by(models.WaterQualityPrediction.timestamp.desc())\
                .first()
                
            formatted_measurements.append({
                "id": measurement.id,
                "timestamp": measurement.timestamp.isoformat(),
                "wqi_value": prediction.wqi_value if prediction else 0,
                "quality_category": prediction.quality_category if prediction else "Unknown",
                "parameters": {
                    "temperature": measurement.temperature,
                    "dissolved_oxygen": measurement.dissolved_oxygen,
                    "ph": measurement.ph,
                    "conductivity": measurement.conductivity,
                    "bod": measurement.bod,
                    "nitrate": measurement.nitrate,
                    "fecal_coliform": measurement.fecal_coliform,
                    "total_coliform": measurement.total_coliform
                }
            })

        return {
            "current_wqi": current_wqi,
            "quality_category": quality_category,
            "parameter_summary": parameter_summary,
            "recent_measurements": formatted_measurements,
            "alerts": alerts,
            "recommendations": recommendations
        }

    except Exception as e:
        print(f"Error in dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

def calculate_wqi(data: WaterQualityData) -> float:
    # Define parameter weights based on their importance
    weights = {
        "temperature": 0.1,
        "dissolved_oxygen": 0.2,
        "ph": 0.15,
        "conductivity": 0.1,
        "bod": 0.15,
        "nitrate": 0.1,
        "fecal_coliform": 0.1,
        "total_coliform": 0.1
    }

    # Define acceptable ranges for each parameter
    ranges = {
        "temperature": {"min": 0, "max": 40, "optimal": (20, 30)},
        "dissolved_oxygen": {"min": 0, "max": 14, "optimal": (6, 8)},
        "ph": {"min": 0, "max": 14, "optimal": (6.5, 8.5)},
        "conductivity": {"min": 0, "max": 2000, "optimal": (200, 800)},
        "bod": {"min": 0, "max": 30, "optimal": (0, 3)},
        "nitrate": {"min": 0, "max": 50, "optimal": (0, 10)},
        "fecal_coliform": {"min": 0, "max": 500, "optimal": (0, 200)},
        "total_coliform": {"min": 0, "max": 1000, "optimal": (0, 500)}
    }

    def normalize_parameter(value: float, param: str) -> float:
        """Normalize parameter value to a 0-100 scale based on its optimal range"""
        range_info = ranges[param]
        min_val, max_val = range_info["min"], range_info["max"]
        opt_min, opt_max = range_info["optimal"]

        # For parameters where lower is better (BOD, nitrate, coliforms)
        if param in ["bod", "nitrate", "fecal_coliform", "total_coliform"]:
            if value <= opt_min:
                return 100
            elif value >= opt_max:
                return 0
            else:
                return 100 * (1 - (value - opt_min) / (opt_max - opt_min))
        
        # For parameters where higher is better (DO)
        elif param == "dissolved_oxygen":
            if value >= opt_max:
                return 100
            elif value <= opt_min:
                return 0
            else:
                return 100 * (value - opt_min) / (opt_max - opt_min)
        
        # For parameters with optimal range (temperature, pH, conductivity)
        else:
            if opt_min <= value <= opt_max:
                return 100
            elif value < opt_min:
                return 100 * (value - min_val) / (opt_min - min_val)
            else:
                return 100 * (1 - (value - opt_max) / (max_val - opt_max))

    # Calculate normalized scores for each parameter
    scores = {
        param: normalize_parameter(getattr(data, param), param)
        for param in weights.keys()
    }

    # Calculate weighted WQI
    wqi = sum(scores[param] * weight for param, weight in weights.items())
    return wqi

def get_quality_category(wqi: float) -> str:
    if wqi >= 90:
        return "Excellent"
    elif wqi >= 70:
        return "Good"
    elif wqi >= 50:
        return "Fair"
    elif wqi >= 25:
        return "Poor"
    else:
        return "Very Poor"

@app.get("/measurements/{measurement_id}")
async def get_measurement_details(measurement_id: int, db: Session = Depends(get_db)):
    """Get details of a specific measurement"""
    try:
        # TODO: Implement database query
        return {
            "id": measurement_id,
            "location": "Sample Location",
            "timestamp": datetime.now().isoformat(),
            "parameters": {
                "temperature": 25.0,
                "do": 6.5,
                "ph": 7.0,
                "conductivity": 500.0,
                "bod": 2.0,
                "nitrate": 5.0,
                "fecalcaliform": 50,
                "totalcaliform": 100
            },
            "wqi_value": 85.0,
            "quality_category": "Good"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends")
async def get_trends(
    days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trend data with enhanced analysis (no location filter)"""
    try:
        # Get all measurements for the specified period for current user
        measurements = crud.get_measurements(
            db,
            user_id=current_user.id,
            start_date=datetime.utcnow() - timedelta(days=days)
        )

        if not measurements:
            return {
                "dates": [],
                "parameters": {},
                "wqi_values": [],
                "trend_analysis": {},
                "recommendations": []
            }

        # Format the data
        dates = [m.timestamp.strftime('%Y-%m-%d') for m in measurements]
        wqi_values = [m.predictions[0].wqi_value if m.predictions else 0 for m in measurements]
        
        parameters = {
            "temperature": [m.temperature for m in measurements],
            "dissolved_oxygen": [m.dissolved_oxygen for m in measurements],
            "ph": [m.ph for m in measurements],
            "conductivity": [m.conductivity for m in measurements],
            "bod": [m.bod for m in measurements],
            "nitrate": [m.nitrate for m in measurements],
            "fecal_coliform": [m.fecal_coliform for m in measurements],
            "total_coliform": [m.total_coliform for m in measurements]
        }
        print("[DEBUG] Trend API parameter values:")
        for param, values in parameters.items():
            print(f"  {param}: {values}")

        # Enhanced trend analysis
        trend_analysis = {}
        recommendations = []

        for param, values in parameters.items():
            if len(values) < 2:
                continue

            # Calculate trend direction and slope
            x = np.arange(len(values))
            y = np.array(values)
            slope = float(np.polyfit(x, y, 1)[0])
            trend = "stable"
            if slope > 0.01:
                trend = "increasing"
            elif slope < -0.01:
                trend = "decreasing"

            # Detect anomalies (spikes/drops > 2 std dev from mean)
            mean = float(np.mean(y))
            std = float(np.std(y))
            anomalies = [float(v) for v in y if abs(v - mean) > 2 * std]

            # Calculate statistics
            current_value = float(y[-1])
            avg_value = float(mean)
            std_dev = float(std)
            min_value = float(np.min(y))
            max_value = float(np.max(y))

            # Thresholds for warnings
            thresholds = {
                "ph": {"min": 6.5, "max": 8.5},
                "dissolved_oxygen": {"min": 4, "max": 8},
                "temperature": {"min": 20, "max": 30},
                "conductivity": {"min": 200, "max": 800},
                "bod": {"min": 1, "max": 5},
                "nitrate": {"min": 0, "max": 10},
                "fecal_coliform": {"min": 0, "max": 500},
                "total_coliform": {"min": 0, "max": 1000}
            }
            warning = None
            if param in thresholds:
                t = thresholds[param]
                if current_value < t["min"]:
                    warning = f"Current value {current_value} is below the acceptable minimum ({t['min']})."
                elif current_value > t["max"]:
                    warning = f"Current value {current_value} is above the acceptable maximum ({t['max']})."
                elif abs(current_value - t["min"]) < 0.1 * (t["max"] - t["min"]):
                    warning = f"Current value {current_value} is close to the minimum threshold ({t['min']})."
                elif abs(current_value - t["max"]) < 0.1 * (t["max"] - t["min"]):
                    warning = f"Current value {current_value} is close to the maximum threshold ({t['max']})."

            # Add to trend analysis
            trend_analysis[param] = {
                "trend": trend,
                "slope": slope,
                "current_value": current_value,
                "average": avg_value,
                "std_dev": std_dev,
                "min": min_value,
                "max": max_value,
                "anomalies": anomalies,
                "warning": warning
            }

            # Add recommendations based on trend and warnings
            if trend == "increasing" and param in ["temperature", "bod", "nitrate", "fecal_coliform", "total_coliform"]:
                recommendations.append({
                    "parameter": param,
                    "severity": "medium",
                    "message": f"{param.replace('_', ' ').title()} is increasing. Monitor closely and consider preventive measures."
                })
            elif trend == "decreasing" and param in ["dissolved_oxygen", "ph"]:
                recommendations.append({
                    "parameter": param,
                    "severity": "high",
                    "message": f"{param.replace('_', ' ').title()} is decreasing. Immediate action may be required."
                })
            if warning:
                recommendations.append({
                    "parameter": param,
                    "severity": "warning",
                    "message": warning
                })
            if anomalies:
                recommendations.append({
                    "parameter": param,
                    "severity": "anomaly",
                    "message": f"Detected anomalies in {param.replace('_', ' ')}: {anomalies}"
                })

        # Add WQI trend analysis
        if len(wqi_values) >= 2:
            x = np.arange(len(wqi_values))
            y = np.array(wqi_values)
            slope = float(np.polyfit(x, y, 1)[0])
            wqi_trend = "stable"
            if slope > 0.01:
                wqi_trend = "improving"
            elif slope < -0.01:
                wqi_trend = "deteriorating"
            trend_analysis["wqi"] = {
                "trend": wqi_trend,
                "slope": slope,
                "current_value": float(y[-1]),
                "average": float(np.mean(y)),
                "std_dev": float(np.std(y)),
                "min": float(np.min(y)),
                "max": float(np.max(y))
            }
            if wqi_trend == "deteriorating":
                recommendations.append({
                    "parameter": "wqi",
                    "severity": "high",
                    "message": "Overall water quality is deteriorating. Comprehensive review of all parameters recommended."
                })

        return {
            "dates": dates,
            "parameters": parameters,
            "wqi_values": wqi_values,
            "trend_analysis": trend_analysis,
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"Error in get_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/parameter/{parameter}")
async def get_parameter_dashboard(parameter: str, db: Session = Depends(get_db)):
    """Get parameter-specific dashboard data"""
    try:
        # Map frontend parameter names to database column names
        parameter_map = {
            "temperature": "temperature",
            "dissolved-oxygen": "dissolved_oxygen",
            "D_O": "dissolved_oxygen",
            "d_o": "dissolved_oxygen",
            "ph": "ph",
            "pH": "ph",
            "conductivity": "conductivity",
            "bod": "bod",
            "B_O_D": "bod",
            "nitrate": "nitrate",
            "fecal-coliform": "fecal_coliform",
            "Fecalcaliform": "fecal_coliform",
            "total-coliform": "total_coliform",
            "Totalcaliform": "total_coliform"
        }
        
        # Convert parameter to lowercase for case-insensitive matching
        param_key = parameter.lower()
        
        # Check if parameter is valid
        if param_key not in [k.lower() for k in parameter_map.keys()]:
            raise HTTPException(status_code=400, detail=f"Invalid parameter: {parameter}")
            
        # Get the database column name
        db_column = parameter_map[param_key]

        # Get recent measurements
        measurements = crud.get_measurements(
            db,
            start_date=datetime.utcnow() - timedelta(days=30)
        )

        if not measurements:
            return {
                "parameter": parameter,
                "current_value": 0,
                "historical_values": {
                    "dates": [],
                    "values": []
                },
                "statistics": {
                    "min": 0,
                    "max": 0,
                    "avg": 0,
                    "std_dev": 0
                },
                "threshold_info": {
                    "min_acceptable": 0,
                    "max_acceptable": 0,
                    "is_within_range": True
                }
            }

        # Get values for the specified parameter
        values = [getattr(m, db_column) for m in measurements]
        dates = [m.timestamp.strftime('%Y-%m-%d') for m in measurements]

        # Calculate statistics
        stats = {
            "min": float(min(values)),
            "max": float(max(values)),
            "avg": float(np.mean(values)),
            "std_dev": float(np.std(values))
        }

        # Define thresholds based on water quality standards
        thresholds = {
            "ph": {"min": 6.5, "max": 8.5},
            "dissolved_oxygen": {"min": 4, "max": 8},
            "temperature": {"min": 20, "max": 30},
            "conductivity": {"min": 200, "max": 800},
            "bod": {"min": 1, "max": 5},
            "nitrate": {"min": 0, "max": 10},
            "fecal_coliform": {"min": 0, "max": 500},
            "total_coliform": {"min": 0, "max": 1000}
        }

        threshold_info = thresholds.get(db_column, {"min": 0, "max": 0})
        is_within_range = (
            threshold_info["min"] <= values[0] <= threshold_info["max"]
            if values else True
        )

        # Generate recommendations based on parameter values
        recommendations = []
        current_value = float(values[0]) if values else 0
        
        if current_value < threshold_info["min"]:
            recommendations.append({
                "severity": "high",
                "message": f"{parameter} is below acceptable range. Consider taking corrective measures."
            })
        elif current_value > threshold_info["max"]:
            recommendations.append({
                "severity": "high",
                "message": f"{parameter} is above acceptable range. Consider taking corrective measures."
            })

        return {
            "parameter": parameter,
            "current_value": current_value,
            "historical_values": {
                "dates": dates,
                "values": [float(v) for v in values]
            },
            "statistics": stats,
            "threshold_info": {
                "min_acceptable": threshold_info["min"],
                "max_acceptable": threshold_info["max"],
                "is_within_range": is_within_range
            },
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"Error in get_parameter_dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/compare")
async def get_comparison_dashboard(locations: str, days: int = 30, db: Session = Depends(get_db)):
    """Get comparison dashboard data for multiple locations"""
    try:
        location_list = locations.split(",")
        dates = pd.date_range(end=datetime.now(), periods=days).strftime('%Y-%m-%d').tolist()
        
        return {
            "locations": location_list,
            "dates": dates,
            "wqi_values": {loc: [85.0] * days for loc in location_list},
            "parameter_averages": {
                loc: {
                    "temperature": 25.0,
                    "do": 6.5,
                    "ph": 7.0,
                    "conductivity": 500.0,
                    "bod": 2.0,
                    "nitrate": 5.0,
                    "fecalcaliform": 50,
                    "totalcaliform": 100
                } for loc in location_list
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/{location}")
async def export_data(location: str, format: str = "csv", db: Session = Depends(get_db)):
    """Export data for a specific location"""
    try:
        # TODO: Implement data export
        # For now, return a dummy CSV
        csv_data = "timestamp,temperature,do,ph,conductivity,bod,nitrate,fecalcaliform,totalcaliform\n"
        csv_data += f"{datetime.now().isoformat()},25.0,6.5,7.0,500.0,2.0,5.0,50,100"
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={location}_data.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-report")
async def generate_report(
    data: WaterQualityData,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get prediction data
        prediction = await predict_water_quality(data, current_user, db)
        
        # Generate PDF
        pdf_buffer = generate_water_quality_report(
            measurement_data=data.dict(),
            prediction_data=prediction.dict(),
            recommendations=prediction.recommendations
        )
        
        # Return PDF as downloadable file
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=water_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 