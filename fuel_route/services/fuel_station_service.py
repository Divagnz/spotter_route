from typing import List
from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.db.models.functions import Distance
from fuel_route.data.models import FuelStation
from fuel_route.data.exceptions import FuelStationNotFoundException

class FuelStationService:
    def get_stations_along_route(self, coordinates: List[List[float]], max_distance_km: float = 5) -> List[FuelStation]:
        route = LineString([Point(lon, lat) for lon, lat in coordinates], srid=4326)
        route_buffer = route.buffer(max_distance_km / 111.32)  # Approximate degrees to km conversion

        stations = FuelStation.objects.filter(location__intersects=route_buffer)
        stations = stations.annotate(
            distance=Distance('location', route)
        ).order_by('distance')[:100]

        if not stations:
            raise FuelStationNotFoundException("No fuel stations found along the route")

        return list(stations)

    def calculate_optimal_fuel_stops(self, fuel_stations: List[FuelStation], total_distance: float) -> List[FuelStation]:
        optimal_stops = []
        current_range = 500  # Start with a full tank
        distance_covered = 0

        while distance_covered < total_distance:
            best_station = min(
                (station for station in fuel_stations if station.price is not None),
                key=lambda s: s.price
            )
            optimal_stops.append(best_station)
            distance_covered += current_range
            current_range = 500  # Refill to full tank

        return optimal_stops

    def calculate_total_cost(self, distance: float, fuel_stops: List[FuelStation]) -> float:
        total_gallons = distance / 10  # Assuming 10 mpg
        return sum(stop.price * (500 / 10) for stop in fuel_stops[:-1]) + fuel_stops[-1].price * (total_gallons % 50)