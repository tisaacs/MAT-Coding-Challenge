from datetime import timedelta

import telemetry.helper as helper
from .car import Car

UPDATE_TOLERANCE = timedelta(milliseconds=300)  # Processes position values when all timestamps within this value


class CarManager():
    def __init__(self, number_of_cars, track_lookup, car_status_event_callback):
        self.cars = []
        self.car_status_event_callback = car_status_event_callback

        for i in range(number_of_cars):
            car = Car(i, track_lookup)
            self.cars.append(car)

    def new_car_data(self, json):
        # We can only calculate positions when all cars have had an update
        index = json['carIndex']

        self.cars[index].update(json)
        event = self.__get_speed_event(self.cars[index])
        self.car_status_event_callback(event)

        received_all_updates = all(x.timestamp and x.timestamp - self.cars[0].timestamp < UPDATE_TOLERANCE
                                   for x in self.cars)
        if received_all_updates:
            self.update_positions()

    def update_positions(self):
        cars_ordered = sorted(self.cars, key=lambda x: x.progress, reverse=True)
        for i, car in enumerate(cars_ordered):
            car.last_position = car.position
            car.position = i + 1

            if car.position != car.last_position:
                event = self.__get_position_event(car)
                self.car_status_event_callback(event)

    def __get_speed_event(self, car):
        return {
            'timestamp': helper.get_timestamp_in_correct_format(car.timestamp),
            'carIndex': car.index,
            'type': 'SPEED',
            'value': car.speed_metres_per_second,
        }

    def __get_position_event(self, car):
        return {
            'timestamp': helper.get_timestamp_in_correct_format(car.timestamp),
            'carIndex': car.index,
            'type': 'POSITION',
            'value': car.position
        }
