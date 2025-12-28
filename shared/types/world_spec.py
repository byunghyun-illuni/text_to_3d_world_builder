"""
World Spec Python Types (Pydantic Models)
Generated from world-spec.schema.json
"""

from typing import Literal, Union
from pydantic import BaseModel, Field


Vector3 = tuple[float, float, float]


class Space(BaseModel):
    type: Literal["room"]
    size: Vector3


class BaseEntity(BaseModel):
    id: str
    name: str | None = None
    position: Vector3
    rotation: Vector3 | None = None
    scale: Vector3 | None = None


class PrimitiveEntity(BaseEntity):
    asset_type: Literal["primitive"] = Field(alias="assetType")
    primitive: Literal["box", "plane", "capsule", "sphere", "cylinder"]
    size: Vector3 | None = None
    color: str | None = None
    role: Literal["character", "prop", "structure"] | None = None

    model_config = {"populate_by_name": True}


class GlbEntity(BaseEntity):
    asset_type: Literal["glb"] = Field(alias="assetType")
    src: str
    role: Literal["character", "prop", "structure"] | None = None

    model_config = {"populate_by_name": True}


class SplatEntity(BaseEntity):
    asset_type: Literal["splat"] = Field(alias="assetType")
    src: str
    format: Literal["ply", "splat", "ksplat", "spz"] | None = None

    model_config = {"populate_by_name": True}


Entity = Union[PrimitiveEntity, GlbEntity, SplatEntity]


class Zone(BaseModel):
    id: str
    name: str
    bounds: tuple[Vector3, Vector3]


class WorldSpec(BaseModel):
    version: str
    name: str
    space: Space
    spawnpoint: Vector3
    entities: list[Entity]
    zones: list[Zone] | None = None


# API Response Types
class CompileResponse(BaseModel):
    dsl: str
    world_spec: WorldSpec = Field(alias="worldSpec")
    warnings: list[str] = []

    model_config = {"populate_by_name": True}


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = []
    warnings: list[str] = []
    auto_fixed: WorldSpec | None = Field(default=None, alias="autoFixed")

    model_config = {"populate_by_name": True}
