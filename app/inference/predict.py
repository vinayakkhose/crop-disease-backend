"""
Inference module - imports from src/inference/predict
"""

import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.inference.predict import AdvancedPredictor

__all__ = ['AdvancedPredictor']
