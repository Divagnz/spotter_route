import folium
from fuel_route.services.route_service import RouteService
from fuel_route.services.fuel_station_service import FuelStationService
from fuel_route.data.data_types import Route
from fuel_route.data.exceptions import RouteNotFoundException, FuelStationNotFoundException
from fuel_route.data.serializers import RouteOutputSerializer

class FuelRouteController:
    def __init__(self, route_service: RouteService, fuel_station_service: FuelStationService):
        self.route_service = route_service
        self.fuel_station_service = fuel_station_service

    def get_optimal_route(self, start: str, end: str):
        try:
            route = self.optimize_route(start, end)
            map_html = self._create_route_map(route)
            output_serializer = RouteOutputSerializer(route)

            return {
                "route": output_serializer.data,
                "map_html": map_html
            }
        except ValueError as e:
            raise e

    def optimize_route(self, start: str, end: str) -> Route:
        try:
            coordinates, distance = self.route_service.get_route(start, end)
            fuel_stations = self.fuel_station_service.get_stations_along_route(coordinates)
            optimal_stops = self.fuel_station_service.calculate_optimal_fuel_stops(fuel_stations, distance)
            total_cost = self.fuel_station_service.calculate_total_cost(distance, optimal_stops)

            return Route(start, end, distance, optimal_stops, total_cost)
        except RouteNotFoundException:
            raise ValueError("Unable to find route")
        except FuelStationNotFoundException:
            raise ValueError("No fuel stations found along the route")

    def _create_route_map(self, route: Route):
        m = folium.Map(location=[route.optimal_stops[0].location.y, route.optimal_stops[0].location.x], zoom_start=6)

        # Add markers for start and end
        folium.Marker([route.optimal_stops[0].location.y, route.optimal_stops[0].location.x], popup="Start").add_to(m)
        folium.Marker([route.optimal_stops[-1].location.y, route.optimal_stops[-1].location.x], popup="End").add_to(m)

        # Add markers for fuel stops
        for stop in route.optimal_stops:
            folium.Marker(
                [stop.location.y, stop.location.x],
                popup=f"{stop.name}<br>Price: ${stop.price:.2f}",
                icon=folium.Icon(color="green", icon="gas-pump", prefix="fa")
            ).add_to(m)

        return m._repr_html_()