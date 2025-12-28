# PRD: Text-to-3D World Builder (MVP)

## 1. 제품 개요

### 제품명
**WorldForge** - AI-Powered 3D World Generator

### 한 줄 설명
텍스트 하나로 **실제 3D 에셋과 환경을 생성**하고, 웹에서 **몰입형 탐험과 편집**이 가능한 차세대 월드 빌더.

### 핵심 가치 제안
- **진짜 3D 생성**: 프리미티브 배치가 아닌, AI가 실제 3D 메시/텍스처를 생성
- **로컬 우선**: 외부 의존성 최소화, 모든 에셋과 데이터는 로컬 저장
- **즉시 탐험**: 생성 즉시 1인칭으로 걸어다니며 확인
- **반복 정제**: "의자를 더 현대적으로", "조명을 따뜻하게" 같은 자연어로 수정

### 경쟁 제품 벤치마크
| 제품 | 특징 | 우리의 차별점 |
|------|------|--------------|
| HunyuanWorld | 비디오 기반 3D 월드 생성 | 텍스트 직접 입력 + 실시간 편집 |
| Blockade Labs | 360 스카이박스 생성 | 실제 걸어다닐 수 있는 3D 공간 |
| Luma AI | 단일 오브젝트 생성 | 전체 씬 구성 + 레이아웃 |

---

## 2. 목표

### 비즈니스 목표
- "텍스트만으로 3D 월드가 만들어진다"는 **와우 모먼트** 제공
- 게임/메타버스/VR 스튜디오에 **프로토타이핑 툴**로 포지셔닝
- **로컬 실행** 가능하여 데이터 보안 우려 해소

### 사용자 목표
- 3D 툴 경험 없이 **상상을 현실로**
- 생성물을 **즉시 체험**하고 **빠르게 수정**
- 결과물을 **GLB/GLTF로 내보내기**하여 다른 툴에서 활용

---

## 3. Non-Goals (MVP 제외)

- 멀티플레이어/실시간 협업
- 애니메이션/리깅 자동화
- 모바일 네이티브 앱
- 자체 3D 생성 모델 학습
- 클라우드 기반 스토리지 (S3, 등)
- 외부 DB/캐시 (Redis, PostgreSQL, 등)

---

## 4. 타겟 사용자

### Primary
- **게임 기획자**: 레벨 디자인 프로토타이핑
- **메타버스/VR 개발자**: 공간 컨셉 검증
- **건축/인테리어 디자이너**: 초기 아이디어 시각화

### Secondary
- 교육 콘텐츠 제작자
- 마케팅/이벤트 기획자
- 인디 게임 개발자

---

## 5. 핵심 사용자 시나리오

### 시나리오 1: 판타지 던전 생성
```
User: "어두운 중세 던전을 만들어줘.
       돌벽과 횃불이 있고, 중앙에 보물상자가 있어."

System:
1. Scene Layout 분석 → 던전 구조 결정 (10x10m 방)
2. Text-to-3D로 에셋 생성:
   - 횃불 오브젝트 (Trellis API)
   - 보물상자 (Trellis API)
3. 로컬 캐시 확인 → 있으면 재사용
4. 바닥/벽 프로시저럴 생성 + PBR 텍스처
5. 조명 배치 (횃불 위치에 포인트 라이트)
6. 사용자 스폰포인트 설정

→ 탐험 가능한 3D 던전 완성
```

### 시나리오 2: 반복 정제
```
User: "보물상자를 더 화려하게 만들어줘. 금색으로."

System:
1. 기존 보물상자 에셋 식별
2. 수정된 프롬프트로 재생성
3. 새 에셋으로 교체 (로컬 저장)
4. 실시간 미리보기 업데이트
```

### 시나리오 3: 내보내기
```
User: "이 씬을 Unity에서 쓸 수 있게 내보내줘"

System:
1. 모든 에셋을 GLB로 패키징
2. 씬 구조를 JSON으로 저장
3. 로컬 폴더에 ZIP 생성
```

---

## 6. 기능 요구사항

### 6.1 텍스트 입력 & 해석

| 기능 | 설명 | 우선순위 |
|------|------|---------|
| 자연어 파싱 | GPT-4/Claude 기반 씬 구조 추출 | P0 |
| 에셋 목록 추출 | 생성해야 할 오브젝트 식별 | P0 |
| 레이아웃 추론 | 공간 배치 자동 결정 | P0 |
| 스타일 태그 | "판타지", "SF", "현대" 등 분류 | P1 |

### 6.2 3D 에셋 생성

| 기능 | 설명 | 우선순위 |
|------|------|---------|
| Text-to-3D | Trellis/Hunyuan3D API 연동 | P0 |
| 로컬 캐싱 | 생성된 에셋 로컬 파일로 저장 | P0 |
| 프리셋 에셋 | 자주 쓰는 오브젝트 사전 포함 | P0 |
| 품질 선택 | Draft(빠름) / Quality(느림) | P1 |

### 6.3 환경 생성

| 기능 | 설명 | 우선순위 |
|------|------|---------|
| 바닥/벽 생성 | 프로시저럴 공간 구조 | P0 |
| PBR 텍스처 | AI 생성 or 프리셋 텍스처 | P0 |
| Skybox | 프리셋 또는 AI 생성 | P1 |
| 조명 자동 배치 | 씬 분위기에 맞는 조명 | P0 |

### 6.4 3D 뷰어 & 탐험

| 기능 | 설명 | 우선순위 |
|------|------|---------|
| 1인칭 이동 | WASD + 마우스 | P0 |
| 충돌 감지 | 벽/바닥/오브젝트 | P0 |
| Edit/Play 전환 | 편집 ↔ 탐험 모드 | P0 |
| 오브젝트 인터랙션 | 클릭 시 정보 표시 | P1 |

### 6.5 편집 기능

| 기능 | 설명 | 우선순위 |
|------|------|---------|
| 오브젝트 선택 | 클릭으로 선택 + 하이라이트 | P0 |
| Transform | 이동/회전/스케일 기즈모 | P0 |
| 자연어 수정 | "이거 더 크게" 같은 명령 | P1 |
| 삭제/복제 | 선택 오브젝트 조작 | P1 |
| Undo/Redo | 작업 취소/복구 | P1 |

### 6.6 저장 & 내보내기

| 기능 | 설명 | 우선순위 |
|------|------|---------|
| 프로젝트 저장 | 로컬 JSON 파일 | P0 |
| 프로젝트 불러오기 | JSON에서 씬 복원 | P0 |
| GLB 내보내기 | 단일 오브젝트/전체 씬 | P0 |
| 씬 JSON | Unity/Unreal 임포트용 | P1 |

---

## 7. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Prompt  │  │  Asset   │  │ Inspector│  │   3D Viewport    │ │
│  │  Input   │  │  Panel   │  │  Panel   │  │ (Three.js/R3F)   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Scene Parser │  │ Asset Cache  │  │   Generation Service   │ │
│  │   (LLM)      │  │  (Local FS)  │  │   (asyncio)            │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
          ┌──────────────────┐ ┌──────────────────┐
          │   Text-to-3D     │ │   Local Storage  │
          │ (Trellis/Hunyuan)│ │   (./data/)      │
          └──────────────────┘ └──────────────────┘
```

### 로컬 디렉토리 구조
```
./data/
├── projects/                    # 프로젝트 저장
│   ├── project_001/
│   │   ├── world.json          # World Spec
│   │   ├── history.json        # Undo/Redo 히스토리
│   │   └── assets/             # 프로젝트 전용 에셋
│   └── project_002/
│       └── ...
├── cache/                       # 생성 에셋 캐시
│   ├── assets/                 # GLB 파일
│   │   ├── {hash}.glb
│   │   └── ...
│   ├── textures/               # 텍스처 파일
│   └── index.json              # 캐시 인덱스 (prompt → file)
├── presets/                     # 프리셋 에셋
│   ├── furniture/
│   ├── nature/
│   ├── architecture/
│   └── skyboxes/
└── exports/                     # 내보내기 결과
    └── {project}_{timestamp}/
```

### 데이터 흐름

```
1. User Input
   "어두운 던전에 보물상자"
          │
          ▼
2. Scene Parser (LLM API)
   {
     "scene_type": "dungeon",
     "style": "dark_fantasy",
     "size": [10, 4, 10],
     "assets": [
       {"name": "treasure_chest", "prompt": "medieval wooden chest..."},
       {"name": "torch", "prompt": "wall mounted torch...", "count": 4}
     ],
     "lighting": "dim_warm"
   }
          │
          ▼
3. Cache Check (Local)
   cache/index.json에서 prompt hash 검색
   ├── HIT: 캐시된 GLB 사용
   └── MISS: Text-to-3D API 호출
          │
          ▼
4. Asset Generation (if cache miss)
   Trellis API → GLB → cache/assets/{hash}.glb
          │
          ▼
5. Scene Assembly
   - 에셋 배치 (레이아웃 알고리즘)
   - 조명 설정
   - 충돌체 생성
          │
          ▼
6. World Spec (JSON)
   projects/{id}/world.json에 저장
          │
          ▼
7. Client Render
   Three.js 씬으로 변환 → 탐험 가능
```

---

## 8. 기술 스택

### Frontend
| 기술 | 용도 |
|------|------|
| React 18+ | UI 프레임워크 |
| TypeScript | 타입 안전성 |
| Three.js + R3F | 3D 렌더링 |
| @react-three/drei | 3D 유틸리티 (OrbitControls, TransformControls 등) |
| Zustand | 상태 관리 |
| TailwindCSS | 스타일링 |

### Backend
| 기술 | 용도 |
|------|------|
| FastAPI | API 서버 |
| asyncio | 비동기 처리 (에셋 생성 병렬화) |
| aiofiles | 비동기 파일 I/O |
| SQLite (선택) | 프로젝트 메타데이터 (또는 JSON) |
| OpenAI/Anthropic | 씬 파싱 LLM |

### External APIs (최소한)
| 서비스 | 용도 | 비고 |
|--------|------|------|
| Trellis | Text-to-3D | 로컬 캐시로 API 호출 최소화 |
| OpenAI/Claude | 씬 파싱 | 프롬프트 해석용 |

### 로컬 대안 (옵션)
| 서비스 | 로컬 대안 |
|--------|----------|
| Trellis API | 로컬 Trellis 모델 (GPU 필요) |
| OpenAI | Ollama + Llama |

---

## 9. UI/UX 설계

### 메인 레이아웃

```
┌────────────────────────────────────────────────────────────────┐
│  [Logo]  Project: "Fantasy Dungeon"  [Save] [Load] [Export]    │
├────────────┬───────────────────────────────────┬───────────────┤
│            │                                   │               │
│   Prompt   │                                   │   Inspector   │
│   Panel    │        3D Viewport                │    Panel      │
│            │                                   │               │
│  ┌──────┐  │      [Perspective View]           │  Selected:    │
│  │ Chat │  │                                   │  "Chest"      │
│  │ UI   │  │         ┌─────┐                   │               │
│  │      │  │         │     │                   │  Position:    │
│  │      │  │         └─────┘                   │  X: 0  Y: 0   │
│  └──────┘  │                                   │               │
│            │                                   │  [Regenerate] │
│  [Assets]  │  [Edit Mode] [Play Mode]          │  [Delete]     │
├────────────┴───────────────────────────────────┴───────────────┤
│  [Status: Ready]                        [Generation: Idle]      │
└────────────────────────────────────────────────────────────────┘
```

### 핵심 인터랙션

1. **프롬프트 입력**: 채팅 형식으로 자연스럽게
2. **생성 진행**: 로딩 스피너 + 에셋별 상태
3. **Edit ↔ Play 전환**: 편집 모드 / 1인칭 탐험 모드
4. **오브젝트 선택**: 클릭 → Inspector에 상세 정보
5. **로컬 저장/불러오기**: 파일 브라우저 다이얼로그

---

## 10. 성공 지표

### 정성적 지표
- "와, 진짜 3D가 만들어지네" 반응
- "설치 없이 바로 쓸 수 있네" 피드백
- 로컬 데이터 보안에 대한 신뢰

### 정량적 지표
| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 첫 월드 생성 시간 | < 60초 | 프롬프트 → 렌더 완료 |
| 캐시 히트율 | > 50% | 중복 에셋 재사용 |
| 생성 성공률 | > 95% | 에러 없이 완료 비율 |

---

## 11. MVP 범위

### Phase 1: Core Generation
- [ ] 텍스트 → 씬 구조 파싱 (LLM)
- [ ] Text-to-3D 연동 (Trellis API)
- [ ] 로컬 에셋 캐시 시스템
- [ ] 기본 씬 조립 (바닥 + 에셋 배치)
- [ ] 3D 뷰어 (Orbit 카메라)
- [ ] 기본 조명

### Phase 2: Exploration
- [ ] 1인칭 이동 (WASD + 마우스)
- [ ] 충돌 감지 (rapier.js or cannon.js)
- [ ] Edit/Play 모드 전환

### Phase 3: Editing
- [ ] 오브젝트 선택 & Inspector
- [ ] Transform 기즈모 (drei TransformControls)
- [ ] 삭제/복제
- [ ] Undo/Redo

### Phase 4: Polish
- [ ] 프로젝트 저장/불러오기 (로컬 JSON)
- [ ] GLB 내보내기
- [ ] 프리셋 에셋 라이브러리
- [ ] UI/UX 개선

### MVP 제외 (Post-MVP)
- 3D Gaussian Splatting 배경
- VR/AR 지원
- 멀티플레이어
- 클라우드 동기화
- 애니메이션 지원

---

## 12. 리스크 & 대응

| 리스크 | 영향 | 확률 | 대응 |
|--------|------|------|------|
| Text-to-3D API 품질 불안정 | 높음 | 중 | 프리셋 에셋 폴백, 여러 API 시도 |
| 생성 시간 너무 길음 | 높음 | 높 | 적극적 캐싱, placeholder 먼저 표시 |
| 로컬 저장 공간 부족 | 중 | 낮 | 캐시 자동 정리 (LRU) |
| 스타일 불일치 | 중 | 높 | 스타일 프롬프트 정교화 |

---

## 13. 캐시 시스템

### 캐시 인덱스 구조 (cache/index.json)
```json
{
  "version": "1.0",
  "entries": {
    "a1b2c3d4": {
      "prompt": "medieval wooden treasure chest, fantasy style",
      "style": "fantasy",
      "file": "assets/a1b2c3d4.glb",
      "created_at": "2024-01-15T10:30:00Z",
      "last_used": "2024-01-20T14:00:00Z",
      "use_count": 5,
      "size_bytes": 245000
    }
  },
  "total_size_bytes": 50000000,
  "max_size_bytes": 500000000
}
```

### 캐시 정책
- **Key**: SHA256(prompt + style + quality)
- **Max Size**: 500MB (설정 가능)
- **Eviction**: LRU (Least Recently Used)
- **TTL**: 없음 (수동 정리)

### 캐시 조회 로직
```python
async def get_or_generate_asset(prompt: str, style: str) -> Path:
    cache_key = hashlib.sha256(f"{prompt}:{style}".encode()).hexdigest()[:8]

    # 1. 캐시 확인
    if cache_key in cache_index:
        entry = cache_index[cache_key]
        entry["last_used"] = datetime.now()
        entry["use_count"] += 1
        return Path(entry["file"])

    # 2. 캐시 미스 → 생성
    glb_data = await trellis_api.generate(prompt)
    file_path = f"cache/assets/{cache_key}.glb"
    await save_file(file_path, glb_data)

    # 3. 캐시 등록
    cache_index[cache_key] = {
        "prompt": prompt,
        "file": file_path,
        ...
    }

    # 4. 캐시 크기 확인 → 필요시 정리
    await cleanup_cache_if_needed()

    return Path(file_path)
```

---

## 14. API 명세 (초안)

### POST /api/world/generate
```json
// Request
{
  "prompt": "어두운 던전에 보물상자와 횃불",
  "style": "dark_fantasy"
}

// Response (SSE Stream)
{"event": "parsing", "data": {"status": "분석 중..."}}
{"event": "layout", "data": {"size": [10, 4, 10], "assets": [...]}}
{"event": "cache_hit", "data": {"asset": "torch", "cached": true}}
{"event": "generating", "data": {"asset": "chest", "progress": 0.5}}
{"event": "asset_ready", "data": {"asset": "chest", "path": "/cache/..."}}
{"event": "complete", "data": {"world_spec": {...}}}
```

### POST /api/world/{id}/save
```json
// Request
{
  "name": "My Dungeon",
  "world_spec": { ... }
}

// Response
{
  "project_id": "project_001",
  "saved_at": "2024-01-15T10:30:00Z",
  "path": "./data/projects/project_001/"
}
```

### GET /api/world/{id}/load
```json
// Response
{
  "project_id": "project_001",
  "name": "My Dungeon",
  "world_spec": { ... },
  "created_at": "...",
  "modified_at": "..."
}
```

### POST /api/world/{id}/export
```json
// Request
{
  "format": "glb",
  "include": "all"
}

// Response
{
  "export_path": "./data/exports/project_001_20240115/",
  "files": ["scene.glb", "scene.json"]
}
```

---

## 15. 프리셋 에셋

MVP에 포함할 기본 에셋 (Text-to-3D 생성 전 즉시 사용 가능):

### 카테고리별 프리셋
```
presets/
├── furniture/
│   ├── chair_wooden.glb
│   ├── table_simple.glb
│   ├── sofa_modern.glb
│   └── desk_office.glb
├── nature/
│   ├── tree_oak.glb
│   ├── rock_large.glb
│   ├── grass_patch.glb
│   └── flower_pot.glb
├── architecture/
│   ├── door_wooden.glb
│   ├── window_glass.glb
│   ├── pillar_stone.glb
│   └── stairs_simple.glb
├── lighting/
│   ├── torch_wall.glb
│   ├── lamp_ceiling.glb
│   └── candle_holder.glb
└── skyboxes/
    ├── day_clear.hdr
    ├── night_stars.hdr
    └── sunset_warm.hdr
```

### 프리셋 매칭 로직
```python
def find_preset_match(asset_name: str, style: str) -> Optional[Path]:
    """프롬프트에서 추출한 에셋명으로 프리셋 검색"""
    keywords = extract_keywords(asset_name)  # "wooden chair" → ["wooden", "chair"]

    for preset in presets:
        if matches_keywords(preset, keywords):
            return preset.path

    return None  # 프리셋 없음 → Text-to-3D 생성
```

---

## 16. 다음 단계

1. **기술 검증**
   - Trellis API 테스트 (품질, 속도)
   - 로컬 캐시 시스템 프로토타입
   - Three.js 1인칭 컨트롤 테스트

2. **프로토타입**
   - 단일 에셋 생성 → 뷰어 표시 E2E
   - 로컬 저장/불러오기

3. **MVP 개발**
   - Phase 1-4 순차 진행

4. **테스트**
   - 다양한 프롬프트 테스트
   - 캐시 성능 측정

---

## 한 줄 요약

> **WorldForge는 "텍스트 → 진짜 3D 월드"를 로컬 환경에서 실현한다.
> 외부 의존성 없이, 생성된 에셋은 모두 로컬에 캐시되어 빠르게 재사용된다.**

---

## 17. 3D 생성 엔진: TRELLIS vs TRELLIS.2

### 비교 분석

| 항목 | TRELLIS (Original) | TRELLIS.2 |
|------|-------------------|-----------|
| **Text-to-3D** | O (네이티브) | X (Image-to-3D만) |
| **Image-to-3D** | O | O |
| **파라미터** | 342M ~ 2B | 4B |
| **GPU VRAM** | 16GB+ | 24GB+ |
| **품질** | 좋음 | 최고 (PBR 완벽 지원) |
| **속도 (512³)** | ~30초 | ~3초 (H100) |
| **O-Voxel** | X | O (복잡한 토폴로지 지원) |
| **라이선스** | MIT | MIT |
| **OS** | Linux | Linux |

### GPU 호환성

| GPU | VRAM | TRELLIS | TRELLIS.2 |
|-----|------|---------|-----------|
| RTX 3080 | 12GB | 제한적 | X |
| RTX 4080 | 16GB | O | X |
| RTX 3090 | 24GB | O | O (느림) |
| RTX 4090 | 24GB | O | O |
| A100 | 40/80GB | O | O |
| H100 | 80GB | O | O (최적) |

### TRELLIS.2 핵심 특징

1. **O-Voxel 표현**
   - "Field-free" 희소 복셀 구조
   - 개방 표면, 비매니폴드, 내부 폐쇄 구조 모두 지원
   - 기존 SDF/NeRF 한계 극복

2. **Full PBR 재질**
   - 기본색 (Base Color)
   - 거칠기 (Roughness)
   - 금속성 (Metallic)
   - 투명도 (Transparency)

3. **생성 속도** (NVIDIA H100 기준)
   | 해상도 | 시간 | 용도 |
   |--------|------|------|
   | 512³ | ~3초 | 실시간 미리보기 |
   | 1024³ | ~17초 | 표준 품질 |
   | 1536³ | ~60초 | 고품질 내보내기 |

---

## 18. Text-to-3D 파이프라인 (TRELLIS.2 기반)

**핵심: TRELLIS.2는 Image-to-3D만 지원하므로, Text→Image 단계가 필요**

### 권장 파이프라인

```
┌─────────────────────────────────────────────────────────────────┐
│                     Text-to-3D Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. User Prompt                                                 │
│      "medieval treasure chest with gold decorations"             │
│                          │                                       │
│                          ▼                                       │
│   2. Text → Image (FLUX/SD3)                                     │
│      ┌─────────────┐                                             │
│      │   [Image]   │  ← 사용자가 미리보기/승인 가능               │
│      └─────────────┘                                             │
│                          │                                       │
│                          ▼                                       │
│   3. Image → 3D (TRELLIS.2)                                      │
│      ┌─────────────┐                                             │
│      │   [GLB]     │  ← PBR 재질 포함                            │
│      └─────────────┘                                             │
│                          │                                       │
│                          ▼                                       │
│   4. Cache & Render                                              │
│      cache/assets/{hash}.glb → Three.js                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 이 파이프라인의 장점

1. **미리보기 가능**: 2D 이미지로 먼저 확인 후 3D 생성
2. **높은 품질**: 이미지 생성 기술이 텍스트 직접 생성보다 성숙
3. **유연성**: 이미지 편집 후 재생성 가능
4. **일관성**: 같은 이미지로 항상 동일한 3D 결과

### Image 생성 옵션

| 서비스 | 타입 | 품질 | 속도 | 비용 |
|--------|------|------|------|------|
| FLUX.1 (로컬) | 오픈소스 | 최고 | 중 | 무료 (GPU 필요) |
| Stable Diffusion 3 | 오픈소스 | 높음 | 빠름 | 무료 |
| DALL-E 3 | API | 높음 | 빠름 | 유료 |
| Midjourney | API | 최고 | 중 | 유료 |

### 업데이트된 데이터 흐름

```
1. User Input
   "어두운 던전에 보물상자"
          │
          ▼
2. Scene Parser (LLM)
   {
     "assets": [
       {
         "name": "treasure_chest",
         "image_prompt": "medieval wooden treasure chest, gold trim,
                          dark fantasy style, single object, white background",
         "position": [0, 0, 0]
       }
     ]
   }
          │
          ▼
3. Cache Check
   ├── HIT: 캐시된 GLB 사용
   └── MISS: 생성 파이프라인 실행
          │
          ▼
4. Image Generation (FLUX/SD3)
   cache/images/{hash}.png
          │
          ▼
5. 3D Generation (TRELLIS.2)
   cache/assets/{hash}.glb
          │
          ▼
6. Scene Assembly & Render
```

### 로컬 TRELLIS.2 설치

```bash
# 1. 저장소 클론
git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive
cd TRELLIS.2

# 2. 환경 설정 (24GB+ GPU 필요)
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm

# 3. 모델 다운로드 (자동)
# 첫 실행 시 Hugging Face에서 microsoft/TRELLIS.2-4B 다운로드
```

### 사용 예시

```python
import os
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

from PIL import Image
from trellis2.pipelines import Trellis2ImageTo3DPipeline
import o_voxel

# 파이프라인 로드
pipeline = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
pipeline.cuda()

# 이미지 → 3D 변환
image = Image.open("chest_preview.png")
mesh = pipeline.run(image)[0]
mesh.simplify(16777216)

# GLB 내보내기
glb = o_voxel.postprocess.to_glb(
    vertices=mesh.vertices,
    faces=mesh.faces,
    attr_volume=mesh.attrs,
    coords=mesh.coords,
    attr_layout=mesh.layout,
    voxel_size=mesh.voxel_size,
    aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
    decimation_target=1000000,
    texture_size=4096,
    remesh=True,
)
glb.export("treasure_chest.glb", extension_webp=True)
```

---

## 19. 듀얼 모드 지원 (권장)

사용자 GPU에 따라 자동 선택:

### Mode 1: Draft (16GB GPU)
```
Text → TRELLIS (text-to-3D) → GLB
- 빠른 프로토타이핑
- 낮은 하드웨어 요구사항
- 품질 trade-off
```

### Mode 2: Quality (24GB+ GPU)
```
Text → FLUX → TRELLIS.2 → GLB
- 최고 품질
- PBR 재질
- 이미지 미리보기
```

### 자동 감지 로직
```python
def get_generation_mode() -> str:
    vram = get_gpu_vram_gb()

    if vram >= 24:
        return "quality"  # TRELLIS.2 사용
    elif vram >= 16:
        return "draft"    # TRELLIS 사용
    else:
        return "api"      # 외부 API 사용
```

---

## 참고 자료

### Text-to-3D 모델
- [TRELLIS](https://github.com/microsoft/TRELLIS) - Text-to-3D 지원 (16GB+)
- [TRELLIS.2](https://github.com/microsoft/TRELLIS.2) - 최신 Image-to-3D (24GB+, PBR)
- [TRELLIS.2-4B (HuggingFace)](https://huggingface.co/microsoft/TRELLIS.2-4B) - 모델 다운로드
- [Hunyuan3D](https://github.com/Tencent/Hunyuan3D-2) - Tencent의 text-to-3D
- [Meshy](https://www.meshy.ai/) - 상용 API
- [Tripo AI](https://www.tripo3d.ai/) - 빠른 생성

### Image 생성
- [FLUX](https://github.com/black-forest-labs/flux) - 최고 품질 오픈소스
- [Stable Diffusion 3](https://stability.ai/stable-diffusion-3) - 빠른 생성

### 3D 렌더링
- [Three.js](https://threejs.org/)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
- [Drei](https://github.com/pmndrs/drei)

### 물리/충돌
- [Rapier](https://rapier.rs/) - Rust 기반 물리 엔진
- [@react-three/rapier](https://github.com/pmndrs/react-three-rapier)
