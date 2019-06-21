from geopy import distance
from datetime import datetime


class Car():
    def __init__(self, car_index):
        self.index = car_index
        self.coordinates = (0, 0)
        self.speed_metres_per_second = 0
        self.position = 0
        self.timestamp = 0
        self.last_coordinates = (0, 0)
        self.last_position = 0
        self.last_timestamp = 0

    def update_speed(self, json):
        self.last_coordinates = self.coordinates
        self.last_timestamp = self.timestamp

        self.coordinates = (json['location']['lat'], json['location']['long'])
        self.timestamp = datetime.utcfromtimestamp(json['timestamp'] / 1000.0)

        if self.last_timestamp == 0:
            return

        displacement = distance.distance(self.coordinates, self.last_coordinates).km
        time_delta = self.timestamp - self.last_timestamp
        self.speed_metres_per_second = displacement * 1000 / time_delta.total_seconds()
