"""
Soil Health Analysis Service
"""

from typing import Dict, Optional
import numpy as np


class SoilHealthAnalyzer:
    """Analyze soil health and provide recommendations"""
    
    def __init__(self):
        # Optimal ranges for different nutrients
        self.optimal_ranges = {
            'pH': {'min': 6.0, 'max': 7.5, 'optimal': 6.5},
            'nitrogen': {'min': 20, 'max': 40, 'optimal': 30},  # ppm
            'phosphorus': {'min': 15, 'max': 30, 'optimal': 20},  # ppm
            'potassium': {'min': 150, 'max': 250, 'optimal': 200},  # ppm
            'organic_matter': {'min': 3, 'max': 5, 'optimal': 4},  # %
            'moisture': {'min': 40, 'max': 60, 'optimal': 50}  # %
        }
    
    def analyze_soil(self, soil_data: Dict) -> Dict:
        """
        Analyze soil health
        
        Args:
            soil_data: Dict with pH, nitrogen, phosphorus, potassium, etc.
        
        Returns:
            Comprehensive soil health analysis
        """
        analysis = {
            'overall_score': 0,
            'parameters': {},
            'recommendations': [],
            'health_status': 'Unknown'
        }
        
        total_score = 0
        param_count = 0
        
        # Analyze each parameter
        for param, value in soil_data.items():
            if param in self.optimal_ranges:
                param_analysis = self._analyze_parameter(param, value)
                analysis['parameters'][param] = param_analysis
                total_score += param_analysis['score']
                param_count += 1
        
        # Calculate overall score
        if param_count > 0:
            analysis['overall_score'] = round(total_score / param_count, 2)
        
        # Determine health status
        if analysis['overall_score'] >= 80:
            analysis['health_status'] = 'Excellent'
        elif analysis['overall_score'] >= 60:
            analysis['health_status'] = 'Good'
        elif analysis['overall_score'] >= 40:
            analysis['health_status'] = 'Fair'
        else:
            analysis['health_status'] = 'Poor'
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis['parameters'])
        
        return analysis
    
    def _analyze_parameter(self, param: str, value: float) -> Dict:
        """Analyze individual parameter"""
        ranges = self.optimal_ranges[param]
        optimal = ranges['optimal']
        min_val = ranges['min']
        max_val = ranges['max']
        
        # Calculate score (100 if optimal, decreases with distance)
        if min_val <= value <= max_val:
            # Within range - calculate score based on distance from optimal
            distance = abs(value - optimal)
            range_size = max_val - min_val
            score = 100 - (distance / range_size * 40)  # Max 40 point deduction
            score = max(60, score)  # Minimum 60 if in range
        else:
            # Outside range
            if value < min_val:
                distance = min_val - value
                score = max(0, 60 - (distance / min_val * 60))
            else:
                distance = value - max_val
                score = max(0, 60 - (distance / max_val * 60))
        
        status = 'Optimal' if min_val <= value <= max_val else 'Needs Attention'
        
        return {
            'value': value,
            'optimal_range': f"{min_val}-{max_val}",
            'optimal_value': optimal,
            'score': round(score, 2),
            'status': status
        }
    
    def _generate_recommendations(self, parameters: Dict) -> list:
        """Generate soil improvement recommendations"""
        recommendations = []
        
        for param, analysis in parameters.items():
            if analysis['status'] != 'Optimal':
                value = analysis['value']
                optimal = analysis['optimal_value']
                
                if param == 'pH':
                    if value < 6.0:
                        recommendations.append("Add lime to raise pH level")
                    else:
                        recommendations.append("Add sulfur to lower pH level")
                
                elif param == 'nitrogen':
                    if value < 20:
                        recommendations.append("Apply nitrogen-rich fertilizer (urea, ammonium nitrate)")
                    else:
                        recommendations.append("Reduce nitrogen application, may cause excessive growth")
                
                elif param == 'phosphorus':
                    if value < 15:
                        recommendations.append("Add phosphorus fertilizer (superphosphate, bone meal)")
                
                elif param == 'potassium':
                    if value < 150:
                        recommendations.append("Apply potassium fertilizer (potash, wood ash)")
                
                elif param == 'organic_matter':
                    if value < 3:
                        recommendations.append("Add compost, manure, or organic matter to improve soil structure")
        
        if not recommendations:
            recommendations.append("Soil health is optimal. Maintain current practices.")
        
        return recommendations
    
    def recommend_fertilizer(self, crop_type: str, soil_data: Dict) -> Dict:
        """Recommend fertilizer based on crop and soil"""
        analysis = self.analyze_soil(soil_data)
        
        # Base recommendations
        base_recommendations = {
            'Tomato': 'NPK 10-10-10 with added calcium',
            'Potato': 'High potassium fertilizer (NPK 5-10-20)',
            'Corn': 'Nitrogen-rich fertilizer (NPK 20-10-10)',
            'Apple': 'Balanced NPK with micronutrients',
            'Grape': 'Potassium-rich fertilizer (NPK 10-10-20)'
        }
        
        recommendation = base_recommendations.get(crop_type, 'Balanced NPK fertilizer')
        
        # Adjust based on soil analysis
        if 'nitrogen' in analysis['parameters']:
            if analysis['parameters']['nitrogen']['value'] < 20:
                recommendation += " + Extra nitrogen"
        
        if 'phosphorus' in analysis['parameters']:
            if analysis['parameters']['phosphorus']['value'] < 15:
                recommendation += " + Extra phosphorus"
        
        return {
            'fertilizer': recommendation,
            'soil_analysis': analysis,
            'application_rate': 'Apply according to package instructions',
            'timing': 'Apply before planting and during growing season'
        }


# Global instance
soil_health_analyzer = SoilHealthAnalyzer()
