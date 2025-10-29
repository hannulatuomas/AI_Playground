"""
Event Bus

Pub/sub event system for inter-module communication.
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """Event object."""
    type: str
    data: Dict[str, Any]
    timestamp: str
    source: str


class EventBus:
    """Event bus for pub/sub communication between modules."""
    
    def __init__(self):
        """Initialize event bus."""
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle event
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """
        Unsubscribe from events.
        
        Args:
            event_type: Type of event
            handler: Handler to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
    
    def publish(self, event: Event):
        """
        Publish event to all subscribers.
        
        Args:
            event: Event to publish
        """
        # Store in history
        self.event_history.append(event)
        
        # Notify subscribers
        if event.type in self.subscribers:
            for handler in self.subscribers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler for {event.type}: {e}")
    
    def emit(self, event_type: str, data: Dict[str, Any], source: str = "system"):
        """
        Convenience method to create and publish event.
        
        Args:
            event_type: Type of event
            data: Event data
            source: Source module
        """
        event = Event(
            type=event_type,
            data=data,
            timestamp=datetime.now().isoformat(),
            source=source
        )
        self.publish(event)
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_type: Optional filter by type
            limit: Maximum events to return
            
        Returns:
            List of events
        """
        if event_type:
            events = [e for e in self.event_history if e.type == event_type]
        else:
            events = self.event_history
        
        return events[-limit:]
    
    def clear_history(self):
        """Clear event history."""
        self.event_history.clear()
