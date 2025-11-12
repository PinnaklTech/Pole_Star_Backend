"""
Main calculation orchestrator that coordinates all calculation parts.
"""

from typing import List

from .models import (
    CalculationInput,
    CalculationOutput,
    CalculationWarning,
    Part1Output,
    Part2Output,
    Part3Output,
)
from .part1_calculations import calculate_part1
from .part2_calculations import calculate_part2
from .part3_calculations import calculate_part3
from .validators import (
    validate_all_inputs,
    validate_calculation_results,
    validate_pole_geometry,
)


def calculate_transmission_line(calc_input: CalculationInput) -> CalculationOutput:
    """
    Execute complete transmission line calculations.
    
    This function orchestrates all three parts of the calculation:
    - Part 1: Sag, Wind & Ice Loads (Steps 1-5)
    - Part 2: Deflected Sag & Clearance (Steps 6-8)
    - Part 3: Pole Loads & NESC Compliance (Steps 9-11)
    
    Args:
        calc_input: Complete input data for all calculations
        
    Returns:
        CalculationOutput with results from all three parts and validation warnings
        
    Raises:
        ValueError: If any calculation fails
        Exception: For unexpected calculation errors
    """
    warnings: List[CalculationWarning] = []
    success = True
    
    try:
        # Pre-calculation validation
        input_warnings = validate_all_inputs(calc_input)
        warnings.extend(input_warnings)
        
        # Check for critical errors in inputs
        critical_errors = [w for w in input_warnings if w.level == "error"]
        if critical_errors:
            raise ValueError(
                f"Critical input validation errors: {', '.join(w.message for w in critical_errors)}"
            )
        
        # Part 1: Sag, Wind & Ice Loads
        part1_output = calculate_part1(
            calc_input.conductor_data,
            calc_input.span_data,
            calc_input.pole_geometry,
            calc_input.environmental_data
        )
        
        # Additional pole geometry validation with calculated sag
        pole_warnings = validate_pole_geometry(
            calc_input.pole_geometry,
            part1_output.initial_sag
        )
        warnings.extend(pole_warnings)
        
        # Part 2: Deflected Sag & Clearance
        part2_output = calculate_part2(
            calc_input.conductor_data,
            calc_input.span_data,
            calc_input.pole_geometry,
            part1_output
        )
        
        # Part 3: Pole Loads & NESC Compliance
        part3_output = calculate_part3(
            calc_input.project_info,
            calc_input.conductor_data,
            calc_input.span_data,
            calc_input.hardware_components,
            part1_output,
            part2_output
        )
        
        # Post-calculation validation
        result_warnings = validate_calculation_results(
            part1_output,
            part2_output,
            calc_input.span_data.effective_weight_span
        )
        warnings.extend(result_warnings)
        
        # Add NESC compliance warning if failed
        if not part3_output.nesc_compliance:
            warnings.append(CalculationWarning(
                level="error",
                message=part3_output.nesc_status,
                field="nesc_compliance"
            ))
        
        # Check if any critical calculation errors occurred
        calc_errors = [w for w in result_warnings if w.level == "error"]
        if calc_errors:
            warnings.append(CalculationWarning(
                level="warning",
                message="Calculation completed but contains errors - review results carefully",
                field="calculation"
            ))
        
    except ValueError as e:
        success = False
        warnings.append(CalculationWarning(
            level="error",
            message=f"Calculation error: {str(e)}",
            field="calculation"
        ))
        # Re-raise to be handled by API
        raise
    
    except Exception as e:
        success = False
        warnings.append(CalculationWarning(
            level="error",
            message=f"Unexpected error: {str(e)}",
            field="calculation"
        ))
        # Re-raise to be handled by API
        raise
    
    return CalculationOutput(
        success=success,
        part1=part1_output,
        part2=part2_output,
        part3=part3_output,
        warnings=warnings
    )

