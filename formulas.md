Initial Tension = 0.35 × RBS
```
where RBS = Rated Breaking Strength of Conductor

### 2. Initial Sag
```
S = (Wc × l²) / (8 × T)
```
where:
- S (ft) = Sag
- l (ft) = Distance between two poles or weight span
- Wc (lbs/ft) = Conductor weight
- T (lbs) = Initial Tension

### 3. Final Tension
```
Final Tension = 0.25 × RBS
```

### 4. Final Sag
Use the same formula as initial sag, replacing initial tension with final tension:
```
S = (Wc × l²) / (8 × T)
```

## Wind Pressure on Conductor Under Ice

### Basic Formula
```
F = Q × Kz × Kzt × (VI)² × Gw × Cf
```

### Component Calculations

**Q (constant):**
```
Q = 0.00256
```

**Kz (velocity pressure exposure coefficient):**
```
Kz = 2.01 × (Zh/Zg)^(2/α)
```
where:
- Zh (ft) = Average Conductor Height
- Zg (ft) = 900 ft (Gradient height for exposure category C)
- α = 9.5 (Power law exponent for exposure category C)

**Kzt (topographic factor):**
```
Kzt = 1 (for plain terrain)
```

**VI:**
```
VI (mph) = Wind Speed from ASCE Hazard Tool
```

**Gw (gust effect factor):**
```
Gw = (1 + 2.7E√(Bw)) / Kv²
```

where:
```
E = 4.9 × √[k × (33/Zh)^(1/αFM)]
```
```
Bw = 1 / (1 + 0.8S/LS)
```
```
Gw × Kv = 1.43
```

Constants:
- k = 0.005 (Power law exponent for exposure category C)
- αFM = 7 (Surface drag coefficient for exposure category C)
- S (ft) = Wind span
- LS (ft) = 200 ft (Turbulence Scale: 220 ft for exposure category C)

**Cf (force coefficient):**
```
Cf = 1 (for tubular steel pole)
```

## Ice Load
```
Wi = 1.24 × (d + Iz) × Iz
```
where:
- Wi (lbs/ft) = Ice Load
- d (in) = Conductor diameter
- Iz (in) = Design thickness of Ice
- I (in) = Nominal ice thickness (from ASCE Hazard tool)
- Zh (ft) = Average wire/conductor height

**Design Ice Thickness:**
```
Iz = I × (Zh/33)^0.10
```

## Wind Load
```
Ww = F × A
```
where:
- Ww (lbs/ft) = Wind Load
- F (psf) = Wind pressure under Ice
- A = di × 1

**Diameter with Ice:**
```
di = (2 × I) + d
```
where:
- di (in) = Diameter with ice
- I (in) = Thickness of ice
- d (in) = Bare diameter of conductor

## Effective Load
```
Wt = √[(Wc + Wi)² + Ww²]
```
where:
- Wt (lbs/ft) = Effective Load
- Wc (lbs/ft) = Conductor weight
- Wi (lbs/ft) = Ice Load
- Ww (lbs/ft) = Wind Load

## Sag Calculations

### Deflected Sag
```
Sdef = (Wt × l²) / (8 × T)
```
where:
- Sdef (ft) = Deflected sag under combined effect of wind and ice
- Wt (lbs/ft) = Effective weight under combined effect of wind and ice
- l (ft) = Distance between two poles
- T (lbs) = 0.8 × RBS (tension at 80% of RBS)

### Vertical Sag
```
Sver = Sdef × [(Wc + Wi) / √[(Wc + Wi)² + Ww²]]
```
where:
- Sdef (ft) = Deflected sag
- Wc (lbs/ft) = Conductor Weight
- Wi (lbs/ft) = Ice Load
- Ww (lbs/ft) = Wind Load

### Total Sag
```
Total Sag = Final Sag (without external loading) + Vertical Sag
```

## Clearance
```
Final Clearance = Conductor Height - Total Sag
```

## NESC Rule 232-C Calculation (for 115 kV)

**Phase to Ground Voltage:**
```
Voltage (phase to ground) = (115 × 1.1) / √3 = 73 kV
```
where 1.1 is the overvoltage factor

**Clearance Requirement:**
```
Clearance = [(73 - 22) × 0.4] / 12 + 18.5 ≈ 20 ft