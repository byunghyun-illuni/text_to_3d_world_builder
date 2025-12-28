import { Canvas } from "@react-three/fiber";
import { Grid, Stats } from "@react-three/drei";
import { Suspense } from "react";
import { WorldRenderer } from "./WorldRenderer";
import { CameraControls } from "./CameraControls";
import type { WorldSpec } from "../types/world_spec";

interface SceneProps {
  worldSpec: WorldSpec | null;
  debugMode?: boolean;
}

export function Scene({ worldSpec, debugMode = false }: SceneProps) {
  return (
    <Canvas
      shadows={false} // 그림자 비활성화 (성능)
      camera={{ fov: 60, near: 0.1, far: 500, position: [0, 5, 10] }}
      style={{ width: "100%", height: "100%" }}
      gl={{ antialias: true, powerPreference: "high-performance" }}
    >
      <Suspense fallback={null}>
        {/* Lighting - 단순화 */}
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 20, 10]} intensity={0.8} />

        {/* Sky color */}
        <color attach="background" args={["#87CEEB"]} />

        {/* Ground Grid (debug) */}
        {debugMode && (
          <Grid
            args={[50, 50]}
            cellSize={1}
            cellThickness={0.5}
            cellColor="#6e6e6e"
            sectionSize={5}
            sectionThickness={1}
            sectionColor="#9d4b4b"
            fadeDistance={30}
            infiniteGrid
          />
        )}

        {/* World Renderer */}
        {worldSpec && <WorldRenderer worldSpec={worldSpec} />}

        {/* Orbit Controls - 마우스로 회전/줌/팬 */}
        <CameraControls spawnpoint={worldSpec?.spawnpoint} />

        {/* Debug Stats */}
        {debugMode && <Stats />}
      </Suspense>
    </Canvas>
  );
}
