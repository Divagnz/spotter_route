import csv
import time

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from fuel_route.data.models import FuelStationModel
from fuel_route.data.data_types import FuelStation
from typing import List

from fuel_route.services.geocoding_service import GeocodingService


class Command(BaseCommand):
    help = 'Import fuel stations from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        fuel_stations = self.read_csv(csv_file_path)
        self.import_fuel_stations(fuel_stations)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(fuel_stations)} fuel stations'))
        self.saved_records = FuelStationModel.objects.all()


    def read_csv(self, file_path: str) -> List[FuelStation]:
        fuel_stations = []
        geolocator = Nominatim(user_agent="spotter-test")

        geocoding_service = GeocodingService()
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if FuelStationModel.objects.filter(opis_id=row['OPIS Truckstop ID']).exists():
                    print(f"Fuel station with OPIS ID {row['OPIS Truckstop ID']} already exists")
                    continue
                formatted_address = geocoding_service.format_address(
                    row['Address'], row['City'], row['State']
                )
                print(f"Geocoding: {formatted_address}")
                coords = geocoding_service.geocode(formatted_address)

                if coords:
                    print(f"Geocoded: {formatted_address}, {coords}")
                    lat, lon = coords
                    fuel_station = FuelStation(
                        opis_id=int(row['OPIS Truckstop ID']),
                        truckstop_name=row['Truckstop Name'],
                        address=row['Address'],
                        city=row['City'],
                        state=row['State'],
                        rack_id=int(row['Rack ID']),
                        location=Point(lon, lat),
                        retail_price=float(row['Retail Price']),
                        id=None
                    )
                    self.import_fuel_stations(fuel_station)
                    fuel_stations.append(fuel_station)
                else:
                    print(f"Couldn't geocode: {formatted_address}")

        return fuel_stations

    @transaction.atomic
    def import_fuel_stations(self, fuel_station: FuelStation):
        FuelStationModel.objects.update_or_create(
            opis_id=fuel_station.opis_id,
            location=fuel_station.location,
            defaults={
                'truckstop_name': fuel_station.truckstop_name,
                'address': fuel_station.address,
                'city': fuel_station.city,
                'state': fuel_station.state,
                'rack_id': fuel_station.rack_id,
                'retail_price': fuel_station.retail_price
            }
        )


    def geocode(self, geolocator, address, max_attempts=3):
        for attempt in range(max_attempts):
            try:
                return geolocator.geocode(address, timeout=10)
            except (GeocoderTimedOut, GeocoderServiceError):
                if attempt == max_attempts - 1:
                    return None
                time.sleep(1)