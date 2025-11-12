"""
Input validation and warning generation for transmission line calculations.
Provides validation checks beyond basic Pydantic model validation.
"""

from typing import List
import math

from .constants import ValidationRanges
from .models import (
    CalculationInput,
    CalculationWarning,
    ConductorData,
    PoleGeometry,
    EnvironmentalData,
    HardwareComponents,
    Part1Output,
    Part2Output,
)


def validate_conductor_data(conductor: ConductorData) -> List[CalculationWarning]:
    """
    Validate conductor specifications and tension factors.
    
    Args:
        conductor: Conductor data to validate
        
    Returns:
        List of validation warnings
    """
    warnings = []
    
    # Check that tension factors are within NESC limits
    initial_tension = conductor.initial_tension
    final_tension = conductor.final_tension
    design_tension = conductor.design_tension
    
    if initial_tension > 0.35 * conductor.rbs:
        warnings.append(CalculationWarning(
            level="error",
            message=f"Initial tension ({initial_tension:.0f} lbs) exceeds 35% of RBS - NESC violation",
            field="conductor_data.rbs"
        ))
    
    if final_tension > 0.25 * conductor.rbs:
        warnings.append(CalculationWarning(
            level="error",
            message=f"Final tension ({final_tension:.0f} lbs) exceeds 25% of RBS - NESC violation",
            field="conductor_data.rbs"
        ))
    
    if design_tension > 0.80 * conductor.rbs:
        warnings.append(CalculationWarning(
            level="error",
            message=f"Design tension ({design_tension:.0f} lbs) exceeds 80% of RBS - NESC violation",
            field="conductor_data.rbs"
        ))
    
    # Check for unrealistic values
    if conductor.weight > 10.0:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Conductor weight ({conductor.weight:.2f} lbs/ft) seems high - verify specification",
            field="conductor_data.weight"
        ))
    
    if conductor.diameter > 5.0:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Conductor diameter ({conductor.diameter:.2f} in) seems high - verify specification",
            field="conductor_data.diameter"
        ))
    
    return warnings


def validate_pole_geometry(pole: PoleGeometry, initial_sag: float = None) -> List[CalculationWarning]:
    """
    Validate pole geometry and conductor heights.
    
    Args:
        pole: Pole geometry data to validate
        initial_sag: Initial sag value if available for cross-checking
        
    Returns:
        List of validation warnings
    """
    warnings = []
    
    # Check if average conductor height exceeds attachment height
    if pole.avg_conductor_height > pole.attachment_height:
        warnings.append(CalculationWarning(
            level="warning",
            message=(
                f"Average conductor height ({pole.avg_conductor_height:.2f} ft) exceeds "
                f"attachment height ({pole.attachment_height:.2f} ft) - unusual configuration"
            ),
            field="pole_geometry.avg_conductor_height"
        ))
    
    # If initial sag is provided, check expected average conductor height
    if initial_sag is not None:
        expected_zh = pole.attachment_height - initial_sag
        deviation = abs(pole.avg_conductor_height - expected_zh)
        
        if deviation > 5.0:  # More than 5 ft deviation
            warnings.append(CalculationWarning(
                level="warning",
                message=(
                    f"Average conductor height ({pole.avg_conductor_height:.2f} ft) differs significantly "
                    f"from expected value ({expected_zh:.2f} ft = attachment height - initial sag)"
                ),
                field="pole_geometry.avg_conductor_height"
            ))
    
    # Check for unrealistic pole heights
    if pole.pole_height > 200:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Pole height ({pole.pole_height:.2f} ft) is unusually high - verify specification",
            field="pole_geometry.pole_height"
        ))
    
    return warnings


def validate_environmental_data(environment: EnvironmentalData) -> List[CalculationWarning]:
    """
    Validate environmental conditions.
    
    Args:
        environment: Environmental data to validate
        
    Returns:
        List of validation warnings
    """
    warnings = []
    
    # Check wind speed ranges
    if environment.basic_wind_speed < ValidationRanges.WIND_SPEED_TYPICAL_MIN:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Wind speed ({environment.basic_wind_speed:.1f} mph) is below typical range",
            field="environmental_data.basic_wind_speed"
        ))
    
    if environment.basic_wind_speed > ValidationRanges.WIND_SPEED_TYPICAL_MAX:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Wind speed ({environment.basic_wind_speed:.1f} mph) is above typical range - verify local conditions",
            field="environmental_data.basic_wind_speed"
        ))
    
    # Check ice thickness
    if environment.ice_thickness > ValidationRanges.ICE_THICKNESS_TYPICAL_MAX:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Ice thickness ({environment.ice_thickness:.2f} in) is above typical range - verify local conditions",
            field="environmental_data.ice_thickness"
        ))
    
    return warnings


def validate_hardware_components(hardware: HardwareComponents) -> List[CalculationWarning]:
    """
    Validate hardware components.
    
    Args:
        hardware: Hardware components to validate
        
    Returns:
        List of validation warnings
    """
    warnings = []
    
    # Check if insulator weight is included
    if hardware.insulator_weight <= 0:
        warnings.append(CalculationWarning(
            level="warning",
            message="No insulator component found - ensure insulator weight is included",
            field="hardware_components"
        ))
    
    # Check total weight
    total_weight = hardware.total_weight
    if total_weight > 1000:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Total hardware weight ({total_weight:.1f} lbs) is unusually high - verify components",
            field="hardware_components"
        ))
    
    return warnings


def validate_span_configuration(span_data, weight_span: float, wind_span: float) -> List[CalculationWarning]:
    """
    Validate span configuration.
    
    Args:
        span_data: Span configuration data
        weight_span: Effective weight span
        wind_span: Effective wind span
        
    Returns:
        List of validation warnings
    """
    warnings = []
    
    # Check span ranges
    if weight_span < ValidationRanges.SPAN_MIN or weight_span > ValidationRanges.SPAN_MAX:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Weight span ({weight_span:.0f} ft) is outside typical range",
            field="span_data.weight_span"
        ))
    
    if wind_span < ValidationRanges.SPAN_MIN or wind_span > ValidationRanges.SPAN_MAX:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Wind span ({wind_span:.0f} ft) is outside typical range",
            field="span_data.wind_span"
        ))
    
    # Check for very long spans
    if weight_span > 2000:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Weight span ({weight_span:.0f} ft) is very long - verify structural capacity",
            field="span_data.weight_span"
        ))
    
    return warnings


def validate_calculation_results(
    part1: Part1Output,
    part2: Part2Output,
    weight_span: float
) -> List[CalculationWarning]:
    """
    Validate calculation results for physical consistency.
    
    Args:
        part1: Part 1 calculation output
        part2: Part 2 calculation output
        weight_span: Weight span in ft
        
    Returns:
        List of validation warnings
    """
    warnings = []
    
    # Check sag relationships
    if part1.final_sag <= part1.initial_sag:
        warnings.append(CalculationWarning(
            level="error",
            message=f"Final sag ({part1.final_sag:.2f} ft) should be greater than initial sag ({part1.initial_sag:.2f} ft)",
            field="calculation"
        ))
    
    if part2.total_sag < part1.final_sag:
        warnings.append(CalculationWarning(
            level="error",
            message=f"Total sag ({part2.total_sag:.2f} ft) should be greater than final sag ({part1.final_sag:.2f} ft)",
            field="calculation"
        ))
    
    # Check sag to span ratio
    sag_ratio = part2.total_sag / weight_span
    if sag_ratio > ValidationRanges.SAG_TO_SPAN_RATIO_MAX:
        warnings.append(CalculationWarning(
            level="error",
            message=f"Sag to span ratio ({sag_ratio:.3f}) exceeds maximum allowed ({ValidationRanges.SAG_TO_SPAN_RATIO_MAX})",
            field="calculation"
        ))
    
    # Check effective load
    if part1.effective_load < part1.ice_load + part1.wind_load:
        warnings.append(CalculationWarning(
            level="warning",
            message="Effective load calculation may be incorrect",
            field="calculation"
        ))
    
    # Check clearance
    if part2.final_clearance < 10:
        warnings.append(CalculationWarning(
            level="warning",
            message=f"Final clearance ({part2.final_clearance:.2f} ft) is very low - review design",
            field="calculation"
        ))
    
    # Check vertical sag component
    if part2.vertical_sag > part2.deflected_sag:
        warnings.append(CalculationWarning(
            level="error",
            message=f"Vertical sag ({part2.vertical_sag:.2f} ft) cannot exceed deflected sag ({part2.deflected_sag:.2f} ft)",
            field="calculation"
        ))
    
    return warnings


def validate_all_inputs(calc_input: CalculationInput) -> List[CalculationWarning]:
    """
    Perform comprehensive validation of all input data.
    
    Args:
        calc_input: Complete calculation input
        
    Returns:
        List of all validation warnings
    """
    warnings = []
    
    # Validate each section
    warnings.extend(validate_conductor_data(calc_input.conductor_data))
    warnings.extend(validate_pole_geometry(calc_input.pole_geometry))
    warnings.extend(validate_environmental_data(calc_input.environmental_data))
    warnings.extend(validate_hardware_components(calc_input.hardware_components))
    warnings.extend(validate_span_configuration(
        calc_input.span_data,
        calc_input.span_data.effective_weight_span,
        calc_input.span_data.effective_wind_span
    ))
    
    return warnings

