import { useState } from "react";
import { Scene } from "./components/Scene";
import type { WorldSpec } from "./types/world_spec";
import "./App.css";

// 테스트용 샘플 WorldSpec - 가벼운 모델만 사용
const SAMPLE_WORLD_SPEC: WorldSpec = {
  version: "0.1",
  name: "로비",
  space: {
    type: "room",
    size: [12, 3, 12],
  },
  spawnpoint: [0, 1.6, 5],
  entities: [
    // 가벼운 GLB 모델들
    {
      id: "fox_1",
      assetType: "glb",
      src: "assets/models/decor/fox.glb",
      role: "character",
      name: "여우",
      position: [0, 0, 0],
      scale: [0.015, 0.015, 0.015],
    },
    {
      id: "parrot_1",
      assetType: "glb",
      src: "assets/models/decor/parrot.glb",
      role: "prop",
      name: "앵무새",
      position: [2, 0.5, -2],
      scale: [0.015, 0.015, 0.015],
    },
    {
      id: "flamingo_1",
      assetType: "glb",
      src: "assets/models/decor/flamingo.glb",
      role: "prop",
      name: "플라밍고",
      position: [-2, 0, -2],
      scale: [0.015, 0.015, 0.015],
    },
    // 프리미티브도 혼합
    {
      id: "box_1",
      assetType: "primitive",
      primitive: "box",
      role: "prop",
      name: "테이블",
      position: [3, 0, 0],
      size: [1.5, 0.5, 1],
      color: "#8B4513",
    },
    {
      id: "box_2",
      assetType: "primitive",
      primitive: "box",
      role: "prop",
      name: "소파",
      position: [-3, 0, 0],
      size: [2, 0.6, 0.8],
      color: "#4A5568",
    },
  ],
  zones: [],
};

function App() {
  const [worldSpec, setWorldSpec] = useState<WorldSpec | null>(
    SAMPLE_WORLD_SPEC
  );
  const [debugMode, setDebugMode] = useState(true);
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/world/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error("Failed to compile");
      }

      const data = await response.json();
      setWorldSpec(data.world_spec);
    } catch (error) {
      console.error("Error:", error);
      alert("월드 생성 실패. 서버가 실행 중인지 확인하세요.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>Text-to-3D World Builder</h1>
        <div className="header-controls">
          <label>
            <input
              type="checkbox"
              checked={debugMode}
              onChange={(e) => setDebugMode(e.target.checked)}
            />
            Debug Mode
          </label>
        </div>
      </header>

      {/* Main Content */}
      <div className="main">
        {/* Left Panel - Input */}
        <aside className="panel left-panel">
          <h2>자연어 입력</h2>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="예: 사각형 로비를 만들고 중앙에 안내원을 배치해줘"
            rows={4}
          />
          <button onClick={handleGenerate} disabled={isLoading}>
            {isLoading ? "생성 중..." : "월드 생성"}
          </button>

          <h2>World Spec</h2>
          <pre className="world-spec-preview">
            {worldSpec ? JSON.stringify(worldSpec, null, 2) : "없음"}
          </pre>
        </aside>

        {/* 3D Viewport */}
        <main className="viewport">
          <Scene worldSpec={worldSpec} debugMode={debugMode} />
          <div className="viewport-hint">
            3D 뷰포트 클릭 → 이동 모드 (WASD + 마우스) | ESC로 해제
          </div>
        </main>

        {/* Right Panel - Inspector */}
        <aside className="panel right-panel">
          <h2>Inspector</h2>
          {worldSpec && (
            <div className="inspector-content">
              <p>
                <strong>World:</strong> {worldSpec.name}
              </p>
              <p>
                <strong>Size:</strong> {worldSpec.space.size.join(" x ")}m
              </p>
              <p>
                <strong>Entities:</strong> {worldSpec.entities.length}
              </p>
              <p>
                <strong>Zones:</strong> {worldSpec.zones?.length || 0}
              </p>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

export default App;
