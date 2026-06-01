/**
 * 速度图例组件
 * 显示粒子颜色与速度的对应关系
 */

import { useSceneStore } from '../store/useSceneStore';
import { SPEED_RANGE } from '../utils/colors';

export function SpeedLegend() {
  const { baseSpeed } = useSceneStore();
  
  const minDisplaySpeed = SPEED_RANGE.MIN;
  const maxDisplaySpeed = SPEED_RANGE.MAX * 2;
  
  return (
    <div className="glass-panel p-4 w-64">
      <h3 className="text-sm font-medium text-wind-tunnel-text mb-3 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-wind-tunnel-high-speed animate-pulse" />
        速度图例
      </h3>
      
      {/* 渐变色条 */}
      <div className="relative mb-3">
        <div className="speed-gradient h-4 rounded-full shadow-glow" />
        <div className="absolute -bottom-1 left-0 right-0 flex justify-between text-[10px] font-mono text-wind-tunnel-text-secondary mt-1">
          <span>慢</span>
          <span>中</span>
          <span>快</span>
        </div>
      </div>
      
      {/* 速度值标注 */}
      <div className="flex justify-between text-xs font-mono text-wind-tunnel-text-secondary mt-4">
        <span>{minDisplaySpeed.toFixed(0)}</span>
        <span>{((minDisplaySpeed + maxDisplaySpeed) / 2).toFixed(0)}</span>
        <span>{maxDisplaySpeed.toFixed(0)}</span>
      </div>
      <div className="text-center text-[10px] text-wind-tunnel-text-secondary mt-1">
        速度 (m/s)
      </div>
      
      {/* 当前基础速度 */}
      <div className="mt-4 pt-3 border-t border-wind-tunnel-border">
        <div className="flex justify-between items-center">
          <span className="text-xs text-wind-tunnel-text-secondary">基础风速</span>
          <span className="text-sm font-mono text-wind-tunnel-high-speed glow-text">
            {baseSpeed.toFixed(1)} m/s
          </span>
        </div>
        <div className="flex justify-between items-center mt-1">
          <span className="text-xs text-wind-tunnel-text-secondary">机翼上方</span>
          <span className="text-sm font-mono text-wind-tunnel-mid-speed">
            {(baseSpeed * 1.5).toFixed(1)} ~ {(baseSpeed * 2.2).toFixed(1)} m/s
          </span>
        </div>
      </div>
      
      {/* 伯努利原理说明 */}
      <div className="mt-4 pt-3 border-t border-wind-tunnel-border">
        <p className="text-[10px] text-wind-tunnel-text-secondary leading-relaxed">
          <span className="text-wind-tunnel-high-speed">伯努利原理:</span>
          机翼上表面气流路径更长，流速更快，压强更低，从而产生升力。
        </p>
      </div>
    </div>
  );
}
