from django.urls import path
from django.views.generic import RedirectView

from fuel_route.views.fuel_route_view import OptimalRouteView, route_planner_view

urlpatterns = [
    path('', RedirectView.as_view(url='planner', permanent=True), name='root_redirect'),
    path('planner', route_planner_view, name='route_planner'),
    path('api/optimal-route/', OptimalRouteView.as_view(), name='optimal_route'),
]