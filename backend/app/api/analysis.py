"""Analysis creation, retrieval, and cancellation routes."""

import asyncio

from fastapi import APIRouter, Request, status

from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisStatusResponse, CancellationResponse, to_response, to_status_response

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_analysis(payload: AnalysisRequest, request: Request) -> AnalysisResponse:
    manager = request.app.state.analysis_manager
    session = await manager.create(str(payload.target_url))
    task = asyncio.create_task(request.app.state.analysis_runner.run(session.analysis_id), name=f"analysis-{session.analysis_id}")
    await manager.register_task(session.analysis_id, task)
    return to_response(await manager.get(session.analysis_id))


@router.get("/{analysis_id}", response_model=AnalysisStatusResponse)
async def get_analysis(analysis_id: str, request: Request) -> AnalysisStatusResponse:
    return to_status_response(await request.app.state.analysis_manager.get(analysis_id))


@router.post("/{analysis_id}/cancel", response_model=CancellationResponse)
async def cancel_analysis(analysis_id: str, request: Request) -> CancellationResponse:
    session = await request.app.state.analysis_manager.request_cancellation(analysis_id)
    await request.app.state.analysis_runner.orchestrator.cancel(session)
    return CancellationResponse(analysis_id=session.analysis_id, status=session.status, message=session.message)
