"""
Yield & Financial Loss Calculator
"""

from typing import Dict, Optional
import math


class YieldCalculator:
    """Calculate estimated yield and financial loss"""
    
    def __init__(self):
        # Average yields per crop (kg per hectare)
        self.base_yields = {
            'Tomato': 50000,  # kg/ha
            'Potato': 40000,
            'Corn': 8000,
            'Apple': 30000,
            'Grape': 15000
        }
        
        # Average prices per kg (USD)
        self.market_prices = {
            'Tomato': 1.5,
            'Potato': 0.8,
            'Corn': 0.3,
            'Apple': 2.0,
            'Grape': 3.0
        }
    
    def calculate_yield_loss(
        self,
        crop_type: str,
        disease_severity: str,
        area_hectares: float,
        infected_percentage: float
    ) -> Dict:
        """
        Calculate yield loss and financial impact
        
        Args:
            crop_type: Type of crop
            disease_severity: Mild, Moderate, or Severe
            area_hectares: Farm area in hectares
            infected_percentage: Percentage of crop infected
        
        Returns:
            Dict with yield estimates and financial impact
        """
        # Base yield for crop
        base_yield = self.base_yields.get(crop_type, 20000)
        
        # Severity impact factors
        severity_factors = {
            'Mild': 0.1,      # 10% yield loss
            'Moderate': 0.3,  # 30% yield loss
            'Severe': 0.6     # 60% yield loss
        }
        
        severity_factor = severity_factors.get(disease_severity, 0.3)
        
        # Calculate expected yield
        expected_yield = base_yield * area_hectares
        
        # Calculate yield loss
        yield_loss_percentage = severity_factor * (infected_percentage / 100)
        yield_loss_kg = expected_yield * yield_loss_percentage
        actual_yield_kg = expected_yield - yield_loss_kg
        
        # Financial impact
        market_price = self.market_prices.get(crop_type, 1.0)
        expected_revenue = expected_yield * market_price
        actual_revenue = actual_yield_kg * market_price
        financial_loss = expected_revenue - actual_revenue
        
        return {
            'crop_type': crop_type,
            'area_hectares': area_hectares,
            'disease_severity': disease_severity,
            'infected_percentage': infected_percentage,
            'expected_yield_kg': round(expected_yield, 2),
            'actual_yield_kg': round(actual_yield_kg, 2),
            'yield_loss_kg': round(yield_loss_kg, 2),
            'yield_loss_percentage': round(yield_loss_percentage * 100, 2),
            'expected_revenue_usd': round(expected_revenue, 2),
            'actual_revenue_usd': round(actual_revenue, 2),
            'financial_loss_usd': round(financial_loss, 2),
            'market_price_per_kg': market_price,
            'recommendation': self._get_recommendation(disease_severity, yield_loss_percentage)
        }
    
    def _get_recommendation(self, severity: str, loss_percentage: float) -> str:
        """Get recommendation based on loss"""
        if loss_percentage < 0.1:
            return "Minimal impact expected. Continue monitoring and preventive measures."
        elif loss_percentage < 0.3:
            return "Moderate impact. Implement treatment measures immediately to minimize further loss."
        else:
            return "Significant impact expected. Take immediate action: apply treatments, consider crop insurance, and consult agricultural experts."


# Global instance
yield_calculator = YieldCalculator()
