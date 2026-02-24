from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.config import get_settings
from app.core.logger import setup_logging

settings = get_settings()
setup_logging()

from app.api import strategy, auth, admin

logger.info(f"Starting server in {'debug' if settings.DEBUG else 'production'} mode")

app = FastAPI(
    title="股票分析系统",
    description="基于 FastAPI 的股票分析平台",
    version="0.1.0",
    debug=settings.DEBUG,
)

# #region agent log
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    import json
    errors = exc.errors()
    body = None
    try:
        body = await request.body()
        body = body.decode('utf-8')
    except:
        pass
    errors_serializable = []
    for err in errors:
        errors_serializable.append({
            "type": err.get("type"),
            "loc": err.get("loc"),
            "msg": err.get("msg"),
            "input": str(err.get("input")) if err.get("input") is not None else None,
            "ctx": str(err.get("ctx")) if err.get("ctx") else None
        })
    with open('/Users/Zhuanz/Code/GitHub/openstock/.cursor/debug-28cd59.log', 'a') as f:
        f.write(json.dumps({"sessionId":"28cd59","location":"main.py:27","message":"422 validation error caught","data":{"url":str(request.url),"method":request.method,"errors":errors_serializable,"body":body},"timestamp":int(__import__('time').time()*1000),"hypothesisId":"H1-H5","runId":"initial"}) + '\n')
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
    )
# #endregion

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(strategy.router)
app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "message": "欢迎使用股票分析系统 API",
        "docs": "/docs",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
