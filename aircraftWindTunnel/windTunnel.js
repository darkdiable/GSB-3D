/**
 * 3D飞机风洞模拟 - 主程序
 * 功能：
 * 1. 透明矩形风洞展示
 * 2. 飞机模型放置
 * 3. 动态气流粒子可视化
 * 4. 交互式视角控制（自定义轨道控制器）
 * 5. 风速、攻角等参数调节
 */

// ========== 全局变量 ==========
let scene, camera, renderer;
let windTunnel, aircraft;
let particleSystem, particleVelocities;
let animationId;
let isWindRunning = true;
let windSpeed = 1.0;
let angleOfAttack = 0;
let particleCount = 2000;

// 自定义轨道控制器状态
let orbitControls = {
    target: new THREE.Vector3(0, 0, 0),
    distance: 35,
    theta: Math.PI / 4,      // 水平角
    phi: Math.PI / 4,        // 垂直角
    minDistance: 10,
    maxDistance: 80,
    minPolarAngle: 0.1,
    maxPolarAngle: Math.PI - 0.1,
    dampingFactor: 0.05
};

// 鼠标状态
let mouseState = {
    isDragging: false,
    isPanning: false,
    previousX: 0,
    previousY: 0,
    rotationSpeed: 0.005,
    zoomSpeed: 0.001,
    panSpeed: 0.01
};

// 风洞尺寸参数
const TUNNEL_LENGTH = 40;
const TUNNEL_WIDTH = 12;
const TUNNEL_HEIGHT = 10;

// ========== 初始化入口 ==========
window.addEventListener('load', init);
window.addEventListener('resize', onWindowResize);

/**
 * 初始化函数
 */
function init() {
    // 创建场景
    createScene();
    
    // 创建相机
    createCamera();
    
    // 创建渲染器
    createRenderer();
    
    // 添加灯光
    createLights();
    
    // 创建风洞
    createWindTunnel();
    
    // 创建飞机
    createAircraft();
    
    // 创建粒子系统
    createParticleSystem();
    
    // 添加自定义轨道控制
    createOrbitControls();
    
    // 绑定控制面板事件
    bindControls();
    
    // 隐藏加载提示
    document.getElementById('loading').style.display = 'none';
    
    // 开始动画循环
    animate();
}

/**
 * 创建自定义轨道控制器
 */
function createOrbitControls() {
    const domElement = renderer.domElement;
    
    // 鼠标按下事件
    domElement.addEventListener('mousedown', function(e) {
        e.preventDefault();
        
        if (e.button === 0) {
            // 左键：旋转
            mouseState.isDragging = true;
            domElement.style.cursor = 'grabbing';
        } else if (e.button === 2) {
            // 右键：平移
            mouseState.isPanning = true;
            domElement.style.cursor = 'move';
        }
        
        mouseState.previousX = e.clientX;
        mouseState.previousY = e.clientY;
    });
    
    // 鼠标移动事件
    domElement.addEventListener('mousemove', function(e) {
        e.preventDefault();
        
        const deltaX = e.clientX - mouseState.previousX;
        const deltaY = e.clientY - mouseState.previousY;
        
        if (mouseState.isDragging) {
            // 旋转相机
            orbitControls.theta -= deltaX * mouseState.rotationSpeed;
            orbitControls.phi -= deltaY * mouseState.rotationSpeed;
            
            // 限制垂直角度
            orbitControls.phi = Math.max(
                orbitControls.minPolarAngle,
                Math.min(orbitControls.maxPolarAngle, orbitControls.phi)
            );
        }
        
        if (mouseState.isPanning) {
            // 平移目标点
            const panOffset = new THREE.Vector3();
            const cameraDirection = new THREE.Vector3();
            camera.getWorldDirection(cameraDirection);
            
            const right = new THREE.Vector3();
            right.crossVectors(cameraDirection, new THREE.Vector3(0, 1, 0)).normalize();
            
            const up = new THREE.Vector3(0, 1, 0);
            
            panOffset.addScaledVector(right, -deltaX * mouseState.panSpeed * orbitControls.distance * 0.1);
            panOffset.addScaledVector(up, deltaY * mouseState.panSpeed * orbitControls.distance * 0.1);
            
            orbitControls.target.add(panOffset);
        }
        
        mouseState.previousX = e.clientX;
        mouseState.previousY = e.clientY;
        
        updateCameraPosition();
    });
    
    // 鼠标释放事件
    document.addEventListener('mouseup', function(e) {
        mouseState.isDragging = false;
        mouseState.isPanning = false;
        domElement.style.cursor = 'grab';
    });
    
    // 鼠标滚轮事件（缩放）
    domElement.addEventListener('wheel', function(e) {
        e.preventDefault();
        const delta = e.deltaY * mouseState.zoomSpeed;
        orbitControls.distance += delta * orbitControls.distance;
        
        // 限制距离范围
        orbitControls.distance = Math.max(
            orbitControls.minDistance,
            Math.min(orbitControls.maxDistance, orbitControls.distance)
        );
        
        updateCameraPosition();
    }, { passive: false });
    
    // 触摸事件支持
    let touchStartDistance = 0;
    
    domElement.addEventListener('touchstart', function(e) {
        if (e.touches.length === 1) {
            mouseState.isDragging = true;
            mouseState.previousX = e.touches[0].clientX;
            mouseState.previousY = e.touches[0].clientY;
        } else if (e.touches.length === 2) {
            const dx = e.touches[1].clientX - e.touches[0].clientX;
            const dy = e.touches[1].clientY - e.touches[0].clientY;
            touchStartDistance = Math.sqrt(dx * dx + dy * dy);
        }
    });
    
    domElement.addEventListener('touchmove', function(e) {
        e.preventDefault();
        
        if (e.touches.length === 1 && mouseState.isDragging) {
            const deltaX = e.touches[0].clientX - mouseState.previousX;
            const deltaY = e.touches[0].clientY - mouseState.previousY;
            
            orbitControls.theta -= deltaX * mouseState.rotationSpeed * 1.5;
            orbitControls.phi -= deltaY * mouseState.rotationSpeed * 1.5;
            orbitControls.phi = Math.max(
                orbitControls.minPolarAngle,
                Math.min(orbitControls.maxPolarAngle, orbitControls.phi)
            );
            
            mouseState.previousX = e.touches[0].clientX;
            mouseState.previousY = e.touches[0].clientY;
            
            updateCameraPosition();
        } else if (e.touches.length === 2) {
            const dx = e.touches[1].clientX - e.touches[0].clientX;
            const dy = e.touches[1].clientY - e.touches[0].clientY;
            const currentDistance = Math.sqrt(dx * dx + dy * dy);
            const delta = (touchStartDistance - currentDistance) * 0.05;
            
            orbitControls.distance += delta;
            orbitControls.distance = Math.max(
                orbitControls.minDistance,
                Math.min(orbitControls.maxDistance, orbitControls.distance)
            );
            
            touchStartDistance = currentDistance;
            updateCameraPosition();
        }
    }, { passive: false });
    
    domElement.addEventListener('touchend', function() {
        mouseState.isDragging = false;
    });
    
    // 禁止右键菜单
    domElement.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });
    
    // 设置初始光标样式
    domElement.style.cursor = 'grab';
    domElement.style.touchAction = 'none';
    
    // 初始化相机位置
    updateCameraPosition();
}

/**
 * 根据轨道参数更新相机位置
 */
function updateCameraPosition() {
    const x = orbitControls.target.x + orbitControls.distance * 
              Math.sin(orbitControls.phi) * Math.sin(orbitControls.theta);
    const y = orbitControls.target.y + orbitControls.distance * 
              Math.cos(orbitControls.phi);
    const z = orbitControls.target.z + orbitControls.distance * 
              Math.sin(orbitControls.phi) * Math.cos(orbitControls.theta);
    
    camera.position.set(x, y, z);
    camera.lookAt(orbitControls.target);
}

/**
 * 创建Three.js场景
 */
function createScene() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a1a);
    scene.fog = new THREE.Fog(0x0a0a1a, 50, 100);
}

/**
 * 创建透视相机
 */
function createCamera() {
    camera = new THREE.PerspectiveCamera(
        60,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
}

/**
 * 创建WebGL渲染器
 */
function createRenderer() {
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    document.getElementById('container').appendChild(renderer.domElement);
}

/**
 * 创建灯光系统
 */
function createLights() {
    // 环境光
    const ambientLight = new THREE.AmbientLight(0x404060, 0.4);
    scene.add(ambientLight);
    
    // 主方向光
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(20, 30, 20);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 100;
    directionalLight.shadow.camera.left = -30;
    directionalLight.shadow.camera.right = 30;
    directionalLight.shadow.camera.top = 30;
    directionalLight.shadow.camera.bottom = -30;
    scene.add(directionalLight);
    
    // 蓝色补光（风洞效果）
    const blueLight = new THREE.PointLight(0x00aaff, 0.5, 60);
    blueLight.position.set(0, 0, -TUNNEL_LENGTH / 2);
    scene.add(blueLight);
    
    // 橙色补光（出口效果）
    const orangeLight = new THREE.PointLight(0xff6600, 0.3, 40);
    orangeLight.position.set(0, 0, TUNNEL_LENGTH / 2);
    scene.add(orangeLight);
}

/**
 * 创建透明矩形风洞
 */
function createWindTunnel() {
    const tunnelGroup = new THREE.Group();
    
    // 风洞边框材质
    const frameMaterial = new THREE.MeshPhongMaterial({
        color: 0x334455,
        emissive: 0x112233,
        shininess: 100,
        transparent: true,
        opacity: 0.9
    });
    
    // 风洞透明壁材质
    const wallMaterial = new THREE.MeshPhongMaterial({
        color: 0x88ccff,
        transparent: true,
        opacity: 0.1,
        side: THREE.DoubleSide,
        depthWrite: false
    });
    
    // 边框尺寸
    const frameSize = 0.3;
    
    // 创建12条边框
    const framePoints = [
        // 前面矩形
        [-TUNNEL_WIDTH/2, -TUNNEL_HEIGHT/2, -TUNNEL_LENGTH/2],
        [TUNNEL_WIDTH/2, -TUNNEL_HEIGHT/2, -TUNNEL_LENGTH/2],
        [TUNNEL_WIDTH/2, TUNNEL_HEIGHT/2, -TUNNEL_LENGTH/2],
        [-TUNNEL_WIDTH/2, TUNNEL_HEIGHT/2, -TUNNEL_LENGTH/2],
        // 后面矩形
        [-TUNNEL_WIDTH/2, -TUNNEL_HEIGHT/2, TUNNEL_LENGTH/2],
        [TUNNEL_WIDTH/2, -TUNNEL_HEIGHT/2, TUNNEL_LENGTH/2],
        [TUNNEL_WIDTH/2, TUNNEL_HEIGHT/2, TUNNEL_LENGTH/2],
        [-TUNNEL_WIDTH/2, TUNNEL_HEIGHT/2, TUNNEL_LENGTH/2]
    ];
    
    // 绘制边框线
    const edges = [
        [0,1], [1,2], [2,3], [3,0], // 前面
        [4,5], [5,6], [6,7], [7,4], // 后面
        [0,4], [1,5], [2,6], [3,7]  // 连接边
    ];
    
    edges.forEach(edge => {
        const p1 = framePoints[edge[0]];
        const p2 = framePoints[edge[1]];
        const dir = new THREE.Vector3(p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]);
        const length = dir.length();
        const center = new THREE.Vector3((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2);
        
        const frameGeo = new THREE.BoxGeometry(frameSize, frameSize, length);
        const frame = new THREE.Mesh(frameGeo, frameMaterial);
        frame.position.copy(center);
        frame.lookAt(new THREE.Vector3(p2[0], p2[1], p2[2]));
        frame.rotateX(Math.PI / 2);
        frame.castShadow = true;
        tunnelGroup.add(frame);
    });
    
    // 创建透明壁面
    const wallThickness = 0.05;
    
    // 顶面
    const topWall = new THREE.Mesh(
        new THREE.BoxGeometry(TUNNEL_WIDTH, wallThickness, TUNNEL_LENGTH),
        wallMaterial
    );
    topWall.position.y = TUNNEL_HEIGHT / 2;
    tunnelGroup.add(topWall);
    
    // 底面
    const bottomWall = new THREE.Mesh(
        new THREE.BoxGeometry(TUNNEL_WIDTH, wallThickness, TUNNEL_LENGTH),
        wallMaterial
    );
    bottomWall.position.y = -TUNNEL_HEIGHT / 2;
    tunnelGroup.add(bottomWall);
    
    // 左面
    const leftWall = new THREE.Mesh(
        new THREE.BoxGeometry(wallThickness, TUNNEL_HEIGHT, TUNNEL_LENGTH),
        wallMaterial
    );
    leftWall.position.x = -TUNNEL_WIDTH / 2;
    tunnelGroup.add(leftWall);
    
    // 右面
    const rightWall = new THREE.Mesh(
        new THREE.BoxGeometry(wallThickness, TUNNEL_HEIGHT, TUNNEL_LENGTH),
        wallMaterial
    );
    rightWall.position.x = TUNNEL_WIDTH / 2;
    tunnelGroup.add(rightWall);
    
    // 入口和出口的发光效果
    const entranceGlow = new THREE.Mesh(
        new THREE.PlaneGeometry(TUNNEL_WIDTH, TUNNEL_HEIGHT),
        new THREE.MeshBasicMaterial({
            color: 0x00aaff,
            transparent: true,
            opacity: 0.2,
            side: THREE.DoubleSide
        })
    );
    entranceGlow.position.z = -TUNNEL_LENGTH / 2;
    tunnelGroup.add(entranceGlow);
    
    const exitGlow = new THREE.Mesh(
        new THREE.PlaneGeometry(TUNNEL_WIDTH, TUNNEL_HEIGHT),
        new THREE.MeshBasicMaterial({
            color: 0xff6600,
            transparent: true,
            opacity: 0.15,
            side: THREE.DoubleSide
        })
    );
    exitGlow.position.z = TUNNEL_LENGTH / 2;
    tunnelGroup.add(exitGlow);
    
    // 地面网格
    const gridHelper = new THREE.GridHelper(60, 60, 0x334455, 0x223344);
    gridHelper.position.y = -TUNNEL_HEIGHT / 2 - 0.01;
    tunnelGroup.add(gridHelper);
    
    windTunnel = tunnelGroup;
    scene.add(windTunnel);
}

/**
 * 创建飞机模型（使用基本几何体组合）
 * 飞机沿Z轴放置，机头朝向Z轴负方向（迎风）
 */
function createAircraft() {
    const aircraftGroup = new THREE.Group();
    
    // 飞机材质
    const bodyMaterial = new THREE.MeshPhongMaterial({
        color: 0xe0e0e0,
        shininess: 100,
        specular: 0x333333
    });
    
    const wingMaterial = new THREE.MeshPhongMaterial({
        color: 0xd0d0d0,
        shininess: 80
    });
    
    const glassMaterial = new THREE.MeshPhongMaterial({
        color: 0x66aaff,
        transparent: true,
        opacity: 0.7,
        shininess: 100
    });
    
    // 机身（沿Z轴方向）
    const bodyGeo = new THREE.CylinderGeometry(0.5, 0.3, 8, 16);
    const body = new THREE.Mesh(bodyGeo, bodyMaterial);
    body.rotation.x = Math.PI / 2;
    body.castShadow = true;
    body.receiveShadow = true;
    aircraftGroup.add(body);
    
    // 机头（朝向Z轴负方向，迎风）
    const noseGeo = new THREE.ConeGeometry(0.5, 2, 16);
    const nose = new THREE.Mesh(noseGeo, bodyMaterial);
    nose.position.z = -5;
    nose.rotation.x = Math.PI / 2;
    nose.castShadow = true;
    aircraftGroup.add(nose);
    
    // 机尾
    const tailGeo = new THREE.ConeGeometry(0.3, 1.5, 16);
    const tail = new THREE.Mesh(tailGeo, bodyMaterial);
    tail.position.z = 4.75;
    tail.rotation.x = -Math.PI / 2;
    tail.castShadow = true;
    aircraftGroup.add(tail);
    
    // 主翼（沿X轴展开）
    const wingShape = new THREE.Shape();
    wingShape.moveTo(-4, 0);
    wingShape.lineTo(-2, 2.5);
    wingShape.lineTo(2, 2.5);
    wingShape.lineTo(4, 0);
    wingShape.lineTo(2, -0.3);
    wingShape.lineTo(-2, -0.3);
    wingShape.lineTo(-4, 0);
    
    const wingExtrudeSettings = {
        depth: 0.3,
        bevelEnabled: true,
        bevelThickness: 0.05,
        bevelSize: 0.05,
        bevelSegments: 2
    };
    
    const wingGeo = new THREE.ExtrudeGeometry(wingShape, wingExtrudeSettings);
    const wing = new THREE.Mesh(wingGeo, wingMaterial);
    wing.rotation.y = Math.PI / 2;
    wing.position.z = 0;
    wing.position.x = 0.15;
    wing.castShadow = true;
    wing.receiveShadow = true;
    aircraftGroup.add(wing);
    
    // 尾翼（水平）
    const hTailGeo = new THREE.BoxGeometry(3, 0.1, 2);
    const hTail = new THREE.Mesh(hTailGeo, wingMaterial);
    hTail.position.set(0, 0.5, 4);
    hTail.castShadow = true;
    aircraftGroup.add(hTail);
    
    // 尾翼（垂直）
    const vTailGeo = new THREE.BoxGeometry(0.1, 1.5, 1.5);
    const vTail = new THREE.Mesh(vTailGeo, wingMaterial);
    vTail.position.set(0, 1.2, 4.2);
    vTail.castShadow = true;
    aircraftGroup.add(vTail);
    
    // 驾驶舱
    const cockpitGeo = new THREE.SphereGeometry(0.6, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2);
    const cockpit = new THREE.Mesh(cockpitGeo, glassMaterial);
    cockpit.position.set(0.4, 0.4, -2.5);
    aircraftGroup.add(cockpit);
    
    // 引擎
    const engineGeo = new THREE.CylinderGeometry(0.4, 0.3, 1.5, 16);
    const engine1 = new THREE.Mesh(engineGeo, bodyMaterial);
    engine1.rotation.x = Math.PI / 2;
    engine1.position.set(1.5, -0.5, 0);
    engine1.castShadow = true;
    aircraftGroup.add(engine1);
    
    const engine2 = new THREE.Mesh(engineGeo, bodyMaterial);
    engine2.rotation.x = Math.PI / 2;
    engine2.position.set(-1.5, -0.5, 0);
    engine2.castShadow = true;
    aircraftGroup.add(engine2);
    
    aircraft = aircraftGroup;
    aircraft.position.set(0, 0, 0);
    scene.add(aircraft);
}

/**
 * 创建粒子系统（气流可视化）
 */
function createParticleSystem() {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    particleVelocities = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount; i++) {
        resetParticle(i, positions, colors, particleVelocities, true);
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    const material = new THREE.PointsMaterial({
        size: 0.15,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending,
        sizeAttenuation: true
    });
    
    particleSystem = new THREE.Points(geometry, material);
    scene.add(particleSystem);
}

/**
 * 重置单个粒子的位置和属性
 * @param {number} index - 粒子索引
 * @param {Float32Array} positions - 位置数组
 * @param {Float32Array} colors - 颜色数组
 * @param {Float32Array} velocities - 速度数组
 * @param {boolean} randomStart - 是否随机起始位置
 */
function resetParticle(index, positions, colors, velocities, randomStart = false) {
    const i3 = index * 3;
    
    // 随机在风洞入口处生成粒子
    positions[i3] = (Math.random() - 0.5) * (TUNNEL_WIDTH - 2);
    positions[i3 + 1] = (Math.random() - 0.5) * (TUNNEL_HEIGHT - 2);
    positions[i3 + 2] = randomStart 
        ? (Math.random() - 0.5) * TUNNEL_LENGTH 
        : -TUNNEL_LENGTH / 2 + 1;
    
    // 初始速度（沿Z轴正方向，从入口流向出口）
    const baseSpeed = 0.2 + Math.random() * 0.1;
    velocities[i3] = (Math.random() - 0.5) * 0.02;
    velocities[i3 + 1] = (Math.random() - 0.5) * 0.02;
    velocities[i3 + 2] = baseSpeed;
    
    // 初始颜色（蓝色调，根据速度变化）
    const color = new THREE.Color();
    color.setHSL(0.55 + Math.random() * 0.1, 0.8, 0.5 + Math.random() * 0.2);
    colors[i3] = color.r;
    colors[i3 + 1] = color.g;
    colors[i3 + 2] = color.b;
}

/**
 * 计算飞机对气流的影响（速度场）
 * 飞机沿Z轴放置，机头朝向Z轴负方向（迎风）
 * @param {THREE.Vector3} position - 粒子位置
 * @returns {THREE.Vector3} - 速度修正量
 */
function calculateVelocityField(position) {
    const correction = new THREE.Vector3(0, 0, 0);
    
    // 机翼区域的影响（飞机沿Z轴方向，机翼沿X轴展开）
    const wingStartZ = -4;
    const wingEndZ = 4;
    const wingSpan = 5;
    const wingThickness = 0.5;
    
    // 检查粒子是否在机翼影响区域
    if (position.z > wingStartZ && position.z < wingEndZ &&
        Math.abs(position.x) < wingSpan &&
        position.y > -wingThickness && position.y < wingThickness + 2) {
        
        // 机翼上方加速（伯努利原理）
        if (position.y > 0) {
            const distanceToWing = Math.max(0.1, position.y);
            const accelerationFactor = Math.max(0, 1 - distanceToWing / 2.5);
            correction.z += accelerationFactor * 0.15;
            
            // 轻微向上的升力效果
            correction.y += accelerationFactor * 0.03;
            
            // 翼尖涡流（沿X轴的翼尖）
            const distanceToTip = Math.max(0, Math.abs(position.x) - 3);
            if (distanceToTip < 1.5) {
                const vortexStrength = (1.5 - distanceToTip) / 1.5;
                correction.z += (position.x > 0 ? -1 : 1) * vortexStrength * 0.05;
                correction.y += (position.x > 0 ? 1 : -1) * vortexStrength * 0.03;
            }
        } else {
            // 机翼下方稍慢
            correction.z -= 0.03;
        }
        
        // 机头扰动（Z轴负方向为前）
        if (position.z < -3 && position.z > -6) {
            const noseDist = Math.max(0, -position.z - 3);
            correction.y += (1 - noseDist / 3) * 0.02;
            correction.x += (1 - noseDist / 3) * 0.01 * Math.sin(position.z * 2);
        }
        
        // 机尾扰动
        if (position.z > 3 && position.z < 6) {
            const tailDist = Math.max(0, position.z - 3);
            correction.y -= (1 - tailDist / 3) * 0.02;
        }
    }
    
    return correction;
}

/**
 * 更新粒子系统
 */
function updateParticles() {
    if (!particleSystem || !isWindRunning) return;
    
    const positions = particleSystem.geometry.attributes.position.array;
    const colors = particleSystem.geometry.attributes.color.array;
    
    for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        
        // 应用速度场修正
        const pos = new THREE.Vector3(
            positions[i3],
            positions[i3 + 1],
            positions[i3 + 2]
        );
        
        const velocityCorrection = calculateVelocityField(pos);
        
        // 更新位置
        positions[i3] += (particleVelocities[i3] + velocityCorrection.x) * windSpeed;
        positions[i3 + 1] += (particleVelocities[i3 + 1] + velocityCorrection.y) * windSpeed;
        positions[i3 + 2] += (particleVelocities[i3 + 2] + velocityCorrection.z) * windSpeed;
        
        // 根据速度更新颜色（速度越快越偏红/橙）
        const totalSpeed = Math.sqrt(
            Math.pow(particleVelocities[i3] + velocityCorrection.x, 2) +
            Math.pow(particleVelocities[i3 + 1] + velocityCorrection.y, 2) +
            Math.pow(particleVelocities[i3 + 2] + velocityCorrection.z, 2)
        );
        
        const normalizedSpeed = Math.min(1, totalSpeed / 0.4);
        const hue = 0.6 - normalizedSpeed * 0.5; // 从蓝色到红色
        const saturation = 0.8;
        const lightness = 0.4 + normalizedSpeed * 0.3;
        
        const color = new THREE.Color();
        color.setHSL(hue, saturation, lightness);
        colors[i3] = color.r;
        colors[i3 + 1] = color.g;
        colors[i3 + 2] = color.b;
        
        // 如果粒子超出风洞范围，重置到入口
        if (positions[i3 + 2] > TUNNEL_LENGTH / 2 ||
            Math.abs(positions[i3]) > TUNNEL_WIDTH / 2 - 1 ||
            Math.abs(positions[i3 + 1]) > TUNNEL_HEIGHT / 2 - 1) {
            resetParticle(i, positions, colors, particleVelocities, false);
        }
    }
    
    particleSystem.geometry.attributes.position.needsUpdate = true;
    particleSystem.geometry.attributes.color.needsUpdate = true;
}

/**
 * 绑定控制面板事件
 */
function bindControls() {
    // 风速控制
    const windSpeedSlider = document.getElementById('windSpeed');
    const speedDisplay = document.getElementById('speedDisplay');
    windSpeedSlider.addEventListener('input', (e) => {
        windSpeed = parseFloat(e.target.value);
        speedDisplay.textContent = `风速: ${windSpeed.toFixed(1)}`;
    });
    
    // 粒子数量控制
    const particleSlider = document.getElementById('particleCount');
    particleSlider.addEventListener('change', (e) => {
        particleCount = parseInt(e.target.value);
        scene.remove(particleSystem);
        createParticleSystem();
    });
    
    // 攻角控制
    const aoaSlider = document.getElementById('angleOfAttack');
    aoaSlider.addEventListener('input', (e) => {
        angleOfAttack = parseFloat(e.target.value);
        if (aircraft) {
            // 飞机沿Z轴方向，攻角绕X轴旋转
            aircraft.rotation.x = angleOfAttack * Math.PI / 180;
        }
    });
    
    // 风洞开关
    const toggleBtn = document.getElementById('toggleWind');
    toggleBtn.addEventListener('click', () => {
        isWindRunning = !isWindRunning;
        toggleBtn.textContent = isWindRunning ? '暂停风洞' : '启动风洞';
        toggleBtn.style.background = isWindRunning ? '#1976d2' : '#d32f2f';
    });
}

/**
 * 窗口大小变化处理
 */
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

/**
 * 动画循环
 */
function animate() {
    animationId = requestAnimationFrame(animate);
    
    // 更新粒子系统
    updateParticles();
    
    // 飞机轻微浮动动画
    if (aircraft && isWindRunning) {
        aircraft.position.y = Math.sin(Date.now() * 0.001) * 0.05;
    }
    
    // 渲染场景
    renderer.render(scene, camera);
}

/**
 * 清理资源（页面关闭时调用）
 */
function cleanup() {
    if (animationId) {
        cancelAnimationFrame(animationId);
    }
    if (renderer) {
        renderer.dispose();
    }
}

window.addEventListener('beforeunload', cleanup);
