import csv
import asyncio
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from fuel_route.data.models import FuelStationModel
from fuel_route.services.async_geocoding_service import AsyncGeocodingService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import fuel stations from CSV file'

    def handle(self, *args, **options):
        asyncio.run(self.async_import())

    async def async_import(self):
        geocoding_service = AsyncGeocodingService()
        tasks = []

        with open('fuel-prices-for-be-assessment_short.csv', 'r') as file:
            reader = csv.DictReader(file)
            async with geocoding_service.geolocator as geolocator:
                for row in reader:
                    formatted_address = geocoding_service.format_address(
                        row['Address'], row['City'], row['State']
                    )
                    task = asyncio.create_task(self.process_row(geocoding_service, row, formatted_address))
                    tasks.append(task)

                await asyncio.gather(*tasks)

        self.stdout.write(self.style.SUCCESS('Successfully imported fuel stations'))

    async def process_row(self, geocoding_service, row, formatted_address):
        coords = await geocoding_service.geocode(formatted_address)

        if coords:
            lat, lon = coords
            await self.create_fuel_station(row, lat, lon)
            logger.info(f"Successfully imported: {formatted_address}")
        else:
            logger.warning(f"Couldn't geocode: {formatted_address}")

    @staticmethod
    async def create_fuel_station(row, lat, lon):
        await asyncio.to_thread(
            FuelStationModel.objects.create,
            opis_id=int(row['OPIS Truckstop ID']),
            name=row['Truckstop Name'],
            address=row['Address'],
            city=row['City'],
            state=row['State'],
            location=Point(lon, lat),
            price=float(row['Retail Price'])
        )