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
  
  // 粒子材质 - 增强视觉效果，在玻璃后面也清晰可见
  const particleMaterial = useMemo(() => new THREE.PointsMaterial({
    size: 0.12,
    vertexColors: true,
    transparent: true,
    opacity: 1.0,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    sizeAttenuation: true,
  }), []);
  
  // 创建拖尾线条几何体（用于表现流线效果）- 增加拖尾数量和长度
  const trailGeometry = useMemo(() => {
    const trailCount = Math.floor(particleCount / 5);
    const trailLength = 5;
    const positions = new Float32Array(trailCount * trailLength * 2 * 3);
    const colors = new Float32Array(trailCount * trailLength * 2 * 3);
    
    for (let i = 0; i < trailCount; i++) {
      const baseX = (Math.random() - 0.5) * 8;
      const baseY = (Math.random() - 0.5) * 6;
      const baseZ = (Math.random() - 0.5) * 20;
      
      for (let j = 0; j < trailLength; j++) {
        const idx = (i * trailLength + j) * 6;
        positions[idx] = baseX;
        positions[idx + 1] = baseY;
        positions[idx + 2] = baseZ - j * 0.15;
        positions[idx + 3] = baseX;
        positions[idx + 4] = baseY;
        positions[idx + 5] = baseZ - (j + 1) * 0.15;
        
        const colorIntensity = 1 - j / trailLength;
        for (let k = 0; k < 6; k++) {
          colors[idx + k] = 0.3 + Math.random() * 0.7;
        }
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
    opacity: 0.6,
    blending: THREE.AdditiveBlending,
  }), []);
  
  // 动画更新
  useFrame((_, delta) => {
    if (!isPlaying || !visible) return;
    
    const now = performance.now();
    const deltaTime = (now - lastTimeRef.current) / 1000;
    lastTimeRef.current = now;
    
    updateParticles(deltaTime * baseSpeed * 0.3);
    
    // 更新拖尾线条 - 增强的流线效果
    if (pointsRef.current) {
      const positions = geometry.attributes.position.array as Float32Array;
      const colors = geometry.attributes.color.array as Float32Array;
      const trailPositions = trailGeometry.attributes.position.array as Float32Array;
      const trailColors = trailGeometry.attributes.color.array as Float32Array;
      
      const trailCount = Math.floor(particleCount / 5);
      const trailLength = 5;
      
      for (let i = 0; i < trailCount; i++) {
        const sourceIdx = (i * 5) % particleCount;
        const i3 = sourceIdx * 3;
        const px = positions[i3];
        const py = positions[i3 + 1];
        const pz = positions[i3 + 2];
        const cr = colors[i3];
        const cg = colors[i3 + 1];
        const cb = colors[i3 + 2];
        
        for (let j = 0; j < trailLength; j++) {
          const idx = (i * trailLength + j) * 6;
          const fadeFactor = 1 - j / trailLength;
          
          trailPositions[idx] = px;
          trailPositions[idx + 1] = py;
          trailPositions[idx + 2] = pz - j * 0.12;
          trailPositions[idx + 3] = px;
          trailPositions[idx + 4] = py;
          trailPositions[idx + 5] = pz - (j + 1) * 0.12;
          
          trailColors[idx] = cr * fadeFactor;
          trailColors[idx + 1] = cg * fadeFactor;
          trailColors[idx + 2] = cb * fadeFactor;
          trailColors[idx + 3] = cr * fadeFactor * 0.5;
          trailColors[idx + 4] = cg * fadeFactor * 0.5;
          trailColors[idx + 5] = cb * fadeFactor * 0.5;
        }
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
