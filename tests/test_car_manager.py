from datetime import datetime
from unittest import mock

from telemetry.car import Car
from telemetry.car_manager import CarManager

# So we can test when the callback is triggered
events = []


def event_callback(event):
    events.append(event)


def setup_function():
    events.clear()


@mock.patch('telemetry.track_lookup.TrackLookup')
def test_should_create_car_objects(track_lookup_mock):
    manager = CarManager(5, track_lookup_mock)
    assert len(manager.cars) == 5

    for i in range(5):
        assert manager.cars[i].index == i


@mock.patch('telemetry.track_lookup.TrackLookup')
def test_should_update_car_speeds(track_lookup_mock):

    manager = CarManager(2, track_lookup_mock)
    manager.subscribe_to_car_status_events(event_callback)

    track_lookup_mock.get_track_percentage.return_value = 0

    car_1_json_1 = {
        "timestamp": 1541693114862,
        "carIndex": 0,
        "location": {
            "lat": 51.349937311969725,
            "long": -0.544958142167281
        }
    }

    car_1_json_2 = {
        "timestamp": 1541693115862,
        "carIndex": 0,
        "location": {
            "lat": 51.359937311969725,
            "long": -0.544958142167281
        }
    }

    car_2_json_1 = {
        "timestamp": 1541693114862,
        "carIndex": 1,
        "location": {
            "lat": 51.349937311969725,
            "long": -0.544958142167281
        }
    }

    car_2_json_2 = {
        "timestamp": 1541693116862,
        "carIndex": 1,
        "location": {
            "lat": 51.359937311969725,
            "long": -0.544958142167281
        }
    }

    manager.new_car_data(car_1_json_1)
    manager.new_car_data(car_2_json_1)
    manager.new_car_data(car_1_json_2)
    manager.new_car_data(car_2_json_2)

    assert round(manager.cars[0].speed_metres_per_second) == 1113
    assert round(manager.cars[1].speed_metres_per_second) == 556

    speed_events = [x for x in events if x['type'] == 'SPEED']

    assert speed_events[2]['timestamp'] == 1541693115862
    assert speed_events[2]['carIndex'] == 0
    assert speed_events[2]['type'] == 'SPEED'
    assert round(speed_events[2]['value']) == 1113

    assert speed_events[3]['timestamp'] == 1541693116862
    assert speed_events[3]['carIndex'] == 1
    assert speed_events[3]['type'] == 'SPEED'
    assert round(speed_events[3]['value']) == 556


@mock.patch('telemetry.track_lookup.TrackLookup')
def test_should_update_car_positions(track_lookup_mock):
    manager = CarManager(3, track_lookup_mock)
    manager.subscribe_to_car_status_events(event_callback)

    for c in manager.cars:
        c.timestamp = datetime.utcfromtimestamp(1541693115862 / 1000)

    manager.cars[0].progress = 0.4
    manager.cars[1].progress = 1.2
    manager.cars[2].progress = 0.8

    manager.update_positions()

    assert manager.cars[0].position == 3
    assert manager.cars[1].position == 1
    assert manager.cars[2].position == 2

    manager.cars[0].progress = 1.4
    manager.cars[1].progress = 1.8
    manager.cars[2].progress = 1.3

    for c in manager.cars:
        c.timestamp = datetime.utcfromtimestamp(1541693116862 / 1000)

    manager.update_positions()

    assert manager.cars[0].position == 2
    assert manager.cars[1].position == 1
    assert manager.cars[2].position == 3

    position_events = [x for x in events if x['type'] == 'POSITION']

    assert position_events[0]['timestamp'] == 1541693115862
    assert position_events[0]['carIndex'] == 1
    assert position_events[0]['type'] == 'POSITION'
    assert position_events[0]['value'] == 1

    assert position_events[1]['timestamp'] == 1541693115862
    assert position_events[1]['carIndex'] == 2
    assert position_events[1]['type'] == 'POSITION'
    assert position_events[1]['value'] == 2

    assert position_events[2]['timestamp'] == 1541693115862
    assert position_events[2]['carIndex'] == 0
    assert position_events[2]['type'] == 'POSITION'
    assert position_events[2]['value'] == 3

    assert position_events[3]['timestamp'] == 1541693116862
    assert position_events[3]['carIndex'] == 0
    assert position_events[3]['type'] == 'POSITION'
    assert position_events[3]['value'] == 2

    assert position_events[4]['timestamp'] == 1541693116862
    assert position_events[4]['carIndex'] == 2
    assert position_events[4]['type'] == 'POSITION'
    assert position_events[4]['value'] == 3
