from datetime import timedelta

from telemetry import config
from telemetry.car import Car
from telemetry.helper import get_timestamp_in_correct_format

UPDATE_TOLERANCE = timedelta(milliseconds=300)  # Processes position values when all timestamps within this value


class CarManager():
    def __init__(self, number_of_cars, track_lookup):
        self.cars = []
        self.__car_status_event_callbacks = []
        self.__race_event_callbacks = []
        self.__last_position_event_for_car_map = {}

        for i in range(number_of_cars):
            car = Car(i, track_lookup)
            self.cars.append(car)
            self.__last_position_event_for_car_map[i] = None

    def new_car_data(self, json):
        # We can only calculate positions when all cars have had an update
        index = json['carIndex']

        self.cars[index].update(json)

        self.__raise_speed_event(self.cars[index])

        received_all_updates = all(x.timestamps and x.timestamps[0] - self.cars[0].timestamps[0] < UPDATE_TOLERANCE
                                   for x in self.cars)
        if received_all_updates:
            self.update_positions()

    def update_positions(self):
        cars_ordered = sorted(self.cars, key=lambda x: x.progress, reverse=True)
        for i, car in enumerate(cars_ordered):
            position = i + 1

            if len(car.positions) == config.POSITION_COUNT:
                car.positions.pop()

            car.positions.appendleft(position)

            last_position = self.__last_position_event_for_car_map[car.index]

            # Position is the same as last event
            if car.positions[0] == last_position:
                continue

            # Check position has been the same for the past N updates
            if all(x == car.positions[0] for x in car.positions):
                self.__last_position_event_for_car_map[car.index] = car.positions[0]
                self.__raise_position_event(car)

                if last_position and car.positions[0] < last_position:
                    overtaken_car_index = cars_ordered[i + 1].index
                    self.__raise_overtake_event(car.index, overtaken_car_index, car.timestamps[0])

    def subscribe_to_car_status_events(self, callback):
        self.__car_status_event_callbacks.append(callback)

    def subscribe_to_race_events(self, callback):
        self.__race_event_callbacks.append(callback)

    def __raise_speed_event(self, car):
        event = {
            'timestamp': get_timestamp_in_correct_format(car.timestamps[0]),
            'carIndex': car.index,
            'type': 'SPEED',
            'value': car.speed_metres_per_second,
        }

        self.__raise_car_status_event(event)

    def __raise_position_event(self, car):
        event = {
            'timestamp': get_timestamp_in_correct_format(car.timestamps[0]),
            'carIndex': car.index,
            'type': 'POSITION',
            'value': car.positions[0]
        }

        self.__raise_car_status_event(event)

    def __raise_car_status_event(self, event):
        for c in self.__car_status_event_callbacks:
            c(event)

    def __raise_overtake_event(self, car_index, overtaken_car_index, timestamp):
        text = f'Car {car_index} races ahead of Car {overtaken_car_index} in a dramatic overtake.'
        event = {
            "timestamp": get_timestamp_in_correct_format(timestamp),
            "text": text,
        }

        for c in self.__race_event_callbacks:
            c(event)
