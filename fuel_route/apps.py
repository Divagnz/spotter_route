from django.apps import AppConfig
import logging

class FuelRouteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fuel_route'

    def ready(self):
        logging.info("Fuel Route application is ready")
        # You can add any startup logic here, such as:
        # - Loading initial data
        # - Setting up background tasks
        # - Initializing external services