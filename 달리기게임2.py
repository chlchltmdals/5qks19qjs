import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Dash Runner", page_icon="🏃", layout="centered")

game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; padding: 0; background-color: #222; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
        #gameContainer { position: relative; width: 800px; height: 400px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); border-radius: 8px; overflow: hidden; }
        canvas { display: block; }
        #uiOverlay { position: absolute; top: 10px; left: 10px; right: 10px; display: flex; justify-content: space-between; font-size: 16px; font-weight: bold; color: white; text-shadow: 2px 2px 4px #000; z-index: 5; }
        .hp-bar-bg { width: 140px; height: 16px; background: #555; border: 2px solid #fff; border-radius: 8px; overflow: hidden; display: inline-block; vertical-align: middle; }
        .hp-bar-fill { width: 100%; height: 100%; background: #ff4757; transition: width 0.1s; }
        
        .overlay-screen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; z-index: 10; }
        .overlay-screen h1 { font-size: 42px; color: #fbc531; margin-bottom: 15px; text-shadow: 2px 2px 4px #000; }
        .btn { padding: 10px 20px; font-size: 16px; background: #2ed573; border: none; color: white; border-radius: 6px; cursor: pointer; font-weight: bold; margin: 5px; transition: 0.2s; }
        .btn:hover { transform: scale(1.05); }
        .btn-shop { background: #e1b12c; }
        
        /* 상점 UI */
        #shopScreen { display: none; }
        .shop-container { display: flex; gap: 20px; margin-bottom: 20px; }
        .shop-box { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: center; width: 200px; }
        .shop-item { margin: 8px 0; padding: 6px; background: rgba(0,0,0,0.3); border-radius: 4px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; }
        .shop-item button { padding: 4px 8px; font-size: 12px; cursor: pointer; }
    </style>
</head>
<body>

<div id="gameContainer">
    <canvas id="gameCanvas" width="800" height="400"></canvas>
    
    <div id="uiOverlay">
        <div>
            HP <div class="hp-bar-bg"><div id="hpFill" class="hp-bar-fill"></div></div>
        </div>
        <div>SCORE: <span id="scoreText">0</span> | COINS: <span id="coinText">0</span> (누적: <span id="totalCoinText">0</span>)</div>
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
        <p>보유 누적 코인: <span id="shopCoinText">0</span></p>
        <div class="shop-container">
            <!-- 배경 선택 -->
            <div class="shop-box">
                <h3>배경 테마</h3>
                <div class="shop-item">
                    <span>낮 (기본)</span>
                    <button id="bg0" onclick="selectBg(0)">선택</button>
                </div>
                <div class="shop-item">
                    <span>밤 (50코인)</span>
                    <button id="bg1" onclick="buyOrSelectBg(1, 50)">구매</button>
                </div>
                <div class="shop-item">
                    <span>석양 (100코인)</span>
                    <button id="bg2" onclick="buyOrSelectBg(2, 100)">구매</button>
                </div>
            </div>
            <!-- 수트 선택 -->
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
        <h1 style="color: #ff4757;">GAME OVER</h1>
        <p>최종 점수: <span id="finalScore">0</span> | 획득 코인: <span id="finalCoins">0</span></p>
        <div>
            <button class="btn" onclick="resetGame()">다시 시작</button>
            <button class="btn btn-shop" onclick="returnToMenu()">메인 메뉴</button>
        </div>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// 커스텀 데이터 & 저장 (로컬스토리지)
let totalCoins = parseInt(localStorage.getItem('dash_totalCoins')) || 0;
let unlockedBgs = JSON.parse(localStorage.getItem('dash_unlockedBgs')) || [true, false, false];
let unlockedSuits = JSON.parse(localStorage.getItem('dash_unlockedSuits')) || [true, false, false];
let currentBg = parseInt(localStorage.getItem('dash_currentBg')) || 0;
let currentSuit = parseInt(localStorage.getItem('dash_currentSuit')) || 0;

// 색상 데이터
const bgStyles = [
    { sky: '#87CEEB', ground: '#2ed573' }, // 낮
    { sky: '#1e272e', ground: '#05c46b' }, // 밤
    { sky: '#e15f41', ground: '#57606f' }  // 석양
];

const suitColors = [
    { shirt: '#fbc531', sleeve: '#e1b12c', pants: '#2f3542', legFront: '#57606f' }, // 옐로우
    { shirt: '#00a8ff', sleeve: '#0097e6', pants: '#192a56', legFront: '#273c75' }, // 블루
    { shirt: '#e84118', sleeve: '#c23616', pants: '#2f3542', legFront: '#3d3d3d' }  // 레드
];

// 게임 상태
let score = 0;
let sessionCoins = 0;
let hp = 100;
let gameOver = false;
let gameRunning = false;
let gameFrame = 0;

// 캐릭터 상태
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
    invincibleTimer: 0, // 거대화 종료 후 1초 무적 (60프레임)
    isGiant: false
};

let obstacles = [];
let items = [];

// 키 입력
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

    // 배경 버튼
    for(let i=0; i<3; i++) {
        let btn = document.getElementById('bg' + i);
        if(currentBg === i) {
            btn.innerText = "착용중"; btn.disabled = true;
        } else if(unlockedBgs[i]) {
            btn.innerText = "선택"; btn.disabled = false;
        } else {
            btn.innerText = "구매"; btn.disabled = false;
        }
    }

    // 수트 버튼
    for(let i=0; i<3; i++) {
        let btn = document.getElementById('suit' + i);
        if(currentSuit === i) {
            btn.innerText = "착용중"; btn.disabled = true;
        } else if(unlockedSuits[i]) {
            btn.innerText = "선택"; btn.disabled = false;
        } else {
            btn.innerText = "구매"; btn.disabled = false;
        }
    }
}

function selectBg(idx) { currentBg = idx; saveUserData(); updateShopUI(); }
function buyOrSelectBg(idx, cost) {
    if(unlockedBgs[idx]) { selectBg(idx); }
    else if(totalCoins >= cost) {
        totalCoins -= cost; unlockedBgs[idx] = true; selectBg(idx);
    } else { alert("코인이 부족합니다!"); }
}

function selectSuit(idx) { currentSuit = idx; saveUserData(); updateShopUI(); }
function buyOrSelectSuit(idx, cost) {
    if(unlockedSuits[idx]) { selectSuit(idx); }
    else if(totalCoins >= cost) {
        totalCoins -= cost; unlockedSuits[idx] = true; selectSuit(idx);
    } else { alert("코인이 부족합니다!"); }
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
    if (gameFrame % 120 === 0) {
        let type = Math.random() < 0.5 ? 'saw' : 'spike';
        obstacles.push({
            x: 800,
            y: type === 'saw' ? 260 : 310,
            width: 40,
            height: 40,
            type: type
        });
    }

    if (gameFrame % 180 === 0) {
        let rand = Math.random();
        let itemType = rand < 0.6 ? 'coin' : (rand < 0.85 ? 'heal' : 'giant');
        items.push({
            x: 800,
            y: itemType === 'coin' ? 220 + Math.random() * 60 : 250,
            width: 25,
            height: 25,
            type: itemType
        });
    }
}

// 다리 그리기
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

// 팔 그리기
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

// 캐릭터 그리기 (자연스러운 달리기 + 수트)
function drawPlayer() {
    ctx.save();
    
    // 무적 상태 시 깜빡임
    if (player.invincibleTimer > 0 && Math.floor(player.invincibleTimer / 5) % 2 === 0) {
        ctx.globalAlpha = 0.4;
    }

    let scale = player.isGiant ? 1.6 : 1.0;
    let suit = suitColors[currentSuit];
    
    let baseWidth = player.width * scale;
    let baseHeight = (player.isSliding ? 35 : player.height) * scale;
    
    let renderX = player.x + baseWidth / 2;
    let renderY = player.y + baseHeight;

    ctx.translate(renderX, renderY);

    if (player.isSliding) {
        ctx.fillStyle = suit.shirt;
        ctx.beginPath();
        ctx.ellipse(-10, -15, 30 * scale, 15 * scale, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#ffdbac";
        ctx.beginPath();
        ctx.arc(15 * scale, -20 * scale, 10 * scale, 0, Math.PI * 2);
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

        // 뒷다리 & 왼팔
        drawLeg(ctx, hipAngle2, kneeAngle2, scale, suit.pants);
        drawArm(ctx, shoulderAngle2, scale, suit.sleeve);

        // 몸통 & 의상
        ctx.fillStyle = suit.shirt;
        ctx.fillRect(-10 * scale, -52 * scale, 20 * scale, 26 * scale);
        ctx.fillStyle = "#2f3542";
        ctx.fillRect(-10 * scale, -28 * scale, 20 * scale, 4 * scale);

        // 머리 & 얼굴
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

        // 앞다리 & 오른팔
        drawLeg(ctx, hipAngle1, kneeAngle1, scale, suit.legFront);
        drawArm(ctx, shoulderAngle1, scale, suit.shirt);
    }

    ctx.restore();
}

function update() {
    if (!gameRunning || gameOver) return;
    gameFrame++;
    score++;

    // 시간 경과 체력 감소
    if (gameFrame % 10 === 0) {
        hp -= 0.5;
    }

    // 물리 엔진
    player.vy += player.gravity;
    player.y += player.vy;

    if (player.y >= 280) {
        player.y = 280;
        player.vy = 0;
        player.jumpCount = 0;
    }

    // 거대화 및 무적 타이머
    if (player.giantTimer > 0) {
        player.giantTimer--;
        if (player.giantTimer === 0) {
            player.isGiant = false;
            player.invincibleTimer = 60; // 거대화 풀린 후 1초간(60프레임) 무적!
        }
    }

    if (player.invincibleTimer > 0) {
        player.invincibleTimer--;
    }

    // 장애물 이동 및 충돌
    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= 6;

        let hitWidth = player.isGiant ? player.width * 1.6 : player.width;
        let hitHeight = player.isGiant ? player.height * 1.6 : (player.isSliding ? 35 : player.height);

        if (
            player.x < obs.x + obs.width &&
            player.x + hitWidth > obs.x &&
            player.y < obs.y + obs.height &&
            player.y + hitHeight > obs.y
        ) {
            if (player.isGiant) {
                obstacles.splice(i, 1);
                score += 50;
            } else if (player.invincibleTimer === 0) {
                // 데미지 20 감소
                hp -= 20;
                obstacles.splice(i, 1);
            }
        }

        if (obs && obs.x + obs.width < 0) {
            obstacles.splice(i, 1);
        }
    }

    // 아이템 이동 및 획득
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
            if (item.type === 'heal') hp = Math.min(100, hp + 25);
            if (item.type === 'giant') {
                player.isGiant = true;
                player.giantTimer = 300; // 5초
            }
            items.splice(i, 1);
        } else if (item.x + item.width < 0) {
            items.splice(i, 1);
        }
    }

    // 게임 오버
    if (hp <= 0) {
        hp = 0;
        gameOver = true;
        document.getElementById('finalScore').innerText = score;
        document.getElementById('finalCoins').innerText = sessionCoins;
        document.getElementById('gameOverScreen').style.display = 'flex';
    }

    // UI 업데이트
    document.getElementById('hpFill').style.width = Math.max(0, hp) + '%';
    document.getElementById('scoreText').innerText = score;
    document.getElementById('coinText').innerText = sessionCoins;
    document.getElementById('totalCoinText').innerText = totalCoins;

    spawnObjects();
}

function draw() {
    let style = bgStyles[currentBg];

    // 배경 테마
    ctx.fillStyle = style.sky;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 바닥 테마
    ctx.fillStyle = style.ground;
    ctx.fillRect(0, 350, canvas.width, 50);

    // 장애물 그리기
    obstacles.forEach(obs => {
        if (obs.type === 'saw') {
            ctx.fillStyle = '#a4b0be';
            ctx.beginPath();
            ctx.arc(obs.x + 20, obs.y + 20, 20, 0, Math.PI * 2);
            ctx.fill();
        } else {
            ctx.fillStyle = '#ff4757';
            ctx.beginPath();
            ctx.moveTo(obs.x, obs.y + obs.height);
            ctx.lineTo(obs.x + obs.width / 2, obs.y);
            ctx.lineTo(obs.x + obs.width, obs.y + obs.height);
            ctx.closePath();
            ctx.fill();
        }
    });

    // 아이템 그리기
    items.forEach(item => {
        if (item.type === 'coin') {
            ctx.fillStyle = '#eccc68';
            ctx.beginPath();
            ctx.arc(item.x + 12, item.y + 12, 10, 0, Math.PI * 2);
            ctx.fill();
        } else if (item.type === 'heal') {
            ctx.fillStyle = '#ff6b81';
            ctx.fillRect(item.x, item.y, item.width, item.height);
        } else if (item.type === 'giant') {
            ctx.fillStyle = '#70a1ff';
            ctx.beginPath();
            ctx.arc(item.x + 12, item.y + 12, 12, 0, Math.PI * 2);
            ctx.fill();
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
    items = [];
    document.getElementById('gameOverScreen').style.display = 'none';
}

updateShopUI();
gameLoop();
</script>
</body>
</html>
"""

components.html(game_html, height=450)
