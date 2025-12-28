"""
TRELLIS.2 파이프라인 래퍼
text_to_3d_world_builder에서 TRELLIS.2 파이프라인을 사용하기 위한 모듈
"""

import sys
import os
from pathlib import Path

# 경로 추가
PROJECT_ROOT = Path(__file__).parent.parent.parent
TRELLIS2_PATH = PROJECT_ROOT / "trellis2"
SCRIPTS_PATH = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(TRELLIS2_PATH))
sys.path.insert(0, str(SCRIPTS_PATH))

# 환경 변수 설정
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# 로컬 모델 경로 (ModelScope에서 다운로드된 경로)
DINOV3_LOCAL_PATH = os.environ.get(
    "DINOV3_MODEL_PATH",
    os.path.expanduser("~/.cache/modelscope/facebook/dinov3-vitl16-pretrain-lvd1689m")
)
RMBG_LOCAL_PATH = os.environ.get(
    "RMBG_MODEL_PATH",
    os.path.expanduser("~/.cache/modelscope/briaai/RMBG-2.0")
)

# TRELLIS.2 파이프라인 import
from text_to_3d_pipeline import (
    TextTo3DPipeline,
    ImageTo3DGenerator,
    TextToImageGenerator,
)

__all__ = [
    'TextTo3DPipeline',
    'ImageTo3DGenerator',
    'TextToImageGenerator',
    'DINOV3_LOCAL_PATH',
    'RMBG_LOCAL_PATH',
]
