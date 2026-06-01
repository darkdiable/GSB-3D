/**
 * 风洞组件
 * 创建透明的矩形风洞壳体，包括玻璃墙面和金属边框
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { COLORS } from '../utils/colors';
import { WIND_TUNNEL_CONFIG } from '../utils/velocityField';

interface WindTunnelProps {
  visible?: boolean;
}

export function WindTunnel({ visible = true }: WindTunnelProps) {
  const groupRef = useRef<THREE.Group>(null);
  const frameRef = useRef<THREE.LineSegments>(null);
  
  const { WIDTH: width, HEIGHT: height, LENGTH: length } = WIND_TUNNEL_CONFIG;
  
  // 创建玻璃墙面材质
  const glassMaterial = useMemo(() => new THREE.MeshPhysicalMaterial({
    color: COLORS.WIND_TUNNEL_GLASS,
    transparent: true,
    opacity: 0.15,
    roughness: 0.1,
    metalness: 0.1,
    transmission: 0.9,
    thickness: 0.5,
    clearcoat: 1.0,
    clearcoatRoughness: 0.1,
    side: THREE.DoubleSide,
  }), []);
  
  // 创建边框线框几何体
  const frameGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    const vertices: number[] = [];
    
    const hw = width / 2;
    const hh = height / 2;
    const hl = length / 2;
    
    // 前面矩形
    vertices.push(-hw, -hh, hl, hw, -hh, hl);
    vertices.push(hw, -hh, hl, hw, hh, hl);
    vertices.push(hw, hh, hl, -hw, hh, hl);
    vertices.push(-hw, hh, hl, -hw, -hh, hl);
    
    // 后面矩形
    vertices.push(-hw, -hh, -hl, hw, -hh, -hl);
    vertices.push(hw, -hh, -hl, hw, hh, -hl);
    vertices.push(hw, hh, -hl, -hw, hh, -hl);
    vertices.push(-hw, hh, -hl, -hw, -hh, -hl);
    
    // 连接线
    vertices.push(-hw, -hh, hl, -hw, -hh, -hl);
    vertices.push(hw, -hh, hl, hw, -hh, -hl);
    vertices.push(hw, hh, hl, hw, hh, -hl);
    vertices.push(-hw, hh, hl, -hw, hh, -hl);
    
    // 添加刻度线
    const tickCount = 9;
    for (let i = 1; i < tickCount; i++) {
      const z = hl - (length / tickCount) * i;
      const tickSize = 0.2;
      
      vertices.push(-hw, -hh, z, -hw + tickSize, -hh, z);
      vertices.push(hw - tickSize, -hh, z, hw, -hh, z);
      vertices.push(-hw, hh, z, -hw + tickSize, hh, z);
      vertices.push(hw - tickSize, hh, z, hw, hh, z);
    }
    
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    return geometry;
  }, [width, height, length]);
  
  // 创建边框材质
  const frameMaterial = useMemo(() => new THREE.LineBasicMaterial({
    color: COLORS.WIND_TUNNEL_FRAME,
    transparent: true,
    opacity: 0.6,
  }), []);
  
  // 入口和出口标记圆环
  const entranceRing = useMemo(() => {
    const shape = new THREE.Shape();
    const hw = width / 2;
    const hh = height / 2;
    shape.moveTo(-hw, -hh);
    shape.lineTo(hw, -hh);
    shape.lineTo(hw, hh);
    shape.lineTo(-hw, hh);
    shape.lineTo(-hw, -hh);
    
    const hole = new THREE.Path();
    const innerHw = hw - 0.3;
    const innerHh = hh - 0.3;
    hole.moveTo(-innerHw, -innerHh);
    hole.lineTo(innerHw, -innerHh);
    hole.lineTo(innerHw, innerHh);
    hole.lineTo(-innerHw, innerHh);
    hole.lineTo(-innerHw, -innerHh);
    shape.holes.push(hole);
    
    return new THREE.ShapeGeometry(shape);
  }, [width, height]);
  
  const ringMaterial = useMemo(() => new THREE.MeshBasicMaterial({
    color: COLORS.WIND_TUNNEL_FRAME,
    transparent: true,
    opacity: 0.3,
    side: THREE.DoubleSide,
  }), []);
  
  // 轻微的动画效果
  useFrame((state) => {
    if (frameRef.current) {
      const pulse = 0.5 + Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
      frameMaterial.opacity = 0.5 + pulse * 0.2;
    }
  });
  
  if (!visible) return null;
  
  return (
    <group ref={groupRef}>
      {/* 玻璃墙面 - 上下左右前后 */}
      <mesh position={[0, height / 2, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <planeGeometry args={[width, length]} />
        <primitive object={glassMaterial} attach="material" />
      </mesh>
      
      <mesh position={[0, -height / 2, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[width, length]} />
        <primitive object={glassMaterial} attach="material" />
      </mesh>
      
      <mesh position={[width / 2, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
        <planeGeometry args={[length, height]} />
        <primitive object={glassMaterial} attach="material" />
      </mesh>
      
      <mesh position={[-width / 2, 0, 0]} rotation={[0, -Math.PI / 2, 0]}>
        <planeGeometry args={[length, height]} />
        <primitive object={glassMaterial} attach="material" />
      </mesh>
      
      {/* 边框线框 */}
      <lineSegments ref={frameRef} geometry={frameGeometry} material={frameMaterial} />
      
      {/* 入口标记环 */}
      <mesh position={[0, 0, length / 2]} geometry={entranceRing} material={ringMaterial} />
      
      {/* 出口标记环 */}
      <mesh position={[0, 0, -length / 2]} geometry={entranceRing} material={ringMaterial} />
      
      {/* 气流方向箭头指示 */}
      <group position={[0, height / 2 - 0.5, 0]}>
        {[-6, -2, 2, 6].map((z, i) => (
          <mesh key={i} position={[0, 0, z]} rotation={[0, 0, Math.PI / 2]}>
            <coneGeometry args={[0.15, 0.4, 4]} />
            <meshBasicMaterial color={COLORS.HIGH_SPEED} transparent opacity={0.6} />
          </mesh>
        ))}
      </group>
    </group>
  );
}
