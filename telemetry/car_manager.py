from datetime import timedelta

from telemetry.helper import get_timestamp_in_correct_format
from telemetry.car import Car

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

        received_all_updates = all(len(x.timestamps) and x.timestamps[0] - self.cars[0].timestamps[0] < UPDATE_TOLERANCE
                                   for x in self.cars)
        if received_all_updates:
            self.update_positions()

    def update_positions(self):
        cars_ordered = sorted(self.cars, key=lambda x: x.progress, reverse=True)
        for i, car in enumerate(cars_ordered):
            car.last_position = car.position
            car.position = i + 1

            if car.position != car.last_position:
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
            'value': car.position
        }

        self.__raise_event(event)

    def __raise_event(self, event):
        for c in self.__car_status_event_callbacks:
            c(event)
