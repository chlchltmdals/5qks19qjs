import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="대시 러너: 익스트림", page_icon="🏃", layout="centered")

st.title("🏃 Dash Runner: Extreme Mode")

game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #111;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: white;
            user-select: none;
        }
        #gameCanvas {
            border: 4px solid #444;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.8);
            background: #000;
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="700" height="350"></canvas>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        let totalCoins = parseInt(localStorage.getItem("dash_runner_total_coins")) || 0;
        let unlockedBgs = JSON.parse(localStorage.getItem("dash_runner_unlocked_bgs")) || [0, 1, 2];
        let unlockedRunners = JSON.parse(localStorage.getItem("dash_runner_unlocked_runners")) || [0, 1, 2];

        // 배경 & 캐릭터 데이터
        const bgThemes = [
            { name: "네온 시티 🏙️", sky: ["#0f0c29", "#302b63", "#24243e"], ground: "#161625", top: "#00f2fe", price: 0 },
            { name: "용암 지대 🌋", sky: ["#200101", "#4a0e0e", "#8a2387"], ground: "#1c0a0a", top: "#ff3300", price: 0 },
            { name: "폐공장 🏭", sky: ["#0f2027", "#203a43", "#2c5364"], ground: "#0b141a", top: "#ffd700", price: 0 },
            { name: "사이보그 랩 🧪", sky: ["#001100", "#003311", "#005522"], ground: "#001a08", top: "#00ff66", price: 150 },
            { name: "네온 우주 🌌", sky: ["#03001e", "#7303c0", "#ec38bc"], ground: "#0a001a", top: "#00ffff", price: 300 },
            { name: "초시공 차원 🔮", sky: ["#14002e", "#31005f", "#6a00a8"], ground: "#0c001c", top: "#e040fb", price: 500 }
        ];

        const runnerThemes = [
            { name: "네온 아머 🏃", skin: "#66FCF1", suit: "#1F2833", eye: "#000", price: 0 },
            { name: "샤이니 스파크 ⚡", skin: "#FFD700", suit: "#FF4500", eye: "#000", price: 0 },
            { name: "섀도우 에이전트 🥷", skin: "#E0E0E0", suit: "#FF0055", eye: "#000", price: 0 },
            { name: "골든 타이탄 🏆", skin: "#FFF", suit: "#FFD700", eye: "#000", price: 200 },
            { name: "크리스탈 파사드 🧊", skin: "#E0F7FA", suit: "#00E5FF", eye: "#000", price: 350 },
            { name: "인페르노 스파크 🔥", skin: "#FFD700", suit: "#D50000", eye: "#000", price: 600 }
        ];

        let selectedBgIdx = 0;
        let selectedRunnerIdx = 0;

        let gameState = 'START';
        let score = 0;
        let coins = 0;
        let frameCount = 0;
        let sawRotation = 0;
        let nextSpawnFrame = 60;

        // 체력 및 아이템 상태 변수
        let hp = 100;
        const maxHp = 100;
        let giantTimer = 0; // 거대화 지속 시간 타이머

        const groundY = 280;
        const NORMAL_HEIGHT = 60;
        const SLIDE_HEIGHT = 30;

        const runner = {
            x: 80,
            y: groundY - NORMAL_HEIGHT,
            width: 34,
            height: NORMAL_HEIGHT,
            dy: 0,
            gravity: 0.65,
            jumpPower: -12,
            jumpCount: 0,
            maxJumps: 2,
            isSliding: false
        };

        const obstacles = [];
        const coinItems = [];
        const potions = []; // 물약 목록 (회복 & 거대화)
        const pits = [];
        const stars = Array.from({length: 30}, () => ({
            x: Math.random() * 700,
            y: Math.random() * 200,
            size: Math.random() * 2 + 1,
            alpha: Math.random()
        }));

        const keys = {};

        const buttons = {
            bgPrev: { x: 180, y: 125, w: 35, h: 32 },
            bgNext: { x: 470, y: 125, w: 35, h: 32 },
            bgBuy: { x: 515, y: 125, w: 90, h: 32 },
            runnerPrev: { x: 180, y: 175, w: 35, h: 32 },
            runnerNext: { x: 470, y: 175, w: 35, h: 32 },
            runnerBuy: { x: 515, y: 175, w: 90, h: 32 },
            play: { x: 260, y: 250, w: 180, h: 50 }
        };

        const gameOverButtons = {
            retry: { x: 180, y: 240, w: 150, h: 45 },
            menu: { x: 370, y: 240, w: 150, h: 45 }
        };

        function saveStorage() {
            localStorage.setItem("dash_runner_total_coins", totalCoins);
            localStorage.setItem("dash_runner_unlocked_bgs", JSON.stringify(unlockedBgs));
            localStorage.setItem("dash_runner_unlocked_runners", JSON.stringify(unlockedRunners));
        }

        window.addEventListener("keydown", function (e) {
            if (["Space", "ArrowDown", "KeyS", "ArrowUp", "KeyM"].includes(e.code)) {
                e.preventDefault();
            }
            keys[e.code] = true;

            if (gameState === 'PLAYING' && (e.code === "Space" || e.code === "ArrowUp")) {
                jump();
            } else if (gameState === 'GAMEOVER') {
                if (e.code === "Space") {
                    resetGame();
                } else if (e.code === "KeyM") {
                    gameState = 'START';
                }
            }
        });

        window.addEventListener("keyup", function (e) {
            keys[e.code] = false;
        });

        canvas.addEventListener("click", function (e) {
            const rect = canvas.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const clickY = e.clientY - rect.top;

            if (gameState === 'START') {
                handleStartMenuClick(clickX, clickY);
            } else if (gameState === 'PLAYING') {
                jump();
            } else if (gameState === 'GAMEOVER') {
                handleGameOverClick(clickX, clickY);
            }
        });

        function handleStartMenuClick(x, y) {
            if (isInside(x, y, buttons.bgPrev)) {
                selectedBgIdx = (selectedBgIdx - 1 + bgThemes.length) % bgThemes.length;
            } else if (isInside(x, y, buttons.bgNext)) {
                selectedBgIdx = (selectedBgIdx + 1) % bgThemes.length;
            } else if (isInside(x, y, buttons.bgBuy)) {
                const item = bgThemes[selectedBgIdx];
                if (!unlockedBgs.includes(selectedBgIdx) && totalCoins >= item.price) {
                    totalCoins -= item.price;
                    unlockedBgs.push(selectedBgIdx);
                    saveStorage();
                }
            } else if (isInside(x, y, buttons.runnerPrev)) {
                selectedRunnerIdx = (selectedRunnerIdx - 1 + runnerThemes.length) % runnerThemes.length;
            } else if (isInside(x, y, buttons.runnerNext)) {
                selectedRunnerIdx = (selectedRunnerIdx + 1) % runnerThemes.length;
            } else if (isInside(x, y, buttons.runnerBuy)) {
                const item = runnerThemes[selectedRunnerIdx];
                if (!unlockedRunners.includes(selectedRunnerIdx) && totalCoins >= item.price) {
                    totalCoins -= item.price;
                    unlockedRunners.push(selectedRunnerIdx);
                    saveStorage();
                }
            } else if (isInside(x, y, buttons.play)) {
                if (unlockedBgs.includes(selectedBgIdx) && unlockedRunners.includes(selectedRunnerIdx)) {
                    startGame();
                }
            }
        }

        function handleGameOverClick(x, y) {
            if (isInside(x, y, gameOverButtons.retry)) {
                resetGame();
            } else if (isInside(x, y, gameOverButtons.menu)) {
                gameState = 'START';
            }
        }

        function isInside(x, y, btn) {
            return x >= btn.x && x <= btn.x + btn.w && y >= btn.y && y <= btn.y + btn.h;
        }

        function jump() {
            if (runner.isSliding) return;
            if (runner.jumpCount < runner.maxJumps) {
                runner.dy = runner.jumpPower;
                runner.jumpCount++;
            }
        }

        function startGame() {
            gameState = 'PLAYING';
            resetGameData();
        }

        function resetGame() {
            gameState = 'PLAYING';
            resetGameData();
        }

        function resetGameData() {
            score = 0;
            coins = 0;
            frameCount = 0;
            nextSpawnFrame = 60;
            hp = maxHp;
            giantTimer = 0;
            obstacles.length = 0;
            coinItems.length = 0;
            potions.length = 0;
            pits.length = 0;
            runner.height = NORMAL_HEIGHT;
            runner.y = groundY - NORMAL_HEIGHT;
            runner.dy = 0;
            runner.jumpCount = 0;
            runner.isSliding = false;
        }

        function spawnRandomElement() {
            const rand = Math.random();

            if (rand < 0.35) {
                obstacles.push({
                    x: canvas.width,
                    y: groundY - 28,
                    width: 45,
                    height: 28,
                    type: "single_jump_spike"
                });
            } else if (rand < 0.65) {
                obstacles.push({
                    x: canvas.width,
                    y: groundY - 45,
                    width: 200,
                    height: 45,
                    type: "double_jump_saw"
                });
            } else if (rand < 0.85) {
                obstacles.push({
                    x: canvas.width,
                    y: 0,
                    width: 60,
                    height: groundY - SLIDE_HEIGHT,
                    type: "spike_ceiling"
                });
            } else {
                pits.push({
                    x: canvas.width,
                    width: 90
                });
            }

            nextSpawnFrame = frameCount + Math.floor(Math.random() * 70) + 60;
        }

        function spawnCoin() {
            const coinY = groundY - (Math.floor(Math.random() * 3) + 1) * 45;
            coinItems.push({
                x: canvas.width,
                y: coinY,
                radius: 12
            });
        }

        // 물약 스폰 (회복 물약 70%, 거대화 물약 30%)
        function spawnPotion() {
            const potionY = groundY - (Math.floor(Math.random() * 2) + 1) * 50;
            const type = Math.random() < 0.7 ? "heal" : "giant";
            potions.push({
                x: canvas.width,
                y: potionY,
                width: 22,
                height: 30,
                type: type
            });
        }

        function triggerGameOver() {
            totalCoins += coins;
            saveStorage();
            gameState = 'GAMEOVER';
        }

        function update() {
            if (gameState !== 'PLAYING') return;

            frameCount++;
            score++;
            sawRotation += 0.2;

            // 1. 시간 지남에 따른 체력 감소 (약 1초당 3.5 HP 감소)
            hp -= 0.06;
            if (hp <= 0) {
                hp = 0;
                triggerGameOver();
                return;
            }

            // 2. 거대화 타이머 감소
            if (giantTimer > 0) {
                giantTimer--;
            }

            // 거대화 유무에 따른 크기/높이 조정
            const scale = giantTimer > 0 ? 1.8 : 1.0;
            const currentNormalHeight = NORMAL_HEIGHT * scale;
            const currentSlideHeight = SLIDE_HEIGHT * scale;
            const currentWidth = 34 * scale;

            runner.width = currentWidth;

            const isDownPressed = keys["ArrowDown"] || keys["KeyS"];
            
            let overPit = false;
            const runnerFootX = runner.x + runner.width / 2;
            pits.forEach(p => {
                if (runnerFootX > p.x && runnerFootX < p.x + p.width) {
                    overPit = true;
                }
            });

            if (isDownPressed && (runner.y + runner.height >= groundY - 1) && !overPit) {
                if (!runner.isSliding) {
                    runner.isSliding = true;
                    runner.height = currentSlideHeight;
                    runner.y = groundY - currentSlideHeight;
                }
            } else {
                if (runner.isSliding) {
                    runner.isSliding = false;
                    runner.height = currentNormalHeight;
                    runner.y = groundY - currentNormalHeight;
                } else if (giantTimer > 0 && runner.height !== currentNormalHeight && runner.y + runner.height >= groundY) {
                    runner.height = currentNormalHeight;
                    runner.y = groundY - currentNormalHeight;
                }
            }

            runner.dy += runner.gravity;
            runner.y += runner.dy;

            if (!overPit && runner.y + runner.height >= groundY) {
                runner.y = groundY - runner.height;
                runner.dy = 0;
                runner.jumpCount = 0;
            }

            if (runner.y > canvas.height) {
                triggerGameOver();
            }

            // 객체 생성
            if (frameCount >= nextSpawnFrame) spawnRandomElement();
            if (frameCount % 45 === 0) spawnCoin();
            if (frameCount % 180 === 0) spawnPotion(); // 3초마다 물약 스폰 시도

            // 낭떨어지 이동
            for (let i = pits.length - 1; i >= 0; i--) {
                pits[i].x -= 7.5;
                if (pits[i].x + pits[i].width < 0) pits.splice(i, 1);
            }

            // 장애물 이동 및 충돌
            for (let i = obstacles.length - 1; i >= 0; i--) {
                const obs = obstacles[i];
                obs.x -= 7.5;

                if (
                    runner.x < obs.x + obs.width &&
                    runner.x + runner.width > obs.x &&
                    runner.y < obs.y + obs.height &&
                    runner.y + runner.height > obs.y
                ) {
                    if (giantTimer > 0) {
                        // 💥 거대화 상태면 장애물 파괴!
                        obstacles.splice(i, 1);
                        score += 100;
                    } else {
                        triggerGameOver();
                    }
                } else if (obs.x + obs.width < 0) {
                    obstacles.splice(i, 1);
                }
            }

            // 코인 습득
            for (let i = coinItems.length - 1; i >= 0; i--) {
                const c = coinItems[i];
                c.x -= 7.5;

                const distX = (runner.x + runner.width / 2) - c.x;
                const distY = (runner.y + runner.height / 2) - c.y;
                if (Math.sqrt(distX * distX + distY * distY) < runner.width / 2 + c.radius) {
                    coins += 10;
                    score += 50;
                    coinItems.splice(i, 1);
                } else if (c.x + c.radius < 0) {
                    coinItems.splice(i, 1);
                }
            }

            // 물약 습득
            for (let i = potions.length - 1; i >= 0; i--) {
                const p = potions[i];
                p.x -= 7.5;

                if (
                    runner.x < p.x + p.width &&
                    runner.x + runner.width > p.x &&
                    runner.y < p.y + p.height &&
                    runner.y + runner.height > p.y
                ) {
                    if (p.type === "heal") {
                        hp = Math.min(maxHp, hp + 25); // 체력 +25 회복
                    } else if (p.type === "giant") {
                        giantTimer = 300; // 약 5초간 거대화
                    }
                    potions.splice(i, 1);
                } else if (p.x + p.width < 0) {
                    potions.splice(i, 1);
                }
            }
        }

        // -------------------------------------------------------------------
        // 렌더링
        // -------------------------------------------------------------------
        function drawBackground() {
            const currentBg = bgThemes[selectedBgIdx];
            
            const grad = ctx.createLinearGradient(0, 0, 0, groundY);
            grad.addColorStop(0, currentBg.sky[0]);
            grad.addColorStop(0.5, currentBg.sky[1]);
            grad.addColorStop(1, currentBg.sky[2]);
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = "#FFF";
            stars.forEach(s => {
                ctx.globalAlpha = (Math.sin(frameCount * 0.05 + s.alpha * 10) + 1) / 2;
                ctx.fillRect(s.x, s.y, s.size, s.size);
            });
            ctx.globalAlpha = 1.0;

            ctx.fillStyle = "rgba(0, 0, 0, 0.25)";
            ctx.beginPath();
            ctx.moveTo(0, groundY);
            for (let x = 0; x <= canvas.width; x += 50) {
                ctx.lineTo(x, groundY - 20 - Math.sin(x * 0.01) * 15);
            }
            ctx.lineTo(canvas.width, groundY);
            ctx.fill();

            ctx.fillStyle = currentBg.ground;
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);

            pits.forEach(p => {
                ctx.clearRect(p.x, groundY, p.width, canvas.height - groundY);
                const pGrad = ctx.createLinearGradient(0, groundY, 0, canvas.height);
                pGrad.addColorStop(0, "rgba(0,0,0,0.8)");
                pGrad.addColorStop(1, "#000");
                ctx.fillStyle = pGrad;
                ctx.fillRect(p.x, groundY, p.width, canvas.height - groundY);
            });

            ctx.fillStyle = currentBg.top;
            let currentX = 0;
            const sortedPits = [...pits].sort((a,b) => a.x - b.x);
            
            sortedPits.forEach(p => {
                if (p.x > currentX) {
                    ctx.fillRect(currentX, groundY, p.x - currentX, 6);
                }
                currentX = Math.max(currentX, p.x + p.width);
            });
            if (currentX < canvas.width) {
                ctx.fillRect(currentX, groundY, canvas.width - currentX, 6);
            }
        }

        function drawHumanRunner() {
            const theme = runnerThemes[selectedRunnerIdx];
            const isGiant = giantTimer > 0;
            const scale = isGiant ? 1.8 : 1.0;

            const rx = runner.x + (17 * scale);
            const ry = runner.y;

            ctx.save();

            // 거대화 오라 효과
            if (isGiant) {
                ctx.shadowColor = "#D500F9";
                ctx.shadowBlur = 15;
            }

            if (runner.isSliding) {
                ctx.fillStyle = theme.skin;
                ctx.beginPath();
                ctx.arc(rx + (20 * scale), ry + (12 * scale), 11 * scale, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = "#000";
                ctx.beginPath();
                ctx.arc(rx + (24 * scale), ry + (10 * scale), 3 * scale, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = theme.suit;
                ctx.beginPath();
                ctx.roundRect(rx - (15 * scale), ry + (12 * scale), 28 * scale, 14 * scale, 6 * scale);
                ctx.fill();

                ctx.strokeStyle = theme.suit;
                ctx.lineWidth = 8 * scale;
                ctx.lineCap = "round";
                ctx.beginPath();
                ctx.moveTo(rx - (12 * scale), ry + (20 * scale));
                ctx.lineTo(rx - (28 * scale), ry + (26 * scale));
                ctx.stroke();

            } else {
                const swing = Math.sin(frameCount * 0.28) * (16 * scale);

                ctx.lineCap = "round";

                // 뒷다리 & 뒷팔
                ctx.strokeStyle = theme.suit;
                ctx.lineWidth = 7 * scale;
                if (runner.jumpCount === 0) {
                    ctx.beginPath();
                    ctx.moveTo(rx, ry + (36 * scale));
                    ctx.lineTo(rx - swing, ry + (48 * scale));
                    ctx.lineTo(rx - swing * 1.2, ry + (58 * scale));
                    ctx.stroke();
                }

                ctx.strokeStyle = theme.skin;
                ctx.lineWidth = 5.5 * scale;
                ctx.beginPath();
                ctx.moveTo(rx, ry + (22 * scale));
                ctx.lineTo(rx + swing * 0.8, ry + (33 * scale));
                ctx.stroke();

                // 몸통 및 머리
                ctx.fillStyle = theme.suit;
                ctx.beginPath();
                ctx.roundRect(rx - (9 * scale), ry + (18 * scale), 18 * scale, 22 * scale, 6 * scale);
                ctx.fill();

                ctx.fillStyle = theme.skin;
                ctx.beginPath();
                ctx.arc(rx, ry + (10 * scale), 11 * scale, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = theme.eye;
                ctx.beginPath();
                ctx.arc(rx + (5 * scale), ry + (9 * scale), 2.5 * scale, 0, Math.PI * 2);
                ctx.fill();

                // 앞다리 & 앞팔
                ctx.strokeStyle = theme.suit;
                ctx.lineWidth = 8 * scale;
                if (runner.jumpCount > 0) {
                    ctx.beginPath();
                    ctx.moveTo(rx - (4 * scale), ry + (38 * scale));
                    ctx.lineTo(rx - (12 * scale), ry + (48 * scale));
                    ctx.lineTo(rx - (6 * scale), ry + (58 * scale));

                    ctx.moveTo(rx + (4 * scale), ry + (38 * scale));
                    ctx.lineTo(rx + (14 * scale), ry + (48 * scale));
                    ctx.lineTo(rx + (8 * scale), ry + (58 * scale));
                    ctx.stroke();
                } else {
                    ctx.beginPath();
                    ctx.moveTo(rx, ry + (36 * scale));
                    ctx.lineTo(rx + swing, ry + (48 * scale));
                    ctx.lineTo(rx + swing * 1.2, ry + (58 * scale));
                    ctx.stroke();
                }

                ctx.strokeStyle = theme.skin;
                ctx.lineWidth = 6 * scale;
                ctx.beginPath();
                ctx.moveTo(rx, ry + (22 * scale));
                ctx.lineTo(rx - swing * 0.8, ry + (33 * scale));
                ctx.stroke();
            }

            ctx.restore();
        }

        function drawPotions() {
            potions.forEach(p => {
                ctx.save();
                if (p.type === "heal") {
                    // 회복 물약 (초록색)
                    ctx.fillStyle = "#00E676";
                    ctx.shadowColor = "#00E676";
                } else {
                    // 거대화 물약 (보라색)
                    ctx.fillStyle = "#D500F9";
                    ctx.shadowColor = "#D500F9";
                }
                ctx.shadowBlur = 10;

                // 물약 병 모형
                ctx.beginPath();
                ctx.fillRect(p.x + 6, p.y, 10, 6); // 병 입구
                ctx.roundRect(p.x, p.y + 6, p.width, p.height - 6, 6); // 병 몸통
                ctx.fill();

                // 텍스트 라벨
                ctx.fillStyle = "#FFF";
                ctx.font = "bold 11px Arial";
                ctx.textAlign = "center";
                ctx.fillText(p.type === "heal" ? "HP" : "BIG", p.x + p.width / 2, p.y + 22);

                ctx.restore();
            });
        }

        function drawDangerousObstacles() {
            obstacles.forEach(obs => {
                if (obs.type === "single_jump_spike") {
                    ctx.fillStyle = "#FF9100";
                    ctx.beginPath();
                    ctx.moveTo(obs.x, obs.y + obs.height);
                    ctx.lineTo(obs.x + obs.width / 2, obs.y);
                    ctx.lineTo(obs.x + obs.width, obs.y + obs.height);
                    ctx.fill();

                } else if (obs.type === "double_jump_saw") {
                    const sawCount = 3;
                    const radius = 22;
                    const spacing = obs.width / sawCount;

                    for (let i = 0; i < sawCount; i++) {
                        const cx = obs.x + radius + (i * spacing);
                        const cy = obs.y + radius;

                        ctx.save();
                        ctx.translate(cx, cy);
                        ctx.rotate(sawRotation + i);

                        ctx.fillStyle = "#FF1744";
                        ctx.beginPath();
                        for (let j = 0; j < 8; j++) {
                            const angle = (j * Math.PI) / 4;
                            ctx.lineTo(Math.cos(angle) * radius, Math.sin(angle) * radius);
                            const innerAngle = angle + Math.PI / 8;
                            ctx.lineTo(Math.cos(innerAngle) * (radius - 8), Math.sin(innerAngle) * (radius - 8));
                        }
                        ctx.closePath();
                        ctx.fill();

                        ctx.fillStyle = "#FFF";
                        ctx.beginPath();
                        ctx.arc(0, 0, 5, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.restore();
                    }

                } else if (obs.type === "spike_ceiling") {
                    ctx.fillStyle = "#D500F9";
                    ctx.fillRect(obs.x, 0, obs.width, obs.height - 15);

                    const spikeWidth = 10;
                    const numSpikes = obs.width / spikeWidth;

                    ctx.beginPath();
                    for (let i = 0; i < numSpikes; i++) {
                        const sx = obs.x + (i * spikeWidth);
                        ctx.moveTo(sx, obs.height - 15);
                        ctx.lineTo(sx + spikeWidth / 2, obs.height);
                        ctx.lineTo(sx + spikeWidth + 0.5, obs.height - 15);
                    }
                    ctx.fill();
                }
            });
        }

        // 체력바 렌더링
        function drawUI() {
            // 체력바 틀
            ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
            ctx.fillRect(20, 15, 160, 18);
            ctx.strokeStyle = "#FFF";
            ctx.lineWidth = 1.5;
            ctx.strokeRect(20, 15, 160, 18);

            // 체력 게이지 (체력 양에 따라 색상 변경)
            const hpWidth = (hp / maxHp) * 156;
            ctx.fillStyle = hp > 30 ? "#00E676" : "#FF1744";
            ctx.fillRect(22, 17, Math.max(0, hpWidth), 14);

            // 체력 텍스트
            ctx.fillStyle = "#FFF";
            ctx.font = "bold 11px Arial";
            ctx.textAlign = "center";
            ctx.fillText(`HP: ${Math.ceil(hp)} / ${maxHp}`, 100, 28);

            // 거대화 상태 표시
            if (giantTimer > 0) {
                ctx.fillStyle = "#D500F9";
                ctx.font = "bold 14px Arial";
                ctx.fillText(`⚡ GIANT MODE! (${Math.ceil(giantTimer / 60)}s)`, 100, 50);
            }

            // 점수 및 코인 표시
            ctx.textAlign = "left";
            ctx.font = "bold 16px Arial";
            ctx.fillText(`Score: ${score}`, 530, 30);
            ctx.fillText(`Coins: 🟡 +${coins}`, 530, 55);
        }

        function drawStartMenu() {
            drawBackground();

            ctx.fillStyle = "rgba(0, 0, 0, 0.78)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = "#FF1744";
            ctx.font = "bold 32px Arial";
            ctx.textAlign = "center";
            ctx.fillText("⚡ DASH RUNNER: EXTREME ⚡", canvas.width / 2, 48);

            ctx.fillStyle = "#FFD700";
            ctx.font = "bold 16px Arial";
            ctx.fillText(`💰 보유 코인: ${totalCoins} G`, canvas.width / 2, 82);

            ctx.textAlign = "left";
            drawSelector("스테이지", bgThemes, selectedBgIdx, unlockedBgs, 125, buttons.bgPrev, buttons.bgNext, buttons.bgBuy);
            drawSelector("러너 수트", runnerThemes, selectedRunnerIdx, unlockedRunners, 175, buttons.runnerPrev, buttons.runnerNext, buttons.runnerBuy);

            const btn = buttons.play;
            const isBgUnlocked = unlockedBgs.includes(selectedBgIdx);
            const isRunnerUnlocked = unlockedRunners.includes(selectedRunnerIdx);
            const canStart = isBgUnlocked && isRunnerUnlocked;

            ctx.fillStyle = canStart ? "#FF1744" : "#555";
            ctx.beginPath();
            ctx.roundRect(btn.x, btn.y, btn.w, btn.h, 12);
            ctx.fill();
            if (canStart) {
                ctx.strokeStyle = "#FFF";
                ctx.lineWidth = 3;
                ctx.stroke();
            }

            ctx.fillStyle = "#FFF";
            ctx.font = "bold 22px Arial";
            ctx.textAlign = "center";
            ctx.fillText(canStart ? "▶ START" : "🔒 구매 후 시작 가능", canvas.width / 2, btn.y + 33);

            ctx.textAlign = "left";
        }

        function drawSelector(label, list, selectedIdx, unlockedList, y, prevBtn, nextBtn, buyBtn) {
            const item = list[selectedIdx];
            const isUnlocked = unlockedList.includes(selectedIdx);

            ctx.fillStyle = "#FFF";
            ctx.font = "bold 15px Arial";
            ctx.fillText(`${label}:`, 70, y + 21);

            ctx.fillStyle = "#333";
            ctx.beginPath();
            ctx.roundRect(prevBtn.x, prevBtn.y, prevBtn.w, prevBtn.h, 5);
            ctx.roundRect(nextBtn.x, nextBtn.y, nextBtn.w, nextBtn.h, 5);
            ctx.fill();

            ctx.fillStyle = "#FFF";
            ctx.font = "bold 15px Arial";
            ctx.fillText("<", prevBtn.x + 12, prevBtn.y + 21);
            ctx.fillText(">", nextBtn.x + 12, nextBtn.y + 21);

            ctx.fillStyle = isUnlocked ? "#FFD700" : "#AAA";
            ctx.fillText(`${item.name} ${isUnlocked ? '' : '🔒'}`, 225, y + 21);

            if (!isUnlocked) {
                const canAfford = totalCoins >= item.price;
                ctx.fillStyle = canAfford ? "#2E7D32" : "#777";
                ctx.beginPath();
                ctx.roundRect(buyBtn.x, buyBtn.y, buyBtn.w, buyBtn.h, 5);
                ctx.fill();

                ctx.fillStyle = "#FFF";
                ctx.font = "bold 12px Arial";
                ctx.fillText(`구매 (${item.price}G)`, buyBtn.x + 8, buyBtn.y + 20);
            }
        }

        function drawGame() {
            drawBackground();

            drawHumanRunner();
            drawDangerousObstacles();
            drawPotions();

            ctx.fillStyle = "#FFD700";
            coinItems.forEach(c => {
                ctx.beginPath();
                ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
                ctx.fill();
            });

            drawUI();

            if (gameState === 'GAMEOVER') {
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#FF1744";
                ctx.font = "bold 38px Arial";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 40);

                ctx.fillStyle = "#AAA";
                ctx.font = "16px Arial";
                ctx.fillText(`획득 점수: ${score}  |  획득 코인: +${coins} G`, canvas.width / 2, canvas.height / 2 - 5);

                const rBtn = gameOverButtons.retry;
                ctx.fillStyle = "#FF1744";
                ctx.beginPath();
                ctx.roundRect(rBtn.x, rBtn.y, rBtn.w, rBtn.h, 8);
                ctx.fill();

                ctx.fillStyle = "#FFF";
                ctx.font = "bold 16px Arial";
                ctx.fillText("🔄 다시 도전 (Space)", rBtn.x + 75, rBtn.y + 28);

                const mBtn = gameOverButtons.menu;
                ctx.fillStyle = "#444";
                ctx.beginPath();
                ctx.roundRect(mBtn.x, mBtn.y, mBtn.w, mBtn.h, 8);
                ctx.fill();
                ctx.strokeStyle = "#888";
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.fillStyle = "#FFF";
                ctx.fillText("⚙️ 상점 / 메뉴 (M)", mBtn.x + 75, mBtn.y + 28);

                ctx.textAlign = "left";
            }
        }

        function gameLoop() {
            if (gameState === 'START') {
                drawStartMenu();
            } else {
                update();
                drawGame();
            }
            requestAnimationFrame(gameLoop);
        }

        gameLoop();
    </script>
</body>
</html>
"""

components.html(game_html, height=380)
