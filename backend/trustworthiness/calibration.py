"""
Confidence calibration for RAG systems.
Ensures predicted confidence scores match actual accuracy.
"""

from typing import List, Dict, Tuple
import numpy as np
from sklearn.isotonic import IsotonicRegression


def calculate_ece(
    confidences: List[float],
    accuracies: List[float],
    n_bins: int = 10
) -> float:
    """
    Calculate Expected Calibration Error (ECE).
    
    Args:
        confidences: Predicted confidence scores (0-1)
        confidences: Actual accuracies (0-1)
        n_bins: Number of bins for calibration
    
    Returns:
        ECE score (lower is better, 0 = perfect calibration)
    """
    confidences = np.array(confidences)
    accuracies = np.array(accuracies)
    
    # Create bins
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    
    ece = 0.0
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        # Find samples in this bin
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = in_bin.mean()
        
        if prop_in_bin > 0:
            accuracy_in_bin = accuracies[in_bin].mean()
            avg_confidence_in_bin = confidences[in_bin].mean()
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
    
    return float(ece)


def get_calibration_curve(
    confidences: List[float],
    accuracies: List[float],
    n_bins: int = 10
) -> Dict:
    """
    Generate calibration curve data for plotting.
    
    Args:
        confidences: Predicted confidence scores
        accuracies: Actual accuracies
        n_bins: Number of bins
    
    Returns:
        Dictionary with calibration curve data
    """
    confidences = np.array(confidences)
    accuracies = np.array(accuracies)
    
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    
    bin_centers = []
    bin_accuracies = []
    bin_confidences = []
    bin_counts = []
    
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        
        if in_bin.sum() > 0:
            bin_centers.append((bin_lower + bin_upper) / 2)
            bin_accuracies.append(float(accuracies[in_bin].mean()))
            bin_confidences.append(float(confidences[in_bin].mean()))
            bin_counts.append(int(in_bin.sum()))
    
    return {
        "bin_centers": bin_centers,
        "bin_accuracies": bin_accuracies,
        "bin_confidences": bin_confidences,
        "bin_counts": bin_counts,
        "ece": calculate_ece(confidences, accuracies, n_bins)
    }


class ConfidenceCalibrator:
    """
    Calibrates confidence scores using temperature scaling or isotonic regression.
    """
    
    def __init__(self, method: str = "temperature"):
        """
        Initialize calibrator.
        
        Args:
            method: "temperature" or "isotonic"
        """
        self.method = method
        self.temperature = 1.0
        self.isotonic_model = None
        self.is_fitted = False
    
    def fit(self, confidences: List[float], accuracies: List[float]):
        """
        Fit calibration model on historical data.
        
        Args:
            confidences: Predicted confidence scores
            accuracies: Actual accuracies
        """
        confidences = np.array(confidences)
        accuracies = np.array(accuracies)
        
        if self.method == "temperature":
            # Simple temperature scaling
            # Find temperature that minimizes calibration error
            best_temp = 1.0
            best_ece = float('inf')
            
            for temp in np.linspace(0.1, 3.0, 30):
                calibrated = self._apply_temperature(confidences, temp)
                ece = calculate_ece(calibrated, accuracies)
                
                if ece < best_ece:
                    best_ece = ece
                    best_temp = temp
            
            self.temperature = best_temp
            
        elif self.method == "isotonic":
            # Isotonic regression
            self.isotonic_model = IsotonicRegression(out_of_bounds='clip')
            self.isotonic_model.fit(confidences, accuracies)
        
        self.is_fitted = True
    
    def _apply_temperature(self, confidences: np.ndarray, temperature: float) -> np.ndarray:
        """Apply temperature scaling to confidences."""
        # Convert to logits (approximate)
        epsilon = 1e-7
        confidences = np.clip(confidences, epsilon, 1 - epsilon)
        logits = np.log(confidences / (1 - confidences))
        
        # Scale by temperature
        scaled_logits = logits / temperature
        
        # Convert back to probabilities
        calibrated = 1 / (1 + np.exp(-scaled_logits))
        
        return calibrated
    
    def calibrate(self, confidence: float) -> float:
        """
        Calibrate a single confidence score.
        
        Args:
            confidence: Raw confidence score
        
        Returns:
            Calibrated confidence score
        """
        if not self.is_fitted:
            return confidence
        
        if self.method == "temperature":
            calibrated = self._apply_temperature(np.array([confidence]), self.temperature)[0]
        elif self.method == "isotonic":
            calibrated = self.isotonic_model.predict([confidence])[0]
        else:
            calibrated = confidence
        
        return float(np.clip(calibrated, 0.0, 1.0))


# Global calibrator instance
_calibrator_instance = None


def get_calibrator() -> ConfidenceCalibrator:
    """Get or create global calibrator instance."""
    global _calibrator_instance
    if _calibrator_instance is None:
        _calibrator_instance = ConfidenceCalibrator(method="temperature")
    return _calibrator_instance


def calibrate_confidence(confidence: float) -> float:
    """
    Calibrate a confidence score using the global calibrator.
    
    Args:
        confidence: Raw confidence score
    
    Returns:
        Calibrated confidence score
    """
    calibrator = get_calibrator()
    if calibrator.is_fitted:
        return calibrator.calibrate(confidence)
    return confidence
