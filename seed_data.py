from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from database.models import WaterQualityMeasurement, WaterQualityPrediction, Recommendation
from database.config import SessionLocal

def seed_database():
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Recommendation).delete()
        db.query(WaterQualityPrediction).delete()
        db.query(WaterQualityMeasurement).delete()
        db.commit()

        # Generate sample measurements
        measurements = []
        for i in range(30):  # Last 30 days
            measurement = WaterQualityMeasurement(
                latitude=random.uniform(-90, 90),
                longitude=random.uniform(-180, 180),
                temperature=random.uniform(20, 30),
                dissolved_oxygen=random.uniform(4, 8),
                ph=random.uniform(6.5, 8.5),
                conductivity=random.uniform(200, 800),
                bod=random.uniform(1, 5),
                nitrate=random.uniform(0, 10),
                fecal_coliform=random.uniform(0, 500),
                total_coliform=random.uniform(0, 1000),
                timestamp=datetime.utcnow() - timedelta(days=i)
            )
            measurements.append(measurement)
            db.add(measurement)
        db.commit()

        # Generate predictions and recommendations
        for measurement in measurements:
            # Calculate WQI (simplified)
            wqi = calculate_wqi(measurement)
            quality_category = get_quality_category(wqi)
            is_potable = wqi >= 50

            # Create prediction
            prediction = WaterQualityPrediction(
                measurement_id=measurement.id,
                is_potable=is_potable,
                confidence=random.uniform(0.8, 0.95),
                wqi_value=wqi,
                quality_category=quality_category
            )
            db.add(prediction)

            # Generate recommendations based on parameters
            recommendations = generate_recommendations(measurement)
            for rec in recommendations:
                recommendation = Recommendation(
                    measurement_id=measurement.id,
                    parameter=rec["parameter"],
                    severity=rec["severity"],
                    priority=rec["priority"],
                    recommendation=rec["recommendation"]
                )
                db.add(recommendation)

        db.commit()
        print("Database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {str(e)}")
        db.rollback()
    finally:
        db.close()

def calculate_wqi(measurement):
    # Simplified WQI calculation
    weights = {
        "temperature": 0.1,
        "dissolved_oxygen": 0.2,
        "ph": 0.2,
        "conductivity": 0.1,
        "bod": 0.15,
        "nitrate": 0.1,
        "fecal_coliform": 0.1,
        "total_coliform": 0.05
    }

    scores = {
        "temperature": score_temperature(measurement.temperature),
        "dissolved_oxygen": score_dissolved_oxygen(measurement.dissolved_oxygen),
        "ph": score_ph(measurement.ph),
        "conductivity": score_conductivity(measurement.conductivity),
        "bod": score_bod(measurement.bod),
        "nitrate": score_nitrate(measurement.nitrate),
        "fecal_coliform": score_fecal_coliform(measurement.fecal_coliform),
        "total_coliform": score_total_coliform(measurement.total_coliform)
    }

    wqi = sum(score * weights[param] for param, score in scores.items())
    return wqi

def get_quality_category(wqi):
    if wqi >= 90:
        return "Excellent"
    elif wqi >= 70:
        return "Good"
    elif wqi >= 50:
        return "Fair"
    else:
        return "Poor"

def score_temperature(value):
    if 20 <= value <= 30:
        return 100
    elif 15 <= value < 20 or 30 < value <= 35:
        return 80
    elif 10 <= value < 15 or 35 < value <= 40:
        return 60
    else:
        return 40

def score_dissolved_oxygen(value):
    if value >= 6:
        return 100
    elif 4 <= value < 6:
        return 80
    elif 2 <= value < 4:
        return 60
    else:
        return 40

def score_ph(value):
    if 6.5 <= value <= 8.5:
        return 100
    elif 6 <= value < 6.5 or 8.5 < value <= 9:
        return 80
    elif 5.5 <= value < 6 or 9 < value <= 9.5:
        return 60
    else:
        return 40

def score_conductivity(value):
    if 200 <= value <= 800:
        return 100
    elif 100 <= value < 200 or 800 < value <= 1000:
        return 80
    elif 50 <= value < 100 or 1000 < value <= 1500:
        return 60
    else:
        return 40

def score_bod(value):
    if value <= 3:
        return 100
    elif 3 < value <= 5:
        return 80
    elif 5 < value <= 10:
        return 60
    else:
        return 40

def score_nitrate(value):
    if value <= 10:
        return 100
    elif 10 < value <= 20:
        return 80
    elif 20 < value <= 30:
        return 60
    else:
        return 40

def score_fecal_coliform(value):
    if value <= 500:
        return 100
    elif 500 < value <= 1000:
        return 80
    elif 1000 < value <= 2000:
        return 60
    else:
        return 40

def score_total_coliform(value):
    if value <= 1000:
        return 100
    elif 1000 < value <= 2000:
        return 80
    elif 2000 < value <= 5000:
        return 60
    else:
        return 40

def generate_recommendations(measurement):
    recommendations = []

    # pH recommendations
    if measurement.ph < 6.5:
        recommendations.append({
            "parameter": "ph",
            "severity": "high",
            "priority": 1,
            "recommendation": "Add alkaline substances to increase pH levels"
        })
    elif measurement.ph > 8.5:
        recommendations.append({
            "parameter": "ph",
            "severity": "high",
            "priority": 1,
            "recommendation": "Add acidic substances to decrease pH levels"
        })

    # Dissolved oxygen recommendations
    if measurement.dissolved_oxygen < 4:
        recommendations.append({
            "parameter": "dissolved_oxygen",
            "severity": "high",
            "priority": 1,
            "recommendation": "Implement aeration systems to increase oxygen levels"
        })

    # BOD recommendations
    if measurement.bod > 5:
        recommendations.append({
            "parameter": "bod",
            "severity": "medium",
            "priority": 2,
            "recommendation": "Implement biological treatment to reduce organic matter"
        })

    # Nitrate recommendations
    if measurement.nitrate > 10:
        recommendations.append({
            "parameter": "nitrate",
            "severity": "high",
            "priority": 1,
            "recommendation": "Implement denitrification process to reduce nitrate levels"
        })

    # Coliform recommendations
    if measurement.fecal_coliform > 500 or measurement.total_coliform > 1000:
        recommendations.append({
            "parameter": "coliform",
            "severity": "high",
            "priority": 1,
            "recommendation": "Implement disinfection process to reduce coliform levels"
        })

    return recommendations

if __name__ == "__main__":
    seed_database() 