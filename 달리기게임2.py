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
        canvas { background: #87CEEB; display: block; }
        #uiOverlay { position: absolute; top: 10px; left: 10px; right: 10px; display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: white; text-shadow: 2px 2px 4px #000; }
        .hp-bar-bg { width: 150px; height: 16px; background: #555; border: 2px solid #fff; border-radius: 8px; overflow: hidden; display: inline-block; vertical-align: middle; }
        .hp-bar-fill { width: 100%; height: 100%; background: #ff4757; transition: width 0.1s; }
        #gameOverScreen { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: none; flex-direction: column; justify-content: center; align-items: center; color: white; }
        #gameOverScreen h1 { font-size: 48px; color: #ff4757; margin-bottom: 10px; }
        #gameOverScreen button { padding: 12px 24px; font-size: 18px; background: #2ed573; border: none; color: white; border-radius: 4px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>

<div id="gameContainer">
    <canvas id="gameCanvas" width="800" height="400"></canvas>
    <div id="uiOverlay">
        <div>
            HP <div class="hp-bar-bg"><div id="hpFill" class="hp-bar-fill"></div></div>
        </div>
        <div>SCORE: <span id="scoreText">0</span> | COINS: <span id="coinText">0</span></div>
    </div>
    <div id="gameOverScreen">
        <h1>GAME OVER</h1>
        <p>최종 점수: <span id="finalScore">0</span></p>
        <button onclick="resetGame()">다시 시작</button>
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let score = 0;
let coins = 0;
let hp = 100;
let gameOver = false;
let gameFrame = 0;

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
let items = [];

window.addEventListener('keydown', (e) => {
    if (gameOver) return;
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
    let baseWidth = player.width * scale;
    let baseHeight = (player.isSliding ? 35 : player.height) * scale;
    
    let renderX = player.x + baseWidth / 2;
    let renderY = player.y + baseHeight;

    ctx.translate(renderX, renderY);

    if (player.isSliding) {
        ctx.fillStyle = "#ff4757";
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

        drawLeg(ctx, hipAngle2, kneeAngle2, scale, "#2f3542");
        drawArm(ctx, shoulderAngle2, scale, "#e1b12c");

        ctx.fillStyle = "#fbc531";
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

        drawLeg(ctx, hipAngle1, kneeAngle1, scale, "#57606f");
        drawArm(ctx, shoulderAngle1, scale, "#fbc531");
    }

    ctx.restore();
}

function update() {
    if (gameOver) return;
    gameFrame++;
    score++;

    if (gameFrame % 10 === 0) {
        hp -= 0.5;
    }

    player.vy += player.gravity;
    player.y += player.vy;

    if (player.y >= 280) {
        player.y = 280;
        player.vy = 0;
        player.jumpCount = 0;
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
            if (item.type === 'coin') coins += 1;
            if (item.type === 'heal') hp = Math.min(100, hp + 25);
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
        document.getElementById('gameOverScreen').style.display = 'flex';
    }

    document.getElementById('hpFill').style.width = Math.max(0, hp) + '%';
    document.getElementById('scoreText').innerText = score;
    document.getElementById('coinText').innerText = coins;

    spawnObjects();
}

function draw() {
    ctx.fillStyle = '#87CEEB';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#2ed573';
    ctx.fillRect(0, 350, canvas.width, 50);

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

    drawPlayer();
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

function resetGame() {
    score = 0;
    coins = 0;
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

gameLoop();
</script>
</body>
</html>
"""

components.html(game_html, height=450)
