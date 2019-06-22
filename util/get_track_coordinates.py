# This script transforms openstreetmap geojson data to a list of coordinates.
#
# It takes two command line arguments:
# - A path to a file containing the relevant way_ids
# - A path to the geojson file
#
# Each way ID represents part of a road, including racetracks.
# Therefore, to get the coordinates for a racetrack we simply need to know the way_ids.


import json
import re
import sys


def main():
    if len(sys.argv) != 3:
        print('Usage: python way_ids.txt silverstone.geojson')
        exit(-1)

    way_ids_path = sys.argv[1]
    geojson_path = sys.argv[2]

    print('Starting')

    with open(way_ids_path) as f:
        way_ids = f.readlines()

    with open(geojson_path) as f:
        data = json.load(f)

    features = data['features']

    print('Building features dictionary')

    features_dict = {}
    for feature in features:
        full_id = feature['id']
        match = re.match('[a-zA-Z]+/([0-9]+)', full_id)
        numeric_id = match.group(1)
        features_dict[numeric_id] = feature

    print('Done')

    print(features_dict.keys())

    track_coordinates = []

    for way_id in way_ids:
        way_id = way_id[:-1] # Get rid of newline
        print(f'Processing way ID {way_id}')
        feature = features_dict[way_id]
        coordinates = feature['geometry']['coordinates']  # There is an extra array
        for c in coordinates:
            track_coordinates.append((c[1], c[0]))

    # Last coordinate is equal to the first, so we have to remove it
    track_coordinates = track_coordinates[:-1]

    print('Writing output file')
    with open('track_coordinates.json', 'w') as f:
        json.dump(track_coordinates, f)

    print('Done')



if __name__ == '__main__':
    main()
