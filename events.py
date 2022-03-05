from typing import Literal, Any, ContextManager, Callable, Generic, TypeVar
from dataclasses import dataclass
from collections import defaultdict
from contextlib import contextmanager


EventContent = TypeVar('EventContent')


@dataclass
class EventRecord:
    type: Literal['subscribe', 'publish']
    event: str
    args: tuple[Any]

    def __str__(self) -> str:
        args_str = ', '.join(str(_) for _ in self.args)
        return f'{self.type} {self.event}: ({args_str})'


class Events:
    def __init__(self):
        self._events = defaultdict(list)
        self.records = None  # type: list | None

    def subscribe(self, event: str, callback: callable):
        if self.records is not None:
            self.records.append(EventRecord(type='subscribe', event=event, args=(callback.__qualname__,)))
        self._events[event].append(callback)

    def publish(self, event, *args, **kwargs):
        if self.records is not None:
            self.records.append(EventRecord(
                type='publish', event=event, args=tuple(args) + tuple(_ for _ in kwargs.values())))
        for callback in self._events[event]:
            callback(*args, **kwargs)


class Event(Generic[EventContent]):
    name: str

    def __init__(self, events: Events):
        self._events = events

    def subscribe(self, callback: Callable[[EventContent], None]):
        self._events.subscribe(self.name, callback)

    def publish(self, content: EventContent):
        self._events.publish(self.name, content)


@contextmanager
def capture_events(events: Events) -> ContextManager[list[EventRecord]]:
    records = []
    events.records = records
    try:
        yield records
    finally:
        events.records = None
