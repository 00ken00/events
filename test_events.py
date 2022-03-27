import pytest

from events import capture_events, Events, Event, _format_template


class Data:
    def __init__(self):
        self.data = None

    def record(self, *args, **kwargs):
        self.data = {'args': args, 'kwargs': kwargs}


class TestEvent(Event[float]):
    name_template = '{var}_event'


def test_format_template():
    assert _format_template('{var}_event', var='test') == 'test_event'
    with pytest.raises(ValueError) as excinfo:
        _format_template('{var}_event')
    assert str(excinfo.value) == 'Missing argument var'
    with pytest.raises(ValueError) as excinfo:
        _format_template('{var}_event', invalid_arg='a')
    assert str(excinfo.value) == 'Missing argument var'


def test_events():
    events = Events()
    data = Data()
    with capture_events(events) as records:
        events.subscribe('event_1', data.record)
        events.publish('event_1', 1, 2, c=None)
    assert [str(_) for _ in records] == [
        'subscribe event_1: (Data.record)', 'publish event_1: (1, 2, None)']
    assert data.data == {'args': (1, 2), 'kwargs': {'c': None}}
    assert events.inspect_subscription() == {'event_1': ['Data.record']}


def test_event():
    events = Events()
    data = Data()
    events.subscribe('event_1', data.record)
    events.publish('event_1', 1, 2, c=None)
    assert data.data == {'args': (1, 2), 'kwargs': {'c': None}}
    event = TestEvent(events, var='test')
    data = Data()
    with capture_events(events) as records:
        event.subscribe(callback=data.record)
        event.publish(content=1.23)
    assert [str(_) for _ in records] == [
        'subscribe test_event: (Data.record)', 'publish test_event: (1.23)']
    assert data.data == {'args': (1.23,), 'kwargs': {}}


if __name__ == '__main__':
    pytest.main()
