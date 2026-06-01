/**
 * 飞机模型组件
 * 使用Three.js基础几何体构建飞机模型，包括机身、机翼、尾翼和驾驶舱
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { COLORS } from '../utils/colors';
import { AIRCRAFT_CONFIG } from '../utils/velocityField';

interface AircraftProps {
  visible?: boolean;
}

export function Aircraft({ visible = true }: AircraftProps) {
  const groupRef = useRef<THREE.Group>(null);
  
  // 飞机材质
  const bodyMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: COLORS.AIRCRAFT_BODY,
    metalness: 0.8,
    roughness: 0.2,
  }), []);
  
  const wingMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: COLORS.AIRCRAFT_WING,
    metalness: 0.7,
    roughness: 0.3,
  }), []);
  
  const cockpitMaterial = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: COLORS.AIRCRAFT_COCKPIT,
    metalness: 0.3,
    roughness: 0.1,
    transparent: true,
    opacity: 0.7,
    clearcoat: 1.0,
    clearcoatRoughness: 0.1,
  }), []);
  
  const accentMaterial = useMemo(() => new THREE.MeshStandardMaterial({
    color: 0xff4444,
    metalness: 0.5,
    roughness: 0.5,
  }), []);
  
  // 创建机身几何体（拉长的椭球体）
  const fuselageGeometry = useMemo(() => {
    const geometry = new THREE.CapsuleGeometry(0.4, 3.2, 8, 16);
    return geometry;
  }, []);
  
  // 创建主机翼几何体（梯形翼）
  const wingGeometry = useMemo(() => {
    const shape = new THREE.Shape();
    const wingSpan = AIRCRAFT_CONFIG.WING_SPAN / 2;
    const rootChord = 1.2;
    const tipChord = 0.4;
    
    shape.moveTo(-rootChord / 2, 0);
    shape.lineTo(rootChord / 2, 0);
    shape.lineTo(tipChord / 2, wingSpan);
    shape.lineTo(-tipChord / 2, wingSpan);
    shape.lineTo(-rootChord / 2, 0);
    
    const extrudeSettings = {
      depth: 0.12,
      bevelEnabled: true,
      bevelThickness: 0.02,
      bevelSize: 0.02,
      bevelSegments: 2,
    };
    
    return new THREE.ExtrudeGeometry(shape, extrudeSettings);
  }, []);
  
  // 创建水平尾翼
  const horizontalStabilizerGeometry = useMemo(() => {
    const shape = new THREE.Shape();
    const span = 1.8;
    const rootChord = 0.6;
    const tipChord = 0.3;
    
    shape.moveTo(-rootChord / 2, 0);
    shape.lineTo(rootChord / 2, 0);
    shape.lineTo(tipChord / 2, span);
    shape.lineTo(-tipChord / 2, span);
    shape.lineTo(-rootChord / 2, 0);
    
    const extrudeSettings = {
      depth: 0.06,
      bevelEnabled: true,
      bevelThickness: 0.01,
      bevelSize: 0.01,
      bevelSegments: 1,
    };
    
    return new THREE.ExtrudeGeometry(shape, extrudeSettings);
  }, []);
  
  // 创建垂直尾翼
  const verticalStabilizerGeometry = useMemo(() => {
    const shape = new THREE.Shape();
    const height = 1.0;
    const rootChord = 0.8;
    const tipChord = 0.3;
    
    shape.moveTo(-rootChord / 2, 0);
    shape.lineTo(rootChord / 2, 0);
    shape.lineTo(tipChord / 2, height);
    shape.lineTo(-tipChord / 4, height);
    shape.lineTo(-rootChord / 2, 0);
    
    const extrudeSettings = {
      depth: 0.06,
      bevelEnabled: true,
      bevelThickness: 0.01,
      bevelSize: 0.01,
      bevelSegments: 1,
    };
    
    return new THREE.ExtrudeGeometry(shape, extrudeSettings);
  }, []);
  
  // 创建驾驶舱
  const cockpitGeometry = useMemo(() => {
    return new THREE.SphereGeometry(0.35, 16, 12, 0, Math.PI * 2, 0, Math.PI / 2);
  }, []);
  
  // 创建引擎
  const engineGeometry = useMemo(() => {
    return new THREE.CylinderGeometry(0.18, 0.2, 0.8, 16);
  }, []);
  
  // 轻微的旋转动画，展示不同角度
  useFrame((state) => {
    if (groupRef.current) {
      // 非常轻微的俯仰和滚转摆动，模拟真实飞行中的微小调整
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.02;
      groupRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.4) * 0.01;
    }
  });
  
  if (!visible) return null;
  
  const pos = AIRCRAFT_CONFIG.POSITION;
  
  return (
    <group ref={groupRef} position={[pos.x, pos.y, pos.z]}>
      {/* 机身 */}
      <mesh 
        geometry={fuselageGeometry} 
        material={bodyMaterial}
        rotation={[Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
      />
      
      {/* 主机翼 - 右侧 */}
      <mesh 
        geometry={wingGeometry} 
        material={wingMaterial}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -0.06, 0]}
      />
      
      {/* 主机翼 - 左侧 */}
      <mesh 
        geometry={wingGeometry} 
        material={wingMaterial}
        rotation={[-Math.PI / 2, Math.PI, 0]}
        position={[0, -0.06, 0]}
      />
      
      {/* 水平尾翼 - 右侧 */}
      <mesh 
        geometry={horizontalStabilizerGeometry} 
        material={wingMaterial}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, -0.03, -1.8]}
      />
      
      {/* 水平尾翼 - 左侧 */}
      <mesh 
        geometry={horizontalStabilizerGeometry} 
        material={wingMaterial}
        rotation={[-Math.PI / 2, Math.PI, 0]}
        position={[0, -0.03, -1.8]}
      />
      
      {/* 垂直尾翼 */}
      <mesh 
        geometry={verticalStabilizerGeometry} 
        material={wingMaterial}
        rotation={[0, 0, 0]}
        position={[0, 0, -1.8]}
      />
      
      {/* 驾驶舱 */}
      <mesh 
        geometry={cockpitGeometry} 
        material={cockpitMaterial}
        rotation={[0, 0, 0]}
        position={[0, 0.1, 0.5]}
      />
      
      {/* 引擎 - 右 */}
      <mesh 
        geometry={engineGeometry} 
        material={bodyMaterial}
        rotation={[0, 0, Math.PI / 2]}
        position={[1.0, -0.3, 0.2]}
      />
      
      {/* 引擎 - 左 */}
      <mesh 
        geometry={engineGeometry} 
        material={bodyMaterial}
        rotation={[0, 0, Math.PI / 2]}
        position={[-1.0, -0.3, 0.2]}
      />
      
      {/* 引擎进气口装饰 */}
      <mesh position={[1.0, -0.3, 0.6]}>
        <circleGeometry args={[0.18, 16]} />
        <meshBasicMaterial color={0x111111} side={THREE.DoubleSide} />
      </mesh>
      
      <mesh position={[-1.0, -0.3, 0.6]}>
        <circleGeometry args={[0.18, 16]} />
        <meshBasicMaterial color={0x111111} side={THREE.DoubleSide} />
      </mesh>
      
      {/* 翼尖标记灯 */}
      <mesh position={[0, -0.1, AIRCRAFT_CONFIG.WING_SPAN / 2 - 0.1]}>
        <sphereGeometry args={[0.06, 8, 8]} />
        <meshBasicMaterial color={0xff0000} />
      </mesh>
      
      <mesh position={[0, -0.1, -AIRCRAFT_CONFIG.WING_SPAN / 2 + 0.1]}>
        <sphereGeometry args={[0.06, 8, 8]} />
        <meshBasicMaterial color={0x00ff00} />
      </mesh>
      
      {/* 机头装饰线 */}
      <mesh position={[0, 0, 2.0]}>
        <coneGeometry args={[0.15, 0.3, 8]} />
        <primitive object={accentMaterial} attach="material" />
      </mesh>
    </group>
  );
}
