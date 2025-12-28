import type { Vector3 } from "../../types/world_spec";

interface RoomSpaceProps {
  size: Vector3;
}

export function RoomSpace({ size }: RoomSpaceProps) {
  const [width, height, depth] = size;
  const wallThickness = 0.1;
  const wallColor = "#e0e0e0";
  const floorColor = "#a0a0a0";

  return (
    <group name="room">
      {/* Floor */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        receiveShadow
      >
        <planeGeometry args={[width, depth]} />
        <meshStandardMaterial color={floorColor} />
      </mesh>

      {/* Back Wall */}
      <mesh position={[0, height / 2, -depth / 2]} receiveShadow>
        <boxGeometry args={[width, height, wallThickness]} />
        <meshStandardMaterial color={wallColor} />
      </mesh>

      {/* Front Wall */}
      <mesh position={[0, height / 2, depth / 2]} receiveShadow>
        <boxGeometry args={[width, height, wallThickness]} />
        <meshStandardMaterial color={wallColor} />
      </mesh>

      {/* Left Wall */}
      <mesh position={[-width / 2, height / 2, 0]} receiveShadow>
        <boxGeometry args={[wallThickness, height, depth]} />
        <meshStandardMaterial color={wallColor} />
      </mesh>

      {/* Right Wall */}
      <mesh position={[width / 2, height / 2, 0]} receiveShadow>
        <boxGeometry args={[wallThickness, height, depth]} />
        <meshStandardMaterial color={wallColor} />
      </mesh>
    </group>
  );
}
