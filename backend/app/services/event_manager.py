from typing import Dict, List, Callable, Any, Coroutine
import asyncio
import logging

logger = logging.getLogger(__name__)

# Type for event handlers: async function that takes any args
Handler = Callable[..., Coroutine[Any, Any, None]]

class EventManager:
    _handlers: Dict[str, List[Handler]] = {}

    @classmethod
    def subscribe(cls, event_name: str, handler: Handler):
        if event_name not in cls._handlers:
            cls._handlers[event_name] = []
        cls._handlers[event_name].append(handler)
        logger.info(f"Subscribed to event: {event_name}")

    @classmethod
    async def emit(cls, event_name: str, *args, **kwargs):
        if event_name not in cls._handlers:
            return
        
        # Run all handlers as background tasks to decouple
        for handler in cls._handlers[event_name]:
            asyncio.create_task(handler(*args, **kwargs))
        
        logger.debug(f"Emitted event: {event_name}")

# Global instance for easy access
event_manager = EventManager()
