/**
 * World Spec TypeScript Types
 * Generated from world-spec.schema.json
 */

export type Vector3 = [number, number, number];

export interface Space {
  type: "room";
  size: Vector3;
}

export interface BaseEntity {
  id: string;
  name?: string;
  position: Vector3;
  rotation?: Vector3;
  scale?: Vector3;
}

export interface PrimitiveEntity extends BaseEntity {
  assetType: "primitive";
  primitive: "box" | "plane" | "capsule" | "sphere" | "cylinder";
  size?: Vector3;
  color?: string;
  role?: "character" | "prop" | "structure";
}

export interface GlbEntity extends BaseEntity {
  assetType: "glb";
  src: string;
  role?: "character" | "prop" | "structure";
}

export interface SplatEntity extends BaseEntity {
  assetType: "splat";
  src: string;
  format?: "ply" | "splat" | "ksplat" | "spz";
}

export type Entity = PrimitiveEntity | GlbEntity | SplatEntity;

export interface Zone {
  id: string;
  name: string;
  bounds: [Vector3, Vector3];
}

export interface WorldSpec {
  version: string;
  name: string;
  space: Space;
  spawnpoint: Vector3;
  entities: Entity[];
  zones?: Zone[];
}

/**
 * API Response Types
 */
export interface CompileResponse {
  dsl: string;
  worldSpec: WorldSpec;
  warnings: string[];
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  autoFixed?: WorldSpec;
}
