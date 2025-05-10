from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Optional
from app.services.websocket import manager
import uuid

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, 
    search_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for clients to connect and receive real-time updates.
    
    If search_id is provided, the client will only receive updates related to that search.
    If no search_id is provided, a new one will be generated.
    """
    # If no search ID is provided, generate one
    if not search_id:
        search_id = str(uuid.uuid4())
    
    # Accept the connection and register it
    connection_id = await manager.connect(websocket, search_id)
    
    # Send initial connection confirmation with search_id
    await websocket.send_json({
        "type": "connection_established",
        "connection_id": connection_id,
        "search_id": search_id
    })
    
    try:
        # Keep the connection alive
        while True:
            # Wait for any messages from the client (can be used for pings/keepalive)
            data = await websocket.receive_text()
            # Echo back as a simple acknowledgment
            await websocket.send_json({
                "type": "ack",
                "message": f"Message received: {data}"
            })
    except WebSocketDisconnect:
        # Remove the connection when the client disconnects
        manager.disconnect(connection_id)