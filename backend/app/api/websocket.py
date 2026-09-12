"""Analysis-specific WebSocket subscription route."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.exceptions import AnalysisNotFoundError

router = APIRouter()


@router.websocket("/analysis/{analysis_id}/ws")
async def analysis_websocket(websocket: WebSocket, analysis_id: str) -> None:
    manager = websocket.app.state.analysis_manager
    try:
        await manager.get(analysis_id)
    except AnalysisNotFoundError:
        await websocket.close(code=4404)
        return
    socket_manager = websocket.app.state.websocket_manager
    await socket_manager.connect(analysis_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await socket_manager.disconnect(analysis_id, websocket)
