"""
Intelligent Fertilizer & Pesticide Recommendation Engine
"""

from typing import Dict, Optional, List
from app.services.soil_health import soil_health_analyzer


class FertilizerRecommender:
    """Intelligent fertilizer and pesticide recommendation"""
    
    def __init__(self):
        self.crop_requirements = {
            'Tomato': {
                'nitrogen': {'min': 25, 'max': 35, 'optimal': 30},
                'phosphorus': {'min': 15, 'max': 25, 'optimal': 20},
                'potassium': {'min': 200, 'max': 300, 'optimal': 250},
                'calcium': {'min': 1000, 'max': 2000, 'optimal': 1500},
                'fertilizer': 'NPK 10-10-10 + Calcium',
                'application_timing': 'Before planting, flowering, fruiting'
            },
            'Potato': {
                'nitrogen': {'min': 20, 'max': 30, 'optimal': 25},
                'phosphorus': {'min': 20, 'max': 30, 'optimal': 25},
                'potassium': {'min': 250, 'max': 350, 'optimal': 300},
                'fertilizer': 'NPK 5-10-20 (High Potassium)',
                'application_timing': 'At planting, tuber formation'
            },
            'Corn': {
                'nitrogen': {'min': 30, 'max': 50, 'optimal': 40},
                'phosphorus': {'min': 15, 'max': 25, 'optimal': 20},
                'potassium': {'min': 150, 'max': 250, 'optimal': 200},
                'fertilizer': 'NPK 20-10-10 (High Nitrogen)',
                'application_timing': 'At planting, knee-high stage, tasseling'
            },
            'Sugarcane': {
                'nitrogen': {'min': 25, 'max': 40, 'optimal': 32},
                'phosphorus': {'min': 15, 'max': 25, 'optimal': 20},
                'potassium': {'min': 200, 'max': 350, 'optimal': 280},
                'fertilizer': 'NPK 20-10-20 (High N and K)',
                'application_timing': 'At planting, tillering, grand growth stage'
            }
        }
        
        self.pesticide_recommendations = {
            'bacterial_spot': {
                'fungicides': ['Copper-based fungicides', 'Streptomycin'],
                'application': 'Apply every 7-10 days during wet weather',
                'organic': 'Copper soap, neem oil'
            },
            'early_blight': {
                'fungicides': ['Chlorothalonil', 'Mancozeb'],
                'application': 'Start before symptoms appear, continue every 7-14 days',
                'organic': 'Copper fungicides, baking soda spray'
            },
            'aphids': {
                'insecticides': ['Neem oil', 'Insecticidal soap', 'Pyrethrin'],
                'application': 'Apply when pests are detected, repeat as needed',
                'organic': 'Neem oil, ladybugs, insecticidal soap'
            }
        }
    
    def recommend_fertilizer(
        self,
        crop_type: str,
        soil_data: Dict,
        growth_stage: Optional[str] = None
    ) -> Dict:
        """Recommend fertilizer based on crop and soil"""
        
        if crop_type not in self.crop_requirements:
            return {
                'fertilizer': 'Balanced NPK fertilizer',
                'message': 'Crop-specific recommendations not available'
            }
        
        crop_req = self.crop_requirements[crop_type]
        soil_analysis = soil_health_analyzer.analyze_soil(soil_data)
        
        # Determine what's needed
        recommendations = []
        adjustments = []
        
        # Check nitrogen
        if 'nitrogen' in soil_data:
            soil_n = soil_data['nitrogen']
            req_n = crop_req['nitrogen']
            if soil_n < req_n['min']:
                adjustments.append(f"Add {req_n['optimal'] - soil_n:.1f} ppm nitrogen")
                recommendations.append("Use nitrogen-rich fertilizer")
        
        # Check phosphorus
        if 'phosphorus' in soil_data:
            soil_p = soil_data['phosphorus']
            req_p = crop_req['phosphorus']
            if soil_p < req_p['min']:
                adjustments.append(f"Add {req_p['optimal'] - soil_p:.1f} ppm phosphorus")
                recommendations.append("Use phosphorus-rich fertilizer")
        
        # Check potassium
        if 'potassium' in soil_data:
            soil_k = soil_data['potassium']
            req_k = crop_req['potassium']
            if soil_k < req_k['min']:
                adjustments.append(f"Add {req_k['optimal'] - soil_k:.1f} ppm potassium")
                recommendations.append("Use potassium-rich fertilizer")
        
        # Base recommendation
        base_fertilizer = crop_req['fertilizer']
        
        # Adjust based on needs
        if adjustments:
            fertilizer = base_fertilizer
            if 'nitrogen' in ' '.join(recommendations).lower():
                fertilizer += " + Extra Nitrogen"
            if 'phosphorus' in ' '.join(recommendations).lower():
                fertilizer += " + Extra Phosphorus"
            if 'potassium' in ' '.join(recommendations).lower():
                fertilizer += " + Extra Potassium"
        else:
            fertilizer = base_fertilizer
        
        # Growth stage adjustments
        timing = crop_req['application_timing']
        if growth_stage:
            if growth_stage == 'Flowering':
                timing = 'Apply during flowering stage'
            elif growth_stage == 'Fruiting':
                timing = 'Apply during fruiting stage'
        
        return {
            'fertilizer': fertilizer,
            'application_timing': timing,
            'soil_analysis': soil_analysis,
            'adjustments_needed': adjustments,
            'application_rate': 'Follow package instructions based on soil test results',
            'frequency': 'Apply as per growth stage requirements'
        }
    
    def recommend_pesticide(
        self,
        disease_name: str,
        severity: str,
        crop_type: str,
        prefer_organic: bool = False
    ) -> Dict:
        """Recommend pesticide for disease/pest"""
        
        disease_lower = disease_name.lower().replace(' ', '_')
        
        if disease_lower not in self.pesticide_recommendations:
            return {
                'pesticide': 'Consult agricultural expert',
                'message': 'Specific recommendations not available for this disease'
            }
        
        rec = self.pesticide_recommendations[disease_lower]
        
        # Choose organic or chemical based on preference
        if prefer_organic and 'organic' in rec:
            pesticides = rec['organic']
            pesticide_type = 'Organic'
        else:
            pesticides = rec.get('fungicides', rec.get('insecticides', []))
            pesticide_type = 'Chemical'
        
        # Adjust application based on severity
        application = rec['application']
        if severity == 'Severe':
            application += " Increase frequency to every 5-7 days."
        elif severity == 'Moderate':
            application += " Continue regular application schedule."
        
        return {
            'pesticide': pesticides[0] if isinstance(pesticides, list) else pesticides,
            'alternatives': pesticides[1:] if isinstance(pesticides, list) and len(pesticides) > 1 else [],
            'type': pesticide_type,
            'application': application,
            'severity': severity,
            'crop_type': crop_type
        }
    
    def get_fertilizer_schedule(
        self,
        crop_type: str,
        planting_date: str
    ) -> List[Dict]:
        """Get fertilizer application schedule"""
        
        if crop_type not in self.crop_requirements:
            return []
        
        crop_req = self.crop_requirements[crop_type]
        timing = crop_req['application_timing']
        
        # Parse timing and create schedule
        schedule = []
        
        if 'Before planting' in timing:
            schedule.append({
                'stage': 'Pre-planting',
                'fertilizer': crop_req['fertilizer'],
                'timing': '1-2 weeks before planting',
                'purpose': 'Prepare soil nutrients'
            })
        
        if 'Flowering' in timing:
            schedule.append({
                'stage': 'Flowering',
                'fertilizer': crop_req['fertilizer'],
                'timing': 'At first flower appearance',
                'purpose': 'Support flower development'
            })
        
        if 'Fruiting' in timing:
            schedule.append({
                'stage': 'Fruiting',
                'fertilizer': crop_req['fertilizer'],
                'timing': 'When fruits start forming',
                'purpose': 'Support fruit development'
            })
        
        return schedule


# Global instance
fertilizer_recommender = FertilizerRecommender()
