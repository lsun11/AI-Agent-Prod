from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional


class WeatherSource(BaseModel):
    title: str = ""
    url: str = ""
    snippet: str = ""


class HourlyPoint(BaseModel):
    time_local: str = ""  # e.g. "2025-12-19 14:00"
    temp: Optional[float] = None
    feels_like: Optional[float] = None
    precipitation_chance: Optional[int] = Field(default=None, ge=0, le=100)
    condition: str = ""  # "Cloudy", "Rain", etc.


class DailyPoint(BaseModel):
    date_local: str = ""  # e.g. "2025-12-19"
    high: Optional[float] = None
    low: Optional[float] = None
    precipitation_chance: Optional[int] = Field(default=None, ge=0, le=100)
    condition: str = ""


class WeatherNow(BaseModel):
    temp: Optional[float] = None
    feels_like: Optional[float] = None
    humidity: Optional[int] = Field(default=None, ge=0, le=100)
    wind: str = ""  # "8 mph NW"
    precipitation: str = ""  # "0.1 in" / "light rain"
    condition: str = ""


class WeatherReport(BaseModel):
    # for display
    location_label: str = ""  # "San Francisco, CA" if available, else "Lat..., Lon..."
    timezone: str = ""

    # collapsed summary
    summary_line: str = ""  # "⛅ 68° • Partly cloudy"

    # expanded detail
    now: WeatherNow = Field(default_factory=WeatherNow)
    hourly: List[HourlyPoint] = Field(default_factory=list)
    daily: List[DailyPoint] = Field(default_factory=list)

    # provenance
    sources: List[WeatherSource] = Field(default_factory=list)
    updated_at_iso: str = ""  # server timestamp
