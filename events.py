from typing import Literal, Any, ContextManager, Callable, Generic, TypeVar, Protocol, Optional
from dataclasses import dataclass
import datetime as dt
from collections import defaultdict
from contextlib import contextmanager

EventContent = TypeVar('EventContent')


class EventCallback(Protocol[EventContent]):
    def __call__(self, timestamp: dt.datetime, content: EventContent) -> None: ...


def _format_template(template: str, **kwargs: Any) -> str:
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f'Missing argument {e.args[0]}')


@dataclass
class EventRecord:
    type: Literal['sub', 'pub', 'unsub']
    event: str
    timestamp: dt.datetime
    content: Any

    def __str__(self) -> str:
        return f'{self.timestamp} {self.type} {self.event}: {self.content}'


class Events:
    def __init__(self, now: Callable[[], dt.datetime] = dt.datetime.now):
        self._now = now
        self._events = defaultdict(list)  # type: dict[str, list[EventCallback]]
        self.records = None  # type: Optional[list]

    def inspect_subscription(self) -> dict:
        return {event: [_.__qualname__ for _ in callbacks] for event, callbacks in self._events.items()}

    def subscribe(self, event: str, callback: EventCallback):
        if self.records is not None:
            record = EventRecord(type='sub', event=event, timestamp=self._now(), content=callback.__qualname__)
            self.records.append(record)
            print(f'{len(self.records)}.{record}')
        self._events[event].append(callback)

    def unsubscribe(self, event: str, callback: EventCallback):
        if self.records is not None:
            record = EventRecord(type='unsub', event=event, timestamp=self._now(), content=callback.__qualname__)
            self.records.append(record)
            print(f'{len(self.records)}.{record}')
        self._events[event].remove(callback)

    def publish(self, event: str, content: Any):
        if self.records is not None:
            record = EventRecord(type='pub', event=event, timestamp=self._now(), content=content)
            self.records.append(record)
            print(f'{len(self.records)}.{record}')
        for callback in self._events[event]:
            callback(timestamp=self._now(), content=content)


class Event(Generic[EventContent]):
    name_template: str

    def __init__(self, events: Events, **kwargs):
        self._events = events
        self.name = _format_template(self.name_template, **kwargs)

    def subscribe(self, callback: EventCallback[EventContent]):
        self._events.subscribe(self.name, callback)

    def unsubscribe(self, callback: EventCallback[EventContent]):
        self._events.unsubscribe(self.name, callback)

    def publish(self, content: EventContent):
        self._events.publish(self.name, content=content)


@contextmanager
def capture_events(events: Events) -> ContextManager[list[EventRecord]]:
    records = []
    events.records = records
    print('\n---captured events---')
    try:
        yield records
    finally:
        events.records = None
