# MAT Fan Engagement Coding Challenge

## Prerequisites:

* [docker](https://docs.docker.com/)
* [docker-compose](https://docs.docker.com/compose/)

## Setup Notes

1. Create a new virtual environment:

```console
$ python3 -m venv venv
```

1. Activate the new virtual environment:

```console
$ source venv/bin/activate
```

1. Install dependencies:

```console
$ pip install -r requirements.txt
```

1. Download docker containers:

```console
$ docker-compose pull
```

## To Run Application

```console
$ docker-compose up -d
```

```console
$ python runner.py
```

## To Stop Application

Hit `ctrl-c`, then run:

```console
$ docker-compose down
```

## To Run Tests

```
$ pytest
```

## Implementation Notes

- To calculate the speed of each car, we calculate the geodesic distance between the updates and divide by the time.
To filter noise, we average a number measurements.

- To calculate the position of each car, we calculate the percentage of the lap completed.
[This file](data/track_coordinates.json) contains a list of coordinates for the track.
This means to calculate the percentage of a lap completed, we simply find the closest coordinate and use its position in the list.
The file is generated from openstreetmap data, using [this script](util/get_track_coordinates.py) to convert it to the right format.

- To stop multiple overtake events from being generated when cars are close to each other, we require a car to be 'ahead' of another car for a number of updates before we generate an event.
