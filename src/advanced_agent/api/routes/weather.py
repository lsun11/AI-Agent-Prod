from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
import httpx
from typing import Any, Optional

router = APIRouter()


def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


@router.get("/api/geoip")
async def geoip(request: Request):
    """
    Returns approximate coords based on public IP.
    Used only as a fallback when browser geolocation fails.
    """
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get("https://ipapi.co/json/")
            r.raise_for_status()
            data = r.json()

        lat = data.get("latitude")
        lon = data.get("longitude")

        try:
            lat = float(lat) if lat is not None else None
            lon = float(lon) if lon is not None else None
        except Exception:
            lat = None
            lon = None

        if lat is None or lon is None:
            raise HTTPException(status_code=502, detail="GeoIP provider did not return coordinates")

        return {
            "lat": lat,
            "lon": lon,
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country_name"),
            "provider": "ipapi.co",
        }

    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"GeoIP lookup failed: {str(e)}") from e


@router.get("/api/weather")
async def weather(lat: float, lon: float, lang: str = "en"):
    """
    Primary: Open-Meteo structured forecast
    Fallback: (later) Firecrawl scrape summary
    """
    lat_f = _safe_float(lat)
    lon_f = _safe_float(lon)
    if lat_f is None or lon_f is None:
        raise HTTPException(status_code=400, detail="Invalid lat/lon")

    # Keep this always defined so we never crash while reporting errors
    open_meteo_err = None

    # ---- Primary: Open-Meteo ----
    try:
        params = {
            "latitude": str(lat_f),
            "longitude": str(lon_f),
            "timezone": "auto",
            "current": ",".join(
                [
                    "temperature_2m",
                    "apparent_temperature",
                    "relative_humidity_2m",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m",
                ]
            ),
            "daily": ",".join(
                [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_probability_max",
                ]
            ),
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
            r.raise_for_status()
            data = r.json()

        return {
            "timezone": data.get("timezone"),
            "current": data.get("current", {}),
            "daily": data.get("daily", {}),
            "source": "open-meteo",
        }

    except Exception as e:
        open_meteo_err = str(e)

    # ---- Fallback (Firecrawl) ----
    # For now return a controlled error instead of 500.
    raise HTTPException(
        status_code=502,
        detail={
            "message": "Weather unavailable",
            "open_meteo_error": open_meteo_err,
            "firecrawl_error": "not wired yet",
        },
    )