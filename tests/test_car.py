from datetime import datetime
from math import isclose
from unittest import mock

import pytest
import telemetry
import telemetry.config as config
from telemetry.car import Car
from telemetry.track_lookup import TrackLookup


@mock.patch('telemetry.track_lookup.TrackLookup')
def test_update(track_lookup_mock):
    config.SPEED_AVERAGE_COUNT = 3

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

    json_3 = {
        "timestamp": 1541693116862,
        "carIndex": 1,
        "location": {
            "lat": 51.379937311969725,
            "long": -0.544958142167281
        }
    }

    json_4 = {
        "timestamp": 1541693117862,
        "carIndex": 1,
        "location": {
            "lat": 51.399937311969725,
            "long": -0.544958142167281
        }
    }

    track_lookup_mock.get_track_percentage.return_value = 0.1

    car.update(json_1)

    track_lookup_mock.get_track_percentage.assert_called_with((51.349937311969725, -0.544958142167281))

    assert car.coordinates[0] == (51.349937311969725, -0.544958142167281)
    assert car.timestamps[0] == datetime(2018, 11, 8, 16, 5, 14, 862000)
    assert car.progress == 0.1
    assert len(car.coordinates) == 1
    assert len(car.timestamps) == 1

    track_lookup_mock.get_track_percentage.return_value = 0.2

    car.update(json_2)

    assert car.coordinates[0] == (51.359937311969725, -0.544958142167281)
    assert car.timestamps[0] == datetime(2018, 11, 8, 16, 5, 15, 862000)
    assert isclose(car.progress, 0.3)
    assert len(car.coordinates) == 2
    assert len(car.timestamps) == 2

    # We don't calculate until we have enough data
    assert car.speed_metres_per_second == 0

    car.update(json_3)

    assert car.coordinates[0] == (51.379937311969725, -0.544958142167281)
    assert car.timestamps[0] == datetime(2018, 11, 8, 16, 5, 16, 862000)
    assert len(car.coordinates) == 3
    assert len(car.timestamps) == 3

    assert round(car.speed_metres_per_second) == 1669

    car.update(json_4)

    assert car.coordinates[0] == (51.399937311969725, -0.544958142167281)
    assert car.timestamps[0] == datetime(2018, 11, 8, 16, 5, 17, 862000)
    assert len(car.coordinates) == 3
    assert len(car.timestamps) == 3

    assert round(car.speed_metres_per_second) == 2225


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
