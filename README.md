# Text-to-3D World Builder

텍스트 프롬프트에서 고품질 3D 모델을 생성하는 로컬 파이프라인

## 아키텍처

```
Text Prompt → [Gemini/Imagen] → Image → [TRELLIS.2] → 3D Model (GLB)
```

- **Text-to-Image**: Gemini 2.0 Flash (Imagen 3)
- **Image-to-3D**: TRELLIS.2 (Microsoft, 4B params, O-Voxel)
- **Output**: GLB with full PBR materials

## 요구사항

- NVIDIA GPU 24GB+ VRAM (RTX 3090, 4090, A5000+)
- CUDA 12.x
- Miniconda/Anaconda

## 설치

### 1. 레포 클론 (서브모듈 포함)

```bash
git clone --recursive https://github.com/your-username/text_to_3d_world_builder.git
cd text_to_3d_world_builder

# 이미 클론한 경우 서브모듈 초기화
git submodule update --init --recursive
```

### 2. TRELLIS.2 환경 설정

```bash
cd trellis2

# conda 환경 생성 및 의존성 설치
. ./setup.sh --new-env
. ./setup.sh --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
```

### 3. Gated 모델 다운로드 (ModelScope)

HuggingFace gated 모델 우회:

```bash
pip install modelscope

# DINOv3
modelscope download --model facebook/dinov3-vitl16-pretrain-lvd1689m --local_dir ~/.cache/modelscope/facebook/dinov3-vitl16-pretrain-lvd1689m

# RMBG-2.0
modelscope download --model briaai/RMBG-2.0 --local_dir ~/.cache/modelscope/briaai/RMBG-2.0
```

### 4. 환경 변수 설정

```bash
cp .env.example .env
# GEMINI_API_KEY 설정
```

## 사용법

### CLI (Image → 3D)

```bash
cd trellis2
conda activate trellis2

# 이미지에서 3D 생성
python text_to_3d_pipeline.py --image input.png --output output.glb
```

### CLI (Text → 3D)

```bash
# 텍스트에서 3D 생성 (Gemini API 필요)
python text_to_3d_pipeline.py "a cute robot" --output robot.glb
```

### API 서버

```bash
./scripts/run_server.sh
# http://localhost:8000
```

**엔드포인트:**
- `POST /api/generate` - Text → 3D
- `POST /api/generate/from-image` - Image → 3D
- `GET /api/generate/{job_id}` - 작업 상태 조회
- `GET /health` - GPU 상태 확인

## 프로젝트 구조

```
text_to_3d_world_builder/
├── trellis2/                 # TRELLIS.2 (Git Submodule)
│   ├── text_to_3d_pipeline.py
│   └── docs/
│       ├── SETUP_GUIDE.md
│       └── INTEGRATION_GUIDE.md
├── server/                   # FastAPI 백엔드
│   ├── main.py
│   ├── routers/generate.py
│   └── services/pipeline.py
├── client/                   # React + Three.js (TODO)
├── scripts/
│   └── run_server.sh
└── assets/                   # 생성된 3D 모델
    ├── models/
    └── images/
```

## 성능

- RTX 3090 24GB 기준
- Image → 3D: ~80초, ~9GB VRAM
- 출력: 6M+ vertices mesh with PBR textures

## 서브모듈 관리

```bash
# 서브모듈 업데이트
git submodule update --remote trellis2

# 변경사항 커밋
git add trellis2
git commit -m "Update TRELLIS.2 submodule"
```

## 라이선스

- This project: MIT
- TRELLIS.2: [MIT License](https://github.com/microsoft/TRELLIS.2/blob/main/LICENSE)
