/**
 * 控制面板组件
 * 提供风速调节、粒子数量控制、显示切换等功能
 */

import { Play, Pause, RotateCcw, Eye, EyeOff, Maximize2, Wind, Settings } from 'lucide-react';
import { useSceneStore } from '../store/useSceneStore';
import { SPEED_RANGE } from '../utils/colors';

export function ControlPanel() {
  const {
    baseSpeed,
    particleCount,
    autoRotate,
    showWindTunnel,
    showAircraft,
    showParticles,
    isPlaying,
    setBaseSpeed,
    setParticleCount,
    setAutoRotate,
    toggleWindTunnel,
    toggleAircraft,
    toggleParticles,
    togglePlay,
    reset,
  } = useSceneStore();
  
  return (
    <div className="glass-panel p-5 w-80">
      {/* 标题 */}
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-wind-tunnel-border">
        <div className="w-10 h-10 rounded-lg bg-wind-tunnel-high-speed/20 flex items-center justify-center">
          <Wind className="w-5 h-5 text-wind-tunnel-high-speed" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-wind-tunnel-text font-display glow-text">
            风洞控制台
          </h2>
          <p className="text-xs text-wind-tunnel-text-secondary">
            3D 气流模拟系统
          </p>
        </div>
      </div>
      
      {/* 播放控制 */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={togglePlay}
          className={`btn-control flex-1 flex items-center justify-center gap-2 ${isPlaying ? 'active' : ''}`}
        >
          {isPlaying ? (
            <>
              <Pause className="w-4 h-4" />
              <span>暂停</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>播放</span>
            </>
          )}
        </button>
        <button
          onClick={reset}
          className="btn-control flex items-center justify-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          <span>重置</span>
        </button>
      </div>
      
      {/* 风速控制 */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm text-wind-tunnel-text-secondary flex items-center gap-2">
            <Settings className="w-4 h-4" />
            气流速度
          </label>
          <span className="text-sm font-mono text-wind-tunnel-high-speed">
            {baseSpeed.toFixed(1)} m/s
          </span>
        </div>
        <input
          type="range"
          min={SPEED_RANGE.MIN}
          max={SPEED_RANGE.MAX}
          step={0.5}
          value={baseSpeed}
          onChange={(e) => setBaseSpeed(parseFloat(e.target.value))}
          className="w-full h-2 bg-wind-tunnel-bg rounded-lg appearance-none cursor-pointer accent-wind-tunnel-high-speed"
        />
        <div className="flex justify-between text-xs text-wind-tunnel-text-secondary mt-1">
          <span>{SPEED_RANGE.MIN}</span>
          <span>{SPEED_RANGE.MAX}</span>
        </div>
      </div>
      
      {/* 粒子数量控制 */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm text-wind-tunnel-text-secondary">
            粒子数量
          </label>
          <span className="text-sm font-mono text-wind-tunnel-high-speed">
            {particleCount.toLocaleString()}
          </span>
        </div>
        <input
          type="range"
          min={500}
          max={8000}
          step={500}
          value={particleCount}
          onChange={(e) => setParticleCount(parseInt(e.target.value))}
          className="w-full h-2 bg-wind-tunnel-bg rounded-lg appearance-none cursor-pointer accent-wind-tunnel-high-speed"
        />
        <div className="flex justify-between text-xs text-wind-tunnel-text-secondary mt-1">
          <span>500</span>
          <span>8000</span>
        </div>
      </div>
      
      {/* 自动旋转 */}
      <div className="mb-6">
        <button
          onClick={() => setAutoRotate(!autoRotate)}
          className={`btn-control w-full flex items-center justify-center gap-2 ${autoRotate ? 'active' : ''}`}
        >
          <Maximize2 className="w-4 h-4" />
          <span>{autoRotate ? '自动旋转: 开启' : '自动旋转: 关闭'}</span>
        </button>
      </div>
      
      {/* 显示控制 */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-wind-tunnel-text border-b border-wind-tunnel-border pb-2">
          显示选项
        </h3>
        
        <button
          onClick={toggleWindTunnel}
          className={`btn-control w-full flex items-center justify-between ${showWindTunnel ? 'active' : ''}`}
        >
          <span className="flex items-center gap-2">
            {showWindTunnel ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            风洞壳体
          </span>
          <span className={`w-3 h-3 rounded-full ${showWindTunnel ? 'bg-wind-tunnel-high-speed' : 'bg-wind-tunnel-text-secondary/30'}`} />
        </button>
        
        <button
          onClick={toggleAircraft}
          className={`btn-control w-full flex items-center justify-between ${showAircraft ? 'active' : ''}`}
        >
          <span className="flex items-center gap-2">
            {showAircraft ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            飞机模型
          </span>
          <span className={`w-3 h-3 rounded-full ${showAircraft ? 'bg-wind-tunnel-high-speed' : 'bg-wind-tunnel-text-secondary/30'}`} />
        </button>
        
        <button
          onClick={toggleParticles}
          className={`btn-control w-full flex items-center justify-between ${showParticles ? 'active' : ''}`}
        >
          <span className="flex items-center gap-2">
            {showParticles ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            粒子气流
          </span>
          <span className={`w-3 h-3 rounded-full ${showParticles ? 'bg-wind-tunnel-high-speed' : 'bg-wind-tunnel-text-secondary/30'}`} />
        </button>
      </div>
      
      {/* 操作提示 */}
      <div className="mt-6 pt-4 border-t border-wind-tunnel-border">
        <p className="text-xs text-wind-tunnel-text-secondary leading-relaxed">
          💡 左键拖拽旋转 · 滚轮缩放 · 右键平移
        </p>
        <p className="text-[10px] text-wind-tunnel-text-secondary/60 mt-1">
          🍎 macOS: 双指滑动平移 · 双指开合缩放
        </p>
      </div>
    </div>
  );
}
