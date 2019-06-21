from .car import Car
from datetime import timedelta

UPDATE_TOLERANCE = timedelta(milliseconds=300)  # Processes position values when all timestamps within this value


class CarManager():
    def __init__(self, number_of_cars, speed_update_callback):
        self.cars = []
        self.speed_update_callback = speed_update_callback

        for i in range(number_of_cars):
            car = Car(i)
            self.cars.append(car)

    def new_car_data(self, json):
        # We can only calculate positions when all cars have had an update
        index = json['carIndex']

        self.cars[index].update_speed(json)
        self.speed_update_callback(self.cars[index])

        received_all_updates = all(x.timestamp and x.timestamp - self.cars[0].timestamp < UPDATE_TOLERANCE for x in self.cars)

        if received_all_updates:
            self.update_positions()

    def update_positions(self):
        pass
