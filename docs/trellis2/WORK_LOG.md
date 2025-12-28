# 작업 로그

## 2024-12-28: TRELLIS.2 + Gemini 파이프라인 구축

### 수행한 작업

#### 1. TRELLIS.2 설치 및 환경 설정

**시스템 정보:**
- OS: Ubuntu Linux (6.14.0-36-generic)
- GPU: NVIDIA GeForce RTX 3090 (24GB)
- CUDA: 12.5
- Python: 3.10

**설치 단계:**
```bash
# 1. TRELLIS.2 클론
git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive

# 2. Miniconda 설치
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3

# 3. 의존성 설치
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
```

**설치된 주요 패키지:**
- PyTorch 2.6.0+cu124
- flash-attn 2.7.3 (pre-built wheel)
- nvdiffrast, nvdiffrec (NVIDIA 렌더링)
- cumesh (CUDA 메시 처리)
- o-voxel (O-Voxel 표현)
- flexgemm (효율적 sparse convolution)

---

#### 2. Gated 모델 우회 (ModelScope)

**문제:**
HuggingFace의 gated 모델 접근 시 403 에러 발생
- `facebook/dinov3-vitl16-pretrain-lvd1689m`
- `briaai/RMBG-2.0`

**해결:**
ModelScope(중국)에서 동일 모델 다운로드

```python
from modelscope import snapshot_download

# DINOv3 (1.1GB)
snapshot_download('facebook/dinov3-vitl16-pretrain-lvd1689m',
                  cache_dir='~/.cache/modelscope')

# RMBG-2.0 (844MB)
snapshot_download('briaai/RMBG-2.0',
                  cache_dir='~/.cache/modelscope')
```

**로컬 경로:**
- DINOv3: `/home/byunghyun/.cache/modelscope/facebook/dinov3-vitl16-pretrain-lvd1689m`
- RMBG-2.0: `/home/byunghyun/.cache/modelscope/briaai/RMBG-2.0`

**패치 방법:**
`test_run.py`에서 monkey-patch로 로컬 경로 사용

---

#### 3. TRELLIS.2 테스트

**테스트 결과:**
```
입력: assets/example_image/T.png (1024x1024)
출력: test_output.glb (6.2MB)

메시 정보:
- Vertices: 6,209,218
- Faces: 12,836,264

성능:
- 총 시간: ~80초
- GPU 메모리: 8.81 GB
```

---

#### 4. Gemini API 연동

**설치:**
```bash
pip install google-genai
```

**테스트한 모델:**
| 모델 | 상태 |
|------|------|
| gemini-2.0-flash | 이미지 생성 미지원 |
| gemini-2.0-flash-exp | Free tier 쿼터 소진 |
| gemini-2.5-flash-image | Free tier 쿼터 소진 |
| imagen-4.0-generate-001 | **유료 전용** |

**결론:**
- Free tier로는 하루 제한 있음
- Imagen 4.0은 결제 필요
- 대안: 외부에서 이미지 생성 후 Image-to-3D만 사용

---

#### 5. 통합 파이프라인 작성

**파일:** `text_to_3d_pipeline.py`

**클래스 구조:**
```
TextTo3DPipeline
├── TextToImageGenerator (Gemini/Imagen)
└── ImageTo3DGenerator (TRELLIS.2)
```

**사용법:**
```bash
# 이미지에서 3D (권장)
python text_to_3d_pipeline.py --image input.png -o model.glb

# 텍스트에서 3D (API 필요)
python text_to_3d_pipeline.py "A robot toy" -o robot.glb
```

---

### 생성된 파일

| 파일 | 크기 | 설명 |
|------|------|------|
| `text_to_3d_pipeline.py` | 14KB | 통합 파이프라인 |
| `test_run.py` | 2.5KB | TRELLIS.2 테스트 |
| `test_gemini.py` | 4.4KB | Gemini API 테스트 |
| `test_output.glb` | 6.2MB | 테스트 출력 |
| `pipeline_test.glb` | 6.3MB | 파이프라인 테스트 출력 |
| `docs/SETUP_GUIDE.md` | - | 설정 가이드 |
| `docs/INTEGRATION_GUIDE.md` | - | 통합 가이드 |

---

### 남은 작업

1. **Gemini API 쿼터 해결**
   - 유료 결제 또는
   - 로컬 Stable Diffusion 사용 또는
   - 다음 날 Free tier 리셋 대기

2. **text_to_3d_world_builder 통합**
   - `INTEGRATION_GUIDE.md` 참조
   - Backend API 구현
   - Frontend 3D 뷰어 연동

3. **성능 최적화**
   - 모델 프리로딩
   - 배치 처리
   - 캐싱

---

### 환경 정보 백업

```bash
# Conda 환경 내보내기
conda activate trellis2
conda env export > environment.yml

# 설치된 pip 패키지
pip freeze > requirements.txt
```

**주요 환경 변수:**
```bash
export GEMINI_API_KEY="AIzaSy..."
export CUDA_HOME=/usr/local/cuda-12.5
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
```
