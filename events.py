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

    def inspect_subscription(self) -> dict:
        return {event: [_.__qualname__ for _ in callbacks] for event, callbacks in self._events.items()}

    def subscribe(self, event: str, callback: callable):
        if self.records is not None:
            record = EventRecord(type='subscribe', event=event, args=(callback.__qualname__,))
            self.records.append(record)
            print(f'{len(self.records)}.{record}')
        self._events[event].append(callback)

    def publish(self, event, *args, **kwargs):
        if self.records is not None:
            record = EventRecord(type='publish', event=event, args=tuple(args) + tuple(_ for _ in kwargs.values()))
            self.records.append(record)
            print(f'{len(self.records)}.{record}')
        for callback in self._events[event]:
            callback(*args, **kwargs)


class Event(Generic[EventContent]):
    name_template: str

    def __init__(self, events: Events, **kwargs):
        self._events = events
        self.name = self.name_template.format(**kwargs)

    def subscribe(self, callback: Callable[[EventContent], None]):
        self._events.subscribe(self.name, callback)

    def publish(self, content: EventContent):
        self._events.publish(self.name, content)


@contextmanager
def capture_events(events: Events) -> ContextManager[list[EventRecord]]:
    records = []
    events.records = records
    print('\n---captured events---')
    try:
        yield records
    finally:
        events.records = None
