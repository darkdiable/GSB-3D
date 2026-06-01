/**
 * 颜色配置文件
 * 定义风洞模拟中使用的所有颜色常量和颜色映射函数
 */

import * as THREE from 'three';

// 基础颜色常量
export const COLORS = {
  BACKGROUND: 0x0a1628,
  WIND_TUNNEL_GLASS: 0x88ccff,
  WIND_TUNNEL_FRAME: 0x00d4ff,
  AIRCRAFT_BODY: 0xc0c0c0,
  AIRCRAFT_WING: 0xa0a0a0,
  AIRCRAFT_COCKPIT: 0x4488ff,
  
  HIGH_SPEED: 0x00d4ff,
  MID_SPEED: 0x9d4edd,
  LOW_SPEED: 0xff6b35,
  
  AMBIENT_LIGHT: 0x404040,
  MAIN_LIGHT: 0xffffff,
  FILL_LIGHT: 0x00d4ff,
} as const;

// 速度范围配置
export const SPEED_RANGE = {
  MIN: 5.0,
  MAX: 20.0,
  DEFAULT: 10.0,
} as const;

/**
 * 根据速度值获取对应的颜色
 * 使用线性插值在低、中、高速度颜色之间过渡
 * @param speed 速度值
 * @param minSpeed 最小速度
 * @param maxSpeed 最大速度
 * @returns THREE.Color 颜色对象
 */
export function getSpeedColor(
  speed: number,
  minSpeed: number = SPEED_RANGE.MIN,
  maxSpeed: number = SPEED_RANGE.MAX
): THREE.Color {
  const normalizedSpeed = Math.max(0, Math.min(1, (speed - minSpeed) / (maxSpeed - minSpeed)));
  
  const lowColor = new THREE.Color(COLORS.LOW_SPEED);
  const midColor = new THREE.Color(COLORS.MID_SPEED);
  const highColor = new THREE.Color(COLORS.HIGH_SPEED);
  
  if (normalizedSpeed < 0.5) {
    const t = normalizedSpeed * 2;
    return lowColor.clone().lerp(midColor, t);
  } else {
    const t = (normalizedSpeed - 0.5) * 2;
    return midColor.clone().lerp(highColor, t);
  }
}

/**
 * 获取颜色的CSS字符串表示
 * @param color 十六进制颜色值
 * @param alpha 透明度 (0-1)
 * @returns CSS rgba 颜色字符串
 */
export function hexToRgba(color: number, alpha: number = 1): string {
  const r = (color >> 16) & 255;
  const g = (color >> 8) & 255;
  const b = color & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}
