from events import capture_events, Events


class Data:
    def __init__(self):
        self.data = None

    def record(self, *args, **kwargs):
        self.data = {'args': args, 'kwargs': kwargs}


def test_events():
    events = Events()
    data = Data()
    with capture_events(events) as records:
        events.subscribe('event_1', data.record)
        events.publish('event_1', 1, 2, c=None)
    assert [str(_) for _ in records] == [
        'subscribe event_1: (Data.record)', 'publish event_1: (1, 2, None)']
    assert data.data == {'args': (1, 2), 'kwargs': {'c': None}}
