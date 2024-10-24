from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from typing import List, Optional
from django.contrib.gis.geos import Point


@dataclass
class Coordinates:
    lat: float
    lon: float


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
    coordinates: List[List[float]]


class ExtendedFuelStation(FuelStation):
    @classmethod
    def from_base(cls, base: FuelStation, location: Point):
        return cls(
            opis_id=base.opis_id,
            truckstop_name=base.truckstop_name,
            address=base.address,
            city=base.city,
            state=base.state,
            rack_id=base.rack_id,
            location=location,
            retail_price=base.retail_price,
            id=base.id,
        )


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class GeometryType:
    type: str
    coordinates: List[float]


@dataclass_json(letter_case=LetterCase.SNAKE, )
@dataclass
class FeatureProperties:
    id: str = None
    gid: str = None
    layer: str = None
    source: str = None
    source_id: str = None
    name: str = None
    confidence: int = None
    match_type: str = None
    accuracy: str = None
    country: str = None
    country_gid: str = None
    country_a: str = None
    region: str = None
    region_gid: str = None
    region_a: str = None
    county: str = None
    county_gid: str = None
    locality: str = None
    locality_gid: str = None
    continent: str = None
    continent_gid: str = None
    label: str = None
    addendum: dict = None


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class GeocodingType:
    version: str = None
    attribution: str = None
    query: dict = None
    engine: dict = None
    timestamp: int = None


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class PeliasFeature:
    type: str
    geometry: GeometryType
    properties: FeatureProperties


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class PeliasSearchResponseType:
    geocoding: GeocodingType
    type: str
    features: List[PeliasFeature]


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class DirectionsStep:
    distance: float
    duration: float
    type: int
    instruction: str
    name: str
    way_points: List[int]


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class DirectionsMetadata:
    attribution: str
    service: str
    timestamp: int
    query: dict
    engine: dict


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class DirectionsSegment:
    distance: float
    duration: float
    steps: List[DirectionsStep]


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class DirectionsWarnings:
    code: int
    message: str


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class DirectionsSummary:
    distance: float
    duration: float


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class DirectionsProperties:
    segments: Optional[List[DirectionsSegment]] = None
    extras: Optional[dict]= None
    warnings: Optional[List[DirectionsWarnings]] = None
    summary: DirectionsSummary = None
    way_points: List[int] = None


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class DirectionsGeometry:
    type: str
    coordinates: List


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class DirectionsFeature:
    bbox: List[float]
    type: str
    geometry: DirectionsGeometry
    properties: Optional[DirectionsProperties] = None


@dataclass_json(letter_case=LetterCase.SNAKE)
@dataclass
class DirectionsResponseType:
    type: str
    bbox: List[float]
    features: List[DirectionsFeature]
    metadata: DirectionsMetadata
