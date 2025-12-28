import { useRef, useEffect } from "react";
import { useThree } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import type { Vector3 } from "../types/world_spec";

interface CameraControlsProps {
  spawnpoint?: Vector3;
}

export function CameraControls({ spawnpoint = [0, 2, 5] }: CameraControlsProps) {
  const { camera } = useThree();
  const controlsRef = useRef<OrbitControlsImpl>(null);

  // 초기 카메라 위치 설정
  useEffect(() => {
    camera.position.set(spawnpoint[0], spawnpoint[1] + 3, spawnpoint[2] + 5);
    camera.lookAt(0, 0, 0);
  }, [camera, spawnpoint]);

  return (
    <OrbitControls
      ref={controlsRef}
      enableDamping
      dampingFactor={0.1}
      rotateSpeed={0.5}
      panSpeed={0.5}
      zoomSpeed={0.5}
      minDistance={1}
      maxDistance={50}
      maxPolarAngle={Math.PI / 2.1} // 바닥 아래로 못 가게
    />
  );
}
