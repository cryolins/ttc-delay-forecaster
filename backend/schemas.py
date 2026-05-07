from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class DirectionEnum(Enum):
    N = "N"
    E = "E"
    S = "S"
    W = "W"
    B = "B"

class WeatherEnum(Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    DUSTY = "dusty"
    FOG = "fog"
    PREVIOUS = "previous"
    SNOW = "snow"
    RAIN = "rain"
    MIXED = "mixed"

class IncidentEnum(Enum):
    LATE_EXIT = "late exit"
    MECHANICAL = "mechanical"
    OPERATIONS = "operations"
    SECURITY = "security"
    BLOCKED = "road blocked"
    COLLISION = "collision"
    DIVERSION = "diversion"
    OFF_ROUTE = "off route"
    EMERGENCY = "emergency services"
    CLEANING = "cleaning"
    VISION = "vision"

class AdvancedPredictParams(BaseModel):
    incident_type: IncidentEnum
    weather_category: WeatherEnum
    temperature_2m: float = Field(ge=-40, le=40)
    precipitation: float = Field(ge=0)
    windspeed_10m: float = Field(ge=0)
    snowfall: float = Field(ge=0)

class PredictRequest(BaseModel):
    route: int
    timestamp: datetime
    direction: Optional[DirectionEnum]
    advanced: Optional[AdvancedPredictParams]

class PredictResponse(BaseModel):
    route: int
    timestamp: datetime
    direction: Optional[DirectionEnum] # None means took weighted average
    predicted_delay: float
    route_avg_delay: float
    route_entries: int
    weather_category: WeatherEnum
    temperature: float
    precipitation: float
    input_advanced: bool # was input given in advanced mode (based on if optional fields are filled)
