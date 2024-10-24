from fuel_route.data.data_types import FuelStation, Route, Coordinates
from rest_framework import serializers

class LocationField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str):
            parts = data.split(',')
            if len(parts) == 2:
                try:
                    lat, lon = map(float, parts)
                    return Coordinates(lat=lat, lon=lon)
                except ValueError:
                    pass
            return data  # Assume it's a place name
        raise serializers.ValidationError("Invalid location format")

    def to_representation(self, value):
        if isinstance(value, Coordinates):
            return f"{value.lat},{value.lon}"
        return str(value)

class RouteInputSerializer(serializers.Serializer):
    start = LocationField()
    end = LocationField()
    include_map_html = serializers.BooleanField(default=True)

    def validate(self, data):
        """
        Check that start and end are different.
        """
        if data['start'] == data['end']:
            raise serializers.ValidationError("Start and end locations must be different")
        print(f"Map HTML: {data['include_map_html']}")
        return data

class FuelStationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    truckstop_name = serializers.CharField()
    address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    lat = serializers.FloatField(source='location.y')
    lon = serializers.FloatField(source='location.x')
    retail_price = serializers.FloatField()


class RouteOutputSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()
    distance = serializers.FloatField()
    fuel_stops = FuelStationSerializer(many=True)
    total_cost = serializers.FloatField()
    coordinates = serializers.ListField(child=serializers.ListField(child=serializers.FloatField()))

    def to_representation(self, instance: Route):
        return {
            'start': instance.start,
            'end': instance.end,
            'distance': instance.distance,
            'fuel_stops': FuelStationSerializer(instance.fuel_stops, many=True).data,
            'total_cost': instance.total_cost,
            'coordinates': instance.coordinates
        }