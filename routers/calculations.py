"""
Transmission Line Design Calculation Routes
Uses calc_engine functions directly with SimpleNamespace to avoid Pydantic recursion
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from types import SimpleNamespace

# Import calc_engine calculation functions directly (NOT models)
from calc_engine.part1_calculations import calculate_part1
from calc_engine.part2_calculations import calculate_part2
from calc_engine.part3_calculations import calculate_part3
from calc_engine.constants import (
    EXPOSURE_CATEGORIES, 
    TensionFactors, 
    WindConstants, 
    IceConstants, 
    NESCClearanceConstants,
    ValidationRanges
)

router = APIRouter()


def build_conductor_object(data: Dict[str, Any]) -> SimpleNamespace:
    """Build conductor object from dict."""
    rbs = float(data.get("rbs", 31500))
    return SimpleNamespace(
        specification=data.get("specification", "Unknown"),
        weight=float(data.get("weight", 1.094)),
        diameter=float(data.get("diameter", 1.108)),
        rbs=rbs,
        # Computed properties
        initial_tension=TensionFactors.INITIAL * rbs,
        final_tension=TensionFactors.FINAL * rbs,
        design_tension=TensionFactors.DESIGN * rbs
    )


def build_span_object(data: Dict[str, Any]) -> SimpleNamespace:
    """Build span data object from dict."""
    spans_list = data.get("spans", [{}])
    use_average = data.get("use_average", False) and len(spans_list) > 1
    
    if use_average:
        avg_weight_span = sum(float(s.get("weight_span", 600)) for s in spans_list) / len(spans_list)
        avg_wind_span = sum(float(s.get("wind_span", 600)) for s in spans_list) / len(spans_list)
        avg_line_angle = sum(float(s.get("line_angle", 0)) for s in spans_list) / len(spans_list)
        
        effective_weight = avg_weight_span
        effective_wind = avg_wind_span
        effective_angle = avg_line_angle
    else:
        first_span = spans_list[0] if spans_list else {}
        effective_weight = float(first_span.get("weight_span", 600))
        effective_wind = float(first_span.get("wind_span", 600))
        effective_angle = float(first_span.get("line_angle", 0))
    
    # Build span configurations
    span_configs = [
        SimpleNamespace(
            distance_between_poles=float(s.get("distance_between_poles", 600)),
            weight_span=float(s.get("weight_span", 600)),
            wind_span=float(s.get("wind_span", 600)),
            line_angle=float(s.get("line_angle", 0))
        )
        for s in spans_list
    ]
    
    return SimpleNamespace(
        spans=span_configs,
        use_average=use_average,
        average_weight_span=effective_weight,
        average_wind_span=effective_wind,
        effective_weight_span=effective_weight,
        effective_wind_span=effective_wind,
        effective_line_angle=effective_angle
    )


def build_geometry_object(data: Dict[str, Any]) -> SimpleNamespace:
    """Build pole geometry object from dict."""
    return SimpleNamespace(
        pole_height=float(data.get("pole_height", 65)),
        attachment_height=float(data.get("attachment_height", 60)),
        avg_conductor_height=float(data.get("avg_conductor_height", 50))
    )


def build_environmental_object(data: Dict[str, Any]) -> SimpleNamespace:
    """Build environmental data object from dict."""
    return SimpleNamespace(
        basic_wind_speed=float(data.get("basic_wind_speed", 105)),
        exposure_category=data.get("exposure_category", "C"),
        ice_thickness=float(data.get("ice_thickness", 0.5)),
        min_temperature=data.get("min_temperature"),
        max_temperature=data.get("max_temperature")
    )


def build_hardware_object(data: Dict[str, Any]) -> SimpleNamespace:
    """Build hardware components object from dict."""
    components_list = data.get("components", [])
    
    components = [
        SimpleNamespace(
            name=c.get("name", "Component"),
            weight=float(c.get("weight", 0))
        )
        for c in components_list
    ]
    
    total_weight = sum(float(c.get("weight", 0)) for c in components_list)
    insulator_weight = next(
        (float(c.get("weight", 0)) for c in components_list if 'insulator' in c.get("name", "").lower()),
        0.0
    )
    
    return SimpleNamespace(
        components=components,
        total_weight=total_weight,
        insulator_weight=insulator_weight
    )


def build_project_object(data: Dict[str, Any]) -> SimpleNamespace:
    """Build project info object from dict."""
    return SimpleNamespace(
        project_name=data.get("project_name", ""),
        location=data.get("location", ""),
        engineer_name=data.get("engineer_name", ""),
        date=data.get("date", ""),
        start_location=data.get("start_location", ""),
        end_location=data.get("end_location", ""),
        distance=float(data.get("distance", 1.0)),
        power_rating=float(data.get("power_rating", 100)),
        system_voltage=float(data.get("system_voltage", 115)),
        pole_type=data.get("pole_type", "Steel")
    )


@router.post("/calculate", response_model=None)
async def calculate_design(data: Dict[str, Any]):
    """
    Execute complete transmission line design calculations using calc_engine.
    
    Accepts plain JSON, uses calc_engine functions, returns plain JSON.
    No Pydantic models = No recursion errors!
    """
    try:
        # Log incoming data for debugging (only in debug mode)
        from config import settings
        import logging
        logger = logging.getLogger(__name__)
        
        if settings.debug:
            logger.debug("="*60)
            logger.debug("INCOMING CALCULATION REQUEST")
            logger.debug("="*60)
            logger.debug(f"Conductor: {data.get('conductor_data', {})}")
            logger.debug(f"Span Data: {data.get('span_data', {})}")
            logger.debug(f"Pole Geometry: {data.get('pole_geometry', {})}")
            logger.debug(f"Environmental: {data.get('environmental_data', {})}")
            logger.debug("="*60)
        
        # Extract and build objects
        conductor = build_conductor_object(data.get("conductor_data", {}))
        span_data = build_span_object(data.get("span_data", {}))
        pole_geometry = build_geometry_object(data.get("pole_geometry", {}))
        environmental = build_environmental_object(data.get("environmental_data", {}))
        hardware = build_hardware_object(data.get("hardware_components", {}))
        project_info = build_project_object(data.get("project_info", {}))
        
        # Call calc_engine functions directly
        part1_result = calculate_part1(
            conductor,
            span_data,
            pole_geometry,
            environmental
        )
        
        part2_result = calculate_part2(
            conductor,
            span_data,
            pole_geometry,
            part1_result
        )
        
        part3_result = calculate_part3(
            project_info,
            conductor,
            span_data,
            hardware,
            part1_result,
            part2_result
        )
        
        # Build response
        warnings = []
        if not part3_result.nesc_compliance:
            warnings.append({
                "level": "error",
                "message": part3_result.nesc_status
            })
        
        return {
            "success": True,
            "part1": {
                "initial_tension": round(part1_result.initial_tension, 2),
                "final_tension": round(part1_result.final_tension, 2),
                "initial_sag": round(part1_result.initial_sag, 2),
                "final_sag": round(part1_result.final_sag, 2),
                "kz": round(part1_result.kz, 4),
                "turbulence_intensity": round(part1_result.turbulence_intensity, 4),
                "background_response": round(part1_result.background_response, 4),
                "gust_factor_component": round(part1_result.gust_factor_component, 4),
                "gust_effect_factor": round(part1_result.gust_effect_factor, 4),
                "wind_pressure": round(part1_result.wind_pressure, 4),
                "adjusted_ice_thickness": round(part1_result.adjusted_ice_thickness, 4),
                "ice_load": round(part1_result.ice_load, 4),
                "diameter_with_ice": round(part1_result.diameter_with_ice, 4),
                "wind_load": round(part1_result.wind_load, 4),
                "effective_load": round(part1_result.effective_load, 4)
            },
            "part2": {
                "design_tension": round(part2_result.design_tension, 2),
                "deflected_sag": round(part2_result.deflected_sag, 4),
                "vertical_sag": round(part2_result.vertical_sag, 4),
                "total_sag": round(part2_result.total_sag, 4),
                "final_clearance": round(part2_result.final_clearance, 4)
            },
            "part3": {
                "vertical_load": round(part3_result.vertical_load, 2),
                "wind_component": round(part3_result.wind_component, 2),
                "tension_component": round(part3_result.tension_component, 2),
                "transverse_load": round(part3_result.transverse_load, 2),
                "adjusted_voltage": round(part3_result.adjusted_voltage, 2),
                "phase_voltage": round(part3_result.phase_voltage, 2),
                "clearance_adder": round(part3_result.clearance_adder, 2),
                "minimum_required_clearance": round(part3_result.minimum_required_clearance, 2),
                "clearance_margin": round(part3_result.clearance_margin, 2),
                "nesc_compliance": part3_result.nesc_compliance,
                "nesc_status": part3_result.nesc_status
            },
            "warnings": warnings
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Calculation error",
                "message": str(e)
            }
        )


@router.get("/exposure-categories")
async def get_exposure_categories():
    """Get wind exposure category constants (B, C, D)."""
    return {
        category: {
            "Zg": constants.Zg,
            "alpha": constants.alpha,
            "k": constants.k,
            "alpha_FM": constants.alpha_FM,
            "LS": constants.LS,
            "description": _get_exposure_description(category)
        }
        for category, constants in EXPOSURE_CATEGORIES.items()
    }


@router.get("/constants")
async def get_constants():
    """Get all calculation constants and validation ranges."""
    return {
        "tension_factors": {
            "initial": TensionFactors.INITIAL,
            "final": TensionFactors.FINAL,
            "design": TensionFactors.DESIGN
        },
        "wind_constants": {
            "Q": WindConstants.Q,
            "Kzt": WindConstants.Kzt,
            "Cf": WindConstants.Cf
        },
        "ice_constants": {
            "density": IceConstants.ICE_DENSITY,
            "height_exponent": IceConstants.HEIGHT_EXPONENT
        },
        "nesc_clearance": {
            "overvoltage_factor": NESCClearanceConstants.OVERVOLTAGE_FACTOR,
            "base_clearance": NESCClearanceConstants.BASE_CLEARANCE,
            "voltage_threshold": NESCClearanceConstants.VOLTAGE_THRESHOLD,
            "adder_factor": NESCClearanceConstants.ADDER_FACTOR
        },
        "validation_ranges": {
            "voltage": {
                "min": ValidationRanges.VOLTAGE_MIN,
                "max": ValidationRanges.VOLTAGE_MAX
            },
            "wind_speed": {
                "min": ValidationRanges.WIND_SPEED_MIN,
                "max": ValidationRanges.WIND_SPEED_MAX
            },
            "ice_thickness": {
                "min": ValidationRanges.ICE_THICKNESS_MIN,
                "max": ValidationRanges.ICE_THICKNESS_MAX
            }
        }
    }


@router.get("/health")
async def calculation_health():
    """Health check for calculation service."""
    return {"status": "healthy", "service": "calc_engine"}


def _get_exposure_description(category: str) -> str:
    """Get human-readable description of exposure category."""
    descriptions = {
        "B": "Urban and suburban areas, wooded terrain",
        "C": "Open terrain with scattered obstructions",
        "D": "Flat, unobstructed areas exposed to wind"
    }
    return descriptions.get(category, "Unknown category")
