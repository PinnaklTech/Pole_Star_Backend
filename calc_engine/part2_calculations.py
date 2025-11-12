"""
Part 2: Deflected Sag & Ground Clearance Calculations (Steps 6-8)

This module implements:
- Step 6: Deflected Sag under combined loads
- Step 7: Vertical Sag component
- Step 8: Total Sag and Final Clearance from ground

All formulas follow NESC standards as specified in the flow document.
"""

from __future__ import annotations
import math
from typing import Tuple, TYPE_CHECKING, Any
from types import SimpleNamespace

from .constants import TensionFactors, ValidationRanges

# Only import types for type hints, not at runtime
if TYPE_CHECKING:
    from .models import (
        ConductorData,
        SpanData,
        PoleGeometry,
        Part1Output,
        Part2Output,
    )


def calculate_deflected_sag(
    effective_load: float,
    weight_span: float,
    rbs: float
) -> Tuple[float, float]:
    """
    Step 6: Calculate deflected sag under combined wind and ice loads.
    
    Design Tension: T = 0.8 × RBS (ALWAYS per NESC, NOT user input)
    Deflected Sag: Sdef = (Wt × l²) / (8 × T)
    
    CRITICAL NOTE: Design tension is ALWAYS 80% of RBS per NESC requirements.
    This is NOT a user input and must be auto-calculated.
    
    Args:
        effective_load: Effective load (Wt) in lbs/ft from Part 1
        weight_span: Weight span (l) in ft
        rbs: Rated Breaking Strength in lbs
        
    Returns:
        Tuple of (design_tension, deflected_sag)
        
    Raises:
        ValueError: If design tension or sag calculations are invalid
    """
    # Calculate design tension (ALWAYS 80% of RBS per NESC)
    design_tension = TensionFactors.DESIGN * rbs
    
    # Validate design tension
    if design_tension <= 0:
        raise ValueError("Design tension must be positive")
    if design_tension >= rbs:
        raise ValueError(
            f"Design tension ({design_tension:.0f} lbs) must be less than RBS ({rbs:.0f} lbs)"
        )
    
    # Calculate deflected sag
    deflected_sag = (effective_load * weight_span ** 2) / (8.0 * design_tension)
    
    # Validation: Sag should not exceed half the span
    max_allowed_sag = weight_span * ValidationRanges.SAG_TO_SPAN_RATIO_MAX
    if deflected_sag > max_allowed_sag:
        raise ValueError(
            f"Deflected sag ({deflected_sag:.2f} ft) exceeds maximum allowed "
            f"({max_allowed_sag:.2f} ft = {ValidationRanges.SAG_TO_SPAN_RATIO_MAX*100}% of span)"
        )
    
    return design_tension, deflected_sag


def calculate_vertical_sag(
    deflected_sag: float,
    conductor_weight: float,
    ice_load: float,
    wind_load: float
) -> float:
    """
    Step 7: Calculate vertical component of sag.
    
    Sver = Sdef × [(Wc + Wi) / √((Wc + Wi)² + Ww²)]
    
    This extracts the vertical component from the total deflected sag.
    
    Args:
        deflected_sag: Deflected sag (Sdef) in ft from Step 6
        conductor_weight: Conductor weight (Wc) in lbs/ft
        ice_load: Ice load (Wi) in lbs/ft
        wind_load: Wind load (Ww) in lbs/ft
        
    Returns:
        Vertical sag (Sver) in ft
        
    Raises:
        ValueError: If vertical sag exceeds deflected sag
    """
    # Calculate vertical component (weight + ice)
    vertical_component = conductor_weight + ice_load
    
    # Calculate total load magnitude
    total_load_magnitude = math.sqrt(vertical_component ** 2 + wind_load ** 2)
    
    # Avoid division by zero
    if total_load_magnitude <= 0:
        raise ValueError("Total load magnitude must be positive")
    
    # Calculate vertical sag component
    vertical_sag = deflected_sag * (vertical_component / total_load_magnitude)
    
    # Validation: Vertical sag should not exceed deflected sag
    if vertical_sag > deflected_sag:
        raise ValueError(
            f"Vertical sag ({vertical_sag:.2f} ft) cannot exceed "
            f"deflected sag ({deflected_sag:.2f} ft)"
        )
    
    return vertical_sag


def calculate_total_sag_and_clearance(
    final_sag_no_load: float,
    vertical_sag: float,
    avg_conductor_height: float
) -> Tuple[float, float]:
    """
    Step 8: Calculate total sag and final clearance from ground.
    
    Total Sag = Sf + Sver
    Final Clearance = Zh - Total Sag
    
    CRITICAL NOTE: Total Sag does NOT include Initial Sag (Si).
    Only Final Sag (Sf) and Vertical Sag (Sver) are summed.
    
    Args:
        final_sag_no_load: Final sag without external load (Sf) from Step 1
        vertical_sag: Vertical sag component (Sver) from Step 7
        avg_conductor_height: Average conductor height (Zh) in ft
        
    Returns:
        Tuple of (total_sag, final_clearance)
        
    Raises:
        ValueError: If clearance is negative or unrealistic
    """
    # Calculate total sag (Sf + Sver only, NOT Si)
    total_sag = final_sag_no_load + vertical_sag
    
    # Validation: Total sag should be greater than final sag alone
    if total_sag < final_sag_no_load:
        raise ValueError(
            f"Total sag ({total_sag:.2f} ft) should be greater than or equal to "
            f"final sag without load ({final_sag_no_load:.2f} ft)"
        )
    
    # Calculate final clearance from ground
    final_clearance = avg_conductor_height - total_sag
    
    # Validation: Clearance must be positive
    if final_clearance < 0:
        raise ValueError(
            f"Negative clearance calculated ({final_clearance:.2f} ft). "
            f"Conductor height ({avg_conductor_height:.2f} ft) is insufficient "
            f"for total sag ({total_sag:.2f} ft)"
        )
    
    return total_sag, final_clearance


def calculate_part2(
    conductor: ConductorData,
    span: SpanData,
    pole: PoleGeometry,
    part1_output: Part1Output
) -> Part2Output:
    """
    Execute all Part 2 calculations (Steps 6-8).
    
    Args:
        conductor: Conductor specifications
        span: Span configuration
        pole: Pole geometry
        part1_output: Results from Part 1 calculations
        
    Returns:
        Part2Output with all calculated values
        
    Raises:
        ValueError: If any calculation fails validation
    """
    # Get effective weight span
    weight_span = span.effective_weight_span
    
    # Step 6: Deflected Sag
    design_tension, deflected_sag = calculate_deflected_sag(
        part1_output.effective_load,
        weight_span,
        conductor.rbs
    )
    
    # Step 7: Vertical Sag
    vertical_sag = calculate_vertical_sag(
        deflected_sag,
        conductor.weight,
        part1_output.ice_load,
        part1_output.wind_load
    )
    
    # Step 8: Total Sag & Clearance
    total_sag, final_clearance = calculate_total_sag_and_clearance(
        part1_output.final_sag,
        vertical_sag,
        pole.avg_conductor_height
    )
    
    # Return structured output as SimpleNamespace
    return SimpleNamespace(
        design_tension=design_tension,
        deflected_sag=deflected_sag,
        vertical_sag=vertical_sag,
        total_sag=total_sag,
        final_clearance=final_clearance
    )

