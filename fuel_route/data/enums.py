from enum import Enum, unique


@unique
class FuelType(Enum):
    GASOLINE = "Gasoline"
    DIESEL = "Diesel"
    ELECTRIC = "Electric"


@unique
class VehicleType(Enum):
    CAR = "Car"
    TRUCK = "Truck"
    VAN = "Van"


@unique
class VehicleProfile(Enum):
    """
    ORS Route profiles enums class
    """

    CAR = "driving-car"
    TRUCK = "driving-hgv"
    WALKING = "foot-walking"
    HIKING = "foot-hiking"
    REGULAR_BIKE = "cycling-regular"
    ROAD_BIKE = "cycling-road"
    MOUNTAIN_BIKE = "cycling-mountain"


# Constants
METERS_TO_MILES = 1609.34
