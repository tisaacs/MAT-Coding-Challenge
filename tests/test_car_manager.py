from telemetry.car import Car
from telemetry.car_manager import CarManager

# So we can test when the callback is triggered
updated_car_indexes = []


def speed_update_callback(car):
    updated_car_indexes.append(car.index)


def test_should_create_car_objects():
    manager = CarManager(5, None)
    assert len(manager.cars) == 5

    for i in range(5):
        assert manager.cars[i].index == i


def test_should_update_speed_for_cars():

    manager = CarManager(2, speed_update_callback)

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

    assert updated_car_indexes == [0, 1, 0, 1]
