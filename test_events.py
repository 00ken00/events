import pytest
import datetime as dt
from typing import Any

from events import capture_events, Events, Event, _format_template


def _timestamp(n: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(n)


class DataRecorder:
    def __init__(self):
        self.data = None

    def record(self, content: Any):
        self.data = content


class _Event(Event[float]):
    name_template = '{var}_event'


@pytest.fixture
def events() -> Events:
    return Events()


@pytest.fixture
def data_recorder() -> DataRecorder:
    return DataRecorder()


@pytest.fixture
def dummy_event(events) -> _Event:
    return _Event(events, now=lambda: _timestamp(1), var='test')


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
        events.publish(event_name, content=1.23)
    assert events.inspect_subscription() == {event_name: ['DataRecorder.record']}
    assert [str(_) for _ in records] == [
        'sub event_1: DataRecorder.record',
        'pub event_1: 1.23']
    assert data_recorder.data == 1.23

    with capture_events(events) as records:
        events.unsubscribe(event_name, data_recorder.record)
        events.publish(event_name, content='will not recorded')
    assert [str(_) for _ in records] == [
        'unsub event_1: DataRecorder.record',
        'pub event_1: will not recorded']
    assert data_recorder.data == 1.23


def test_event(events, data_recorder, dummy_event):
    with capture_events(events) as records:
        dummy_event.subscribe(callback=data_recorder.record)
        dummy_event.publish(content=1.23)
    assert [str(_) for _ in records] == [
        'sub test_event: DataRecorder.record',
        'pub test_event: 1.23']
    assert data_recorder.data == 1.23
    with capture_events(events) as records:
        dummy_event.unsubscribe(callback=data_recorder.record)
        dummy_event.publish(content=3.21)
    assert [str(_) for _ in records] == [
        'unsub test_event: DataRecorder.record',
        'pub test_event: 3.21']
    assert data_recorder.data == 1.23


def test_event_error(events, dummy_event):
    def _raise(content: float):
        raise RuntimeError('test error')

    dummy_event.subscribe(_raise)
    with pytest.raises(RuntimeError, match='test error'):
        dummy_event.publish(content=1.23)


def test_type_hint(dummy_event):
    def invalid_event_callback(content: int): pass
    def valid_event_callback(content: float): pass
    dummy_event.subscribe(invalid_event_callback)  # should highlight error in Pycharm
    dummy_event.subscribe(valid_event_callback)


if __name__ == '__main__':
    pytest.main()
