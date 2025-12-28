import { useMemo } from "react";
import type { PrimitiveEntity as PrimitiveEntityType } from "../../types/world_spec";

interface PrimitiveEntityProps {
  entity: PrimitiveEntityType;
}

export function PrimitiveEntity({ entity }: PrimitiveEntityProps) {
  const { primitive, position, rotation, scale, size, color, role } = entity;

  const meshPosition = useMemo(() => {
    const [x, y, z] = position;
    // Adjust Y position based on size for ground placement
    const entitySize = size || getDefaultSize(primitive, role);
    return [x, y + entitySize[1] / 2, z] as [number, number, number];
  }, [position, size, primitive, role]);

  const meshRotation = useMemo(() => {
    if (!rotation) return [0, 0, 0] as [number, number, number];
    return rotation as [number, number, number];
  }, [rotation]);

  const meshScale = useMemo(() => {
    return (scale || [1, 1, 1]) as [number, number, number];
  }, [scale]);

  const entitySize = size || getDefaultSize(primitive, role);
  const entityColor = color || getDefaultColor(role);

  return (
    <mesh
      position={meshPosition}
      rotation={meshRotation}
      scale={meshScale}
      castShadow
      receiveShadow
    >
      <PrimitiveGeometry type={primitive} size={entitySize} />
      <meshStandardMaterial color={entityColor} />
    </mesh>
  );
}

interface PrimitiveGeometryProps {
  type: "box" | "plane" | "capsule" | "sphere" | "cylinder";
  size: [number, number, number];
}

function PrimitiveGeometry({ type, size }: PrimitiveGeometryProps) {
  const [width, height, depth] = size;

  switch (type) {
    case "box":
      return <boxGeometry args={[width, height, depth]} />;

    case "plane":
      return <planeGeometry args={[width, depth]} />;

    case "capsule":
      // Capsule: radius = width/2, length = height - width (for caps)
      const radius = width / 2;
      const capsuleLength = Math.max(0, height - width);
      return <capsuleGeometry args={[radius, capsuleLength, 8, 16]} />;

    case "sphere":
      return <sphereGeometry args={[width / 2, 32, 32]} />;

    case "cylinder":
      return <cylinderGeometry args={[width / 2, width / 2, height, 32]} />;

    default:
      return <boxGeometry args={[width, height, depth]} />;
  }
}

function getDefaultSize(
  primitive: string,
  role?: string
): [number, number, number] {
  if (role === "character") {
    return [0.5, 1.8, 0.5];
  }
  if (role === "prop") {
    return [1, 1, 1];
  }

  switch (primitive) {
    case "capsule":
      return [0.5, 1.8, 0.5];
    case "sphere":
      return [1, 1, 1];
    case "cylinder":
      return [0.5, 1, 0.5];
    case "plane":
      return [1, 0.01, 1];
    default:
      return [1, 1, 1];
  }
}

function getDefaultColor(role?: string): string {
  switch (role) {
    case "character":
      return "#4A90D9"; // Blue
    case "prop":
      return "#808080"; // Gray
    case "structure":
      return "#8B4513"; // Brown
    default:
      return "#808080";
  }
}
