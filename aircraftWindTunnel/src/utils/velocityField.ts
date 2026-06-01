/**
 * 速度场计算函数
 * 实现风洞内的气流速度分布，包括机翼上方的流速提升效果
 */

import * as THREE from 'three';

// 风洞尺寸配置
export const WIND_TUNNEL_CONFIG = {
  WIDTH: 8,
  HEIGHT: 6,
  LENGTH: 20,
} as const;

// 飞机位置和尺寸配置
export const AIRCRAFT_CONFIG = {
  POSITION: new THREE.Vector3(0, 0, 2),
  WING_SPAN: 5,
  WING_CHORD: 1.5,
  FUSELAGE_LENGTH: 4,
} as const;

/**
 * 计算空间中某点的速度向量
 * 实现伯努利原理：机翼上方气流速度更快
 * @param position 空间点位置
 * @param baseSpeed 基础气流速度
 * @returns 速度向量
 */
export function getVelocityAt(
  position: THREE.Vector3,
  baseSpeed: number
): THREE.Vector3 {
  const velocity = new THREE.Vector3(0, 0, -baseSpeed);
  
  const aircraftPos = AIRCRAFT_CONFIG.POSITION;
  const wingSpan = AIRCRAFT_CONFIG.WING_SPAN;
  const wingChord = AIRCRAFT_CONFIG.WING_CHORD;
  const fuselageLength = AIRCRAFT_CONFIG.FUSELAGE_LENGTH;
  
  // 计算机翼影响区域
  const dx = position.x - aircraftPos.x;
  const dy = position.y - aircraftPos.y;
  const dz = position.z - aircraftPos.z;
  
  // 机翼区域判断 (X-Z平面内的机翼投影)
  const inWingSpan = Math.abs(dx) < wingSpan / 2;
  const inWingChord = dz > -wingChord / 2 && dz < wingChord / 2;
  const nearWingY = dy > -0.5 && dy < 2.0;
  
  if (inWingSpan && inWingChord && nearWingY) {
    // 机翼上方区域：速度提升 (伯努利原理)
    // 使用高斯函数模拟速度分布，机翼上表面速度最大
    const wingHeightFactor = Math.exp(-Math.pow(dy - 0.3, 2) / 0.8);
    const wingSpanFactor = Math.exp(-Math.pow(dx / (wingSpan / 2), 2) / 2);
    const wingChordFactor = Math.exp(-Math.pow(dz / (wingChord / 2), 2) / 4);
    
    // 速度提升系数：最大可达基础速度的2倍
    const speedMultiplier = 1 + wingHeightFactor * wingSpanFactor * wingChordFactor * 1.2;
    velocity.z *= speedMultiplier;
    
    // 添加微小的向上分量，模拟升力产生的气流偏转
    velocity.y += wingHeightFactor * wingSpanFactor * baseSpeed * 0.15;
    
    // 添加翼尖涡流效果
    const tipDistance = Math.abs(dx) - wingSpan / 2 + 0.3;
    if (tipDistance > -0.5 && tipDistance < 0.5) {
      const tipStrength = Math.exp(-Math.pow(tipDistance / 0.3, 2));
      const swirlDirection = dx > 0 ? 1 : -1;
      velocity.x += tipStrength * baseSpeed * 0.3 * swirlDirection;
      velocity.y -= tipStrength * baseSpeed * 0.2;
    }
  }
  
  // 机身附近的气流扰动
  const nearFuselage = Math.abs(dx) < 0.5 && Math.abs(dy) < 0.8 && dz > -fuselageLength / 2 && dz < fuselageLength / 2;
  if (nearFuselage) {
    const fuselageFactor = Math.exp(-Math.pow(dz / (fuselageLength / 2), 2) / 2);
    velocity.z *= 1 + fuselageFactor * 0.3;
  }
  
  // 风洞壁面边界层效应：靠近壁面速度降低
  const wallDistanceX = Math.min(position.x + WIND_TUNNEL_CONFIG.WIDTH / 2, WIND_TUNNEL_CONFIG.WIDTH / 2 - position.x);
  const wallDistanceY = Math.min(position.y + WIND_TUNNEL_CONFIG.HEIGHT / 2, WIND_TUNNEL_CONFIG.HEIGHT / 2 - position.y);
  
  const boundaryLayerFactor = Math.min(
    Math.exp(-Math.pow((1.0 - wallDistanceX) / 0.5, 2)),
    Math.exp(-Math.pow((1.0 - wallDistanceY) / 0.5, 2))
  );
  
  velocity.z *= 0.2 + 0.8 * boundaryLayerFactor;
  
  // 添加轻微的湍流扰动
  const turbulence = (Math.sin(position.x * 3 + position.z * 2) * 0.05 + 
                      Math.cos(position.y * 4) * 0.03) * baseSpeed;
  velocity.x += turbulence;
  velocity.y += turbulence * 0.5;
  
  return velocity;
}

/**
 * 计算某点的速度标量值（用于颜色映射）
 * @param position 空间点位置
 * @param baseSpeed 基础气流速度
 * @returns 速度标量
 */
export function getSpeedAt(position: THREE.Vector3, baseSpeed: number): number {
  return getVelocityAt(position, baseSpeed).length();
}

/**
 * 检查粒子是否在风洞范围内
 * @param position 粒子位置
 * @param margin 边界余量
 * @returns 是否在风洞内
 */
export function isInsideWindTunnel(position: THREE.Vector3, margin: number = 0.5): boolean {
  const halfWidth = WIND_TUNNEL_CONFIG.WIDTH / 2 - margin;
  const halfHeight = WIND_TUNNEL_CONFIG.HEIGHT / 2 - margin;
  const halfLength = WIND_TUNNEL_CONFIG.LENGTH / 2 - margin;
  
  return (
    position.x >= -halfWidth && position.x <= halfWidth &&
    position.y >= -halfHeight && position.y <= halfHeight &&
    position.z >= -halfLength && position.z <= halfLength
  );
}

/**
 * 获取风洞入口位置（用于粒子生成）
 * @param randomOffset 是否添加随机偏移
 * @returns 入口位置
 */
export function getTunnelEntrancePosition(randomOffset: boolean = true): THREE.Vector3 {
  const halfWidth = WIND_TUNNEL_CONFIG.WIDTH / 2 - 0.3;
  const halfHeight = WIND_TUNNEL_CONFIG.HEIGHT / 2 - 0.3;
  const zPos = WIND_TUNNEL_CONFIG.LENGTH / 2 - 0.1;
  
  if (randomOffset) {
    return new THREE.Vector3(
      (Math.random() - 0.5) * 2 * halfWidth,
      (Math.random() - 0.5) * 2 * halfHeight,
      zPos + Math.random() * 2
    );
  }
  
  return new THREE.Vector3(0, 0, zPos);
}
