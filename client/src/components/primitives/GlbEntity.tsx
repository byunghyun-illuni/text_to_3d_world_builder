import { useRef, useEffect } from "react";
import { useGLTF } from "@react-three/drei";
import * as THREE from "three";
import type { GlbEntity as GlbEntityType } from "../../types/world_spec";

interface GlbEntityProps {
  entity: GlbEntityType;
}

export function GlbEntity({ entity }: GlbEntityProps) {
  const { src, position, rotation, scale } = entity;
  const groupRef = useRef<THREE.Group>(null);

  // src에서 public 경로 추출 (assets/models/... 형태)
  const modelPath = src.startsWith("/") ? src : `/${src}`;

  // GLTF 로드
  const { scene } = useGLTF(modelPath);

  // 씬 클론 (같은 모델을 여러 번 사용할 수 있도록)
  const clonedScene = scene.clone();

  // 그림자 설정
  useEffect(() => {
    if (groupRef.current) {
      groupRef.current.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });
    }
  }, []);

  // 위치/회전/스케일 계산
  const meshPosition: [number, number, number] = position
    ? [position[0], position[1], position[2]]
    : [0, 0, 0];

  const meshRotation: [number, number, number] = rotation
    ? [rotation[0], rotation[1], rotation[2]]
    : [0, 0, 0];

  const meshScale: [number, number, number] = scale
    ? [scale[0], scale[1], scale[2]]
    : [1, 1, 1];

  return (
    <group ref={groupRef} position={meshPosition} rotation={meshRotation} scale={meshScale}>
      <primitive object={clonedScene} />
    </group>
  );
}
