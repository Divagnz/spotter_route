from rest_framework import serializers
from fuel_route.data.data_types import FuelStation, Route

class FuelStationSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(source='location.y')
    lon = serializers.FloatField(source='location.x')

    class Meta:
        model = FuelStation
        fields = ['id', 'name', 'address', 'city', 'state', 'lat', 'lon', 'price']

class RouteInputSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()

class RouteOutputSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()
    distance = serializers.FloatField()
    fuel_stops = FuelStationSerializer(many=True)
    total_cost = serializers.FloatField()

    def to_representation(self, instance: Route):
        return {
            'start': instance.start,
            'end': instance.end,
            'distance': instance.distance,
            'fuel_stops': FuelStationSerializer(instance.fuel_stops, many=True).data,
            'total_cost': instance.total_cost
        }