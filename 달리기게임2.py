import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dash Runner", page_icon="🏃", layout="centered")

game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; padding: 0; background-color: #1a1a2e; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
        #gameContainer { position: relative; width: 800px; height: 400px; box-shadow: 0 12px 30px rgba(0,0,0,0.7); border-radius: 12px; overflow: hidden; border: 2px solid rgba(255,255,255,0.1); background: #000; }
        
        /* 전체화면 스타일 설정 */
        #gameContainer:fullscreen { width: 100vw; height: 100vh; border-radius: 0; border: none; display: flex; justify-content: center; align-items: center; }
        #gameContainer:-webkit-full-screen { width: 100vw; height: 100vh; border-radius: 0; border: none; display: flex; justify-content: center; align-items: center; }
        
        canvas { display: block; }
        
        #uiOverlay { position: absolute; top: 12px; left: 15px; right: 15px; display: flex; justify-content: space-between; align-items: center; font-size: 15px; font-weight: 800; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); z-index: 5; letter-spacing: 0.5px; }
        .hp-bar-bg { width: 140px; height: 16px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 10px; overflow: hidden; display: inline-block; vertical-align: middle; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5); }
        .hp-bar-fill { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #ff6b81); transition: width 0.1s; }
        
        .fullscreen-btn { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.4); color: white; font-size: 18px; width: 32px; height: 32px; border-radius: 6px; cursor: pointer; display: flex; justify-content: center; align-items: center; transition: 0.2s; margin-left: 10px; }
        .fullscreen-btn:hover { background: rgba(255,255,255,0.4); transform: scale(1.08); }

        .overlay-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 15, 26, 0.88); backdrop-filter: blur(4px); display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; z-index: 10; }
        .overlay-screen h1 { font-size: 44px; color: #fbc531; margin-bottom: 15px; text-shadow: 0 4px 10px rgba(251, 197, 49, 0.4); font-weight: 900; letter-spacing: 2px; }
        .btn { padding: 12px 24px; font-size: 16px; background: linear-gradient(135deg, #2ed573, #26af5f); border: none; color: white; border-radius: 8px; cursor: pointer; font-weight: bold; margin: 6px; transition: 0.2s; box-shadow: 0 4px 12px rgba(46, 213, 115, 0.3); }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(46, 213, 115, 0.5); }
        .btn-shop { background: linear-gradient(135deg, #e1b12c, #c89a1c); box-shadow: 0 4px 12px rgba(225, 177, 44, 0.3); }
        .btn-shop:hover { box-shadow: 0 6px 16px rgba(225, 177, 44, 0.5); }
        
        /* 상점 UI */
        #shopScreen { display: none; }
        .shop-container { display: flex; gap: 20px; margin-bottom: 20px; }
        .shop-box { background: rgba(255,255,255,0.06); padding: 18px; border-radius: 12px; text-align: center; width: 220px; border: 1px solid rgba(255,255,255,0.1); }
        .shop-box h3 { margin-top: 0; color: #fbc531; font-size: 18px; }
        .shop-item { margin: 10px 0; padding: 8px 10px; background: rgba(0,0,0,0.4); border-radius: 6px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
        .shop-item button { padding: 5px 10px; font-size: 12px; cursor: pointer; border-radius: 4px; border: none; font-weight: bold; background: #70a1ff; color: white; }
        .shop-item button:disabled { background: #57606f; cursor: default; }
    </style>
</head>
<body>

<div id="gameContainer">
    <canvas id="gameCanvas" width="800" height="400"></canvas>
    
    <div id="uiOverlay">
        <div>
            HP <div class="hp-bar-bg"><div id="hpFill" class="hp-bar-fill"></div></div>
        </div>
        <div style="display: flex; align-items: center;">
            <span>SCORE: <span id="scoreText">0</span> | COINS: <span id="coinText">0</span> (누적: <span id="totalCoinText">0</span>)</span>
            <button class="fullscreen-btn" onclick="toggleFullScreen()" title="전체화면 전환">⛶</button>
        </div>
    </div>

    <!-- 메인 메뉴 -->
    <div id="mainMenuScreen" class="overlay-screen">
        <h1>DASH RUNNER</h1>
        <button class="btn" onclick="startGame()">게임 시작</button>
        <button class="btn btn-shop" onclick="openShop()">상점 / 커스텀</button>
    </div>

    <!-- 상점 메뉴 -->
    <div id="shopScreen" class="overlay-screen">
        <h1>ITEM SHOP</h1>
        <p>보유 누적 코인: <span id="shopCoinText" style="color: #fbc531; font-weight: bold;">0</span></p>
        <div class="shop-container">
            <div class="shop-box">
                <h3>배경 테마</h3>
                <div class="shop-item">
                    <span>푸른 초원 (기본)</span>
                    <button id="bg0" onclick="selectBg(0)">선택</button>
                </div>
                <div class="shop-item">
                    <span>별빛 시티 (50코인)</span>
                    <button id="bg1" onclick="buyOrSelectBg(1, 50)">구매</button>
                </div>
                <div class="shop-item">
                    <span>노을 산맥 (100코인)</span>
                    <button id="bg2" onclick="buyOrSelectBg(2, 100)">구매</button>
                </div>
            </div>
            <div class="shop-box">
                <h3>캐릭터 수트</h3>
                <div class="shop-item">
                    <span>옐로우 (기본)</span>
                    <button id="suit0" onclick="selectSuit(0)">선택</button>
                </div>
                <div class="shop-item">
                    <span>블루 (30코인)</span>
                    <button id="suit1" onclick="buyOrSelectSuit(1, 30)">구매</button>
                </div>
                <div class="shop-item">
                    <span>레드 (70코인)</span>
                    <button id="suit2" onclick="buyOrSelectSuit(2, 70)">구매</button>
                </div>
            </div>
        </div>
        <button class="btn" onclick="closeShop()">메뉴로 돌아가기</button>
    </div>

    <!-- 게임 오버 -->
    <div id="gameOverScreen" class="overlay-screen" style="display: none;">
        <h1 style="color: #ff4757; text-shadow: 0 4px 10px rgba(255,71,87,0.4);">GAME OVER</h1>
        <p style="font-size: 18px;">최종 점수: <span id="finalScore" style="color: #fbc531;">0</span> | 획득 코인: <span id="finalCoins" style="color: #eccc68;">0</span></p>
        <div style="margin-top: 10px;">
            <button class="btn" onclick="resetGame()">다시 시작</button>
            <button class="btn btn-shop" onclick="returnToMenu()">메인 메뉴</button>
        </div>
    </div>
</div>

<script>
const container = document.getElementById('gameContainer');
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

function toggleFullScreen() {
    if (!document.fullscreenElement && !document.webkitFullscreenElement) {
        if (container.requestFullscreen) {
            container.requestFullscreen();
        } else if (container.webkitRequestFullscreen) {
            container.webkitRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        }
    }
}

let totalCoins = parseInt(localStorage.getItem('dash_totalCoins')) || 0;
let unlockedBgs = JSON.parse(localStorage.getItem('dash_unlockedBgs')) || [true, false, false];
let unlockedSuits = JSON.parse(localStorage.getItem('dash_unlockedSuits')) || [true, false, false];
let currentBg = parseInt(localStorage.getItem('dash_currentBg')) || 0;
let currentSuit = parseInt(localStorage.getItem('dash_currentSuit')) || 0;

const suitColors = [
    { shirt: '#fbc531', sleeve: '#e1b12c', pants: '#2f3542', legFront: '#57606f' },
    { shirt: '#00a8ff', sleeve: '#0097e6', pants: '#192a56', legFront: '#273c75' },
    { shirt: '#e84118', sleeve: '#c23616', pants: '#2f3542', legFront: '#3d3d3d' }
];

let score = 0;
let sessionCoins = 0;
let hp = 100;
let gameOver = false;
let gameRunning = false;
let gameFrame = 0;

const clouds = [
    { x: 50, y: 50, speed: 0.5, scale: 0.8 },
    { x: 300, y: 80, speed: 0.3, scale: 1.2 },
    { x: 600, y: 40, speed: 0.6, scale: 1.0 }
];

const stars = Array.from({ length: 40 }, () => ({
    x: Math.random() * 800,
    y: Math.random() * 200,
    size: Math.random() * 2 + 1,
    alpha: Math.random()
}));

const player = {
    x: 100,
    y: 280,
    width: 40,
    height: 70,
    vy: 0,
    gravity: 0.8,
    jumpCount: 0,
    maxJumps: 2,
    isSliding: false,
    giantTimer: 0,
    invincibleTimer: 0,
    isGiant: false
};

let obstacles = [];
let pits = [];
let items = [];

window.addEventListener('keydown', (e) => {
    if (!gameRunning || gameOver) return;
    if ((e.code === 'Space' || e.code === 'ArrowUp') && player.jumpCount < player.maxJumps && !player.isSliding) {
        player.vy = -12;
        player.jumpCount++;
    }
    if (e.code === 'ArrowDown' && player.jumpCount === 0) {
        player.isSliding = true;
    }
});

window.addEventListener('keyup', (e) => {
    if (e.code === 'ArrowDown') {
        player.isSliding = false;
    }
});

function saveUserData() {
    localStorage.setItem('dash_totalCoins', totalCoins);
    localStorage.setItem('dash_unlockedBgs', JSON.stringify(unlockedBgs));
    localStorage.setItem('dash_unlockedSuits', JSON.stringify(unlockedSuits));
    localStorage.setItem('dash_currentBg', currentBg);
    localStorage.setItem('dash_currentSuit', currentSuit);
}

function updateShopUI() {
    document.getElementById('shopCoinText').innerText = totalCoins;
    document.getElementById('totalCoinText').innerText = totalCoins;

    for(let i=0; i<3; i++) {
        let btn = document.getElementById('bg' + i);
        if(currentBg === i) { btn.innerText = "착용중"; btn.disabled = true; }
        else if(unlockedBgs[i]) { btn.innerText = "선택"; btn.disabled = false; }
        else { btn.innerText = "구매"; btn.disabled = false; }
    }

    for(let i=0; i<3; i++) {
        let btn = document.getElementById('suit' + i);
        if(currentSuit === i) { btn.innerText = "착용중"; btn.disabled = true; }
        else if(unlockedSuits[i]) { btn.innerText = "선택"; btn.disabled = false; }
        else { btn.innerText = "구매"; btn.disabled = false; }
    }
}

function selectBg(idx) { currentBg = idx; saveUserData(); updateShopUI(); }
function buyOrSelectBg(idx, cost) {
    if(unlockedBgs[idx]) { selectBg(idx); }
    else if(totalCoins >= cost) { totalCoins -= cost; unlockedBgs[idx] = true; selectBg(idx); }
    else { alert("코인이 부족합니다!"); }
}

function selectSuit(idx) { currentSuit = idx; saveUserData(); updateShopUI(); }
function buyOrSelectSuit(idx, cost) {
    if(unlockedSuits[idx]) { selectSuit(idx); }
    else if(totalCoins >= cost) { totalCoins -= cost; unlockedSuits[idx] = true; selectSuit(idx); }
    else { alert("코인이 부족합니다!"); }
}

function openShop() {
    updateShopUI();
    document.getElementById('mainMenuScreen').style.display = 'none';
    document.getElementById('shopScreen').style.display = 'flex';
}

function closeShop() {
    document.getElementById('shopScreen').style.display = 'none';
    document.getElementById('mainMenuScreen').style.display = 'flex';
}

function startGame() {
    document.getElementById('mainMenuScreen').style.display = 'none';
    resetGame();
    gameRunning = true;
}

function returnToMenu() {
    document.getElementById('gameOverScreen').style.display = 'none';
    document.getElementById('mainMenuScreen').style.display = 'flex';
    gameRunning = false;
    updateShopUI();
}

function spawnObjects() {
    if (gameFrame % 130 === 0) {
        let rand = Math.random();
        let type = rand < 0.4 ? 'spike' : (rand < 0.7 ? 'saw' : 'high_saw');
        obstacles.push({
            x: 800,
            y: type === 'spike' ? 310 : (type === 'saw' ? 270 : 220),
            width: 40,
            height: 40,
            type: type
        });
    }

    if (gameFrame % 280 === 0 && Math.random() < 0.6) {
        pits.push({ x: 800, width: 90 });
    }

    if (gameFrame % 170 === 0) {
        let rand = Math.random();
        let itemType = rand < 0.6 ? 'coin' : (rand < 0.85 ? 'heal' : 'giant');
        items.push({
            x: 800,
            y: itemType === 'coin' ? 200 + Math.random() * 60 : 250,
            width: 25,
            height: 25,
            type: itemType
        });
    }
}

function drawBackground() {
    if (currentBg === 0) {
        let skyGradient = ctx.createLinearGradient(0, 0, 0, 350);
        skyGradient.addColorStop(0, '#54a0ff');
        skyGradient.addColorStop(1, '#74b9ff');
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, 800, 350);

        ctx.fillStyle = '#55efc4';
        let mountainOffset = (gameFrame * 0.5) % 400;
        ctx.beginPath();
        ctx.moveTo(0 - mountainOffset, 350);
        for (let i = -1; i <= 3; i++) {
            let cx = i * 400 - mountainOffset;
            ctx.quadraticCurveTo(cx + 100, 220, cx + 200, 350);
            ctx.quadraticCurveTo(cx + 300, 260, cx + 400, 350);
        }
        ctx.fill();

        ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
        clouds.forEach(cloud => {
            if (gameRunning) cloud.x -= cloud.speed;
            if (cloud.x < -100) cloud.x = 850;
            ctx.beginPath();
            ctx.arc(cloud.x, cloud.y, 20 * cloud.scale, 0, Math.PI * 2);
            ctx.arc(cloud.x + 15 * cloud.scale, cloud.y - 10 * cloud.scale, 25 * cloud.scale, 0, Math.PI * 2);
            ctx.arc(cloud.x + 35 * cloud.scale, cloud.y, 20 * cloud.scale, 0, Math.PI * 2);
            ctx.fill();
        });

    } else if (currentBg === 1) {
        let skyGradient = ctx.createLinearGradient(0, 0, 0, 350);
        skyGradient.addColorStop(0, '#0c2461');
        skyGradient.addColorStop(1, '#1e3799');
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, 800, 350);

        stars.forEach(star => {
            ctx.fillStyle = `rgba(255, 255, 255, ${0.3 + Math.sin(gameFrame * 0.05 + star.x) * 0.4})`;
            ctx.fillRect(star.x, star.y, star.size, star.size);
        });

        ctx.fillStyle = '#f8c291';
        ctx.shadowColor = '#f8c291';
        ctx.shadowBlur = 15;
        ctx.beginPath();
        ctx.arc(700, 70, 30, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.fillStyle = '#0a192f';
        let cityOffset = (gameFrame * 0.8) % 300;
        for (let i = -1; i < 4; i++) {
            let bx = i * 300 - cityOffset;
            ctx.fillRect(bx + 10, 180, 40, 170);
            ctx.fillRect(bx + 60, 130, 55, 220);
            ctx.fillRect(bx + 125, 210, 45, 140);
            ctx.fillRect(bx + 180, 150, 70, 200);

            ctx.fillStyle = '#f6b93b';
            for (let wy = 150; wy < 320; wy += 25) {
                if ((i + wy) % 2 === 0) ctx.fillRect(bx + 72, wy, 8, 12);
                if ((i + wy) % 3 === 0) ctx.fillRect(bx + 195, wy + 10, 8, 12);
            }
            ctx.fillStyle = '#0a192f';
        }

    } else if (currentBg === 2) {
        let skyGradient = ctx.createLinearGradient(0, 0, 0, 350);
        skyGradient.addColorStop(0, '#b71540');
        skyGradient.addColorStop(0.5, '#e55039');
        skyGradient.addColorStop(1, '#f6b93b');
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, 800, 350);

        ctx.fillStyle = '#ffda79';
        ctx.shadowColor = '#ffda79';
        ctx.shadowBlur = 25;
        ctx.beginPath();
        ctx.arc(400, 220, 50, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.fillStyle = 'rgba(78, 15, 30, 0.6)';
        let mountOffset1 = (gameFrame * 0.3) % 600;
        ctx.beginPath();
        ctx.moveTo(-mountOffset1, 350);
        ctx.lineTo(150 - mountOffset1, 180);
        ctx.lineTo(350 - mountOffset1, 350);
        ctx.lineTo(500 - mountOffset1, 210);
        ctx.lineTo(750 - mountOffset1, 350);
        ctx.lineTo(1000 - mountOffset1, 350);
        ctx.fill();

        ctx.fillStyle = '#2c0b0e';
        let mountOffset2 = (gameFrame * 0.7) % 500;
        ctx.beginPath();
        ctx.moveTo(-mountOffset2, 350);
        ctx.lineTo(100 - mountOffset2, 240);
        ctx.lineTo(250 - mountOffset2, 350);
        ctx.lineTo(400 - mountOffset2, 220);
        ctx.lineTo(600 - mountOffset2, 350);
        ctx.lineTo(850 - mountOffset2, 350);
        ctx.fill();
    }

    let groundColor = currentBg === 0 ? '#2ed573' : (currentBg === 1 ? '#1e272e' : '#3c6382');
    let dirtColor = currentBg === 0 ? '#b8e994' : (currentBg === 1 ? '#0f171e' : '#218c74');

    ctx.fillStyle = groundColor;
    ctx.fillRect(0, 350, 800, 12);

    ctx.fillStyle = dirtColor;
    ctx.fillRect(0, 362, 800, 38);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
    let groundLineOffset = (gameFrame * 6) % 40;
    for (let x = -40; x < 840; x += 40) {
        ctx.fillRect(x - groundLineOffset, 368, 20, 4);
        ctx.fillRect(x - groundLineOffset + 15, 382, 10, 4);
    }
}

function drawLeg(ctx, hipAngle, kneeAngle, scale, color) {
    ctx.save();
    ctx.translate(0, -24 * scale);
    ctx.rotate(hipAngle);

    ctx.fillStyle = color;
    ctx.fillRect(-4 * scale, 0, 8 * scale, 15 * scale);

    ctx.translate(0, 13 * scale);
    ctx.rotate(kneeAngle);
    ctx.fillRect(-3.5 * scale, 0, 7 * scale, 14 * scale);

    ctx.fillStyle = "#1e272e";
    ctx.fillRect(-3.5 * scale, 12 * scale, 10 * scale, 5 * scale);

    ctx.restore();
}

function drawArm(ctx, angle, scale, color) {
    ctx.save();
    ctx.translate(0, -48 * scale);
    ctx.rotate(angle);

    ctx.fillStyle = color;
    ctx.fillRect(-3 * scale, 0, 6 * scale, 13 * scale);

    ctx.translate(0, 11 * scale);
    ctx.rotate(0.4);
    ctx.fillRect(-2.5 * scale, 0, 5 * scale, 12 * scale);

    ctx.fillStyle = "#ffdbac";
    ctx.beginPath();
    ctx.arc(0, 12 * scale, 3 * scale, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
}

function drawPlayer() {
    ctx.save();
    
    if (player.invincibleTimer > 0 && Math.floor(player.invincibleTimer / 5) % 2 === 0) {
        ctx.globalAlpha = 0.4;
    }

    let scale = player.isGiant ? 1.6 : 1.0;
    let suit = suitColors[currentSuit];
    
    let curWidth = (player.isSliding ? 55 : player.width) * scale;
    let curHeight = (player.isSliding ? 30 : player.height) * scale;
    
    let renderX = player.x + curWidth / 2;
    let renderY = player.y + (player.isSliding ? 35 * scale : player.height * scale);

    ctx.translate(renderX, renderY);

    if (player.isSliding) {
        ctx.fillStyle = suit.shirt;
        ctx.beginPath();
        ctx.ellipse(-5 * scale, -12 * scale, 25 * scale, 12 * scale, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = suit.pants;
        ctx.fillRect(-28 * scale, -10 * scale, 20 * scale, 10 * scale);

        ctx.fillStyle = "#ffdbac";
        ctx.beginPath();
        ctx.arc(18 * scale, -14 * scale, 9 * scale, 0, Math.PI * 2);
        ctx.fill();
    } else {
        let runCycle = gameFrame * 0.2;
        let isAir = player.y < 280;

        let bobbing = isAir ? 0 : Math.sin(runCycle * 2) * 4 * scale;
        
        let hipAngle1 = isAir ? -0.4 : Math.sin(runCycle) * 0.8;
        let hipAngle2 = isAir ? 0.6 : -Math.sin(runCycle) * 0.8;
        let kneeAngle1 = isAir ? 0.8 : Math.max(0, Math.sin(runCycle + 1.2) * 0.9);
        let kneeAngle2 = isAir ? 0.3 : Math.max(0, -Math.sin(runCycle + 1.2) * 0.9);

        let shoulderAngle1 = isAir ? 0.5 : -Math.sin(runCycle) * 0.7;
        let shoulderAngle2 = isAir ? -0.5 : Math.sin(runCycle) * 0.7;

        ctx.translate(0, -bobbing);

        drawLeg(ctx, hipAngle2, kneeAngle2, scale, suit.pants);
        drawArm(ctx, shoulderAngle2, scale, suit.sleeve);

        ctx.fillStyle = suit.shirt;
        ctx.fillRect(-10 * scale, -52 * scale, 20 * scale, 26 * scale);
        ctx.fillStyle = "#2f3542";
        ctx.fillRect(-10 * scale, -28 * scale, 20 * scale, 4 * scale);

        let headY = -63 * scale;
        ctx.fillStyle = "#ffdbac";
        ctx.beginPath();
        ctx.arc(0, headY, 11 * scale, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#485460";
        ctx.beginPath();
        ctx.arc(0, headY - 2 * scale, 12 * scale, Math.PI * 0.8, Math.PI * 2.2);
        ctx.fill();

        ctx.fillStyle = "#000";
        ctx.fillRect(4 * scale, headY - 2 * scale, 3 * scale, 3 * scale);
        ctx.fillStyle = "#e84118";
        ctx.fillRect(4 * scale, headY + 4 * scale, 4 * scale, 2 * scale);

        drawLeg(ctx, hipAngle1, kneeAngle1, scale, suit.legFront);
        drawArm(ctx, shoulderAngle1, scale, suit.shirt);
    }

    ctx.restore();
}

function update() {
    if (!gameRunning || gameOver) return;
    gameFrame++;
    score++;

    if (gameFrame % 10 === 0) {
        hp -= 0.5;
    }

    player.vy += player.gravity;
    player.y += player.vy;

    let overPit = false;
    let scale = player.isGiant ? 1.6 : 1.0;
    let playerFootX = player.x + (player.width * scale) / 2;

    pits.forEach(pit => {
        if (playerFootX > pit.x && playerFootX < pit.x + pit.width) {
            overPit = true;
        }
    });

    if (player.y >= 280) {
        if (overPit) {
            if (player.y > 380) {
                hp = 0;
            }
        } else {
            player.y = 280;
            player.vy = 0;
            player.jumpCount = 0;
        }
    }

    if (player.giantTimer > 0) {
        player.giantTimer--;
        if (player.giantTimer === 0) {
            player.isGiant = false;
            player.invincibleTimer = 60;
        }
    }

    if (player.invincibleTimer > 0) {
        player.invincibleTimer--;
    }

    for (let i = pits.length - 1; i >= 0; i--) {
        pits[i].x -= 6;
        if (pits[i].x + pits[i].width < 0) {
            pits.splice(i, 1);
        }
    }

    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= 6;

        let pBox = {
            x: player.x,
            y: player.isSliding ? player.y + 35 * scale : player.y,
            width: (player.isSliding ? 55 : player.width) * scale,
            height: (player.isSliding ? 35 : player.height) * scale
        };

        if (
            pBox.x < obs.x + obs.width &&
            pBox.x + pBox.width > obs.x &&
            pBox.y < obs.y + obs.height &&
            pBox.y + pBox.height > obs.y
        ) {
            if (player.isGiant) {
                obstacles.splice(i, 1);
                score += 50;
            } else if (player.invincibleTimer === 0) {
                hp -= 20;
                obstacles.splice(i, 1);
            }
        }

        if (obs && obs.x + obs.width < 0) {
            obstacles.splice(i, 1);
        }
    }

    for (let i = items.length - 1; i >= 0; i--) {
        let item = items[i];
        item.x -= 6;

        if (
            player.x < item.x + item.width &&
            player.x + player.width > item.x &&
            player.y < item.y + item.height &&
            player.y + player.height > item.y
        ) {
            if (item.type === 'coin') {
                sessionCoins += 1;
                totalCoins += 1;
                saveUserData();
            }
            if (item.type === 'heal') hp = Math.min(100, hp + 10);
            if (item.type === 'giant') {
                player.isGiant = true;
                player.giantTimer = 300;
            }
            items.splice(i, 1);
        } else if (item.x + item.width < 0) {
            items.splice(i, 1);
        }
    }

    if (hp <= 0) {
        hp = 0;
        gameOver = true;
        document.getElementById('finalScore').innerText = score;
        document.getElementById('finalCoins').innerText = sessionCoins;
        document.getElementById('gameOverScreen').style.display = 'flex';
    }

    document.getElementById('hpFill').style.width = Math.max(0, hp) + '%';
    document.getElementById('scoreText').innerText = score;
    document.getElementById('coinText').innerText = sessionCoins;
    document.getElementById('totalCoinText').innerText = totalCoins;

    spawnObjects();
}

function draw() {
    drawBackground();

    pits.forEach(pit => {
        ctx.fillStyle = '#0f0f1a';
        ctx.fillRect(pit.x, 350, pit.width, 50);
        ctx.fillStyle = 'rgba(0,0,0,0.5)';
        ctx.fillRect(pit.x, 350, 4, 50);
        ctx.fillRect(pit.x + pit.width - 4, 350, 4, 50);
    });

    obstacles.forEach(obs => {
        if (obs.type === 'saw' || obs.type === 'high_saw') {
            ctx.save();
            ctx.translate(obs.x + 20, obs.y + 20);
            ctx.rotate(gameFrame * 0.15);
            ctx.fillStyle = obs.type === 'high_saw' ? '#ff3838' : '#718093';
            ctx.beginPath();
            for (let i = 0; i < 8; i++) {
                ctx.rotate(Math.PI / 4);
                ctx.lineTo(22, 0);
                ctx.lineTo(12, 6);
            }
            ctx.fill();
            ctx.fillStyle = '#f5f6fa';
            ctx.beginPath();
            ctx.arc(0, 0, 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        } else {
            ctx.fillStyle = '#ff4757';
            ctx.beginPath();
            ctx.moveTo(obs.x, obs.y + obs.height);
            ctx.lineTo(obs.x + obs.width / 2, obs.y);
            ctx.lineTo(obs.x + obs.width, obs.y + obs.height);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }
    });

    items.forEach(item => {
        if (item.type === 'coin') {
            ctx.fillStyle = '#f1c40f';
            ctx.shadowColor = '#f1c40f';
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.arc(item.x + 12, item.y + 12, 10, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#f39c12';
            ctx.font = 'bold 12px sans-serif';
            ctx.fillText('$', item.x + 8, item.y + 16);
            ctx.shadowBlur = 0;
        } else if (item.type === 'heal') {
            ctx.fillStyle = '#ff6b81';
            ctx.fillRect(item.x + 4, item.y, 8, 24);
            ctx.fillRect(item.x, item.y + 8, 16, 8);
        } else if (item.type === 'giant') {
            ctx.fillStyle = '#70a1ff';
            ctx.shadowColor = '#70a1ff';
            ctx.shadowBlur = 10;
            ctx.beginPath();
            ctx.arc(item.x + 12, item.y + 12, 12, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    });

    if (gameRunning) {
        drawPlayer();
    }
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

function resetGame() {
    score = 0;
    sessionCoins = 0;
    hp = 100;
    gameOver = false;
    gameFrame = 0;
    player.y = 280;
    player.vy = 0;
    player.isGiant = false;
    player.giantTimer = 0;
    player.invincibleTimer = 0;
    obstacles = [];
    pits = [];
    items = [];
    document.getElementById('gameOverScreen').style.display = 'none';
}

updateShopUI();
gameLoop();
</script>
</body>
</html>
"""

# components.html의 allow="fullscreen" 속성 지정
components.html(game_html, height=450)
