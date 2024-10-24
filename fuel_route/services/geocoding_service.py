from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from typing import Optional, Tuple


class GeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="fuel_route_app")

    def geocode(self, address: str, max_attempts: int = 3) -> Optional[Tuple[float, float]]:
        for attempt in range(max_attempts):
            try:
                location = self.geolocator.geocode(address, timeout=30)
                if location:
                    return location.latitude, location.longitude

                # If not found, try with a more general search
                state = address.split(',')[-1].strip()
                general_location = self.geolocator.geocode(f"{state}, USA")
                if general_location:
                    return general_location.latitude, general_location.longitude

                return None
            except (GeocoderTimedOut, GeocoderServiceError):
                if attempt == max_attempts - 1:
                    return None
                time.sleep(1)

    def format_address(self, address: str, city: str, state: str) -> str:
        # Remove exit information
        address = address.split(',')[0].strip()

        # # Remove highway prefixes
        # address = address.replace('I-', 'Interstate ')
        address = address.replace('SR ', 'State Route ')
        # address = address.replace('HWY ', 'Highway ')

        return f"{address}, {city}, {state}, USA"