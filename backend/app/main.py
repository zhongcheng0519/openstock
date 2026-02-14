from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import strategy

settings = get_settings()

app = FastAPI(
    title="股票分析系统",
    description="基于 FastAPI 的股票分析平台",
    version="0.1.0",
    debug=settings.DEBUG,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(strategy.router)


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
