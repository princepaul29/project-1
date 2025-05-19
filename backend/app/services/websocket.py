from fastapi import WebSocket
from typing import Dict, List, Set, Any
import json
import uuid
import asyncio
from datetime import datetime

class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts messages to connected clients.
    """
    def __init__(self):
        # Maps connection_id to WebSocket instance
        self.active_connections: Dict[str, WebSocket] = {}
        # Maps search_id to set of connection_ids
        self.search_subscriptions: Dict[str, Set[str]] = {}
        # Maps connection_id to search_id
        self.connection_searches: Dict[str, str] = {}
        
    async def connect(self, websocket: WebSocket, search_id: str) -> str:
        """
        Accept a new WebSocket connection and register it with a search ID.
        Returns a unique connection ID.
        """
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        # Register this connection for the search ID
        if search_id not in self.search_subscriptions:
            self.search_subscriptions[search_id] = set()
        self.search_subscriptions[search_id].add(connection_id)
        self.connection_searches[connection_id] = search_id
        
        return connection_id
        
    def disconnect(self, connection_id: str) -> None:
        """
        Remove a connection when it's closed.
        """
        if connection_id in self.active_connections:
            # Get the search_id this connection was subscribed to
            search_id = self.connection_searches.get(connection_id)
            if search_id and search_id in self.search_subscriptions:
                # Remove this connection from the search subscriptions
                self.search_subscriptions[search_id].discard(connection_id)
                # Clean up empty subscription sets
                if not self.search_subscriptions[search_id]:
                    del self.search_subscriptions[search_id]
            
            # Remove from active connections and connection mapping
            del self.active_connections[connection_id]
            if connection_id in self.connection_searches:
                del self.connection_searches[connection_id]
    
    # For SQLModel objects, explicitly handle SQLAlchemy attributes
    def sqlmodel_to_dict(self, model):
        """Convert SQLModel object to dictionary, handling relationships properly"""
        if model is None:
            return None
        
        # Get all columns defined in the model
        data = {}
        for column in model.__table__.columns:
            attr_name = column.name
            value = getattr(model, attr_name)
            
            # Handle datetime objects specially
            if isinstance(value, datetime):
                data[attr_name] = value.isoformat()
            else:
                data[attr_name] = value
        
        return data

    def _serialize_datetime(self, obj): 
        if isinstance(obj, datetime.datetime): 
            return obj.isoformat() 
        raise TypeError("Type not serializable") 

    async def broadcast_to_search(self, search_id: str, message: Any) -> None:
        """
        Send a message to all connections subscribed to a specific search ID.
        """
        if search_id not in self.search_subscriptions:
            return
            
        # Convert message to JSON if it's not already a string
        if not isinstance(message, str):
            if hasattr(message, "model_dump"):
                # For Pydantic models
                message_str = json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "data": message.model_dump(mode="json")
                })
            elif hasattr(message, "__dict__"):
                # For regular classes
                message_str = json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "data": message.__dict__
                })
            else:
                # For dictionaries and other JSON-serializable objects
                message_str = json.dumps({
                    "timestamp": datetime.now().isoformat(),
                    "data": message
                })
        else:
            message_str = message
            
        disconnected = set()
        # Send to all subscribers
        for connection_id in self.search_subscriptions[search_id]:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_text(message_str)
                except RuntimeError:
                    # Connection might be closed or invalid
                    disconnected.add(connection_id)
            else:
                disconnected.add(connection_id)
                
        # Clean up any disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
            
    async def broadcast_to_all(self, message: Any) -> None:
        """
        Send a message to all active connections.
        """
        if not isinstance(message, str):
            message_str = json.dumps({
                "timestamp": datetime.now().isoformat(),
                "data": message
            })
        else:
            message_str = message
            
        disconnected = set()
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message_str)
            except RuntimeError:
                disconnected.add(connection_id)
                
        # Clean up any disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)

# Create a global instance of the connection manager
manager = ConnectionManager()