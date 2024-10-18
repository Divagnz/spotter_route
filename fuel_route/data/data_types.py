from dataclasses import dataclass
from typing import List, Optional
from django.contrib.gis.geos import Point


@dataclass
class FuelStation:
    opis_id: int
    truckstop_name: str
    address: str
    city: str
    state: str
    rack_id: int
    location: Point
    retail_price: float
    id: Optional[int]


@dataclass
class Route:
    start: str
    end: str
    distance: float
    fuel_stops: List[FuelStation]
    total_cost: float