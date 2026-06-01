/**
 * 粒子系统自定义Hook
 * 管理粒子的位置、速度和动画更新逻辑
 */

import { useRef, useMemo, useEffect } from 'react';
import * as THREE from 'three';
import { getVelocityAt, getSpeedAt, isInsideWindTunnel, getTunnelEntrancePosition } from '../utils/velocityField';
import { getSpeedColor, SPEED_RANGE } from '../utils/colors';

interface UseParticleSystemOptions {
  count: number;
  baseSpeed: number;
  isPlaying: boolean;
}

interface ParticleData {
  positions: Float32Array;
  colors: Float32Array;
  velocities: THREE.Vector3[];
  geometry: THREE.BufferGeometry;
}

export function useParticleSystem({ count, baseSpeed, isPlaying }: UseParticleSystemOptions) {
  const particleDataRef = useRef<ParticleData | null>(null);
  const animationFrameRef = useRef<number>(0);
  
  // 初始化粒子数据
  const particleData = useMemo(() => {
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const velocities: THREE.Vector3[] = [];
    
    for (let i = 0; i < count; i++) {
      const position = getTunnelEntrancePosition(true);
      // 初始时随机分布在整个风洞内，避免所有粒子同时从入口进入
      position.z = (Math.random() - 0.5) * 20;
      
      positions[i * 3] = position.x;
      positions[i * 3 + 1] = position.y;
      positions[i * 3 + 2] = position.z;
      
      const speed = getSpeedAt(position, baseSpeed);
      const color = getSpeedColor(speed, SPEED_RANGE.MIN, SPEED_RANGE.MAX * 2);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
      
      velocities.push(getVelocityAt(position, baseSpeed));
    }
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    particleDataRef.current = { positions, colors, velocities, geometry };
    
    return { positions, colors, velocities, geometry };
  }, [count]);
  
  // 更新粒子动画
  const updateParticles = (deltaTime: number) => {
    if (!isPlaying || !particleDataRef.current) return;
    
    const { positions, colors, velocities, geometry } = particleDataRef.current;
    const dt = Math.min(deltaTime, 0.05); // 限制最大时间步长，避免跳跃
    
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      
      let x = positions[i3];
      let y = positions[i3 + 1];
      let z = positions[i3 + 2];
      
      const position = new THREE.Vector3(x, y, z);
      const velocity = getVelocityAt(position, baseSpeed);
      velocities[i].copy(velocity);
      
      // 更新位置
      x += velocity.x * dt;
      y += velocity.y * dt;
      z += velocity.z * dt;
      
      // 检查是否超出风洞范围，如果超出则重置到入口
      const newPosition = new THREE.Vector3(x, y, z);
      if (!isInsideWindTunnel(newPosition) || z < -10) {
        const resetPos = getTunnelEntrancePosition(true);
        x = resetPos.x;
        y = resetPos.y;
        z = resetPos.z;
      }
      
      positions[i3] = x;
      positions[i3 + 1] = y;
      positions[i3 + 2] = z;
      
      // 更新颜色
      const speed = new THREE.Vector3(x, y, z).distanceTo(new THREE.Vector3(
        x - velocity.x * dt,
        y - velocity.y * dt,
        z - velocity.z * dt
      )) / dt;
      const color = getSpeedColor(speed, SPEED_RANGE.MIN, SPEED_RANGE.MAX * 2);
      colors[i3] = color.r;
      colors[i3 + 1] = color.g;
      colors[i3 + 2] = color.b;
    }
    
    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.color.needsUpdate = true;
  };
  
  // 清理资源
  useEffect(() => {
    return () => {
      if (particleDataRef.current?.geometry) {
        particleDataRef.current.geometry.dispose();
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);
  
  return {
    geometry: particleData.geometry,
    updateParticles,
  };
}
