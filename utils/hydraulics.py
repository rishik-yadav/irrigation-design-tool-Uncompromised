import math

PUMP_DB = [
    {'model': 'Pump-A', 'flow': 5, 'head': 50},
    {'model': 'Pump-B', 'flow': 10, 'head': 60},
    {'model': 'Pump-C', 'flow': 20, 'head': 80},
]


def size_pipe(Q, v_max=2.0):
    """Pipe diameter (m) for Q (m³/hr) at max vel v_max (m/s)."""
    Q_m3s = Q / 3600
    return math.sqrt(4 * Q_m3s / (math.pi * v_max))


def calc_TDH(elevation, slope_percent, diameter):
    """Total head = elevation + Darcy-Weisbach friction."""
    elevation_head = elevation
    L = 100  # m main length
    velocity = 2.0
    f = 0.02
    hf = f * (L / diameter) * (velocity ** 2 / (2 * 9.81))
    return elevation_head + hf


def select_pump(Q, TDH):
    """Choose smallest pump meeting Q & TDH."""
    for pump in PUMP_DB:
        if pump['flow'] >= Q and pump['head'] >= TDH:
            return pump
    best = max(PUMP_DB, key=lambda p: p['flow'])
    return {**best, 'note': 'Consider multiple pumps or more zones.'}


def recommend_zones(area_acres, soil, slope, demand_mm, Q_total, pump_flow):
    """Return optimal zone count."""
    factors = {'clay': 1.5, 'loam': 1.0, 'sandy': 0.5}
    bf = factors.get(soil, 1)
    sf = 1.0 if slope < 2 else (0.7 if slope <= 8 else 0.4)
    base = 2 if area_acres < 5 else (5 if area_acres <= 50 else 10)
    zones = int(base * bf / sf)
    Q_zone = Q_total / zones
    if Q_zone > pump_flow:
        zones = int(zones * (Q_zone / pump_flow)) + 1
    return zones