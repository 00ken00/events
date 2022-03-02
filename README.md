![CI](https://github.com/KenExplore/exchange-api/actions/workflows/ci.yml/badge.svg)

## events

A module for event-driven architecture with publish/subscribe.


## Quickstart

```python
from events import Events
events = Events()
events.subscribe('event_1', callback)
events.publish('event_1', *args, **kwargs)
```
