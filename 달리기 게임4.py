import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dash Runner", page_icon="🏃", layout="wide")

game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; padding: 0; background-color: #1a1a2e; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
        #gameContainer { position: relative; width: 1000px; height: 500px; box-shadow: 0 12px 30px rgba(0,0,0,0.7); border-radius: 12px; overflow: hidden; border: 2px solid rgba(255,255,255,0.1); background: #000; }
        
        #gameContainer:fullscreen { width: 100vw; height: 100vh; border-radius: 0; border: none; display: flex; justify-content: center; align-items: center; }
        #gameContainer:-webkit-full-screen { width: 100vw; height: 100vh; border-radius: 0; border: none; display: flex; justify-content: center; align-items: center; }
        
        canvas { display: block; width: 100%; height: 100%; }
        
        #uiOverlay { position: absolute; top: 15px; left: 20px; right: 20px; display: flex; justify-content: space-between; align-items: center; font-size: 17px; font-weight: 800; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); z-index: 5; letter-spacing: 0.5px; }
        .hp-bar-bg { width: 180px; height: 20px; background: rgba(0,0,0,0.5); border: 2px solid #fff; border-radius: 10px; overflow: hidden; display: inline-block; vertical-align: middle; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5); }
        .hp-bar-fill { width: 100%; height: 100%; background: linear-gradient(90deg, #ff4757, #ff6b81); transition: width 0.1s; }
        
        .fullscreen-btn { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.4); color: white; font-size: 20px; width: 36px; height: 36px; border-radius: 8px; cursor: pointer; display: flex; justify-content: center; align-items: center; transition: 0.2s; margin-left: 15px; }
        .fullscreen-btn:hover { background: rgba(255,255,255,0.4); transform: scale(1.08); }

        .overlay-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(15, 15, 26, 0.88); backdrop-filter: blur(4px); display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; z-index: 10; }
        .overlay-screen h1 { font-size: 52px; color: #fbc531; margin-bottom: 20px; text-shadow: 0 4px 10px rgba(251, 197, 49, 0.4); font-weight: 900; letter-spacing: 2px; }
        .btn { padding: 14px 28px; font-size: 18px; background: linear-gradient(135deg, #2ed573, #26af5f); border: none; color: white; border-radius: 8px; cursor: pointer; font-weight: bold; margin: 8px; transition: 0.2s; box-shadow: 0 4px 12px rgba(46, 213, 115, 0.3); }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(46, 213, 115, 0.5); }
        .btn-shop { background: linear-gradient(135deg, #e1b12c, #c89a1c); box-shadow: 0 4px 12px rgba(225, 177, 44, 0.3); }
        .btn-shop:hover { shadow: 0 6px 16px rgba(225, 177, 44, 0.5); }
        
        #shopScreen { display: none; }
        .shop-container { display: flex; gap: 30px; margin-bottom: 25px; }
        .shop-box { background: rgba(255,255,255,0.06); padding: 22px; border-radius: 12px; text-align: center; width: 260px; border: 1px solid rgba(255,255,255,0.1); }
        .shop-box h3 { margin-top: 0; color: #fbc531; font-size: 20px; }
        .shop-item { margin: 12px 0; padding: 10px 12px; background: rgba(0,0,0,0.4); border-radius: 6px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
        .shop-item button { padding: 6px 12px; font-size: 13px; cursor: pointer; border-radius: 4px; border: none; font-weight: bold; background: #70a1ff; color: white; }
        .shop-item button:disabled { background: #57606f; cursor: default; }
    </style>
</head>
<body>

<div id="gameContainer">
    <canvas id="gameCanvas" width="1000" height="500"></canvas>
    
    <div id="uiOverlay">
        <div>
            HP <div class="hp-bar-bg"><div id="hpFill" class="hp-bar-fill"></div></div>
        </div>
        <div style="display: flex; align-items: center;">
            <span>SCORE: <span id="scoreText">0</span> | COINS: <span id="coinText">0</span> (누적: <span id="totalCoinText">0</span>)</span>
            <button class="fullscreen-btn" onclick="toggleFullScreen()" title="전체화면 전환">⛶</button>
        </div>
    </div>

    <div id="mainMenuScreen" class="overlay-screen">
        <h1>DASH RUNNER</h1>
        <button class="btn" onclick="startGame()">게임 시작</button>
        <button class="btn btn-shop" onclick="openShop()">상점 / 커스텀</button>
    </div>

    <div id="shopScreen" class="overlay-screen">
        <h1>ITEM SHOP</h1>
        <p style="font-size: 18px;">보유 누적 코인: <span id="shopCoinText" style="color: #fbc531; font-weight: bold;">0</span></p>
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

    <div id="gameOverScreen" class="overlay-screen" style="display: none;">
        <h1 style="color: #ff4757; text-shadow: 0 4px 10px rgba(255,71,87,0.4);">GAME OVER</h1>
        <p style="font-size: 20px;">최종 점수: <span id="finalScore" style="color: #fbc531;">0</span> | 획득 코인: <span id="finalCoins" style="color: #eccc68;">0</span></p>
        <div style="margin-top: 15px;">
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
    { x: 50, y: 60, speed: 0.5, scale: 1.0 },
    { x: 400, y: 100, speed: 0.3, scale: 1.4 },
    { x: 800, y: 50, speed: 0.6, scale: 1.2 }
];

const stars = Array.from({ length: 50 }, () => ({
    x: Math.random() * 1000,
    y: Math.random() * 250,
    size: Math.random() * 2.5 + 1,
    alpha: Math.random()
}));

const player = {
    x: 120,
    y: 360,
    width: 40,
    height: 70,
    slideHeight: 30,
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
        player.vy = -12.5;
        player.jumpCount++;
    }
    if ((e.code === 'ArrowDown' || e.code === 'KeyS') && player.jumpCount === 0) {
        player.isSliding = true;
    }
});

window.addEventListener('keyup', (e) => {
    if (e.code === 'ArrowDown' || e.code === 'KeyS') {
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
            x: 1000,
            y: type === 'spike' ? 390 : (type === 'saw' ? 350 : 210),
            width: type === 'high_saw' ? 50 : 40,
            height: type === 'high_saw' ? 180 : 40,
            type: type
        });
    }

    if (gameFrame % 280 === 0 && Math.random() < 0.6) {
        pits.push({ x: 1000, width: 100 });
    }

    if (gameFrame % 110 === 0) {
        let rand = Math.random();
        let itemType = rand < 0.20 ? 'heal' : (rand < 0.90 ? 'coin' : 'giant');
        items.push({
            x: 1000,
            y: itemType === 'coin' ? 260 + Math.random() * 80 : 320,
            width: 30,
            height: 35,
            type: itemType
        });
    }
}

function drawBackground() {
    if (currentBg === 0) {
        let skyGradient = ctx.createLinearGradient(0, 0, 0, 430);
        skyGradient.addColorStop(0, '#54a0ff');
        skyGradient.addColorStop(1, '#74b9ff');
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, 1000, 430);

        ctx.fillStyle = '#55efc4';
        let mountainOffset = (gameFrame * 0.5) % 500;
        ctx.beginPath();
        ctx.moveTo(0 - mountainOffset, 430);
        for (let i = -1; i <= 3; i++) {
            let cx = i * 500 - mountainOffset;
            ctx.quadraticCurveTo(cx + 125, 280, cx + 250, 430);
            ctx.quadraticCurveTo(cx + 375, 320, cx + 500, 430);
        }
        ctx.fill();

        ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
        clouds.forEach(cloud => {
            if (gameRunning) cloud.x -= cloud.speed;
            if (cloud.x < -120) cloud.x = 1050;
            ctx.beginPath();
            ctx.arc(cloud.x, cloud.y, 20 * cloud.scale, 0, Math.PI * 2);
            ctx.arc(cloud.x + 15 * cloud.scale, cloud.y - 10 * cloud.scale, 25 * cloud.scale, 0, Math.PI * 2);
            ctx.arc(cloud.x + 35 * cloud.scale, cloud.y, 20 * cloud.scale, 0, Math.PI * 2);
            ctx.fill();
        });

    } else if (currentBg === 1) {
        let skyGradient = ctx.createLinearGradient(0, 0, 0, 430);
        skyGradient.addColorStop(0, '#0c2461');
        skyGradient.addColorStop(1, '#1e3799');
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, 1000, 430);

        stars.forEach(star => {
            ctx.fillStyle = `rgba(255, 255, 255, ${0.3 + Math.sin(gameFrame * 0.05 + star.x) * 0.4})`;
            ctx.fillRect(star.x, star.y, star.size, star.size);
        });

        ctx.fillStyle = '#f8c291';
        ctx.shadowColor = '#f8c291';
        ctx.shadowBlur = 15;
        ctx.beginPath();
        ctx.arc(880, 80, 35, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.fillStyle = '#0a192f';
        let cityOffset = (gameFrame * 0.8) % 350;
        for (let i = -1; i < 4; i++) {
            let bx = i * 350 - cityOffset;
            ctx.fillRect(bx + 10, 220, 50, 210);
            ctx.fillRect(bx + 75, 160, 65, 270);
            ctx.fillRect(bx + 155, 250, 55, 180);
            ctx.fillRect(bx + 225, 180, 85, 250);

            ctx.fillStyle = '#f6b93b';
            for (let wy = 180; wy < 400; wy += 30) {
                if ((i + wy) % 2 === 0) ctx.fillRect(bx + 88, wy, 10, 14);
                if ((i + wy) % 3 === 0) ctx.fillRect(bx + 245, wy + 10, 10, 14);
            }
            ctx.fillStyle = '#0a192f';
        }

    } else if (currentBg === 2) {
        let skyGradient = ctx.createLinearGradient(0, 0, 0, 430);
        skyGradient.addColorStop(0, '#b71540');
        skyGradient.addColorStop(0.5, '#e55039');
        skyGradient.addColorStop(1, '#f6b93b');
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, 1000, 430);

        ctx.fillStyle = '#ffda79';
        ctx.shadowColor = '#ffda79';
        ctx.shadowBlur = 25;
        ctx.beginPath();
        ctx.arc(500, 280, 60, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        ctx.fillStyle = 'rgba(78, 15, 30, 0.6)';
        let mountOffset1 = (gameFrame * 0.3) % 700;
        ctx.beginPath();
        ctx.moveTo(-mountOffset1, 430);
        ctx.lineTo(200 - mountOffset1, 220);
        ctx.lineTo(450 - mountOffset1, 430);
        ctx.lineTo(650 - mountOffset1, 260);
        ctx.lineTo(950 - mountOffset1, 430);
        ctx.lineTo(1300 - mountOffset1, 430);
        ctx.fill();

        ctx.fillStyle = '#2c0b0e';
        let mountOffset2 = (gameFrame * 0.7) % 600;
        ctx.beginPath();
        ctx.moveTo(-mountOffset2, 430);
        ctx.lineTo(130 - mountOffset2, 300);
        ctx.lineTo(320 - mountOffset2, 430);
        ctx.lineTo(520 - mountOffset2, 280);
        ctx.lineTo(750 - mountOffset2, 430);
        ctx.lineTo(1100 - mountOffset2, 430);
        ctx.fill();
    }

    let groundColor = currentBg === 0 ? '#2ed573' : (currentBg === 1 ? '#1e272e' : '#3c6382');
    let dirtColor = currentBg === 0 ? '#b8e994' : (currentBg === 1 ? '#0f171e' : '#218c74');

    ctx.fillStyle = groundColor;
    ctx.fillRect(0, 430, 1000, 15);

    ctx.fillStyle = dirtColor;
    ctx.fillRect(0, 445, 1000, 55);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
    let groundLineOffset = (gameFrame * 6) % 50;
    for (let x = -50; x < 1050; x += 50) {
        ctx.fillRect(x - groundLineOffset, 452, 25, 5);
        ctx.fillRect(x - groundLineOffset + 20, 470, 12, 5);
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
    let renderX = player.x + curWidth / 2;
    let renderY = player.y + (player.height * scale); 

    ctx.translate(renderX, renderY);

    if (player.isSliding) {
        ctx.fillStyle = suit.shirt;
        ctx.beginPath();
        ctx.ellipse(-5 * scale, -12 * scale, 25 * scale, 10 * scale, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = suit.pants;
        ctx.fillRect(-28 * scale, -10 * scale, 20 * scale, 10 * scale);

        ctx.fillStyle = "#ffdbac";
        ctx.beginPath();
        ctx.arc(18 * scale, -12 * scale, 8 * scale, 0, Math.PI * 2);
        ctx.fill();
    } else {
        let runCycle = gameFrame * 0.2;
        let isAir = player.y < 360;

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

    if (player.y >= 360) {
        if (overPit) {
            if (player.y > 430) {
                hp = 0;
            }
        } else {
            player.y = 360;
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

        let currentHeight = player.isSliding ? player.slideHeight : player.height;
        let pBox = {
            x: player.x,
            y: player.y + (player.height - currentHeight) * scale,
            width: (player.isSliding ? 55 : player.width) * scale,
            height: currentHeight * scale
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

        let currentHeight = player.isSliding ? player.slideHeight : player.height;
        let pBox = {
            x: player.x,
            y: player.y + (player.height - currentHeight) * scale,
            width: (player.isSliding ? 55 : player.width) * scale,
            height: currentHeight * scale
        };

        if (
            pBox.x < item.x + item.width &&
            pBox.x + pBox.width > item.x &&
            pBox.y < item.y + item.height &&
            pBox.y + pBox.height > item.y
        ) {
            if (item.type === 'coin') {
                sessionCoins += 3;
                totalCoins += 3;
                saveUserData();
            }
            if (item.type === 'heal') {
                hp = Math.min(100, hp + 15);
            }
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

function drawObstacle(obs) {
    ctx.save();
    let cx = obs.x + obs.width / 2;

    if (currentBg === 0) {
        if (obs.type === 'spike') {
            ctx.fillStyle = '#8e582e';
            ctx.fillRect(obs.x + 5, obs.y + 15, obs.width - 10, obs.height - 15);
            ctx.fillStyle = '#6d3f1e';
            for (let i = 0; i < 3; i++) {
                let px = obs.x + i * 13 + 3;
                ctx.beginPath();
                ctx.moveTo(px, obs.y + 15);
                ctx.lineTo(px + 6, obs.y);
                ctx.lineTo(px + 12, obs.y + 15);
                ctx.fill();
            }
        } else if (obs.type === 'saw') {
            ctx.translate(cx, obs.y + 20);
            ctx.rotate(gameFrame * 0.1);
            ctx.fillStyle = '#78e08f';
            for (let i = 0; i < 4; i++) {
                ctx.rotate(Math.PI / 2);
                ctx.beginPath();
                ctx.arc(12, 0, 8, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.fillStyle = '#38ada9';
            ctx.beginPath();
            ctx.arc(0, 0, 7, 0, Math.PI * 2);
            ctx.fill();
        } else if (obs.type === 'high_saw') {
            // 히트박스 영역(obs.y ~ obs.y + obs.height)에 맞춰서 그래픽 출력 위치 수정
            let centerY = obs.y + obs.height / 2;

            ctx.strokeStyle = '#b2bec3';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(cx, 0);
            ctx.lineTo(cx, centerY);
            ctx.stroke();

            ctx.fillStyle = '#636e72';
            ctx.shadowColor = '#2d3436';
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.arc(cx, centerY, 22, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            ctx.fillStyle = '#d63031';
            for (let a = 0; a < Math.PI * 2; a += Math.PI / 3) {
                let sx = cx + Math.cos(a) * 22;
                let sy = centerY + Math.sin(a) * 22;
                ctx.beginPath();
                ctx.arc(sx, sy, 4, 0, Math.PI * 2);
                ctx.fill();
            }
        }

    } else if (currentBg === 1) {
        if (obs.type === 'spike') {
            ctx.fillStyle = '#ff3838';
            ctx.beginPath();
            ctx.moveTo(obs.x + 5, obs.y + obs.height);
            ctx.lineTo(cx, obs.y);
            ctx.lineTo(obs.x + obs.width - 5, obs.y + obs.height);
            ctx.fill();

            ctx.fillStyle = '#fff200';
            ctx.fillRect(obs.x + 12, obs.y + 15, obs.width - 24, 6);
            ctx.shadowColor = '#ff3838';
            ctx.shadowBlur = 10;
            ctx.strokeStyle = '#ff4d4d';
            ctx.strokeRect(obs.x + 3, obs.y + obs.height - 4, obs.width - 6, 4);
            ctx.shadowBlur = 0;
        } else if (obs.type === 'saw') {
            ctx.translate(cx, obs.y + 20);
            ctx.rotate(-gameFrame * 0.2);
            ctx.fillStyle = '#17c0eb';
            ctx.shadowColor = '#17c0eb';
            ctx.shadowBlur = 12;
            ctx.beginPath();
            for (let i = 0; i < 8; i++) {
                ctx.rotate(Math.PI / 4);
                ctx.lineTo(22, 0);
                ctx.lineTo(10, 8);
            }
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(0, 0, 6, 0, Math.PI * 2);
            ctx.fill();
        } else if (obs.type === 'high_saw') {
            let centerY = obs.y + obs.height / 2;

            ctx.fillStyle = '#3d3d3d';
            ctx.fillRect(cx - 20, centerY - 10, 40, 15);
            ctx.fillStyle = '#718093';
            ctx.fillRect(cx - 12, centerY - 15, 24, 6);

            ctx.fillStyle = '#ff3838';
            ctx.shadowColor = '#ff3838';
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.arc(cx, centerY - 3, 4, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = 'rgba(255, 56, 56, 0.7)';
            ctx.fillRect(cx - 4, centerY + 5, 8, obs.height / 2);
            ctx.shadowBlur = 0;
        }

    } else if (currentBg === 2) {
        if (obs.type === 'spike') {
            ctx.fillStyle = '#2c0b0e';
            ctx.beginPath();
            ctx.moveTo(obs.x, obs.y + obs.height);
            ctx.lineTo(obs.x + 10, obs.y + 8);
            ctx.lineTo(cx, obs.y + 20);
            ctx.lineTo(obs.x + obs.width - 8, obs.y);
            ctx.lineTo(obs.x + obs.width, obs.y + obs.height);
            ctx.fill();

            ctx.fillStyle = '#ff5252';
            ctx.shadowColor = '#ff5252';
            ctx.shadowBlur = 8;
            ctx.fillRect(obs.x + 8, obs.y + 22, 6, 3);
            ctx.fillRect(obs.x + 22, obs.y + 14, 8, 3);
            ctx.shadowBlur = 0;
        } else if (obs.type === 'saw') {
            ctx.translate(cx, obs.y + 20);
            ctx.rotate(gameFrame * 0.18);
            ctx.fillStyle = '#ff726f';
            ctx.shadowColor = '#ff5252';
            ctx.shadowBlur = 15;
            ctx.beginPath();
            for (let i = 0; i < 6; i++) {
                ctx.rotate(Math.PI / 3);
                ctx.lineTo(25, 0);
                ctx.lineTo(8, 12);
            }
            ctx.fill();
            ctx.fillStyle = '#ffda79';
            ctx.beginPath();
            ctx.arc(0, 0, 8, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        } else if (obs.type === 'high_saw') {
            let centerY = obs.y + obs.height / 2;

            ctx.strokeStyle = '#ffb142';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(cx, 0);
            ctx.lineTo(cx, centerY);
            ctx.stroke();

            ctx.fillStyle = '#cc8e35';
            ctx.shadowColor = '#ff5252';
            ctx.shadowBlur = 12;
            ctx.beginPath();
            ctx.arc(cx, centerY, 22, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#ff5252';
            ctx.beginPath();
            ctx.arc(cx, centerY, 14, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }
    ctx.restore();
}

function draw() {
    drawBackground();

    pits.forEach(pit => {
        ctx.fillStyle = '#0f0f1a';
        ctx.fillRect(pit.x, 430, pit.width, 70);
        ctx.fillStyle = 'rgba(0,0,0,0.5)';
        ctx.fillRect(pit.x, 430, 5, 70);
        ctx.fillRect(pit.x + pit.width - 5, 430, 5, 70);
    });

    obstacles.forEach(obs => {
        drawObstacle(obs);
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
            ctx.save();
            ctx.translate(item.x + 15, item.y + 15);
            
            ctx.shadowColor = '#ff4757';
            ctx.shadowBlur = 12;

            ctx.fillStyle = '#a4b0be';
            ctx.fillRect(-4, -16, 8, 4);

            ctx.fillStyle = '#ffffff';
            ctx.fillRect(-6, -12, 12, 3);

            ctx.beginPath();
            ctx.arc(0, 3, 13, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            ctx.beginPath();
            let wave = Math.sin(gameFrame * 0.1) * 2;
            ctx.arc(0, 3, 11, 0.1 * Math.PI, 0.9 * Math.PI, false);
            ctx.quadraticCurveTo(0, 3 + wave, -11, 3);
            ctx.fillStyle = '#ff4757';
            ctx.fill();

            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(-4, -2, 3, 0, Math.PI * 2);
            ctx.fill();

            ctx.restore();
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
    player.y = 360;
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

components.html(game_html, height=550)
