"""Real Earth Geographic Coordinate & Continental Region Mapper (1:1 Scale).

Maps simulation coordinates `(x, y)` onto real Earth `(latitude, longitude)` degrees
and authentic terrestrial geographic regions so every birth, settlement, invention,
and inter-generational migration is logged with verifiable Earth geography.
"""

from __future__ import annotations

from typing import Tuple

# World simulation extent mapped cleanly onto Earth's inhabited latitude/longitude belt
WORLD_HALF_SPAN_X = 240.0
WORLD_HALF_SPAN_Y = 200.0


def coords_to_lat_lon(x: float, y: float) -> Tuple[float, float]:
    """Converts simulation `(x, y)` to real Earth `(lat, lon)` in degrees."""
    lon = max(-180.0, min(180.0, (x / WORLD_HALF_SPAN_X) * 180.0))
    # North is negative y in our 3D map, South is positive y
    lat = max(-72.0, min(72.0, (-y / WORLD_HALF_SPAN_Y) * 72.0))
    return (round(lat, 2), round(lon, 2))


def classify_earth_region(lat: float, lon: float) -> Tuple[str, str]:
    """Returns `(continent_en, region_name_en)` for any `(lat, lon)` on Earth."""
    # Americas
    if lon < -30.0:
        if lat >= 15.0:
            if lat >= 58.0:
                return ("North America", "Boreal Shield")
            if lon < -102.0:
                return ("North America", "Rocky Cordillera")
            return ("North America", "Great Plains")
        if lat >= -5.0 and lon >= -76.0:
            return ("South America", "Amazon Basin")
        if lon < -68.0:
            return ("South America", "Andean Cordillera")
        return ("South America", "Pampas & Gran Chaco")

    # Africa & Middle East
    if -20.0 <= lon <= 52.0 and lat <= 35.0:
        if lat >= 18.0:
            if lon >= 32.0:
                return ("Eurasia-Africa Crossroads", "Fertile Crescent & Nile")
            return ("Africa", "Sahara & Sahel Belt")
        if lon >= 26.0 and lat >= -15.0:
            return ("Africa", "East African Rift")
        if lat >= -12.0:
            return ("Africa", "Congo Rainforest Basin")
        return ("Africa", "Southern Savanna")

    # Europe & Mediterranean
    if -15.0 <= lon <= 45.0 and lat > 35.0:
        if lat <= 45.0:
            return ("Europe", "Mediterranean Basin")
        if lat >= 60.0:
            return ("Europe", "Fennoscandian Tundra")
        return ("Europe", "Central European Plain")

    # Oceania / Australia
    if lon >= 110.0 and lat < -10.0:
        return ("Oceania", "Australian Outback")

    # Asia
    if lat >= 55.0:
        return ("Asia", "Siberian Taiga")
    if 65.0 <= lon <= 105.0 and 25.0 <= lat <= 40.0:
        return ("Asia", "Himalayan Plateau")
    if 65.0 <= lon <= 95.0 and lat < 25.0:
        return ("Asia", "Indus & Ganges Valley")
    if lon > 95.0:
        return ("Asia", "East Asian River Valleys")
    return ("Asia", "Eurasian Steppe")


def earth_location_summary(x: float, y: float) -> dict:
    """Returns structured real-Earth geographic telemetry for an agent or event."""
    lat, lon = coords_to_lat_lon(x, y)
    continent, region = classify_earth_region(lat, lon)
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return {
        "lat": lat,
        "lon": lon,
        "coords_str": f"{abs(lat):.1f}°{ns}, {abs(lon):.1f}°{ew}",
        "continent": continent,
        "region": region,
    }
