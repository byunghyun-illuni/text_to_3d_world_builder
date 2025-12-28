# Text-to-3D World Builder 통합 가이드

## 개요

이 문서는 TRELLIS.2 파이프라인을 기존 `text_to_3d_world_builder` 레포지토리와 통합하는 방법을 설명합니다.

---

## 1. 프로젝트 구조 설계

### 1.1 권장 디렉토리 구조

```
text_to_3d_world_builder/
├── client/                    # Frontend (React/Three.js)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Viewer3D.tsx   # GLB 뷰어
│   │   │   ├── PromptInput.tsx
│   │   │   └── AssetLibrary.tsx
│   │   └── services/
│   │       └── api.ts         # Backend API 호출
│   └── package.json
│
├── server/                    # Backend (Python FastAPI)
│   ├── main.py               # FastAPI 앱
│   ├── routers/
│   │   ├── generate.py       # 3D 생성 API
│   │   └── assets.py         # 에셋 관리 API
│   ├── services/
│   │   ├── text_to_image.py  # Gemini API 래퍼
│   │   ├── image_to_3d.py    # TRELLIS.2 래퍼
│   │   └── pipeline.py       # 통합 파이프라인
│   ├── models/               # Pydantic 모델
│   └── requirements.txt
│
├── shared/                    # 공유 타입/유틸
│   └── types.ts
│
├── assets/                    # 생성된 에셋 저장
│   ├── images/               # 중간 이미지
│   ├── models/               # GLB 파일
│   └── cache/                # 캐시
│
├── trellis2/                  # TRELLIS.2 서브모듈 (심볼릭 링크)
│   └── -> /path/to/TRELLIS.2
│
└── docs/
    └── prd/
        └── planning_mvp.md
```

### 1.2 TRELLIS.2 연결 방법

**옵션 A: 심볼릭 링크 (개발용)**
```bash
cd text_to_3d_world_builder
ln -s /home/byunghyun/workspace/github/TRELLIS.2 trellis2
```

**옵션 B: Git Submodule (프로덕션용)**
```bash
git submodule add https://github.com/microsoft/TRELLIS.2.git trellis2
git submodule update --init --recursive
```

**옵션 C: 패키지로 설치**
```bash
pip install -e /home/byunghyun/workspace/github/TRELLIS.2
```

---

## 2. Backend API 구현

### 2.1 FastAPI 서버 (`server/main.py`)

```python
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from pathlib import Path

app = FastAPI(title="Text-to-3D API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (생성된 GLB)
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


class GenerateRequest(BaseModel):
    prompt: str
    options: dict = {}


class GenerateResponse(BaseModel):
    job_id: str
    status: str
    model_url: str | None = None
    image_url: str | None = None
    error: str | None = None


# 작업 상태 저장 (프로덕션에서는 Redis 사용)
jobs = {}


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_3d(request: GenerateRequest, background_tasks: BackgroundTasks):
    """텍스트에서 3D 모델 생성 (비동기)"""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "progress": 0}

    background_tasks.add_task(run_pipeline, job_id, request.prompt)

    return GenerateResponse(job_id=job_id, status="pending")


@app.get("/api/generate/{job_id}", response_model=GenerateResponse)
async def get_job_status(job_id: str):
    """작업 상태 조회"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return GenerateResponse(
        job_id=job_id,
        status=job["status"],
        model_url=job.get("model_url"),
        image_url=job.get("image_url"),
        error=job.get("error"),
    )


@app.post("/api/generate-from-image", response_model=GenerateResponse)
async def generate_from_image(image_path: str, background_tasks: BackgroundTasks):
    """이미지에서 3D 모델 생성"""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending"}

    background_tasks.add_task(run_image_to_3d, job_id, image_path)

    return GenerateResponse(job_id=job_id, status="pending")


async def run_pipeline(job_id: str, prompt: str):
    """백그라운드에서 파이프라인 실행"""
    from services.pipeline import TextTo3DPipeline

    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 10

        pipeline = TextTo3DPipeline()
        output_path = f"assets/models/{job_id}.glb"
        image_path = f"assets/images/{job_id}.png"

        # Step 1: Text → Image
        jobs[job_id]["progress"] = 30
        # ... (이미지 생성)

        # Step 2: Image → 3D
        jobs[job_id]["progress"] = 60
        result = pipeline.generate(prompt, output_path, keep_image=True)

        if result["success"]:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["model_url"] = f"/assets/models/{job_id}.glb"
            jobs[job_id]["image_url"] = f"/assets/images/{job_id}.png"
            jobs[job_id]["progress"] = 100
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = result["error"]

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


async def run_image_to_3d(job_id: str, image_path: str):
    """이미지에서 3D 생성"""
    from services.pipeline import TextTo3DPipeline

    try:
        jobs[job_id]["status"] = "processing"

        pipeline = TextTo3DPipeline()
        output_path = f"assets/models/{job_id}.glb"

        result = pipeline.generate_from_image(image_path, output_path)

        if result["success"]:
            jobs[job_id]["status"] = "completed"
            jobs[job_id]["model_url"] = f"/assets/models/{job_id}.glb"
        else:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = result["error"]

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
```

### 2.2 파이프라인 서비스 (`server/services/pipeline.py`)

```python
import sys
sys.path.insert(0, '/home/byunghyun/workspace/github/TRELLIS.2')

from text_to_3d_pipeline import TextTo3DPipeline, ImageTo3DGenerator, TextToImageGenerator

# Re-export
__all__ = ['TextTo3DPipeline', 'ImageTo3DGenerator', 'TextToImageGenerator']
```

---

## 3. Frontend 구현

### 3.1 API 서비스 (`client/src/services/api.ts`)

```typescript
const API_BASE = 'http://localhost:8000/api';

export interface GenerateResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  model_url?: string;
  image_url?: string;
  error?: string;
}

export async function generateFrom3D(prompt: string): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  return response.json();
}

export async function getJobStatus(jobId: string): Promise<GenerateResponse> {
  const response = await fetch(`${API_BASE}/generate/${jobId}`);
  return response.json();
}

export async function pollJobStatus(
  jobId: string,
  onProgress?: (status: GenerateResponse) => void,
  intervalMs = 2000
): Promise<GenerateResponse> {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const status = await getJobStatus(jobId);
        onProgress?.(status);

        if (status.status === 'completed') {
          resolve(status);
        } else if (status.status === 'failed') {
          reject(new Error(status.error || 'Generation failed'));
        } else {
          setTimeout(poll, intervalMs);
        }
      } catch (error) {
        reject(error);
      }
    };
    poll();
  });
}
```

### 3.2 3D 뷰어 컴포넌트 (`client/src/components/Viewer3D.tsx`)

```tsx
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Environment } from '@react-three/drei';
import { Suspense } from 'react';

interface Viewer3DProps {
  modelUrl: string;
}

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  return <primitive object={scene} />;
}

export function Viewer3D({ modelUrl }: Viewer3DProps) {
  return (
    <Canvas camera={{ position: [2, 2, 2], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <Suspense fallback={null}>
        <Model url={modelUrl} />
        <Environment preset="studio" />
      </Suspense>
      <OrbitControls />
    </Canvas>
  );
}
```

### 3.3 생성 UI (`client/src/components/GeneratePanel.tsx`)

```tsx
import { useState } from 'react';
import { generateFrom3D, pollJobStatus, GenerateResponse } from '../services/api';
import { Viewer3D } from './Viewer3D';

export function GeneratePanel() {
  const [prompt, setPrompt] = useState('');
  const [status, setStatus] = useState<GenerateResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const job = await generateFrom3D(prompt);
      const result = await pollJobStatus(job.job_id, setStatus);
      setStatus(result);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="generate-panel">
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe the 3D object..."
      />
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate 3D'}
      </button>

      {status?.status === 'processing' && (
        <div className="progress">Processing... {status.progress}%</div>
      )}

      {status?.model_url && (
        <div className="viewer-container">
          <Viewer3D modelUrl={status.model_url} />
        </div>
      )}
    </div>
  );
}
```

---

## 4. 환경 설정

### 4.1 Backend 의존성 (`server/requirements.txt`)

```
fastapi>=0.100.0
uvicorn>=0.23.0
python-multipart>=0.0.6
pydantic>=2.0.0
google-genai>=1.0.0

# TRELLIS.2 의존성은 conda 환경에서 관리
```

### 4.2 환경 변수 (`.env`)

```bash
# Gemini API
GEMINI_API_KEY=your-api-key-here

# 모델 경로 (ModelScope 캐시)
DINOV3_MODEL_PATH=/home/byunghyun/.cache/modelscope/facebook/dinov3-vitl16-pretrain-lvd1689m
RMBG_MODEL_PATH=/home/byunghyun/.cache/modelscope/briaai/RMBG-2.0

# 에셋 디렉토리
ASSETS_DIR=./assets

# GPU 설정
CUDA_VISIBLE_DEVICES=0
```

### 4.3 실행 스크립트 (`run.sh`)

```bash
#!/bin/bash

# Conda 환경 활성화
source ~/miniconda3/bin/activate trellis2

# 환경 변수 로드
export $(cat .env | xargs)

# Backend 서버 시작
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# Frontend 개발 서버 시작
cd ../client
npm run dev
```

---

## 5. SSE 실시간 진행 상황 (선택사항)

### 5.1 Backend SSE 엔드포인트

```python
from fastapi.responses import StreamingResponse
import asyncio

@app.get("/api/generate/{job_id}/stream")
async def stream_job_status(job_id: str):
    """SSE로 실시간 진행 상황 전송"""
    async def event_generator():
        while True:
            if job_id not in jobs:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break

            job = jobs[job_id]
            yield f"data: {json.dumps(job)}\n\n"

            if job["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 5.2 Frontend SSE 클라이언트

```typescript
export function subscribeToJob(
  jobId: string,
  onUpdate: (data: GenerateResponse) => void
): () => void {
  const eventSource = new EventSource(`${API_BASE}/generate/${jobId}/stream`);

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onUpdate(data);

    if (data.status === 'completed' || data.status === 'failed') {
      eventSource.close();
    }
  };

  return () => eventSource.close();
}
```

---

## 6. 체크리스트

### 통합 전 확인사항

- [ ] TRELLIS.2 독립 테스트 통과 (`python test_run.py`)
- [ ] Gemini API 키 발급 완료
- [ ] ModelScope 모델 다운로드 완료
- [ ] GPU 메모리 확인 (24GB 이상)

### 통합 단계

1. [ ] 디렉토리 구조 생성
2. [ ] TRELLIS.2 연결 (심볼릭 링크 또는 서브모듈)
3. [ ] Backend API 구현
4. [ ] Frontend 컴포넌트 구현
5. [ ] 환경 변수 설정
6. [ ] 통합 테스트

### 테스트

```bash
# Backend 테스트
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cute robot toy"}'

# 상태 확인
curl http://localhost:8000/api/generate/{job_id}
```

---

## 7. 참고 자료

- [TRELLIS.2 GitHub](https://github.com/microsoft/TRELLIS.2)
- [Gemini API 문서](https://ai.google.dev/gemini-api/docs)
- [Three.js React-Three-Fiber](https://docs.pmnd.rs/react-three-fiber)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
