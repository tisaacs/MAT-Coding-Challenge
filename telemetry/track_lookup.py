import json
from scipy import spatial


class TrackLookup():
    def __init__(self, track_coordinates_path):
        self.__build_lookup(track_coordinates_path)

    def get_track_percentage(self, coordinates):
        result = self.tree.query(coordinates)
        index = result[1]
        percentage = index / self.number_of_points
        return percentage

    def __build_lookup(self, track_coordinates_path):
        with open(track_coordinates_path) as f:
            data = json.load(f)

        self.number_of_points = len(data)
        self.tree = spatial.KDTree(data)

