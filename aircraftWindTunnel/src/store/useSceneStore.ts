/**
 * 场景状态管理
 * 使用 Zustand 管理风洞模拟的全局状态
 */

import { create } from 'zustand';
import { SPEED_RANGE } from '../utils/colors';

interface SceneState {
  baseSpeed: number;
  particleCount: number;
  autoRotate: boolean;
  showWindTunnel: boolean;
  showAircraft: boolean;
  showParticles: boolean;
  showVelocityVectors: boolean;
  isPlaying: boolean;
  
  setBaseSpeed: (speed: number) => void;
  setParticleCount: (count: number) => void;
  setAutoRotate: (enabled: boolean) => void;
  toggleWindTunnel: () => void;
  toggleAircraft: () => void;
  toggleParticles: () => void;
  toggleVelocityVectors: () => void;
  togglePlay: () => void;
  reset: () => void;
}

const DEFAULT_STATE = {
  baseSpeed: SPEED_RANGE.DEFAULT,
  particleCount: 3000,
  autoRotate: true,
  showWindTunnel: true,
  showAircraft: true,
  showParticles: true,
  showVelocityVectors: false,
  isPlaying: true,
};

export const useSceneStore = create<SceneState>((set) => ({
  ...DEFAULT_STATE,
  
  setBaseSpeed: (speed) => set({ 
    baseSpeed: Math.max(SPEED_RANGE.MIN, Math.min(SPEED_RANGE.MAX, speed)) 
  }),
  
  setParticleCount: (count) => set({ 
    particleCount: Math.max(500, Math.min(8000, count)) 
  }),
  
  setAutoRotate: (enabled) => set({ autoRotate: enabled }),
  
  toggleWindTunnel: () => set((state) => ({ showWindTunnel: !state.showWindTunnel })),
  
  toggleAircraft: () => set((state) => ({ showAircraft: !state.showAircraft })),
  
  toggleParticles: () => set((state) => ({ showParticles: !state.showParticles })),
  
  toggleVelocityVectors: () => set((state) => ({ showVelocityVectors: !state.showVelocityVectors })),
  
  togglePlay: () => set((state) => ({ isPlaying: !state.isPlaying })),
  
  reset: () => set(DEFAULT_STATE),
}));
