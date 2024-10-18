from django.contrib.gis.db import models

from fuel_route.data.data_types import FuelStation


class FuelStationModel(models.Model):
    id = models.AutoField(primary_key=True)
    opis_id: int = models.IntegerField(unique=True)
    truckstop_name: str = models.CharField(max_length=255)
    address: str = models.CharField(max_length=255)
    city: str = models.CharField(max_length=100)
    state: str = models.CharField(max_length=2)
    rack_id: int = models.IntegerField(max_length=255)
    location = models.PointField(srid=4326)
    retail_price: float = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['opis_id'])
        ]

    def to_domain(self) -> FuelStation:
        return FuelStation(
            id=self.id,
            opis_id=self.opis_id,
            truckstop_name=self.truckstop_name,
            address=self.address,
            city=self.city,
            state=self.state,
            rack_id=self.rack_id,
            location=self.location,
            retail_price=self.retail_price
        )
    class Meta:
        indexes = [models.Index(fields=['location'])]