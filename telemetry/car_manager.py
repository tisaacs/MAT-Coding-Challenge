from datetime import timedelta

from telemetry import config
from telemetry.car import Car
from telemetry.helper import get_timestamp_in_correct_format

UPDATE_TOLERANCE = timedelta(milliseconds=300)  # Processes position values when all timestamps within this value


class CarManager():
    def __init__(self, number_of_cars, track_lookup):
        self.cars = []
        self.__car_status_event_callbacks = []

        for i in range(number_of_cars):
            car = Car(i, track_lookup)
            self.cars.append(car)

    def new_car_data(self, json):
        # We can only calculate positions when all cars have had an update
        index = json['carIndex']

        self.cars[index].update(json)

        self.__raise_speed_event(self.cars[index])

        received_all_updates = all(
            len(x.timestamps) and x.timestamps[0] - self.cars[0].timestamps[0] < UPDATE_TOLERANCE for x in self.cars)
        if received_all_updates:
            self.update_positions()

    def update_positions(self):
        cars_ordered = sorted(self.cars, key=lambda x: x.progress, reverse=True)
        for i, car in enumerate(cars_ordered):
            position = i + 1

            if len(car.positions) == config.POSITION_COUNT:
                car.positions.pop()

            car.positions.appendleft(position)

            # Raise initial position events
            if len(car.positions) == 1:
                self.__raise_position_event(car)
                continue

            if len(car.positions) != config.POSITION_COUNT:
                continue

            # If all positions are the same, nothing has changed so we don't want to raise an event
            if car.positions[0] == car.positions[-1]:
                continue

            # Position must be 'stable' apart from the last item
            positions_apart_from_last_item = list(car.positions)[:-1]
            if all(x == car.positions[0] for x in positions_apart_from_last_item):
                self.__raise_position_event(car)

    def subscribe_to_car_status_events(self, callback):
        self.__car_status_event_callbacks.append(callback)

    def __raise_speed_event(self, car):
        event = {
            'timestamp': get_timestamp_in_correct_format(car.timestamps[0]),
            'carIndex': car.index,
            'type': 'SPEED',
            'value': car.speed_metres_per_second,
        }

        self.__raise_event(event)

    def __raise_position_event(self, car):
        event = {
            'timestamp': get_timestamp_in_correct_format(car.timestamps[0]),
            'carIndex': car.index,
            'type': 'POSITION',
            'value': car.positions[0]
        }

        self.__raise_event(event)

    def __raise_event(self, event):
        for c in self.__car_status_event_callbacks:
            c(event)
