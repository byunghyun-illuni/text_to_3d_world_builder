# TRELLIS.2 + Gemini 파이프라인 설정 가이드

## 개요

이 문서는 Text → Image → 3D 파이프라인 구축 과정을 기록합니다.

### 파이프라인 구조

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Text Prompt   │ ──► │  Gemini/Imagen  │ ──► │   TRELLIS.2     │
│  "A robot toy"  │     │  (Text-to-Image)│     │  (Image-to-3D)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                        │
                              ▼                        ▼
                         image.png                 model.glb
```

---

## 1. 환경 설정

### 1.1 시스템 요구사항

| 항목 | 최소 요구사항 | 권장 |
|------|--------------|------|
| GPU | NVIDIA 24GB VRAM | RTX 3090/4090/A100 |
| CUDA | 12.4+ | 12.5 |
| RAM | 32GB | 64GB |
| OS | Linux | Ubuntu 22.04+ |

### 1.2 Miniconda 설치

```bash
# Miniconda 설치 (이미 있으면 스킵)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
~/miniconda3/bin/conda init bash
source ~/.bashrc
```

### 1.3 TRELLIS.2 설치

```bash
# 저장소 클론
git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive
cd TRELLIS.2

# conda 환경 생성 및 의존성 설치
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm

# 환경 활성화
conda activate trellis2
```

### 1.4 Gated 모델 다운로드 (ModelScope 우회)

HuggingFace의 gated 모델(DINOv3, RMBG-2.0) 접근 문제 해결:

```bash
# ModelScope 패키지 설치
pip install modelscope

# 모델 다운로드
python -c "
from modelscope import snapshot_download

# DINOv3 모델
snapshot_download('facebook/dinov3-vitl16-pretrain-lvd1689m',
                  cache_dir='/home/byunghyun/.cache/modelscope')

# RMBG-2.0 모델 (배경 제거)
snapshot_download('briaai/RMBG-2.0',
                  cache_dir='/home/byunghyun/.cache/modelscope')
"
```

### 1.5 Gemini API 설정

```bash
# Google AI Studio에서 API 키 발급
# https://aistudio.google.com/apikey

# 패키지 설치
pip install google-genai

# 환경변수 설정
export GEMINI_API_KEY="your-api-key-here"
```

---

## 2. 파이프라인 사용법

### 2.1 이미지에서 3D 생성 (권장)

```bash
# 기존 이미지를 3D로 변환
python text_to_3d_pipeline.py --image input.png --output model.glb
```

### 2.2 텍스트에서 3D 생성

```bash
# 텍스트 프롬프트로 3D 생성
python text_to_3d_pipeline.py "A cute cartoon robot toy" --output robot.glb

# 중간 이미지 보존
python text_to_3d_pipeline.py "A medieval sword" --output sword.glb --keep-image
```

### 2.3 Python API로 사용

```python
from text_to_3d_pipeline import TextTo3DPipeline

# 파이프라인 초기화
pipeline = TextTo3DPipeline(api_key="your-gemini-api-key")

# 텍스트에서 3D 생성
result = pipeline.generate(
    text_prompt="A cute cartoon robot",
    output_path="robot.glb",
    keep_image=True
)

# 이미지에서 3D 생성
result = pipeline.generate_from_image(
    image_path="input.png",
    output_path="model.glb"
)
```

---

## 3. 주요 파일 설명

| 파일 | 설명 |
|------|------|
| `text_to_3d_pipeline.py` | 메인 파이프라인 (Text → Image → 3D) |
| `test_gemini.py` | Gemini API 테스트 스크립트 |
| `test_run.py` | TRELLIS.2 단독 테스트 |

---

## 4. 성능 벤치마크

RTX 3090 24GB 기준:

| 단계 | 소요 시간 | GPU 메모리 |
|------|----------|-----------|
| 모델 로딩 | ~30초 | ~4GB |
| Image → 3D | ~80초 | ~8.8GB |
| GLB 내보내기 | ~5초 | - |

출력 품질:
- 메시: ~6M vertices, ~12M faces
- GLB 파일 크기: ~6MB
- 텍스처: 2048x2048 PBR

---

## 5. 트러블슈팅

### 5.1 HuggingFace Gated Model 403 에러

```
huggingface_hub.errors.GatedRepoError: 403 Client Error
```

**해결**: ModelScope에서 다운로드 (위의 1.4 섹션 참조)

### 5.2 Gemini API 429 에러 (쿼터 초과)

```
google.api_core.exceptions.ResourceExhausted: 429
```

**해결**:
- Free tier는 일일 제한 있음 (자정에 리셋)
- Imagen 4.0은 유료 결제 필요
- 대안: 로컬 Stable Diffusion 사용

### 5.3 CUDA Out of Memory

```
RuntimeError: CUDA out of memory
```

**해결**:
- `pipeline_type='512'` 사용 (저해상도)
- `low_vram=True` 확인
- 다른 GPU 프로세스 종료

---

## 6. API 참조

### TextTo3DPipeline

```python
class TextTo3DPipeline:
    def __init__(self, api_key: str)

    def generate(
        self,
        text_prompt: str,           # 텍스트 설명
        output_path: str = "output.glb",
        keep_image: bool = True,    # 중간 이미지 보존
    ) -> dict

    def generate_from_image(
        self,
        image_path: str,            # 입력 이미지 경로
        output_path: str = "output.glb",
    ) -> dict
```

### ImageTo3DGenerator

```python
class ImageTo3DGenerator:
    def generate(
        self,
        image: PIL.Image,           # PIL 이미지 객체
        output_path: str,
        decimation_target: int = 100000,  # 면 수 제한
        texture_size: int = 2048,   # 텍스처 해상도
    ) -> str
```

---

## 7. 변경 이력

- 2024-12-28: 초기 설정 완료
  - TRELLIS.2 설치 및 테스트
  - ModelScope 우회 설정
  - Gemini API 연동
  - 통합 파이프라인 작성
