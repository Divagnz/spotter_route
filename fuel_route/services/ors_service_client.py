from typing import List

import openrouteservice
from django.conf import settings
import logging

from geopy import Point
from openrouteservice import Client

from fuel_route.data.data_types import (
    PeliasSearchResponseType,
    Coordinates,
    DirectionsResponseType,
)
from fuel_route.data.enums import VehicleProfile
from fuel_route.data.exceptions import GeocodeNotFoundException

logger = logging.getLogger(__name__)


class ORSClient:
    def __init__(self):
        self.client: Client = openrouteservice.Client(
            key=settings.OPENROUTESERVICE_API_KEY
        )

    def geocode(self, address: str, dry_run: bool = False) -> Coordinates:
        _sources = ["osm", "gn", "wof"]
        _country = "US"
        _layers = ["venue", "address", "street"]
        _size = 1
        _geocoding_response = self.client.pelias_search(
            text=address, sources=_sources, country=_country, layers=_layers, size=_size
        )
        _pelias_response = PeliasSearchResponseType.from_dict(_geocoding_response)
        if not _pelias_response.features:
            raise GeocodeNotFoundException(f"Unable to geocode location: {address}")
        _coordinates: Coordinates = Coordinates(
            lat=_pelias_response.features[0].geometry.coordinates[1],
            lon=_pelias_response.features[0].geometry.coordinates[0],
        )
        logger.info(f"ORS Geocoding response coordenates: {_coordinates}")
        return _coordinates

    def get_directions(
        self,
        start: Coordinates,
        end: Coordinates,
        vehicle_profile: VehicleProfile = VehicleProfile.TRUCK.value,
        output_format: str = "geojson",
        instructions: bool = False,
        include_geometry: bool = True,
    ):
        _directions = self.client.directions(
            coordinates=[[start.lon, start.lat], [end.lon, end.lat]],
            profile=vehicle_profile,
            format=output_format,
            instructions=instructions,
            geometry=include_geometry,
            units="mi",
            language="en",
            dry_run=False,
        )
        _ors_directions = DirectionsResponseType.from_dict(_directions)
        return _ors_directions


    def get_directions_from_multipoint(
        self,
        route: List[Coordinates],
        vehicle_profile: VehicleProfile = VehicleProfile.TRUCK.value,
        output_format: str = "geojson",
        instructions: bool = False,
        include_geometry: bool = True,
    ):
        _route_coords = [[coord.lon, coord.lat] for coord in route]
        _directions = self.client.directions(
            coordinates=_route_coords,
            profile=vehicle_profile,
            format=output_format,
            instructions=instructions,
            geometry=include_geometry,
            units="mi",
            language="en",
            dry_run=False,
        )
        _ors_directions = DirectionsResponseType.from_dict(_directions)
        return _ors_directions
