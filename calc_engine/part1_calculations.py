"""
Part 1: Sag, Wind & Ice Loads Calculations (Steps 1-5)

This module implements:
- Step 1: Initial & Final Sag (no external load)
- Step 2: Wind Pressure under ice
- Step 3: Ice Load
- Step 4: Wind Load
- Step 5: Effective Load

All formulas follow NESC and ASCE MOP 74 standards as specified in the flow document.
"""

from __future__ import annotations
import math
from typing import Tuple, TYPE_CHECKING, Any
from types import SimpleNamespace

from .constants import (
    TensionFactors,
    WindConstants,
    IceConstants,
    get_exposure_constants,
)

# Only import types for type hints, not at runtime
if TYPE_CHECKING:
    from .models import (
        ConductorData,
        SpanData,
        PoleGeometry,
        EnvironmentalData,
        Part1Output,
    )


def calculate_initial_final_sag(
    conductor: ConductorData,
    weight_span: float
) -> Tuple[float, float, float, float]:
    """
    Step 1: Calculate initial and final sag without external loads.
    
    Initial Sag (Si) = (Wc × l²) / (8 × Initial Tension)
    Final Sag (Sf) = (Wc × l²) / (8 × Final Tension)
    
    where:
    - Initial Tension = 0.35 × RBS (NESC compliance)
    - Final Tension = 0.25 × RBS (NESC compliance)
    
    Args:
        conductor: Conductor specifications
        weight_span: Weight span (l) in ft
        
    Returns:
        Tuple of (initial_tension, final_tension, initial_sag, final_sag)
        
    Raises:
        ValueError: If tensions are zero or sag calculations result in invalid values
    """
    # Calculate tensions per NESC guidelines
    initial_tension = TensionFactors.INITIAL * conductor.rbs  # 35% of RBS
    final_tension = TensionFactors.FINAL * conductor.rbs      # 25% of RBS
    
    # Validate tensions
    if initial_tension <= 0 or final_tension <= 0:
        raise ValueError("Conductor tensions must be positive")
    
    # Calculate sags using parabolic approximation
    # Sag = (Weight × Span²) / (8 × Tension)
    numerator = conductor.weight * weight_span ** 2
    
    initial_sag = numerator / (8 * initial_tension)
    final_sag = numerator / (8 * final_tension)
    
    # Validation: Final sag should be greater than initial sag
    if final_sag <= initial_sag:
        raise ValueError(
            f"Invalid sag calculation: Final sag ({final_sag:.2f} ft) should be "
            f"greater than initial sag ({initial_sag:.2f} ft)"
        )
    
    return initial_tension, final_tension, initial_sag, final_sag


def calculate_wind_pressure(
    zh: float,
    vi: float,
    wind_span: float,
    exposure_category: str
) -> Tuple[float, float, float, float, float, float]:
    """
    Step 2: Calculate wind pressure under ice conditions.
    
    Main formula: F = Q × Kz × Kzt × VI² × Gw × Cf
    
    Sub-calculations:
    1. Kz = 2.01 × (Zh / Zg)^(2/α)  [Velocity pressure exposure coefficient]
    2. E = 4.9 × √[k × (33/Zh)^(1/αFM)]  [Turbulence intensity]
    3. Bw = 1 / [1 + (0.8 × S / LS)]  [Background response factor]
    4. Kv = (E / Bw)²  [Gust effect factor component]
    5. Gw = [1 + 2.7 × E] / √(Bw × Kv²)  [Gust effect factor]
    
    Args:
        zh: Average conductor height in ft
        vi: Basic wind speed in mph
        wind_span: Wind span (S) in ft
        exposure_category: Exposure category ("B", "C", or "D")
        
    Returns:
        Tuple of (Kz, E, Bw, Kv, Gw, F) where F is wind pressure in psf
        
    Raises:
        ValueError: If any intermediate calculation is invalid
    """
    # Get exposure constants for the specified category
    exp_const = get_exposure_constants(exposure_category)
    
    # Step 2.1: Velocity Pressure Exposure Coefficient (Kz)
    kz = 2.01 * (zh / exp_const.Zg) ** (2.0 / exp_const.alpha)
    
    if kz <= 0:
        raise ValueError(f"Invalid Kz calculation: {kz}")
    
    # Step 2.2: Turbulence Intensity (E)
    turbulence_intensity = 4.9 * math.sqrt(exp_const.k) * ((33.0 / zh) ** (1.0 / exp_const.alpha_FM))
 # sqrt for k only 
    
    if turbulence_intensity <= 0:
        raise ValueError(f"Invalid turbulence intensity: {turbulence_intensity}")
    
    # Step 2.3: Background Response Factor (Bw)
    background_response = 1.0 / (1.0 + (0.8 * wind_span / exp_const.LS))
    
    if background_response <= 0 or background_response > 1:
        raise ValueError(f"Invalid background response factor: {background_response}")
    
    # Step 2.4: Kv is a CONSTANT = 1.43 (NOT calculated)
    gust_factor_component = 1.43  # Kv constant from formulas.md
    
    # Step 2.5: Gust Effect Factor (Gw)
    # Formula: Gw = (1 + 2.7 × E × √(Bw)) / Kv²
    # Where Kv = 1.43 (constant)
    numerator = 1.0 + 2.7 * turbulence_intensity * math.sqrt(background_response)
    denominator = gust_factor_component ** 2  # Kv² = 1.43² = 2.0449
    gust_effect_factor = numerator / denominator
    
    if gust_effect_factor <= 0:
        raise ValueError(f"Invalid gust effect factor: {gust_effect_factor}")
    
    # Main formula: Wind Pressure (F)
    wind_pressure = (
        WindConstants.Q *
        kz *
        WindConstants.Kzt *
        vi ** 2 *
        gust_effect_factor *
        WindConstants.Cf
    )
    
    if wind_pressure < 0:
        raise ValueError(f"Invalid wind pressure: {wind_pressure}")
    
    return (
        kz,
        turbulence_intensity,
        background_response,
        gust_factor_component,
        gust_effect_factor,
        wind_pressure
    )


def calculate_ice_load(
    diameter: float,
    ice_thickness: float,
    zh: float
) -> Tuple[float, float]:
    """
    Step 3: Calculate ice load on conductor.
    
    Adjusted ice thickness: Iz = I × (Zh/33)^0.10
    Ice load: Wi = 1.24 × (d + Iz) × Iz
    
    Args:
        diameter: Conductor diameter (d) in inches
        ice_thickness: Nominal ice thickness (I) in inches
        zh: Average conductor height in ft
        
    Returns:
        Tuple of (adjusted_ice_thickness, ice_load) where ice_load is in lbs/ft
    """
    # If no ice, return zeros
    if ice_thickness <= 0:
        return 0.0, 0.0
    
    # Calculate height-adjusted ice thickness
    adjusted_ice_thickness = ice_thickness * (zh / 33.0) ** 0.10
    
    # Calculate ice load per foot
    ice_load = IceConstants.ICE_DENSITY * (diameter + adjusted_ice_thickness) * adjusted_ice_thickness
    
    # Validation
    if ice_load < 0:
        raise ValueError(f"Invalid ice load: {ice_load}")
    
    return adjusted_ice_thickness, ice_load


def calculate_wind_load(
    wind_pressure: float,
    diameter: float,
    ice_thickness: float
) -> Tuple[float, float]:
    """
    Step 4: Calculate wind load on conductor.
    
    Diameter with ice: di = d + (2 × I)
    Wind load: Ww = F × (di / 12)
    
    Args:
        wind_pressure: Wind pressure (F) in psf
        diameter: Conductor diameter (d) in inches
        ice_thickness: Ice thickness (I) in inches
        
    Returns:
        Tuple of (diameter_with_ice, wind_load) where wind_load is in lbs/ft
    """
    # Calculate diameter with ice coating
    diameter_with_ice = diameter + (2.0 * ice_thickness)
    
    # Validate
    if diameter_with_ice < diameter:
        raise ValueError("Diameter with ice cannot be less than bare diameter")
    
    # Calculate wind load per foot
    # Convert diameter from inches to feet (divide by 12)
    wind_load = wind_pressure * (diameter_with_ice / 12.0)
    
    if wind_load < 0:
        raise ValueError(f"Invalid wind load: {wind_load}")
    
    return diameter_with_ice, wind_load


def calculate_effective_load(
    conductor_weight: float,
    ice_load: float,
    wind_load: float
) -> float:
    """
    Step 5: Calculate effective load on conductor.
    
    Wt = √[(Wc + Wi)² + Ww²]
    
    This represents the vector sum of vertical loads (conductor + ice)
    and horizontal load (wind).
    
    Args:
        conductor_weight: Conductor weight (Wc) in lbs/ft
        ice_load: Ice load (Wi) in lbs/ft
        wind_load: Wind load (Ww) in lbs/ft
        
    Returns:
        Effective load (Wt) in lbs/ft
    """
    # Calculate vertical component (weight + ice)
    vertical_component = conductor_weight + ice_load
    
    # Calculate effective load using Pythagorean theorem
    effective_load = math.sqrt(vertical_component ** 2 + wind_load ** 2)
    
    # Validation: Effective load should be at least as large as conductor weight
    if effective_load < conductor_weight:
        raise ValueError(
            f"Effective load ({effective_load:.2f}) cannot be less than "
            f"conductor weight ({conductor_weight:.2f})"
        )
    
    return effective_load


def calculate_part1(
    conductor: ConductorData,
    span: SpanData,
    pole: PoleGeometry,
    environment: EnvironmentalData
) -> Part1Output:
    """
    Execute all Part 1 calculations (Steps 1-5).
    
    Args:
        conductor: Conductor specifications
        span: Span configuration
        pole: Pole geometry
        environment: Environmental conditions
        
    Returns:
        Part1Output with all calculated values
        
    Raises:
        ValueError: If any calculation fails validation
    """
    # Get effective spans
    weight_span = span.effective_weight_span
    wind_span = span.effective_wind_span
    
    # Step 1: Initial & Final Sag
    initial_tension, final_tension, initial_sag, final_sag = calculate_initial_final_sag(
        conductor, weight_span
    )
    
    # Step 2: Wind Pressure
    kz, turb_intensity, bg_response, gust_comp, gust_factor, wind_pressure = calculate_wind_pressure(
        pole.avg_conductor_height,
        environment.basic_wind_speed,
        wind_span,
        environment.exposure_category
    )
    
    # Step 3: Ice Load
    adjusted_ice, ice_load = calculate_ice_load(
        conductor.diameter,
        environment.ice_thickness,
        pole.avg_conductor_height
    )
    
    # Step 4: Wind Load
    diameter_with_ice, wind_load = calculate_wind_load(
        wind_pressure,
        conductor.diameter,
        environment.ice_thickness
    )
    
    # Step 5: Effective Load
    effective_load = calculate_effective_load(
        conductor.weight,
        ice_load,
        wind_load
    )
    
    # Return structured output as SimpleNamespace
    return SimpleNamespace(
        # Step 1
        initial_tension=initial_tension,
        final_tension=final_tension,
        initial_sag=initial_sag,
        final_sag=final_sag,
        # Step 2
        kz=kz,
        turbulence_intensity=turb_intensity,
        background_response=bg_response,
        gust_factor_component=gust_comp,
        gust_effect_factor=gust_factor,
        wind_pressure=wind_pressure,
        # Step 3
        adjusted_ice_thickness=adjusted_ice,
        ice_load=ice_load,
        # Step 4
        diameter_with_ice=diameter_with_ice,
        wind_load=wind_load,
        # Step 5
        effective_load=effective_load
    )

