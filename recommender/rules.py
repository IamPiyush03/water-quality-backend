from typing import Dict, List
from .guidelines import GUIDELINES

class WaterQualityRecommender:
    def __init__(self):
        self.guidelines = GUIDELINES
    
    def _get_severity_level(self, value: float, param: str, direction: str) -> str:
        """Determine severity level based on value and parameter"""
        if param not in self.guidelines:
            return "unknown"
            
        param_guidelines = self.guidelines[param]
        severity_levels = param_guidelines["severity_levels"]
        
        if direction == "low":
            for level, threshold in severity_levels.items():
                if value <= threshold:
                    return level
        else:  # high
            for level, threshold in severity_levels.items():
                if value >= threshold:
                    return level
                    
        return "normal"
    
    def _get_parameter_description(self, param: str) -> str:
        """Get parameter description and health implications"""
        descriptions = {
            "ph": "pH measures water's acidity or alkalinity. Extreme values can affect water treatment efficiency and pipe corrosion.",
            "dissolved_oxygen": "Dissolved oxygen is crucial for aquatic life. Low levels can cause fish kills and anaerobic conditions.",
            "conductivity": "Conductivity indicates water's ability to conduct electricity, reflecting dissolved solids content.",
            "bod": "Biochemical Oxygen Demand measures organic matter content. High BOD indicates poor water quality.",
            "nitrate": "Nitrate levels above 10 mg/L can cause methemoglobinemia (blue baby syndrome) in infants.",
            "fecal_coliform": "Fecal coliform indicates potential presence of disease-causing organisms from human/animal waste.",
            "total_coliform": "Total coliform indicates overall microbial water quality and potential contamination."
        }
        return descriptions.get(param, "No description available")
    
    def _get_health_implications(self, param: str, severity: str) -> List[str]:
        """Get health implications based on parameter and severity"""
        implications = {
            "ph": {
                "mild": ["Slight irritation to eyes and skin", "Reduced effectiveness of disinfection"],
                "moderate": ["Increased corrosion of pipes", "Reduced effectiveness of water treatment"],
                "severe": ["Significant corrosion of infrastructure", "Potential health risks from heavy metal leaching"],
                "critical": ["Immediate health risks", "Severe infrastructure damage"]
            },
            "dissolved_oxygen": {
                "mild": ["Stress on aquatic life", "Reduced water quality"],
                "moderate": ["Fish kills possible", "Anaerobic conditions developing"],
                "severe": ["Mass fish kills", "Severe ecosystem damage"],
                "critical": ["Complete ecosystem collapse", "Production of toxic gases"]
            },
            "conductivity": {
                "mild": ["Slight taste changes", "Minor scaling in pipes"],
                "moderate": ["Increased scaling", "Reduced effectiveness of treatment"],
                "severe": ["Severe scaling", "Potential health risks from high mineral content"],
                "critical": ["Immediate health risks", "Infrastructure damage"]
            },
            "bod": {
                "mild": ["Slight odor issues", "Minor water quality degradation"],
                "moderate": ["Significant odor problems", "Reduced oxygen levels"],
                "severe": ["Severe water quality issues", "Potential health risks"],
                "critical": ["Immediate health risks", "Complete water quality failure"]
            },
            "nitrate": {
                "mild": ["Slight risk to sensitive populations", "Minor water quality issues"],
                "moderate": ["Risk to infants and pregnant women", "Potential health impacts"],
                "severe": ["Significant health risks", "Potential for methemoglobinemia"],
                "critical": ["Immediate health risks", "Life-threatening conditions possible"]
            },
            "fecal_coliform": {
                "mild": ["Low risk of waterborne illness", "Minor contamination"],
                "moderate": ["Moderate risk of illness", "Significant contamination"],
                "severe": ["High risk of illness", "Severe contamination"],
                "critical": ["Immediate health risks", "Outbreak potential"]
            },
            "total_coliform": {
                "mild": ["Low risk of contamination", "Minor water quality issues"],
                "moderate": ["Moderate risk of contamination", "Significant water quality issues"],
                "severe": ["High risk of contamination", "Severe water quality issues"],
                "critical": ["Immediate health risks", "Outbreak potential"]
            }
        }
        return implications.get(param, {}).get(severity, ["Unknown health implications"])
    
    def generate_recommendations(self, input_values: Dict[str, float]) -> Dict[str, List[Dict]]:
        """Generate comprehensive recommendations based on input values and WHO guidelines"""
        recommendations = {
            "immediate": [],
            "short_term": [],
            "long_term": [],
            "preventive": []
        }
        
        # Convert string values to numeric values
        value_mapping = {
            "low": 0.0,
            "high": 1000.0,  # Use appropriate high value based on parameter
            "normal": 50.0   # Use appropriate normal value based on parameter
        }
        
        for param, value in input_values.items():
            try:
                # Convert string values to numeric
                if isinstance(value, str):
                    value = value_mapping.get(value.lower(), 0.0)
                
                # Check if parameter exists in guidelines
                if param not in self.guidelines:
                    print(f"Warning: No guidelines found for parameter {param}")
                    continue
                    
                param_guidelines = self.guidelines[param]
                min_val, max_val = param_guidelines["range"]
                
                # Determine if value is low or high
                if value < min_val:
                    direction = "low"
                    severity = self._get_severity_level(value, param, direction)
                elif value > max_val:
                    direction = "high"
                    severity = self._get_severity_level(value, param, direction)
                else:
                    continue  # Value is within acceptable range
                
                # Get measures for the current direction and severity
                measures = param_guidelines["measures"][direction]
                
                # Get parameter description and health implications
                description = self._get_parameter_description(param)
                health_implications = self._get_health_implications(param, severity)
                
                # Add recommendations only for priority levels that have specific measures
                for priority in ["immediate", "short_term", "long_term", "preventive"]:
                    if priority in measures and measures[priority] and len(measures[priority]) > 0:
                        for action in measures[priority]:
                            recommendation = {
                                "parameter": param,
                                "severity": severity,
                                "description": description,
                                "health_implications": health_implications,
                                "action": action,
                                "priority": priority,
                                "current_value": value,
                                "acceptable_range": [min_val, max_val]
                            }
                            recommendations[priority].append(recommendation)
                        
            except Exception as e:
                print(f"Error processing {param}: {str(e)}")
                continue
        
        return recommendations 