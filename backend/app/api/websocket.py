from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.exceptions import AnalysisNotFoundError
router = APIRouter()
@router.websocket("/analysis/{analysis_id}/ws")
async def analysis_websocket(websocket: WebSocket, analysis_id: str) -> None:
    try:
        await websocket.app.state.analysis_manager.get(analysis_id)
    except AnalysisNotFoundError:
        await websocket.close(code=4404)
        return
    sockets = websocket.app.state.websocket_manager
    await sockets.connect(analysis_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await sockets.disconnect(analysis_id, websocket)
