"""
Constants and reference values for transmission line calculations.
Based on NESC and ASCE MOP 74 standards.
"""

import math
from typing import Dict, NamedTuple


class ExposureConstants(NamedTuple):
    """Constants for each wind exposure category."""
    Zg: float  # Nominal height of the atmospheric boundary layer (ft)
    alpha: float  # Power law exponent for wind profile
    k: float  # Surface roughness coefficient
    alpha_FM: float  # Exponent for turbulence intensity
    LS: float  # Integral length scale (ft)


# NESC/ASCE Wind Exposure Category Constants
EXPOSURE_CATEGORIES: Dict[str, ExposureConstants] = {
    "B": ExposureConstants(Zg=1200, alpha=7.0, k=0.010, alpha_FM=4.5, LS=170),
    "C": ExposureConstants(Zg=900, alpha=9.5, k=0.005, alpha_FM=7.0, LS=220),  
    "D": ExposureConstants(Zg=700, alpha=11.5, k=0.003, alpha_FM=10.0, LS=250),
}


# NESC Conductor Tension Factors
class TensionFactors:
    """NESC-compliant tension factors as percentages of RBS."""
    INITIAL = 0.35  # 35% of RBS - Initial stringing tension
    FINAL = 0.25    # 25% of RBS - Final operating tension
    DESIGN = 0.80   # 80% of RBS - Design tension for deflected sag


# Wind Load Constants (ASCE 7 methodology)
class WindConstants:
    """Constants for wind pressure calculations."""
    Q = 0.00256      # Velocity pressure constant for imperial units (psf/(mph²))
    Kzt = 1.0        # Topographic factor (1.0 for flat/plain terrain)
    Cf = 1.0         # Force coefficient for cylindrical conductors


# Ice Load Constants (ASCE MOP 74)
class IceConstants:
    """Constants for ice load calculations."""
    ICE_DENSITY = 1.24  # Radial ice weight factor (lbs/ft per in²)
    HEIGHT_EXPONENT = 0.10  # Height adjustment exponent for ice thickness


# Physical Constants
class PhysicalConstants:
    """General physical constants."""
    SQRT_3 = math.sqrt(3)  # Square root of 3 (for phase voltage conversion)
    GRAVITY = 32.174  # ft/s² (for reference, not used directly in calculations)


# NESC Table 232-1 Clearance Constants
class NESCClearanceConstants:
    """Constants for NESC Table 232-1 clearance calculations."""
    OVERVOLTAGE_FACTOR = 1.1  # 10% overvoltage adjustment
    BASE_CLEARANCE = 18.5  # Base clearance in feet (for conductors at crossings)
    VOLTAGE_THRESHOLD = 22.0  # Voltage threshold in kV for clearance adder
    ADDER_FACTOR = 0.4  # Clearance adder factor (inches per kV above threshold)


# Validation Ranges
class ValidationRanges:
    """Acceptable ranges for input validation."""
    
    # System voltage (kV)
    VOLTAGE_MIN = 0.1
    VOLTAGE_MAX = 765.0
    VOLTAGE_TYPICAL_MIN = 12.0
    VOLTAGE_TYPICAL_MAX = 765.0
    
    # Wind speed (mph)
    WIND_SPEED_MIN = 0.1
    WIND_SPEED_MAX = 250.0
    WIND_SPEED_TYPICAL_MIN = 10.0
    WIND_SPEED_TYPICAL_MAX = 200.0
    
    # Ice thickness (inches)
    ICE_THICKNESS_MIN = 0.0
    ICE_THICKNESS_MAX = 10.0
    ICE_THICKNESS_TYPICAL_MAX = 2.0
    
    # Line angle (degrees)
    LINE_ANGLE_MIN = 0.0
    LINE_ANGLE_MAX = 180.0
    
    # Temperature (°F)
    TEMP_MIN = -100.0
    TEMP_MAX = 200.0
    
    # Span length (ft)
    SPAN_MIN = 1.0
    SPAN_MAX = 10000.0
    
    # Sag constraints
    SAG_TO_SPAN_RATIO_MAX = 0.5  # Sag should not exceed half the span


# Helper function to get exposure constants
def get_exposure_constants(category: str) -> ExposureConstants:
    """
    Retrieve exposure constants for a given category.
    
    Args:
        category: Exposure category ("B", "C", or "D")
        
    Returns:
        ExposureConstants for the specified category
        
    Raises:
        ValueError: If category is not valid
    """
    category = category.upper()
    if category not in EXPOSURE_CATEGORIES:
        raise ValueError(f"Invalid exposure category: {category}. Must be B, C, or D.")
    return EXPOSURE_CATEGORIES[category]

