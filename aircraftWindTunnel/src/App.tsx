/**
 * 主应用组件
 * 布局: 全屏3D画布 + 悬浮UI面板
 */

import { WindTunnelScene } from '@/components/WindTunnelScene';
import { ControlPanel } from '@/components/ControlPanel';
import { SpeedLegend } from '@/components/SpeedLegend';
import { useSceneStore } from '@/store/useSceneStore';
import { Info, Zap } from 'lucide-react';

function App() {
  const { baseSpeed, particleCount, isPlaying } = useSceneStore();
  
  return (
    <div className="w-full h-full relative overflow-hidden">
      {/* 3D场景画布 */}
      <div className="canvas-container">
        <WindTunnelScene />
      </div>
      
      {/* 顶部标题栏 */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10">
        <div className="glass-panel px-8 py-3 flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-wind-tunnel-high-speed animate-pulse" />
            <h1 className="text-xl font-bold text-wind-tunnel-text font-display glow-text tracking-wider">
              3D 飞机风洞模拟
            </h1>
          </div>
          <div className="w-px h-6 bg-wind-tunnel-border" />
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${isPlaying ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`} />
              <span className="text-wind-tunnel-text-secondary">
                {isPlaying ? '运行中' : '已暂停'}
              </span>
            </div>
            <div className="text-wind-tunnel-text-secondary">
              粒子: <span className="text-wind-tunnel-high-speed font-mono">{particleCount.toLocaleString()}</span>
            </div>
            <div className="text-wind-tunnel-text-secondary">
              风速: <span className="text-wind-tunnel-high-speed font-mono">{baseSpeed.toFixed(1)} m/s</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* 左侧控制面板 */}
      <div className="absolute top-24 left-4 z-10">
        <ControlPanel />
      </div>
      
      {/* 右侧速度图例 */}
      <div className="absolute top-24 right-4 z-10">
        <SpeedLegend />
      </div>
      
      {/* 底部信息栏 */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10">
        <div className="glass-panel px-6 py-3 flex items-center gap-3">
          <Info className="w-4 h-4 text-wind-tunnel-high-speed" />
          <p className="text-xs text-wind-tunnel-text-secondary">
            <span className="text-wind-tunnel-high-speed">伯努利原理演示:</span>
            观察机翼上方的青色粒子 — 流速更快（约为基础风速的1.5-2.2倍），压强更低，从而产生升力
          </p>
        </div>
      </div>
      
      {/* 左下角技术信息 */}
      <div className="absolute bottom-4 left-4 z-10">
        <div className="text-[10px] text-wind-tunnel-text-secondary/60 font-mono">
          <div>Three.js + React Three Fiber</div>
          <div>Powered by Vite + React 18</div>
        </div>
      </div>
    </div>
  );
}

export default App;
