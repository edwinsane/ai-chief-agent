"""
WebSocket endpoint — prepared for future live event streaming.

Currently provides a simple connection that sends the latest
event summary on connect. In production, this would be upgraded to:
- Push new events as they're ingested
- Stream risk level changes
- Broadcast sweep completions

Usage (future React client):
    const ws = new WebSocket("ws://localhost:8000/api/ws/live");
    ws.onmessage = (e) => { const data = JSON.parse(e.data); ... };
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.predictions import generate_outlook
from app.storage.database import get_articles, get_freshness_info

router = APIRouter()


class ConnectionManager:
    """Tracks active WebSocket connections for broadcasting."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/ws/live")
async def live_feed(ws: WebSocket):
    """
    WebSocket connection for live intelligence streaming.

    On connect: sends current snapshot (freshness + risk pulse).
    Future: push new events as they arrive from sweeps.
    """
    await manager.connect(ws)
    try:
        # Send initial snapshot
        articles = get_articles(limit=500)
        outlook = generate_outlook(articles)
        freshness = get_freshness_info()
        await ws.send_json({
            "type": "snapshot",
            "freshness": freshness,
            "risk_pulse": {
                "escalation": outlook["escalation_risk"]["level"],
                "market": outlook["market_reaction"]["level"],
                "ai_momentum": outlook["ai_momentum"]["level"],
                "confidence": outlook["overall_confidence"],
            },
            "event_count": len(articles),
        })

        # Keep alive — wait for client messages or disconnect
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(ws)
