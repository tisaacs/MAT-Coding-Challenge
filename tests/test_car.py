from datetime import datetime
from math import isclose
from unittest import mock

import pytest
from context import telemetry
from telemetry.car import Car
from telemetry.track_lookup import TrackLookup


@mock.patch('telemetry.track_lookup.TrackLookup')
def test_update(track_lookup_mock):
    car = Car(1, track_lookup_mock)

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

    track_lookup_mock.get_track_percentage.return_value = 0.1

    car.update(json_1)

    assert car.coordinates == (51.349937311969725, -0.544958142167281)
    assert car.timestamp == datetime(2018, 11, 8, 16, 5, 14, 862000)
    assert car.progress == 0.1

    track_lookup_mock.get_track_percentage.return_value = 0.2

    car.update(json_2)

    assert car.coordinates == (51.359937311969725, -0.544958142167281)
    assert car.timestamp == datetime(2018, 11, 8, 16, 5, 15, 862000)
    assert isclose(car.progress, 0.3)

    assert round(car.speed_metres_per_second) == 1113


def test_should_raise_exception_if_given_incorrect_data():
    car = Car(1, None)

    json = {
        "timestamp": 1541693114862,
        "carIndex": 2,
        "location": {
            "lat": 51.349937311969725,
            "long": -0.544958142167281
        }
    }

    with pytest.raises(ValueError):
        car.update(json)
