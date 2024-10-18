from django.urls import path
from .views import get_optimal_route

urlpatterns = [
    path('optimal-route/', get_optimal_route, name='optimal_route'),
]