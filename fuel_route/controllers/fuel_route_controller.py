from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.measure import D
from folium import PolyLine

from fuel_route.services.ors_service_client import ORSClient
from fuel_route.services.fuel_station_service import FuelStationService
from fuel_route.data.data_types import Route, Coordinates
from fuel_route.data.exceptions import (
    RouteNotFoundException,
    FuelStationNotFoundException,
    InvalidCoordinatesException,
)
from fuel_route.data.serializers import RouteOutputSerializer
import folium


class FuelRouteController:
    def __init__(self):
        self.fuel_station_service = FuelStationService()
        self.ors_client: ORSClient = ORSClient()

    def get_optimal_route(self, start, end, include_map_html=True):
        try:
            route = self.optimize_route(start, end)
            map_html = self._create_route_map(route)
            output_serializer = RouteOutputSerializer(route)
            response = { "route": output_serializer.data }
            if include_map_html:
                response["map_html"] = map_html
            return response
        except ValueError as e:
            raise e

    def optimize_route(self, start, end) -> Route:
        try:
            start_coords = self._ensure_coordinates(start)
            end_coords = self._ensure_coordinates(end)

            directions_response = self.ors_client.get_directions(
                start=start_coords, end=end_coords
            )
            _coordinates = directions_response.features[0].geometry.coordinates
            route = LineString([Point(lon, lat) for lon, lat in _coordinates], srid=4326)
            _distance = directions_response.features[0].properties.summary.distance
            print(f"Distance: {_distance}")
            fuel_stations_by_distance_to_start = self.fuel_station_service.get_stations_along_route(
                route=route, max_distance_km=1
            )
            fuel_stops, _new_route = self.fuel_station_service.calculate_optimal_fuel_stops(fuel_stations_by_distance_to_start, route, _distance)
            _new_directions = self.ors_client.get_directions_from_multipoint(
                route=[Coordinates(lat=_point.coords[1], lon=_point.coords[0]) for _point in _new_route]
            )
            _distance = _new_directions.features[0].properties.summary.distance
            print(f"New distance: {_distance}")
            _coordinates = _new_directions.features[0].geometry.coordinates
            route = LineString([Point(lon, lat) for lon, lat in _coordinates], srid=4326)
            _total_distance = D(m=route.transform(5069, clone=True).length).mi
            total_cost = self.fuel_station_service.calculate_total_cost(route=route, fuel_stops=fuel_stops, total_distance=_total_distance)
            return Route(str(start), str(end), _total_distance, fuel_stops, total_cost, _coordinates)
        except RouteNotFoundException:
            raise ValueError("Unable to find route")
        except FuelStationNotFoundException:
            raise ValueError("No fuel stations found along the route")
        except InvalidCoordinatesException as e:
            raise ValueError(str(e))

    def _ensure_coordinates(self, location) -> Coordinates:
        if isinstance(location, Coordinates):
            return location
        elif isinstance(location, str):
            coords = self.ors_client.geocode(location)

            if coords is None:
                raise InvalidCoordinatesException(
                    f"Unable to geocode location: {location}"
                )
            return coords
        else:
            raise InvalidCoordinatesException(
                f"Invalid location type: {type(location)}"
            )

    def _create_route_map(self, route: Route):
        m = folium.Map(location=[route.coordinates[0][1], route.coordinates[0][0]], zoom_start=6)

        folium.Marker([route.coordinates[0][1], route.coordinates[0][0]], popup="Start",
                      icon=folium.Icon(color="green")).add_to(m)
        folium.Marker([route.coordinates[-1][1], route.coordinates[-1][0]], popup="End",
                      icon=folium.Icon(color="red")).add_to(m)

        _line_string = LineString([Point(lon, lat) for lon, lat in route.coordinates], srid=4326)
        _total_distance = D(m=_line_string.transform(5069, clone=True).length).mi
        print(f"Total distance: {_total_distance}")
        prev_stop = None
        total_distance = 0
        print(f"Number of fuel stops: {len(route.fuel_stops)}")
        for i, stop in enumerate(route.fuel_stops):
            _location = stop.location.coords
            route_array = route.coordinates
            curr_idx = 0
            for _index, _coord in enumerate(route_array):
                if abs(round(_coord[0], 3) - round(_location[0], 3)) < 0.002 and abs(round(_coord[1], 3) == round(_location[1], 3)) < 0.002:
                    curr_idx = _index
                    break
            for _index, _coord in enumerate(route_array):
                if curr_idx != 0:
                    break
                if abs(round(_coord[0], 3) - round(_location[0], 3)) < 0.02 and abs(round(_coord[1], 3) == round(_location[1], 3)) < 0.01:
                    curr_idx = _index
                    break

            _partial_route = route_array[:curr_idx]
            _partial_line_string = LineString(_partial_route, srid=4326)
            _partial_distance = D(m=_partial_line_string.transform(5069, clone=True).length).mi
            folium.Marker(
                location=[_location[1], _location[0]],
                popup=f"{stop.truckstop_name}<br>Price: ${stop.retail_price:.2f}, Distance to last point: {stop.distance.mi if not prev_stop else stop.distance_to_last_point.mi:.4f} mi, Distance to route: {stop.distance_to_route.mi:.4f} mi",
                icon=folium.Icon(color="blue", icon="gas-pump", prefix="fa")
            ).add_to(m)
            if prev_stop is None:
                segment_distance = _partial_distance
                midpoint = [(route.coordinates[0][1] + stop.location.y) / 2,
                            (route.coordinates[0][0] + stop.location.x) / 2]
            else:
                segment_distance = _partial_distance - total_distance
                midpoint = [(prev_stop.location.y + stop.location.y) / 2,
                            (prev_stop.location.x + stop.location.x) / 2]
            total_distance += segment_distance

            folium.Marker(
                midpoint,
                icon=folium.DivIcon(html=f'<div style="font-size: 12pt;font-weight: bolder;">{segment_distance:.1f} mi</div>')
            ).add_to(m)

            prev_stop = stop


        segment_distance = _total_distance - total_distance
        midpoint = [(prev_stop.location.y + route.coordinates[-1][1]) / 2,
                    (prev_stop.location.x + route.coordinates[-1][0]) / 2]
        folium.Marker(
            midpoint,
            icon=folium.DivIcon(
                html=f'<div style="font-size: 12pt;font-weight: bolder;">{segment_distance:.1f} mi</div>')
        ).add_to(m)
        total_distance += segment_distance
        # Create a PolyLine for the complete route
        PolyLine(
            [(lat, lon) for lon, lat in route.coordinates],
            weight=5,
            color="red",
            opacity=0.8
        ).add_to(m)

        folium.Marker(
            [route.coordinates[0][1], route.coordinates[0][0]],
            icon=folium.DivIcon(
                html=f'<div style="font-size: 12pt"><strong>Total: {total_distance:.1f} mi</strong></div>'),
            popup=f"Total distance: {total_distance:.1f} miles"
        ).add_to(m)


        m.fit_bounds([(lat, lon) for lon, lat in route.coordinates])

        return m._repr_html_()