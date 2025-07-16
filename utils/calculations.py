import math
import requests
# Removed shapely dependency; using manual area calculation
from .hydraulics import size_pipe, calc_TDH, select_pump, recommend_zones

M2_TO_ACRES = 1 / 4046.86
ELEVATION_API_URL = 'https://api.open-elevation.com/api/v1/lookup'


def _latlngs_to_xy(coords):
    """Convert lat/lng list to Cartesian meters using equirectangular projection."""
    # Reference latitude for projection
    lat_ref = math.radians(coords[0][0])
    xy = []
    for lat, lng in coords:
        x = math.radians(lng) * 6371000 * math.cos(lat_ref)
        y = math.radians(lat) * 6371000
        xy.append((x, y))
    return xy


def calculate_area(coords):
    """Compute polygon area in acres from list of [lat, lng] without shapely."""
    xy = _latlngs_to_xy(coords)
    # Shoelace formula
    area = 0
    n = len(xy)
    for i in range(n):
        x1, y1 = xy[i]
        x2, y2 = xy[(i+1) % n]
        area += x1*y2 - x2*y1
    area_m2 = abs(area) / 2
    return area_m2 * M2_TO_ACRES


def calculate_elevation(coords):
    """Fetch average elevation (m) for coords via API."""
    locations = [{'latitude': lat, 'longitude': lng} for lat, lng in coords]
    resp = requests.post(ELEVATION_API_URL, json={'locations': locations})
    results = resp.json().get('results', [])
    elevs = [pt.get('elevation', 0) for pt in results]
    return sum(elevs) / len(elevs) if elevs else 0


