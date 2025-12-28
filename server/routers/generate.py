"""
3D 생성 API 라우터
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from pathlib import Path

router = APIRouter(prefix="/api/generate", tags=["generate"])

# 작업 상태 저장 (프로덕션에서는 Redis 사용 권장)
jobs: dict = {}


class GenerateRequest(BaseModel):
    """3D 생성 요청"""
    prompt: str
    options: dict = {}


class GenerateFromImageRequest(BaseModel):
    """이미지에서 3D 생성 요청"""
    image_path: str
    options: dict = {}


class GenerateResponse(BaseModel):
    """생성 응답"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int = 0
    model_url: Optional[str] = None
    image_url: Optional[str] = None
    error: Optional[str] = None


@router.post("", response_model=GenerateResponse)
async def generate_3d(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    텍스트 프롬프트에서 3D 모델 생성 (비동기)

    1. Gemini/Imagen으로 이미지 생성
    2. TRELLIS.2로 3D 변환
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "prompt": request.prompt,
    }

    background_tasks.add_task(run_text_to_3d_pipeline, job_id, request.prompt)

    return GenerateResponse(job_id=job_id, status="pending", progress=0)


@router.post("/from-image", response_model=GenerateResponse)
async def generate_from_image(request: GenerateFromImageRequest, background_tasks: BackgroundTasks):
    """
    기존 이미지에서 3D 모델 생성 (비동기)
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "image_path": request.image_path,
    }

    background_tasks.add_task(run_image_to_3d_pipeline, job_id, request.image_path)

    return GenerateResponse(job_id=job_id, status="pending", progress=0)


@router.get("/{job_id}", response_model=GenerateResponse)
async def get_job_status(job_id: str):
    """작업 상태 조회"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return GenerateResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", 0),
        model_url=job.get("model_url"),
        image_url=job.get("image_url"),
        error=job.get("error"),
    )


async def run_text_to_3d_pipeline(job_id: str, prompt: str):
    """백그라운드에서 Text → Image → 3D 파이프라인 실행"""
    from services.pipeline import TextTo3DPipeline

    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10

        # 출력 경로 설정
        assets_dir = Path(__file__).parent.parent.parent / "assets"
        output_path = assets_dir / "models" / f"{job_id}.glb"
        image_path = assets_dir / "images" / f"{job_id}.png"

        # 파이프라인 실행
        pipeline = TextTo3DPipeline()

        jobs[job_id]["progress"] = 20

        result = pipeline.generate(
            text_prompt=prompt,
            output_path=str(output_path),
            keep_image=True,
        )

        if result["success"]:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["model_url"] = f"/assets/models/{job_id}.glb"
            if result.get("image_path"):
                jobs[job_id]["image_url"] = f"/assets/images/{job_id}.png"
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = result.get("error", "Unknown error")

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


async def run_image_to_3d_pipeline(job_id: str, image_path: str):
    """백그라운드에서 Image → 3D 파이프라인 실행"""
    from services.pipeline import TextTo3DPipeline

    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10

        # 출력 경로 설정
        assets_dir = Path(__file__).parent.parent.parent / "assets"
        output_path = assets_dir / "models" / f"{job_id}.glb"

        # 파이프라인 실행
        pipeline = TextTo3DPipeline()

        jobs[job_id]["progress"] = 30

        result = pipeline.generate_from_image(
            image_path=image_path,
            output_path=str(output_path),
        )

        if result["success"]:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["progress"] = 100
            jobs[job_id]["model_url"] = f"/assets/models/{job_id}.glb"
            jobs[job_id]["image_url"] = f"/assets/images/{Path(image_path).name}"
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = result.get("error", "Unknown error")

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
