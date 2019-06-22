from telemetry.track_lookup import TrackLookup

lookup = None


def setup_module(module):
    global lookup
    lookup = TrackLookup('data/track_coordinates.json')


def test_get_track_percentage_start():
    result = lookup.get_track_percentage((52.0766819, -1.0214368))
    assert result == 0


def test_get_track_percentage_middle():
    result = lookup.get_track_percentage((52.0761712, -1.0216768))
    assert result != 0 and result != 1


def test_get_track_percentage_end():
    result = lookup.get_track_percentage((52.0766119, -1.0214952))

    # Check we're within 99% of end
    assert 1 - result < 0.01
