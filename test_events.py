import pytest

from events import capture_events, Events, Event, _format_template


class DataRecorder:
    def __init__(self):
        self.data = None

    def record(self, *args, **kwargs):
        self.data = {'args': args, 'kwargs': kwargs}

    async def async_record(self, *args, **kwargs):
        self.data = {'args': args, 'kwargs': kwargs}


@pytest.fixture
def events() -> Events:
    return Events()


@pytest.fixture
def data_recorder() -> DataRecorder:
    return DataRecorder()


@pytest.fixture
def dummy_event(events) -> Event[float]:
    class _Event(Event[float]):
        name_template = '{var}_event'
    return _Event(events, var='test')


def test_format_template():
    assert _format_template('{var}_event', var='test') == 'test_event'
    with pytest.raises(ValueError) as excinfo:
        _format_template('{var}_event')
    assert str(excinfo.value) == 'Missing argument var'
    with pytest.raises(ValueError) as excinfo:
        _format_template('{var}_event', invalid_arg='a')
    assert str(excinfo.value) == 'Missing argument var'


def test_events(events, data_recorder):
    event_name = 'event_1'
    with capture_events(events) as records:
        events.subscribe(event_name, data_recorder.record)
        events.publish(event_name, 1, 2, c=None)
    assert events.inspect_subscription() == {event_name: ['DataRecorder.record']}
    assert [str(_) for _ in records] == [
        f'subscribe {event_name}: (DataRecorder.record)',
        f'publish {event_name}: (1, 2, None)']
    assert data_recorder.data == (prev_data := {'args': (1, 2), 'kwargs': {'c': None}})

    with capture_events(events) as records:
        events.unsubscribe(event_name, data_recorder.record)
        events.publish(event_name, 'will not recorded')
    assert [str(_) for _ in records] == [
        f'unsubscribe {event_name}: (DataRecorder.record)',
        f'publish {event_name}: (will not recorded)']
    assert data_recorder.data == prev_data


def test_event(events, data_recorder, dummy_event):
    with capture_events(events) as records:
        dummy_event.subscribe(callback=data_recorder.record)
        dummy_event.publish(content=1.23)
    assert [str(_) for _ in records] == [
        f'subscribe {dummy_event.name}: (DataRecorder.record)',
        f'publish {dummy_event.name}: (1.23)']
    assert data_recorder.data == (prev_data := {'args': (1.23,), 'kwargs': {}})
    with capture_events(events) as records:
        dummy_event.unsubscribe(callback=data_recorder.record)
        dummy_event.publish(content=3.21)
    assert [str(_) for _ in records] == [
        f'unsubscribe {dummy_event.name}: (DataRecorder.record)',
        f'publish {dummy_event.name}: (3.21)']
    assert data_recorder.data == prev_data


if __name__ == '__main__':
    pytest.main()
