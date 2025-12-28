"""
Text-to-3D World Builder API Server
FastAPI 기반 백엔드 서버
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "trellis2"))

# 라우터 import
from routers import generate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 코드"""
    # 시작 시
    print("Starting Text-to-3D API Server...")
    print(f"Project root: {PROJECT_ROOT}")

    # Assets 디렉토리 확인
    assets_dir = PROJECT_ROOT / "assets"
    (assets_dir / "models").mkdir(parents=True, exist_ok=True)
    (assets_dir / "images").mkdir(parents=True, exist_ok=True)

    yield

    # 종료 시
    print("Shutting down...")


# FastAPI 앱 생성
app = FastAPI(
    title="Text-to-3D World Builder API",
    description="텍스트 프롬프트에서 3D 모델을 생성하는 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (생성된 GLB, 이미지)
assets_path = PROJECT_ROOT / "assets"
if assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

# 라우터 등록
app.include_router(generate.router)


@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "status": "ok",
        "message": "Text-to-3D World Builder API",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    import torch

    return {
        "status": "healthy",
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(PROJECT_ROOT / "server")],
    )
