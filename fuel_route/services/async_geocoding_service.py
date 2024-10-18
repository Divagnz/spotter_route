from geopy.geocoders import Nominatim
from geopy.adapters import AioHTTPAdapter
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AsyncGeocodingService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="fuel_route_app", adapter_factory=AioHTTPAdapter)

    async def geocode(self, address: str, max_attempts: int = 3) -> Optional[Tuple[float, float]]:
        for attempt in range(max_attempts):
            try:
                location = await self.geolocator.geocode(address)
                if location:
                    return location.latitude, location.longitude

                # If not found, try with a more general search
                state = address.split(',')[-1].strip()
                general_location = await self.geolocator.geocode(f"{state}, USA")
                if general_location:
                    return general_location.latitude, general_location.longitude

                return None
            except Exception as e:
                logger.error(f"Geocoding error for {address}: {str(e)}")
                if attempt == max_attempts - 1:
                    return None

    def format_address(self, address: str, city: str, state: str) -> str:
        # Remove exit information
        address = address.split(',')[0].strip()

        # Remove highway prefixes
        # address = address.replace('I-', 'Interstate ')
        address = address.replace('SR ', 'State Route ')
        # address = address.replace('HWY ', 'Highway ')

        return f"{address}, {city}, {state}, USA"