from collections import deque
from datetime import datetime

from geopy import distance


 # We average speed over several measurements to reduce noise.
 # This constant determines how many values to use
SPEED_AVERAGE_COUNT = 5

class Car():
    def __init__(self, car_index, track_lookup):
        self.index = car_index
        self.coordinates = deque(maxlen=SPEED_AVERAGE_COUNT)
        self.speed_metres_per_second = 0
        self.progress = 0
        self.position = 0
        self.timestamps =  deque(maxlen=SPEED_AVERAGE_COUNT)
        self.last_position = 0
        self.__track_lookup = track_lookup

    def update(self, json):
        if json['carIndex'] != self.index:
            raise ValueError('Invalid carIndex')

        new_coordinate = (json['location']['lat'], json['location']['long'])

        if len(self.coordinates) == SPEED_AVERAGE_COUNT:
            self.coordinates.pop()
            self.timestamps.pop()

        self.coordinates.appendleft(new_coordinate)

        t = datetime.utcfromtimestamp(json['timestamp'] / 1000.0)
        self.timestamps.appendleft(t)

        self.progress += self.__track_lookup.get_track_percentage(self.coordinates[0])

        queue_full = len(self.coordinates) == SPEED_AVERAGE_COUNT
        if not queue_full:
            return

        speeds = []
        for i in range(SPEED_AVERAGE_COUNT - 1):
            current = self.coordinates[i]
            last = self.coordinates[i + 1]
            displacement = distance.distance(current, last).km

            time_delta = self.timestamps[i] - self.timestamps[i + 1]
            speed = displacement * 1000 / time_delta.total_seconds()
            speeds.append(speed)

        self.speed_metres_per_second = sum(speeds) / len(speeds)
