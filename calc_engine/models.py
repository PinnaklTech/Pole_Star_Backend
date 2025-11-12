"""
Pydantic models for input validation and output structuring.
All models follow the specifications from the overhead line calculation flow document.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import date


# ============================================================================
# INPUT MODELS (matching the 6 input pages from the spec)
# ============================================================================

class ProjectInfo(BaseModel):
    """Page 1: Project Information and system parameters."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    project_name: str = Field(..., min_length=1, description="Project name")
    location: str = Field(..., min_length=1, description="Project location")
    engineer_name: str = Field(..., min_length=1, description="Engineer name")
    date: date = Field(..., description="Project date")
    start_location: str = Field(..., min_length=1, description="Start location")
    end_location: str = Field(..., min_length=1, description="End location")
    distance: float = Field(..., gt=0, description="Total distance in miles")
    power_rating: float = Field(..., gt=0, description="Power rating in MW")
    system_voltage: float = Field(..., gt=0, description="System voltage (phase-to-phase) in kV")
    pole_type: str = Field(..., min_length=1, description="Pole type (Wood/Steel/Concrete)")


class ConductorData(BaseModel):
    """Page 2: Conductor specifications."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    specification: str = Field(..., min_length=1, description="Conductor specification")
    weight: float = Field(..., gt=0, description="Weight per unit length (Wc) in lbs/ft")
    diameter: float = Field(..., gt=0, description="Conductor diameter (d) in inches")
    rbs: float = Field(..., gt=0, description="Rated Breaking Strength in lbs")
    
    @property
    def initial_tension(self) -> float:
        """Calculate initial tension (35% of RBS)."""
        return 0.35 * self.rbs
    
    @property
    def final_tension(self) -> float:
        """Calculate final tension (25% of RBS)."""
        return 0.25 * self.rbs
    
    @property
    def design_tension(self) -> float:
        """Calculate design tension (80% of RBS) for deflected sag."""
        return 0.80 * self.rbs


class SpanConfiguration(BaseModel):
    """Page 3: Single span configuration."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    distance_between_poles: float = Field(..., gt=0, description="Distance between poles in ft")
    weight_span: float = Field(..., gt=0, description="Weight span (l) in ft")
    wind_span: float = Field(..., gt=0, description="Wind span (S) in ft")
    line_angle: float = Field(0.0, ge=0, le=180, description="Line angle in degrees")


class SpanData(BaseModel):
    """Page 3: Span configuration (can include multiple spans)."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    spans: List[SpanConfiguration] = Field(..., min_length=1, description="List of span configurations")
    use_average: bool = Field(False, description="Use average span values if multiple spans")
    
    @property
    def average_weight_span(self) -> float:
        """Calculate average weight span."""
        return sum(s.weight_span for s in self.spans) / len(self.spans)
    
    @property
    def average_wind_span(self) -> float:
        """Calculate average wind span."""
        return sum(s.wind_span for s in self.spans) / len(self.spans)
    
    @property
    def effective_weight_span(self) -> float:
        """Get the effective weight span for calculations."""
        return self.average_weight_span if self.use_average else self.spans[0].weight_span
    
    @property
    def effective_wind_span(self) -> float:
        """Get the effective wind span for calculations."""
        return self.average_wind_span if self.use_average else self.spans[0].wind_span
    
    @property
    def effective_line_angle(self) -> float:
        """Get the effective line angle for calculations."""
        if self.use_average:
            return sum(s.line_angle for s in self.spans) / len(self.spans)
        return self.spans[0].line_angle


class PoleGeometry(BaseModel):
    """Page 4: Pole and conductor heights."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    pole_height: float = Field(..., gt=0, description="Pole height in ft")
    attachment_height: float = Field(..., gt=0, description="Conductor attachment height in ft")
    avg_conductor_height: float = Field(..., gt=0, description="Average conductor height (Zh) in ft")
    
    @model_validator(mode='after')
    def validate_heights(self):
        """Validate that attachment height doesn't exceed pole height."""
        if self.attachment_height > self.pole_height:
            raise ValueError("Attachment height cannot exceed pole height")
        if self.avg_conductor_height > self.attachment_height:
            # Warning, not error - this is physically possible but unusual
            pass
        return self


class EnvironmentalData(BaseModel):
    """Page 5: Environmental conditions."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    basic_wind_speed: float = Field(..., gt=0, description="Basic wind speed (VI) in mph")
    exposure_category: Literal["B", "C", "D"] = Field(..., description="Wind exposure category")
    ice_thickness: float = Field(0.0, ge=0, description="Nominal ice thickness (I) in inches")
    min_temperature: Optional[float] = Field(None, description="Minimum temperature in °F")
    max_temperature: Optional[float] = Field(None, description="Maximum temperature in °F")
    
    @model_validator(mode='after')
    def validate_temperatures(self):
        """Validate that max temp > min temp if both provided."""
        if self.min_temperature is not None and self.max_temperature is not None:
            if self.max_temperature <= self.min_temperature:
                raise ValueError("Maximum temperature must be greater than minimum temperature")
        return self


class HardwareComponent(BaseModel):
    """Individual hardware component."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = Field(..., min_length=1, description="Component name")
    weight: float = Field(..., ge=0, description="Component weight in lbs")


class HardwareComponents(BaseModel):
    """Page 6: Hardware components and weights."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    components: List[HardwareComponent] = Field(..., min_length=1, description="List of hardware components")
    
    @property
    def total_weight(self) -> float:
        """Calculate total hardware weight."""
        return sum(c.weight for c in self.components)
    
    @property
    def insulator_weight(self) -> float:
        """
        Get insulator weight. Assumes first component with 'insulator' in name.
        If none found, returns 0 (will trigger validation warning).
        """
        for component in self.components:
            if 'insulator' in component.name.lower():
                return component.weight
        return 0.0


class CalculationInput(BaseModel):
    """Complete input model for the calculation endpoint."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    project_info: ProjectInfo
    conductor_data: ConductorData
    span_data: SpanData
    pole_geometry: PoleGeometry
    environmental_data: EnvironmentalData
    hardware_components: HardwareComponents


# ============================================================================
# OUTPUT MODELS (structured by calculation parts)
# ============================================================================

class Part1Output(BaseModel):
    """Output from Part 1: Sag, Wind & Ice Loads (Steps 1-5)."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Step 1: Initial & Final Sag
    initial_tension: float = Field(..., description="Initial tension (0.35 × RBS) in lbs")
    final_tension: float = Field(..., description="Final tension (0.25 × RBS) in lbs")
    initial_sag: float = Field(..., description="Initial sag (Si) in ft")
    final_sag: float = Field(..., description="Final sag (Sf) in ft")
    
    # Step 2: Wind Pressure (with intermediate values)
    kz: float = Field(..., description="Velocity pressure exposure coefficient")
    turbulence_intensity: float = Field(..., description="Turbulence intensity (E)")
    background_response: float = Field(..., description="Background response factor (Bw)")
    gust_factor_component: float = Field(..., description="Gust effect factor component (Kv)")
    gust_effect_factor: float = Field(..., description="Gust effect factor (Gw)")
    wind_pressure: float = Field(..., description="Wind pressure (F) in psf")
    
    # Step 3: Ice Load
    adjusted_ice_thickness: float = Field(..., description="Height-adjusted ice thickness (Iz) in inches")
    ice_load: float = Field(..., description="Ice load (Wi) in lbs/ft")
    
    # Step 4: Wind Load
    diameter_with_ice: float = Field(..., description="Conductor diameter with ice (di) in inches")
    wind_load: float = Field(..., description="Wind load (Ww) in lbs/ft")
    
    # Step 5: Effective Load
    effective_load: float = Field(..., description="Effective load (Wt) in lbs/ft")


class Part2Output(BaseModel):
    """Output from Part 2: Deflected Sag & Ground Clearance (Steps 6-8)."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Step 6: Deflected Sag
    design_tension: float = Field(..., description="Design tension (0.8 × RBS) in lbs")
    deflected_sag: float = Field(..., description="Deflected sag (Sdef) in ft")
    
    # Step 7: Vertical Sag
    vertical_sag: float = Field(..., description="Vertical sag component (Sver) in ft")
    
    # Step 8: Total Sag & Clearance
    total_sag: float = Field(..., description="Total sag (Sf + Sver) in ft")
    final_clearance: float = Field(..., description="Final clearance from ground in ft")


class Part3Output(BaseModel):
    """Output from Part 3: Pole Loads & NESC Compliance (Steps 9-11)."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Step 9: Vertical Load
    vertical_load: float = Field(..., description="Vertical load on pole in lbs")
    
    # Step 10: Transverse Load
    wind_component: float = Field(..., description="Wind component of transverse load in lbs")
    tension_component: float = Field(..., description="Tension component of transverse load in lbs")
    transverse_load: float = Field(..., description="Total transverse load on pole in lbs")
    
    # Step 11: NESC Clearance Validation
    adjusted_voltage: float = Field(..., description="Adjusted system voltage (1.1 × Vsys) in kV")
    phase_voltage: float = Field(..., description="Phase voltage in kV")
    clearance_adder: float = Field(..., description="Clearance adder in inches")
    minimum_required_clearance: float = Field(..., description="Minimum required clearance per NESC in ft")
    clearance_margin: float = Field(..., description="Clearance margin (actual - required) in ft")
    nesc_compliance: bool = Field(..., description="NESC compliance status (True = PASS, False = FAIL)")
    nesc_status: str = Field(..., description="NESC compliance status text")


class CalculationWarning(BaseModel):
    """Warning or validation message."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    level: Literal["info", "warning", "error"] = Field(..., description="Warning level")
    message: str = Field(..., description="Warning message")
    field: Optional[str] = Field(None, description="Related field name if applicable")


class CalculationOutput(BaseModel):
    """Complete output from the calculation endpoint."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool = Field(..., description="Overall calculation success status")
    part1: Part1Output = Field(..., description="Part 1 results: Sag, Wind & Ice Loads")
    part2: Part2Output = Field(..., description="Part 2 results: Deflected Sag & Clearance")
    part3: Part3Output = Field(..., description="Part 3 results: Pole Loads & NESC Compliance")
    warnings: List[CalculationWarning] = Field(default_factory=list, description="Warnings and validation messages")
    
    @property
    def overall_status(self) -> str:
        """Get overall calculation status."""
        if not self.success:
            return "CALCULATION FAILED"
        if self.part3.nesc_compliance:
            return "PASS - Design meets all requirements"
        else:
            return "FAIL - NESC clearance requirement not met"

