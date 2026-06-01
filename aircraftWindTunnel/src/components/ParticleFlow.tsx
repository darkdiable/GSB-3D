/**
 * 粒子流系统组件
 * 实现动态气流可视化，使用彩色粒子表现速度场分布
 * 机翼上方粒子流速更快，颜色更偏向青色
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useParticleSystem } from '../hooks/useParticleSystem';
import { useSceneStore } from '../store/useSceneStore';

interface ParticleFlowProps {
  visible?: boolean;
}

export function ParticleFlow({ visible = true }: ParticleFlowProps) {
  const pointsRef = useRef<THREE.Points>(null);
  const lastTimeRef = useRef<number>(performance.now());
  
  const { particleCount, baseSpeed, isPlaying } = useSceneStore();
  
  const { geometry, updateParticles } = useParticleSystem({
    count: particleCount,
    baseSpeed,
    isPlaying,
  });
  
  // 粒子材质
  const particleMaterial = useMemo(() => new THREE.PointsMaterial({
    size: 0.08,
    vertexColors: true,
    transparent: true,
    opacity: 0.9,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true,
  }), []);
  
  // 创建拖尾线条几何体（用于表现流线效果）
  const trailGeometry = useMemo(() => {
    const trailCount = Math.floor(particleCount / 10);
    const positions = new Float32Array(trailCount * 6); // 每条线2个点，每个点3个坐标
    const colors = new Float32Array(trailCount * 6);
    
    for (let i = 0; i < trailCount; i++) {
      const i6 = i * 6;
      positions[i6] = (Math.random() - 0.5) * 8;
      positions[i6 + 1] = (Math.random() - 0.5) * 6;
      positions[i6 + 2] = (Math.random() - 0.5) * 20;
      positions[i6 + 3] = positions[i6];
      positions[i6 + 4] = positions[i6 + 1];
      positions[i6 + 5] = positions[i6 + 2] - 0.5;
      
      for (let j = 0; j < 6; j++) {
        colors[i6 + j] = 0.5 + Math.random() * 0.5;
      }
    }
    
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    return geo;
  }, [particleCount]);
  
  const trailMaterial = useMemo(() => new THREE.LineBasicMaterial({
    vertexColors: true,
    transparent: true,
    opacity: 0.4,
    blending: THREE.AdditiveBlending,
  }), []);
  
  // 动画更新
  useFrame((_, delta) => {
    if (!isPlaying || !visible) return;
    
    const now = performance.now();
    const deltaTime = (now - lastTimeRef.current) / 1000;
    lastTimeRef.current = now;
    
    updateParticles(deltaTime * baseSpeed * 0.3);
    
    // 更新拖尾线条
    if (pointsRef.current) {
      const positions = geometry.attributes.position.array as Float32Array;
      const colors = geometry.attributes.color.array as Float32Array;
      const trailPositions = trailGeometry.attributes.position.array as Float32Array;
      const trailColors = trailGeometry.attributes.color.array as Float32Array;
      
      const trailCount = trailPositions.length / 6;
      for (let i = 0; i < trailCount; i++) {
        const sourceIdx = (i * 10) % particleCount;
        const i3 = sourceIdx * 3;
        const i6 = i * 6;
        
        trailPositions[i6] = positions[i3];
        trailPositions[i6 + 1] = positions[i3 + 1];
        trailPositions[i6 + 2] = positions[i3 + 2];
        trailPositions[i6 + 3] = positions[i3];
        trailPositions[i6 + 4] = positions[i3 + 1];
        trailPositions[i6 + 5] = positions[i3 + 2] - 0.3;
        
        trailColors[i6] = colors[i3];
        trailColors[i6 + 1] = colors[i3 + 1];
        trailColors[i6 + 2] = colors[i3 + 2];
        trailColors[i6 + 3] = colors[i3] * 0.5;
        trailColors[i6 + 4] = colors[i3 + 1] * 0.5;
        trailColors[i6 + 5] = colors[i3 + 2] * 0.5;
      }
      
      trailGeometry.attributes.position.needsUpdate = true;
      trailGeometry.attributes.color.needsUpdate = true;
    }
  });
  
  if (!visible) return null;
  
  return (
    <group>
      {/* 主粒子系统 */}
      <points ref={pointsRef} geometry={geometry} material={particleMaterial} />
      
      {/* 流线拖尾效果 */}
      <lineSegments geometry={trailGeometry} material={trailMaterial} />
    </group>
  );
}
