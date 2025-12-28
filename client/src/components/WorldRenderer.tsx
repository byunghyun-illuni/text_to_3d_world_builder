import { useMemo, Suspense } from "react";
import type { WorldSpec, Entity } from "../types/world_spec";
import { RoomSpace } from "./primitives/RoomSpace";
import { PrimitiveEntity } from "./primitives/PrimitiveEntity";
import { GlbEntity } from "./primitives/GlbEntity";

interface WorldRendererProps {
  worldSpec: WorldSpec;
}

export function WorldRenderer({ worldSpec }: WorldRendererProps) {
  const { space, entities, zones } = worldSpec;

  return (
    <group name="world">
      {/* Room Space (floor + walls) */}
      {space && <RoomSpace size={space.size} />}

      {/* Entities */}
      {entities.map((entity) => (
        <EntityRenderer key={entity.id} entity={entity} />
      ))}

      {/* Zones (debug visualization) */}
      {zones?.map((zone) => (
        <ZoneRenderer key={zone.id} zone={zone} />
      ))}
    </group>
  );
}

interface EntityRendererProps {
  entity: Entity;
}

function EntityRenderer({ entity }: EntityRendererProps) {
  switch (entity.assetType) {
    case "primitive":
      return <PrimitiveEntity entity={entity} />;
    case "glb":
      return (
        <Suspense fallback={<FallbackBox position={entity.position} />}>
          <GlbEntity entity={entity} />
        </Suspense>
      );
    case "splat":
      // TODO: Implement Splat loader
      return null;
    default:
      return null;
  }
}

// GLB 로딩 중 표시할 폴백 박스
function FallbackBox({ position }: { position: [number, number, number] }) {
  return (
    <mesh position={[position[0], position[1] + 0.5, position[2]]}>
      <boxGeometry args={[0.5, 1, 0.5]} />
      <meshStandardMaterial color="#cccccc" wireframe />
    </mesh>
  );
}

interface ZoneRendererProps {
  zone: {
    id: string;
    name: string;
    bounds: [[number, number, number], [number, number, number]];
  };
}

function ZoneRenderer({ zone }: ZoneRendererProps) {
  const { bounds } = zone;
  const [min, max] = bounds;

  const size = useMemo(
    () => [max[0] - min[0], max[1] - min[1] || 0.1, max[2] - min[2]] as const,
    [min, max]
  );

  const position = useMemo(
    () =>
      [
        (min[0] + max[0]) / 2,
        (min[1] + max[1]) / 2 || 0.05,
        (min[2] + max[2]) / 2,
      ] as const,
    [min, max]
  );

  return (
    <mesh position={position}>
      <boxGeometry args={[size[0], size[1], size[2]]} />
      <meshBasicMaterial
        color="#00ff00"
        transparent
        opacity={0.1}
        wireframe={false}
      />
    </mesh>
  );
}
