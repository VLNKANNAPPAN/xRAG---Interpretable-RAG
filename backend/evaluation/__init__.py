"""
Evaluation module initialization.
"""

from .quality_gates import check_quality_gates, get_quality_recommendations

__all__ = [
    'check_quality_gates',
    'get_quality_recommendations'
]
