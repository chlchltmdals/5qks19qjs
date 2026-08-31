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

        // 누적 코인 및 해금 데이터 (로컬 저장소 저장)
        let totalCoins = parseInt(localStorage.getItem("dash_runner_total_coins")) || 0;
        let unlockedBgs = JSON.parse(localStorage.getItem("dash_runner_unlocked_bgs")) || [0, 1, 2];
        let unlockedRunners = JSON.parse(localStorage.getItem("dash_runner_unlocked_runners")) || [0, 1, 2];

        // -------------------------------------------------------------------
        // 테마 및 캐릭터 데이터
        // -------------------------------------------------------------------
        const bgThemes = [
            { name: "위험한 사이버시티 🏙️", sky: ["#0B0C10", "#1F2833"], ground: "#0B0C10", top: "#66FCF1", price: 0 },
            { name: "지옥의 용암 지대 🌋", sky: ["#1A0000", "#4A0000"], ground: "#110000", top: "#FF3300", price: 0 },
            { name: "심야의 폐공장 🏭", sky: ["#141E30", "#243B55"], ground: "#0F171E", top: "#FFD700", price: 0 },
            { name: "사이보그 랩 🧪", sky: ["#002B11", "#005C29"], ground: "#001408", top: "#00FF66", price: 150 },
            { name: "네온 우주 공간 🌌", sky: ["#050014", "#190033"], ground: "#0A001F", top: "#D500F9", price: 300 },
            { name: "초시공 차원 🔮", sky: ["#1A0022", "#3D0052"], ground: "#0D0012", top: "#00E5FF", price: 500 }
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

        // -------------------------------------------------------------------
        // 이벤트 핸들러
        // -------------------------------------------------------------------
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
            obstacles.length = 0;
            coinItems.length = 0;
            runner.height = NORMAL_HEIGHT;
            runner.y = groundY - NORMAL_HEIGHT;
            runner.dy = 0;
            runner.jumpCount = 0;
            runner.isSliding = false;
        }

        // -------------------------------------------------------------------
        // 로직 업데이트
        // -------------------------------------------------------------------
        function spawnObstacle() {
            const isDoubleJump = Math.random() < 0.5;

            if (isDoubleJump) {
                obstacles.push({
                    x: canvas.width,
                    y: groundY - 45,
                    width: 230,
                    height: 45,
                    type: "double_jump_saw"
                });
            } else {
                obstacles.push({
                    x: canvas.width,
                    y: 0,
                    width: 60,
                    height: groundY - SLIDE_HEIGHT,
                    type: "spike_ceiling"
                });
            }
        }

        function spawnCoin() {
            const coinY = groundY - (Math.floor(Math.random() * 3) + 1) * 45;
            coinItems.push({
                x: canvas.width,
                y: coinY,
                radius: 12
            });
        }

        function update() {
            if (gameState !== 'PLAYING') return;

            frameCount++;
            score++;
            sawRotation += 0.2;

            const isDownPressed = keys["ArrowDown"] || keys["KeyS"];
            const isGrounded = runner.y + runner.height >= groundY - 1;

            if (isDownPressed && isGrounded) {
                if (!runner.isSliding) {
                    runner.isSliding = true;
                    runner.height = SLIDE_HEIGHT;
                    runner.y = groundY - SLIDE_HEIGHT;
                }
            } else {
                if (runner.isSliding) {
                    runner.isSliding = false;
                    runner.height = NORMAL_HEIGHT;
                    runner.y = groundY - NORMAL_HEIGHT;
                }
            }

            runner.dy += runner.gravity;
            runner.y += runner.dy;

            if (runner.y + runner.height >= groundY) {
                runner.y = groundY - runner.height;
                runner.dy = 0;
                runner.jumpCount = 0;
            }

            if (frameCount % 90 === 0) spawnObstacle();
            if (frameCount % 45 === 0) spawnCoin();

            for (let i = obstacles.length - 1; i >= 0; i--) {
                const obs = obstacles[i];
                obs.x -= 7.5;

                if (
                    runner.x < obs.x + obs.width &&
                    runner.x + runner.width > obs.x &&
                    runner.y < obs.y + obs.height &&
                    runner.y + runner.height > obs.y
                ) {
                    totalCoins += coins;
                    saveStorage();
                    gameState = 'GAMEOVER';
                }

                if (obs.x + obs.width < 0) obstacles.splice(i, 1);
            }

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
        }

        // -------------------------------------------------------------------
        // 렌더링 (두꺼워진 사람 캐릭터 & 얼굴 이목구비)
        // -------------------------------------------------------------------
        function drawBackground() {
            const currentBg = bgThemes[selectedBgIdx];
            const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
            grad.addColorStop(0, currentBg.sky[0]);
            grad.addColorStop(1, currentBg.sky[1]);
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = currentBg.ground;
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.fillStyle = currentBg.top;
            ctx.fillRect(0, groundY, canvas.width, 10);
        }

        // 👤 더 두껍고 이목구비가 있는 사람 캐릭터 그리기
        function drawHumanRunner() {
            const theme = runnerThemes[selectedRunnerIdx];
            const rx = runner.x + 17;
            const ry = runner.y;

            if (runner.isSliding) {
                // --- 엎드린 슬라이딩 포즈 ---
                // 1. 머리 (크게 확대)
                ctx.fillStyle = theme.skin;
                ctx.beginPath();
                ctx.arc(rx + 20, ry + 12, 11, 0, Math.PI * 2);
                ctx.fill();

                // 2. 눈 (놀란 동공 표정 ⊙_⊙)
                ctx.fillStyle = "#000";
                ctx.beginPath();
                ctx.arc(rx + 24, ry + 10, 3, 0, Math.PI * 2); // 큰 눈
                ctx.arc(rx + 28, ry + 10, 2, 0, Math.PI * 2);
                ctx.fill();

                // 3. 두꺼운 몸통
                ctx.fillStyle = theme.suit;
                ctx.beginPath();
                ctx.roundRect(rx - 15, ry + 12, 28, 14, 6);
                ctx.fill();

                // 4. 두꺼운 다리
                ctx.strokeStyle = theme.suit;
                ctx.lineWidth = 8;
                ctx.lineCap = "round";
                ctx.beginPath();
                ctx.moveTo(rx - 12, ry + 20);
                ctx.lineTo(rx - 28, ry + 26);
                ctx.stroke();

            } else {
                // --- 달리기 / 점프 포즈 ---
                const legSwing = Math.sin(frameCount * 0.3) * 14;

                // 1. 두꺼운 몸통 (볼륨감 있는 수트)
                ctx.fillStyle = theme.suit;
                ctx.beginPath();
                ctx.roundRect(rx - 9, ry + 18, 18, 22, 6);
                ctx.fill();

                // 2. 머리 (피부색 + 큰 두상)
                ctx.fillStyle = theme.skin;
                ctx.beginPath();
                ctx.arc(rx, ry + 10, 11, 0, Math.PI * 2);
                ctx.fill();

                // 3. 얼굴 이목구비 (달리는 방향 바라보는 눈 & 표정)
                ctx.fillStyle = theme.eye;
                if (runner.jumpCount > 0) {
                    // 점프 시 (깜짝 놀란 눈)
                    ctx.beginPath();
                    ctx.arc(rx + 4, ry + 8, 3, 0, Math.PI * 2);
                    ctx.arc(rx + 8, ry + 8, 2, 0, Math.PI * 2);
                    ctx.fill();
                } else {
                    // 기본 달리기 (집중한 눈)
                    ctx.beginPath();
                    ctx.arc(rx + 5, ry + 9, 2.5, 0, Math.PI * 2);
                    ctx.fill();
                    // 입
                    ctx.strokeStyle = theme.eye;
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    ctx.arc(rx + 4, ry + 13, 3, 0, Math.PI * 0.8);
                    ctx.stroke();
                }

                ctx.strokeStyle = theme.suit;
                ctx.lineWidth = 7.5; // 두꺼운 관절 두께
                ctx.lineCap = "round";

                // 4. 두꺼운 다리 (점프 vs 달리기 모션)
                if (runner.jumpCount > 0) {
                    // 점프 다리 포즈
                    ctx.beginPath();
                    ctx.moveTo(rx - 4, ry + 38);
                    ctx.lineTo(rx - 12, ry + 48);
                    ctx.lineTo(rx - 6, ry + 58);

                    ctx.moveTo(rx + 4, ry + 38);
                    ctx.lineTo(rx + 14, ry + 48);
                    ctx.lineTo(rx + 8, ry + 58);
                    ctx.stroke();
                } else {
                    // 달리기 다리 모션
                    ctx.beginPath();
                    ctx.moveTo(rx - 3, ry + 38);
                    ctx.lineTo(rx + legSwing, ry + 48);
                    ctx.lineTo(rx + legSwing * 1.1, ry + 58);

                    ctx.moveTo(rx + 3, ry + 38);
                    ctx.lineTo(rx - legSwing, ry + 48);
                    ctx.lineTo(rx - legSwing * 1.1, ry + 58);
                    ctx.stroke();
                }

                // 5. 두꺼운 팔 모션
                ctx.strokeStyle = theme.skin;
                ctx.lineWidth = 6;
                ctx.beginPath();
                ctx.moveTo(rx, ry + 22);
                ctx.lineTo(rx - legSwing * 0.9, ry + 32);

                ctx.moveTo(rx, ry + 22);
                ctx.lineTo(rx + legSwing * 0.9, ry + 32);
                ctx.stroke();
            }
        }

        function drawDangerousObstacles() {
            obstacles.forEach(obs => {
                if (obs.type === "double_jump_saw") {
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

                    ctx.fillStyle = "#FF1744";
                    ctx.font = "bold 13px Arial";
                    ctx.fillText("⚠️ DANGER: 2단 점프!", obs.x + 35, obs.y - 8);

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

                    ctx.fillStyle = "#FFF";
                    ctx.font = "bold 12px Arial";
                    ctx.fillText("⬇️ ONLY SLIDE!", obs.x - 15, obs.height / 2);
                }
            });
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

            ctx.fillStyle = "#FFD700";
            coinItems.forEach(c => {
                ctx.beginPath();
                ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
                ctx.fill();
            });

            ctx.fillStyle = "#FFF";
            ctx.font = "bold 18px Arial";
            ctx.fillText(`Score: ${score}`, 20, 35);
            ctx.fillText(`Coins: 🟡 +${coins}`, 20, 60);

            if (gameState === 'GAMEOVER') {
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#FF1744";
                ctx.font = "bold 38px Arial";
                ctx.textAlign = "center";
                ctx.fillText("DESTROYED!", canvas.width / 2, canvas.height / 2 - 40);

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
