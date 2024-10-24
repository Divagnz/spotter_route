import copy
from typing import List
import numpy as np

from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.db.models.functions import (
    Distance,
    Transform,
    LineLocatePoint,
    GeomOutputGeoFunc, GeoFunc,
)
from django.contrib.gis.measure import D
from django.db.models import QuerySet, Value
from django.utils.functional import cached_property

from fuel_route.data.models import FuelStationModel
from fuel_route.data.exceptions import FuelStationNotFoundException

METERS_TO_MILES = 1609.34


class RouteInterpolateMine(GeomOutputGeoFunc):
    arity = 2
    geom_param_pos = (0,)

    def __init__(self, route, fraction_expression, **extra):
        if not isinstance(route, (LineString, Value)):
            raise TypeError("Route parameter must be a LineString")

        super().__init__(route, fraction_expression, **extra)

    @cached_property
    def output_field(self):
        return GeometryField(srid=4326)

    def as_sql(self, compiler, connection, **extra_context):
        # Use ST_LineInterpolatePoint for PostGIS
        function = connection.ops.spatial_function_name("LineInterpolatePoint")
        return super().as_sql(compiler, connection, function=function, **extra_context)


class FuelStationService:
    @staticmethod
    def calculate_optimal_fuel_stops(
        fuel_stations_distance_to_start: QuerySet[FuelStationModel],
        route: LineString,
        total_distance: float,
    ) -> List[FuelStationModel]:
        optimal_stops = []
        current_position = 0.0  # Miles along the route
        max_millage_per_tank = 500
        min_millage_for_refill = max_millage_per_tank * 0.7
        print(f"Stations: {len(fuel_stations_distance_to_start)}")
        _route_np_array = route.array
        latest_point = None
        _new_route: List[Point] = []
        _new_route.append(Point(route.coords[0], srid=4326))
        _last_index = 0
        stations_to_exclude = []
        while current_position < total_distance - max_millage_per_tank:
            stations_in_range = []
            print(f"Current position: {current_position}")

            if current_position == 0:
                for station in fuel_stations_distance_to_start:
                    if (
                        max_millage_per_tank*0.2
                        > station.distance.mi
                    ):
                        stations_to_exclude.append(station.opis_id)
                    elif(
                        max_millage_per_tank*0.2
                        < station.distance.mi
                        <= min_millage_for_refill
                    ):
                        stations_in_range.append(station)
                        print(f"Station in range: {station}")
                    elif(
                        station.distance.mi
                        > min_millage_for_refill
                    ):
                        break
            else:
                _new_stations = copy.deepcopy(fuel_stations_distance_to_start)
                _new_stations = _new_stations.exclude(opis_id__in=stations_to_exclude).annotate(
                    distance_to_last_point=Distance(
                        "location",
                        latest_point, srid=4326),
                    ).order_by("distance")
                if _new_stations:
                    print(f"New stations: {len(_new_stations)}")
                    print(f"last station: {_new_stations.last().distance_to_last_point.mi}")
                for station in _new_stations:
                    if (
                        station.distance.mi
                        < optimal_stops[-1].distance.mi
                    ):
                        stations_to_exclude.append(station.opis_id)
                        continue
                    if (
                        max_millage_per_tank*0.5
                        < station.distance_to_last_point.mi
                        <= min_millage_for_refill
                    ):
                        stations_in_range.append(station)
                        print(f"Station in range: {station}")

            if not stations_in_range:
                print("no stations_in_range")
            else:
                # Get the cheapest station
                if current_position == 0:
                    optimal_station = min(stations_in_range, key=lambda x: x.retail_price)
                    print(
                        f"segment length = {optimal_station.distance.mi - current_position}"
                    )
                    optimal_stops.append(optimal_station)
                else:
                    optimal_station = min(stations_in_range, key=lambda x: x.retail_price)
                    print(
                        f"segment length = {optimal_station.distance_to_last_point.mi}"
                    )
                    optimal_stops.append(optimal_station)
                for station in stations_in_range:
                    if station.opis_id == optimal_station.opis_id:
                        stations_to_exclude.append(station.opis_id)
                        break
                    stations_to_exclude.append(station.opis_id)
                stations_to_exclude.extend([station.opis_id for station in stations_in_range])
                _point_on_route = optimal_station.closest_point_on_route_coords
                _new_route.append(optimal_station.tranformed_location)
                _new_position = D(m=LineString(_new_route, srid=4326).transform(5069, clone=True).length).mi
                print(f"New position: {_new_position}")
                latest_point = optimal_station.tranformed_location
                current_position = _new_position
        _new_route.append(Point(route.coords[-1], srid=4326))
        print(f"Optimal stops: {optimal_stops}")
        print(f"Total distance: {total_distance}")
        print(f"Total stops: {len(optimal_stops)}")
        return optimal_stops, _new_route

    @staticmethod
    def get_stations_along_route(
        route: LineString, max_distance_km: float = 0.5
    ) -> List[FuelStationModel]:
        _conversion_to_degrees = ((max_distance_km*1000)*0.000000039)/0.00362333
        route_buffer = route.buffer(_conversion_to_degrees)
        stations = FuelStationModel.objects.filter(location__intersects=route_buffer)

        stations_distance_to_origin_not_transformed = (
            stations
            .annotate(tranformed_location=Transform("location", 4326, clone=True))
            .annotate(
                distance=Distance(
                    "tranformed_location",
                    Point(route.coords[0], srid=4326),
                )
            )
            .annotate(closest_point_on_route=LineLocatePoint(route, "tranformed_location"))
            .annotate(distance_to_route=Distance("tranformed_location", route))
            .annotate(closest_point_on_route_coords=RouteInterpolateMine(route, "closest_point_on_route"))

        ).order_by("distance")
        print(f"Farthest station to route: {stations_distance_to_origin_not_transformed.last().distance_to_route}")
        print(
            f"Station closest to origin: {list(stations_distance_to_origin_not_transformed)[0].distance.mi}"
        )
        print(
            f"Station closest to origin coords: {list(stations_distance_to_origin_not_transformed)[0].location.coords}"
        )
        print(
            f"Station closest to origin distance to route: {list(stations_distance_to_origin_not_transformed)[0].distance_to_route.mi}"
        )
        print(
            f"Point in route closest to station: {list(stations_distance_to_origin_not_transformed)[0].closest_point_on_route_coords.coords}"
        )
        print(
            f"Station further from origin: {list(stations_distance_to_origin_not_transformed)[-1].distance.mi}"
        )
        if not stations:
            raise FuelStationNotFoundException("No fuel stations found along the route")

        return stations_distance_to_origin_not_transformed

    @staticmethod
    def calculate_total_cost(
        route: LineString,
        fuel_stops: List[FuelStationModel],
        total_distance: float = 0,
        fuel_efficiency: float = 6,
    ) -> float:
        total_cost = 0
        last_stop_distance = 0

        for idx, stop in enumerate(fuel_stops):
            if idx == 0:
                stop_distance = stop.distance.mi
            else:
                stop_distance = stop.distance_to_last_point.mi
            distance_traveled = stop_distance - last_stop_distance
            fuel_used = distance_traveled / fuel_efficiency
            total_cost += stop.retail_price * fuel_used
            last_stop_distance = stop_distance

        # Account for any remaining distance
        if total_distance > last_stop_distance:
            remaining_distance = total_distance - last_stop_distance
            fuel_used = remaining_distance / fuel_efficiency
            total_cost += fuel_stops[-1].retail_price * fuel_used

        return total_cost
