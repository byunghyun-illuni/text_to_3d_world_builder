#!/bin/bash
# Text-to-3D World Builder API Server 실행 스크립트
# TRELLIS.2 conda 환경에서 실행

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRELLIS2_DIR="$PROJECT_ROOT/trellis2"

echo "=== Text-to-3D World Builder API Server ==="
echo "Project root: $PROJECT_ROOT"

# .env 파일 로드
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Loading .env file..."
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# CUDA 설정
export CUDA_HOME=${CUDA_HOME:-/usr/local/cuda-12.5}
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-"expandable_segments:True"}
export OPENCV_IO_ENABLE_OPENEXR=1

# Python 경로 설정
export PYTHONPATH="$PROJECT_ROOT:$TRELLIS2_DIR:$PYTHONPATH"

# assets 디렉토리 생성
mkdir -p "$PROJECT_ROOT/assets/models"
mkdir -p "$PROJECT_ROOT/assets/images"

# trellis2 conda 환경 활성화 확인
if ! command -v conda &> /dev/null; then
    echo "Error: conda not found. Please install Miniconda/Anaconda."
    exit 1
fi

# conda 환경 활성화
eval "$(conda shell.bash hook)"
conda activate trellis2

echo ""
echo "CUDA available: $(python -c 'import torch; print(torch.cuda.is_available())')"
echo "GPU: $(python -c 'import torch; print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A")')"
echo ""

# 서버 실행
cd "$PROJECT_ROOT/server"
echo "Starting FastAPI server on http://0.0.0.0:${PORT:-8000}"
python -m uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000} --reload --reload-dir .
