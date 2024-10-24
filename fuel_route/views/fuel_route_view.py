from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.shortcuts import render
from fuel_route.data.serializers import RouteInputSerializer
from fuel_route.controllers.fuel_route_controller import FuelRouteController

class OptimalRouteView(APIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.controller = FuelRouteController()

    def post(self, request):
        serializer = RouteInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start = serializer.validated_data['start']
        end = serializer.validated_data['end']
        include_map_html = serializer.validated_data['include_map_html']

        try:
            route_data = self.controller.get_optimal_route(start, end, include_map_html)
            return Response(route_data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def route_planner_view(request):
    return render(request, 'route_planner.html')