from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from fuel_route.controllers.fuel_route_controller import FuelRouteController
from fuel_route.services.route_service import RouteService
from fuel_route.services.fuel_station_service import FuelStationService
from fuel_route.data.serializers import RouteInputSerializer, RouteOutputSerializer

class OptimalRouteView(APIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        route_service = RouteService()
        fuel_station_service = FuelStationService()
        self.controller = FuelRouteController(route_service, fuel_station_service)

    def post(self, request):
        serializer = RouteInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start = serializer.validated_data['start']
        end = serializer.validated_data['end']

        try:
            route_data = self.controller.get_optimal_route(start, end)
            return Response(route_data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)