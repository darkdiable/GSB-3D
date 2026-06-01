/**
 * 主3D场景组件
 * 整合风洞、飞机、粒子系统等所有3D元素
 * 设置相机、灯光、后处理效果
 */

import { useRef, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing';
import * as THREE from 'three';
import { WindTunnel } from './WindTunnel';
import { Aircraft } from './Aircraft';
import { ParticleFlow } from './ParticleFlow';
import { useSceneStore } from '../store/useSceneStore';
import { COLORS } from '../utils/colors';

/**
 * 场景内部组件 - 可以访问Three.js上下文
 */
function SceneContent() {
  const { autoRotate, showWindTunnel, showAircraft, showParticles } = useSceneStore();
  const controlsRef = useRef<any>(null);
  const { camera } = useThree();
  
  // 相机自动旋转
  useFrame((state) => {
    if (autoRotate && controlsRef.current) {
      const time = state.clock.elapsedTime * 0.1;
      const radius = 18;
      const height = 6 + Math.sin(time * 0.5) * 2;
      
      camera.position.x = Math.cos(time) * radius;
      camera.position.y = height;
      camera.position.z = Math.sin(time) * radius;
      camera.lookAt(0, 0, 0);
    }
  });
  
  return (
    <>
      {/* 环境光 */}
      <ambientLight intensity={0.3} color={COLORS.AMBIENT_LIGHT} />
      
      {/* 主方向光 */}
      <directionalLight
        position={[10, 15, 10]}
        intensity={1.2}
        color={COLORS.MAIN_LIGHT}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      
      {/* 补光 - 青色调 */}
      <pointLight
        position={[-8, 5, -8]}
        intensity={0.5}
        color={COLORS.FILL_LIGHT}
      />
      
      {/* 底部补光 */}
      <pointLight
        position={[0, -5, 0]}
        intensity={0.2}
        color={COLORS.HIGH_SPEED}
      />
      
      {/* 风洞组件 */}
      <WindTunnel visible={showWindTunnel} />
      
      {/* 飞机组件 */}
      <Aircraft visible={showAircraft} />
      
      {/* 粒子流系统 */}
      <ParticleFlow visible={showParticles} />
      
      {/* 星空背景 */}
      <Stars
        radius={100}
        depth={50}
        count={2000}
        factor={4}
        saturation={0}
        fade
        speed={0.5}
      />
      
      {/* 地面网格辅助 */}
      <gridHelper
        args={[40, 40, 0x00d4ff, 0x0a1628]}
        position={[0, -3.1, 0]}
      />
      
      {/* 控制器 */}
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.05}
        minDistance={8}
        maxDistance={40}
        maxPolarAngle={Math.PI / 2 + 0.3}
        minPolarAngle={0.2}
        enablePan={true}
        enabled={!autoRotate}
      />
      
      {/* 后处理效果 */}
      <EffectComposer>
        {/* 发光效果 */}
        <Bloom
          luminanceThreshold={0.2}
          luminanceSmoothing={0.9}
          height={300}
          intensity={0.8}
        />
        {/* 暗角效果 */}
        <Vignette
          offset={0.5}
          darkness={0.6}
        />
      </EffectComposer>
    </>
  );
}

/**
 * 主场景组件
 */
export function WindTunnelScene() {
  const cameraProps = useMemo(() => ({
    fov: 60,
    near: 0.1,
    far: 1000,
    position: [15, 8, 15] as [number, number, number],
  }), []);
  
  return (
    <Canvas
      camera={cameraProps}
      gl={{
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance',
      }}
      style={{
        background: `linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a1628 100%)`,
      }}
      dpr={[1, 2]}
    >
      <SceneContent />
    </Canvas>
  );
}
