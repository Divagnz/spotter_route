import requests
from typing import Tuple, List
from fuel_route.data.exceptions import RouteNotFoundException

class RouteService:
    def get_route(self, start: str, end: str) -> Tuple[List[List[float]], float]:
        url = f"http://router.project-osrm.org/route/v1/driving/{start};{end}?overview=full&geometries=geojson"
        response = requests.get(url)
        data = response.json()

        if "routes" not in data or not data["routes"]:
            raise RouteNotFoundException("Unable to find route")

        route = data["routes"][0]
        coordinates = route["geometry"]["coordinates"]
        distance = route["distance"] / 1609.34  # Convert meters to miles

        return coordinates, distance