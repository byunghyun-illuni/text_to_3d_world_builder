import { useRef, useEffect, useState } from "react";
import { useThree, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { Vector3 } from "../types/world_spec";

interface FirstPersonControlsProps {
  spawnpoint?: Vector3;
  moveSpeed?: number;
}

export function FirstPersonControls({
  spawnpoint = [0, 1, 0],
  moveSpeed = 5,
}: FirstPersonControlsProps) {
  const { camera, gl } = useThree();
  const [isLocked, setIsLocked] = useState(false);
  const moveState = useRef({
    forward: false,
    backward: false,
    left: false,
    right: false,
  });
  const euler = useRef(new THREE.Euler(0, 0, 0, "YXZ"));

  // Set initial camera position
  useEffect(() => {
    camera.position.set(spawnpoint[0], spawnpoint[1], spawnpoint[2]);
  }, [camera, spawnpoint]);

  // Pointer lock handlers
  useEffect(() => {
    const canvas = gl.domElement;

    const handleClick = () => {
      canvas.requestPointerLock();
    };

    const handleLockChange = () => {
      setIsLocked(document.pointerLockElement === canvas);
    };

    const handleLockError = () => {
      console.error("Pointer lock error");
    };

    canvas.addEventListener("click", handleClick);
    document.addEventListener("pointerlockchange", handleLockChange);
    document.addEventListener("pointerlockerror", handleLockError);

    return () => {
      canvas.removeEventListener("click", handleClick);
      document.removeEventListener("pointerlockchange", handleLockChange);
      document.removeEventListener("pointerlockerror", handleLockError);
    };
  }, [gl]);

  // Mouse movement handler
  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (!isLocked) return;

      const sensitivity = 0.002;
      euler.current.setFromQuaternion(camera.quaternion);
      euler.current.y -= event.movementX * sensitivity;
      euler.current.x -= event.movementY * sensitivity;
      euler.current.x = Math.max(
        -Math.PI / 2,
        Math.min(Math.PI / 2, euler.current.x)
      );
      camera.quaternion.setFromEuler(euler.current);
    };

    document.addEventListener("mousemove", handleMouseMove);
    return () => document.removeEventListener("mousemove", handleMouseMove);
  }, [camera, isLocked]);

  // Keyboard event handlers
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isLocked) return;

      switch (event.code) {
        case "KeyW":
        case "ArrowUp":
          moveState.current.forward = true;
          break;
        case "KeyS":
        case "ArrowDown":
          moveState.current.backward = true;
          break;
        case "KeyA":
        case "ArrowLeft":
          moveState.current.left = true;
          break;
        case "KeyD":
        case "ArrowRight":
          moveState.current.right = true;
          break;
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      switch (event.code) {
        case "KeyW":
        case "ArrowUp":
          moveState.current.forward = false;
          break;
        case "KeyS":
        case "ArrowDown":
          moveState.current.backward = false;
          break;
        case "KeyA":
        case "ArrowLeft":
          moveState.current.left = false;
          break;
        case "KeyD":
        case "ArrowRight":
          moveState.current.right = false;
          break;
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("keyup", handleKeyUp);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("keyup", handleKeyUp);
    };
  }, [isLocked]);

  // Movement update
  useFrame((_, delta) => {
    if (!isLocked) return;

    const velocity = new THREE.Vector3();
    const direction = new THREE.Vector3();

    // Get camera direction
    camera.getWorldDirection(direction);
    direction.y = 0;
    direction.normalize();

    // Calculate right vector
    const right = new THREE.Vector3();
    right.crossVectors(camera.up, direction).normalize();

    // Apply movement
    if (moveState.current.forward) velocity.add(direction);
    if (moveState.current.backward) velocity.sub(direction);
    if (moveState.current.left) velocity.add(right);
    if (moveState.current.right) velocity.sub(right);

    // Normalize and apply speed
    if (velocity.length() > 0) {
      velocity.normalize().multiplyScalar(moveSpeed * delta);
      camera.position.add(velocity);
    }
  });

  return null;
}
