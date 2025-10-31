"""
Part 3: Pole Loads & NESC Compliance Calculations (Steps 9-11)

This module implements:
- Step 9: Vertical Load on Pole
- Step 10: Transverse Load on Pole
- Step 11: NESC Table 232-1 Clearance Validation

All formulas follow NESC standards as specified in the flow document.
"""

from __future__ import annotations
import math
from typing import Tuple, TYPE_CHECKING, Any
from types import SimpleNamespace

from .constants import NESCClearanceConstants, PhysicalConstants

# Only import types for type hints, not at runtime
if TYPE_CHECKING:
    from .models import (
        ConductorData,
        SpanData,
        ProjectInfo,
        HardwareComponents,
        Part1Output,
        Part2Output,
        Part3Output,
    )


def calculate_vertical_load(
    weight_span: float,
    conductor_weight: float,
    ice_load: float,
    insulator_weight: float
) -> float:
    """
    Step 9: Calculate vertical load on pole.
    
    Vertical Load = [Weight Span × (Wc + Wi)] + Insulator Weight
    
    Args:
        weight_span: Weight span (l) in ft
        conductor_weight: Conductor weight (Wc) in lbs/ft
        ice_load: Ice load (Wi) in lbs/ft
        insulator_weight: Insulator weight in lbs
        
    Returns:
        Vertical load in lbs
        
    Raises:
        ValueError: If load is negative or unrealistic
    """
    # Calculate conductor and ice load component
    conductor_load = weight_span * (conductor_weight + ice_load)
    
    # Add insulator and hardware weight
    vertical_load = conductor_load + insulator_weight
    
    # Validation
    if vertical_load <= 0:
        raise ValueError("Vertical load must be positive")
    
    return vertical_load


def calculate_transverse_load(
    wind_pressure: float,
    diameter_with_ice: float,
    wind_span: float,
    initial_tension: float,
    line_angle_degrees: float
) -> Tuple[float, float, float]:
    """
    Step 10: Calculate transverse load on pole.
    
    Transverse Load = Wind Component + Tension Component
    
    where:
    - Wind Component = F × (di/12) × S
    - Tension Component = 2 × T × sin(θ/2)
    
    Args:
        wind_pressure: Wind pressure (F) in psf
        diameter_with_ice: Conductor diameter with ice (di) in inches
        wind_span: Wind span (S) in ft
        initial_tension: Initial tension (T) in lbs
        line_angle_degrees: Line angle (θ) in degrees
        
    Returns:
        Tuple of (wind_component, tension_component, total_transverse_load)
        
    Raises:
        ValueError: If load components are negative
    """
    # Calculate wind component
    # F × (di/12) × S  [convert diameter from inches to feet]
    wind_component = wind_pressure * (diameter_with_ice / 12.0) * wind_span
    
    if wind_component < 0:
        raise ValueError("Wind component cannot be negative")
    
    # Calculate tension component from line angle
    # 2 × T × sin(θ/2)
    angle_radians = math.radians(line_angle_degrees)
    tension_component = 2.0 * initial_tension * math.sin(angle_radians / 2.0)
    
    if tension_component < 0:
        raise ValueError("Tension component cannot be negative")
    
    # Calculate total transverse load
    transverse_load = wind_component + tension_component
    
    return wind_component, tension_component, transverse_load


def calculate_nesc_clearance_compliance(
    system_voltage_kv: float,
    final_clearance: float
) -> Tuple[float, float, float, float, float, bool, str]:
    """
    Step 11: Validate clearance against NESC Table 232-1 requirements.
    
    Calculation sequence:
    1. Adjusted Voltage = System Voltage × 1.1
    2. Phase Voltage = Adjusted Voltage / √3
    3. Clearance Adder = (Phase Voltage - 22) × 0.4 inches
    4. Minimum Required Clearance = (Clearance Adder / 12) + 18.5 ft
    5. Clearance Margin = Final Clearance - Minimum Required Clearance
    6. Compliance = PASS if Clearance Margin ≥ 0, else FAIL
    
    Reference: NESC Rule 232-C, Table 232-1, Row 2, Column 5
    
    Args:
        system_voltage_kv: System voltage (phase-to-phase) in kV
        final_clearance: Final clearance from ground in ft
        
    Returns:
        Tuple of (adjusted_voltage, phase_voltage, clearance_adder, 
                  min_required_clearance, clearance_margin, compliance_status, status_text)
        
    Raises:
        ValueError: If voltage is invalid
    """
    # Validate system voltage
    if system_voltage_kv <= 0:
        raise ValueError("System voltage must be positive")
    
    # Step 11.1: Adjust for overvoltage (10% margin)
    adjusted_voltage = system_voltage_kv * NESCClearanceConstants.OVERVOLTAGE_FACTOR
    
    # Step 11.2: Convert to phase voltage (line-to-ground)
    phase_voltage = adjusted_voltage / PhysicalConstants.SQRT_3
    
    # Step 11.3: Calculate clearance adder
    # Adder = (Phase Voltage - 22 kV) × 0.4 inches per kV
    clearance_adder = (phase_voltage - NESCClearanceConstants.VOLTAGE_THRESHOLD) * \
                      NESCClearanceConstants.ADDER_FACTOR
    
    # Clearance adder cannot be negative
    if clearance_adder < 0:
        clearance_adder = 0.0
    
    # Step 11.4: Calculate minimum required clearance
    # Base clearance + adder (converted from inches to feet)
    min_required_clearance = (clearance_adder / 12.0) + NESCClearanceConstants.BASE_CLEARANCE
    
    # Step 11.5: Calculate clearance margin
    clearance_margin = final_clearance - min_required_clearance
    
    # Step 11.6: Determine compliance status
    nesc_compliance = clearance_margin >= 0
    
    if nesc_compliance:
        status_text = f"PASS ✓ - Meets NESC Table 232-1 requirements (Margin: {clearance_margin:.2f} ft)"
    else:
        status_text = f"FAIL ✗ - Does not meet NESC requirements (Shortage: {abs(clearance_margin):.2f} ft)"
    
    return (
        adjusted_voltage,
        phase_voltage,
        clearance_adder,
        min_required_clearance,
        clearance_margin,
        nesc_compliance,
        status_text
    )


def calculate_part3(
    project_info: ProjectInfo,
    conductor: ConductorData,
    span: SpanData,
    hardware: HardwareComponents,
    part1_output: Part1Output,
    part2_output: Part2Output
) -> Part3Output:
    """
    Execute all Part 3 calculations (Steps 9-11).
    
    Args:
        project_info: Project information including system voltage
        conductor: Conductor specifications
        span: Span configuration
        hardware: Hardware components including insulator weight
        part1_output: Results from Part 1 calculations
        part2_output: Results from Part 2 calculations
        
    Returns:
        Part3Output with all calculated values and NESC compliance status
        
    Raises:
        ValueError: If any calculation fails validation
    """
    # Get effective spans
    weight_span = span.effective_weight_span
    wind_span = span.effective_wind_span
    line_angle = span.effective_line_angle
    
    # Step 9: Vertical Load
    vertical_load = calculate_vertical_load(
        weight_span,
        conductor.weight,
        part1_output.ice_load,
        hardware.insulator_weight
    )
    
    # Step 10: Transverse Load
    wind_comp, tension_comp, transverse_load = calculate_transverse_load(
        part1_output.wind_pressure,
        part1_output.diameter_with_ice,
        wind_span,
        part1_output.initial_tension,
        line_angle
    )
    
    # Step 11: NESC Clearance Compliance
    (adj_voltage, phase_voltage, clearance_adder, min_clearance,
     clearance_margin, nesc_compliance, status_text) = calculate_nesc_clearance_compliance(
        project_info.system_voltage,
        part2_output.final_clearance
    )
    
    # Return structured output
    # Return structured output as SimpleNamespace
    return SimpleNamespace(
        # Step 9
        vertical_load=vertical_load,
        # Step 10
        wind_component=wind_comp,
        tension_component=tension_comp,
        transverse_load=transverse_load,
        # Step 11
        adjusted_voltage=adj_voltage,
        phase_voltage=phase_voltage,
        clearance_adder=clearance_adder,
        minimum_required_clearance=min_clearance,
        clearance_margin=clearance_margin,
        nesc_compliance=nesc_compliance,
        nesc_status=status_text
    )

