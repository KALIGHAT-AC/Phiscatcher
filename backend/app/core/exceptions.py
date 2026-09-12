from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
class AnalysisNotFoundError(Exception):
    pass
class AnalysisNotCancellableError(Exception):
    pass
def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AnalysisNotFoundError)
    async def not_found(_: Request, exc: AnalysisNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"error": "analysis_not_found", "message": str(exc)})
    @app.exception_handler(AnalysisNotCancellableError)
    async def not_cancellable(_: Request, exc: AnalysisNotCancellableError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"error": "analysis_not_cancellable", "message": str(exc)})
