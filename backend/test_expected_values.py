"""
Test to verify calc_engine produces expected results
"""
from types import SimpleNamespace
from calc_engine.part1_calculations import (
    calculate_initial_final_sag,
    calculate_wind_pressure,
    calculate_ice_load,
    calculate_wind_load,
    calculate_effective_load
)

# Expected inputs (based on user's expected results)
# RBS = 31500 lbs (since T_init = 11025 = 0.35 × RBS)
conductor = SimpleNamespace(
    weight=1.0930, # lbs/ft
    diameter=1.1070, # inches
    rbs=31500  # lbs
)

weight_span = 300 #ft
wind_span = 300  # ft
avg_conductor_height = 70# ft (Zh)
basic_wind_speed = 30# mph
exposure_category = "C"
ice_thickness = 0.25 # inches

print("=" * 60)
print("TESTING WITH EXPECTED INPUTS")
print("=" * 60)
print(f"Conductor Weight: {conductor.weight} lbs/ft")
print(f"Conductor Diameter: {conductor.diameter} in")
print(f"RBS: {conductor.rbs} lbs")
print(f"Weight Span: {weight_span} ft")
print(f"Wind Span: {wind_span} ft")
print(f"Conductor Height (Zh): {avg_conductor_height} ft")
print(f"Wind Speed: {basic_wind_speed} mph")
print(f"Exposure Category: {exposure_category}")
print(f"Ice Thickness: {ice_thickness} in")
print()

# Calculate Step 1: Initial & Final Sag
initial_tension, final_tension, initial_sag, final_sag = calculate_initial_final_sag(
    conductor, weight_span
)

print("STEP 1: Initial & Final Sag")
print(f"  Initial Tension: {initial_tension:.0f} lbs (Expected: 11025)")
print(f"  Final Tension: {final_tension:.0f} lbs (Expected: 7875)")
print(f"  Initial Sag: {initial_sag:.3f} ft (Expected: 1.115)")
print(f"  Final Sag: {final_sag:.3f} ft (Expected: 1.561)")
print()

# Calculate Step 2: Wind Pressure
kz, turbulence, background, gust_comp, gust_factor, wind_pressure = calculate_wind_pressure(
    avg_conductor_height, basic_wind_speed, wind_span, exposure_category
)

print("STEP 2: Wind Pressure")
print(f"  Kz: {kz:.3f} (Expected: 1.174)")
print(f"  E (Turbulence): {turbulence:.3f} (Expected: 0.311)")
print(f"  Bw: {background:.3f} (Expected: 0.478)")
print(f"  Gw: {gust_factor:.3f} (Expected: 0.771)")
print(f"  F (Wind Pressure): {wind_pressure:.3f} psf (Expected: 2.086)")
print()

# Calculate Step 3: Ice Load
adjusted_ice, ice_load = calculate_ice_load(
    conductor.diameter, ice_thickness, avg_conductor_height
)

print("STEP 3: Ice Load")
print(f"  Iz (Adjusted Ice): {adjusted_ice:.4f} in (Expected: 0.2695)")
print(f"  Wi (Ice Load): {ice_load:.3f} lb/ft (Expected: 0.460)")
print()

# Calculate Step 4: Wind Load
diameter_with_ice, wind_load = calculate_wind_load(
    wind_pressure, conductor.diameter, ice_thickness
)

print("STEP 4: Wind Load")
print(f"  di (Diameter with Ice): {diameter_with_ice:.3f} in (Expected: 1.607)")
print(f"  Ww (Wind Load): {wind_load:.3f} lb/ft (Expected: 0.279)")
print()

# Calculate Step 5: Effective Load
effective_load = calculate_effective_load(
    conductor.weight, ice_load, wind_load
)

print("STEP 5: Effective Load")
print(f"  Wt (Effective Load): {effective_load:.3f} lb/ft (Expected: 1.578)")
print()

print("=" * 60)
print("COMPARISON SUMMARY")
print("=" * 60)
print("Parameter          | Calculated | Expected  | Match?")
print("-" * 60)
print(f"Initial Tension    | {initial_tension:10.0f} | 11025     | {'✅' if abs(initial_tension - 11025) < 1 else '❌'}")
print(f"Final Tension      | {final_tension:10.0f} | 7875      | {'✅' if abs(final_tension - 7875) < 1 else '❌'}")
print(f"Initial Sag        | {initial_sag:10.3f} | 1.115     | {'✅' if abs(initial_sag - 1.115) < 0.01 else '❌'}")
print(f"Final Sag          | {final_sag:10.3f} | 1.561     | {'✅' if abs(final_sag - 1.561) < 0.01 else '❌'}")
print(f"Kz                 | {kz:10.3f} | 1.174     | {'✅' if abs(kz - 1.174) < 0.01 else '❌'}")
print(f"E (Turbulence)     | {turbulence:10.3f} | 0.311     | {'✅' if abs(turbulence - 0.311) < 0.01 else '❌'}")
print(f"Bw                 | {background:10.3f} | 0.478     | {'✅' if abs(background - 0.478) < 0.01 else '❌'}")
print(f"Gw                 | {gust_factor:10.3f} | 0.771     | {'✅' if abs(gust_factor - 0.771) < 0.01 else '❌'}")
print(f"F (Wind Pressure)  | {wind_pressure:10.3f} | 2.086     | {'✅' if abs(wind_pressure - 2.086) < 0.01 else '❌'}")
print(f"Iz (Adj Ice)       | {adjusted_ice:10.4f} | 0.2695    | {'✅' if abs(adjusted_ice - 0.2695) < 0.001 else '❌'}")
print(f"Wi (Ice Load)      | {ice_load:10.3f} | 0.460     | {'✅' if abs(ice_load - 0.460) < 0.01 else '❌'}")
print(f"di (Diameter+Ice)  | {diameter_with_ice:10.3f} | 1.607     | {'✅' if abs(diameter_with_ice - 1.607) < 0.01 else '❌'}")
print(f"Ww (Wind Load)     | {wind_load:10.3f} | 0.279     | {'✅' if abs(wind_load - 0.279) < 0.01 else '❌'}")
print(f"Wt (Effective)     | {effective_load:10.3f} | 1.578     | {'✅' if abs(effective_load - 1.578) < 0.01 else '❌'}")

