import pytest
from context import telemetry
from datetime import datetime
from telemetry.car import Car


def test_update_speed():
    car = Car(1)

    json_1 = {
        "timestamp": 1541693114862,
        "carIndex": 1,
        "location": {
            "lat": 51.349937311969725,
            "long": -0.544958142167281
        }
    }

    json_2 = {
        "timestamp": 1541693115862,
        "carIndex": 1,
        "location": {
            "lat": 51.359937311969725,
            "long": -0.544958142167281
        }
    }

    car.update_speed(json_1)

    assert car.coordinates == (51.349937311969725, -0.544958142167281)
    assert car.timestamp == datetime(2018, 11, 8, 16, 5, 14, 862000)

    car.update_speed(json_2)

    assert car.coordinates == (51.359937311969725, -0.544958142167281)
    assert car.timestamp == datetime(2018, 11, 8, 16, 5, 15, 862000)

    assert round(car.speed_metres_per_second) == 1113


def test_should_raise_exception_if_given_incorrect_data():
    car = Car(1)

    json = {
        "timestamp": 1541693114862,
        "carIndex": 2,
        "location": {
            "lat": 51.349937311969725,
            "long": -0.544958142167281
        }
    }

    with pytest.raises(ValueError):
        car.update_speed(json)
