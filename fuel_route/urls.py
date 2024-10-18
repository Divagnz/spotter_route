from django.urls import path
from fuel_route.views.fuel_route_view import OptimalRouteView

urlpatterns = [
    path('optimal-route/', OptimalRouteView.as_view(), name='optimal_route'),
]