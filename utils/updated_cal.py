import math

# Roughness (epsilon) in meters
PIPE_MATERIALS = {
    'PVC': 0.0000015,
    'HDPE': 0.00003,
    'LLDPE': 0.00005
}

EMITTER_PRESSURE = {
    'drip': 10,         # meters (1 bar)
    'sprinkler': 20,    # meters (2 bar)
    'pop-up': 30
}

SAFETY_MARGIN = 5  # meters


def friction_loss(Q, D, L, material):
    # Darcy-Weisbach: hf = f*(L/D)*(v²/2g)
    # Estimate friction factor (f) using Swamee-Jain equation
    v = (4 * Q) / (math.pi * D**2)  # m/s
    Re = (v * D) / (1e-6)  # assume kinematic viscosity of water
    e = PIPE_MATERIALS[material.upper()]

    if Re < 4000:
        f = 64 / Re  # Laminar flow
    else:
        f = 0.25 / (math.log10(e / (3.7 * D) + 5.74 / Re**0.9)) ** 2

    hf = f * (L / D) * (v ** 2 / (2 * 9.81))
    return hf, v


def suggest_pipe(Q_m3hr, L, material):
    Q = Q_m3hr / 3600  # m³/s
    diameters = [0.025, 0.032, 0.04, 0.05, 0.063, 0.075, 0.09, 0.11, 0.125]
    for D in diameters:
        hf, v = friction_loss(Q, D, L, material)
        if v <= 2.0 and hf <= 10:  # Friction loss threshold
            return D, hf, v
    return diameters[-1], hf, v  # fallback to max size


def calculate_tdh(elevation, slope, method, hf):
    return elevation + hf + EMITTER_PRESSURE[method] + SAFETY_MARGIN


def calculate_pump_hp(Q_m3hr, TDH):
    Q_lps = Q_m3hr / 3.6  # convert to liters/sec
    η = 0.7  # assume 70% pump efficiency
    power_kW = (9.81 * Q_lps * TDH) / (η * 1000)
    return round(power_kW * 1.341, 2)  # kW to HP

def recommend_zones(area_acres, soil, slope, Q_total, TDH):
    """Return optimal zone count."""
    factors = {'clay': 1.5, 'loam': 1.0, 'sandy': 0.5}
    bf = factors.get(soil, 1)
    sf = 1.0 if slope < 2 else (0.7 if slope <= 8 else 0.4)
    base = 2 if area_acres < 5 else (5 if area_acres <= 50 else 10)
    zones = int(base * bf / sf)-1
    Q_zone = Q_total / zones
    pump_size_per_zone = calculate_pump_hp(Q_zone, TDH)
    if pump_size_per_zone > 10:
        zones = int(zones * (pump_size_per_zone / 10)) + 1
        Q_zone = Q_total/zones
        pump_size_per_zone = calculate_pump_hp(Q_zone, TDH)
    return zones,pump_size_per_zone

def compute_design(data):
    area_acres = data['area']
    elevation = data['elevation']
    slope = data['slope']
    method = data['method']
    demand_mm = data['water_demand']
    material = data['material']
    pipe_length = data['pipe_length']
    soil = data['soil']
    zone = data['Zone']

    area_m2 = area_acres * 4046.86
    depth = demand_mm / 1000
    Q_m3hr = (area_m2 * depth) / 6

    D, hf, v = suggest_pipe(Q_m3hr, pipe_length, material)
    TDH = calculate_tdh(elevation, slope, method, hf)
    
    zones = 1
    
    result = "Sufficient"
    if(zone == "Suggest"):
       zones,hp = recommend_zones(area_acres,soil,slope,Q_m3hr,TDH)
    else:
        zones = int(zone)
        Q_zone = Q_m3hr / zones
        hp = calculate_pump_hp(Q_zone, TDH)
        if(hp>10):
            result = "Not Sufficient"
    Q_zones = Q_m3hr/zones
    Q_zones = Q_zones/3.6


    return {
        'flow_total': round(Q_m3hr/3.6, 2),
        'zones': zones,
        'flow_per_zone': round(Q_zones,2),
        'pipe_diameter': round(D, 3)*1000,
        'friction_loss_m': round(hf, 2),
        'velocity_mps': round(v, 2),
        'TDH_m': round(TDH, 2),
        
        'Verdict' : result,
        'Areao' : round(area_m2,2)
    }