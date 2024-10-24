from django.urls import path
from fuel_route.views.fuel_route_view import OptimalRouteView, route_planner_view

urlpatterns = [
    path('planner', route_planner_view, name='route_planner'),
    path('api/optimal-route/', OptimalRouteView.as_view(), name='optimal_route'),
]