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

        // -------------------------------------------------------------------
        // 테마 및 캐릭터 데이터
        // -------------------------------------------------------------------
        const bgThemes = [
            { name: "위험한 사이버시티 🏙️", sky: ["#0B0C10", "#1F2833"], ground: "#0B0C10", top: "#66FCF1" },
            { name: "지옥의 용암 지대 🌋", sky: ["#1A0000", "#4A0000"], ground: "#110000", top: "#FF3300" },
            { name: "심야의 폐공장 🏭", sky: ["#141E30", "#243B55"], ground: "#0F171E", top: "#FFD700" }
        ];

        const runnerThemes = [
            { name: "네온 아머 🏃", skin: "#66FCF1", suit: "#1F2833" },
            { name: "샤이니 스파크 ⚡", skin: "#FFD700", suit: "#FF4500" },
            { name: "섀도우 에이전트 🥷", skin: "#E0E0E0", suit: "#FF0055" }
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
            width: 30,
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

        // 시작 화면 UI 버튼 좌표
        const buttons = {
            bgPrev: { x: 200, y: 130, w: 40, h: 30 },
            bgNext: { x: 460, y: 130, w: 40, h: 30 },
            runnerPrev: { x: 200, y: 190, w: 40, h: 30 },
            runnerNext: { x: 460, y: 190, w: 40, h: 30 },
            play: { x: 275, y: 250, w: 150, h: 50 }
        };

        // 게임 오버 메뉴 버튼 좌표
        const gameOverButtons = {
            retry: { x: 180, y: 240, w: 150, h: 45 },
            menu: { x: 370, y: 240, w: 150, h: 45 }
        };

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
                    resetGame(); // 바로 다시 시작
                } else if (e.code === "KeyM") {
                    gameState = 'START'; // M 키 누르면 시작 메뉴로 이동
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
            } else if (isInside(x, y, buttons.runnerPrev)) {
                selectedRunnerIdx = (selectedRunnerIdx - 1 + runnerThemes.length) % runnerThemes.length;
            } else if (isInside(x, y, buttons.runnerNext)) {
                selectedRunnerIdx = (selectedRunnerIdx + 1) % runnerThemes.length;
            } else if (isInside(x, y, buttons.play)) {
                startGame();
            }
        }

        function handleGameOverClick(x, y) {
            if (isInside(x, y, gameOverButtons.retry)) {
                resetGame();
            } else if (isInside(x, y, gameOverButtons.menu)) {
                gameState = 'START'; // 메뉴 버튼 클릭 시 시작 화면으로
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
                    y: groundY - 95,
                    width: 50,
                    height: 60,
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
        // 렌더링
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

        function drawHumanRunner() {
            const theme = runnerThemes[selectedRunnerIdx];
            const rx = runner.x + 15;
            const ry = runner.y;

            ctx.lineWidth = 4;
            ctx.strokeStyle = theme.skin;
            ctx.fillStyle = theme.skin;

            if (runner.isSliding) {
                ctx.beginPath();
                ctx.arc(rx + 15, ry + 10, 7, 0, Math.PI * 2);
                ctx.fill();

                ctx.beginPath();
                ctx.moveTo(rx - 10, ry + 18);
                ctx.lineTo(rx + 10, ry + 18);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(rx - 10, ry + 18);
                ctx.lineTo(rx - 22, ry + 25);
                ctx.stroke();
            } else {
                const legSwing = Math.sin(frameCount * 0.3) * 12;

                ctx.beginPath();
                ctx.arc(rx, ry + 8, 8, 0, Math.PI * 2);
                ctx.fill();

                ctx.beginPath();
                ctx.moveTo(rx, ry + 16);
                ctx.lineTo(rx, ry + 38);
                ctx.strokeStyle = theme.suit;
                ctx.lineWidth = 6;
                ctx.stroke();

                ctx.strokeStyle = theme.skin;
                ctx.lineWidth = 4;

                if (runner.jumpCount > 0) {
                    ctx.beginPath();
                    ctx.moveTo(rx, ry + 38);
                    ctx.lineTo(rx - 10, ry + 48);
                    ctx.lineTo(rx - 5, ry + 58);
                    ctx.moveTo(rx, ry + 38);
                    ctx.lineTo(rx + 12, ry + 48);
                    ctx.lineTo(rx + 8, ry + 58);
                    ctx.stroke();
                } else {
                    ctx.beginPath();
                    ctx.moveTo(rx, ry + 38);
                    ctx.lineTo(rx + legSwing, ry + 48);
                    ctx.lineTo(rx + legSwing * 1.2, ry + 58);

                    ctx.moveTo(rx, ry + 38);
                    ctx.lineTo(rx - legSwing, ry + 48);
                    ctx.lineTo(rx - legSwing * 1.2, ry + 58);
                    ctx.stroke();
                }

                ctx.beginPath();
                ctx.moveTo(rx, ry + 20);
                ctx.lineTo(rx - legSwing, ry + 30);
                ctx.moveTo(rx, ry + 20);
                ctx.lineTo(rx + legSwing, ry + 30);
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
                    const spikeWidth = 10;
                    const numSpikes = obs.width / spikeWidth;

                    ctx.fillRect(obs.x, obs.y, obs.width, 10);

                    ctx.beginPath();
                    for (let i = 0; i < numSpikes; i++) {
                        const sx = obs.x + (i * spikeWidth);
                        ctx.moveTo(sx, obs.y + 10);
                        ctx.lineTo(sx + spikeWidth / 2, obs.y + obs.height);
                        ctx.lineTo(sx + spikeWidth, obs.y + 10);
                    }
                    ctx.fill();

                    ctx.fillStyle = "#D500F9";
                    ctx.font = "bold 11px Arial";
                    ctx.fillText("SLIDE!", obs.x + 5, obs.y - 6);
                }
            });
        }

        function drawStartMenu() {
            drawBackground();

            ctx.fillStyle = "rgba(0, 0, 0, 0.65)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = "#FF1744";
            ctx.font = "bold 34px Arial";
            ctx.textAlign = "center";
            ctx.fillText("⚡ DASH RUNNER: EXTREME ⚡", canvas.width / 2, 70);

            ctx.font = "bold 15px Arial";
            ctx.fillStyle = "#FFF";

            drawSelector("스테이지", bgThemes[selectedBgIdx].name, 130, buttons.bgPrev, buttons.bgNext);
            drawSelector("러너 수트", runnerThemes[selectedRunnerIdx].name, 190, buttons.runnerPrev, buttons.runnerNext);

            const btn = buttons.play;
            ctx.fillStyle = "#FF1744";
            ctx.beginPath();
            ctx.roundRect(btn.x, btn.y, btn.w, btn.h, 12);
            ctx.fill();
            ctx.strokeStyle = "#FFF";
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.fillStyle = "#FFF";
            ctx.font = "bold 24px Arial";
            ctx.fillText("▶ START", canvas.width / 2, btn.y + 33);

            ctx.textAlign = "left";
        }

        function drawSelector(label, value, y, prevBtn, nextBtn) {
            ctx.fillStyle = "#FFF";
            ctx.font = "bold 15px Arial";
            ctx.fillText(`${label}:`, 120, y + 20);

            ctx.fillStyle = "#333";
            ctx.beginPath();
            ctx.roundRect(prevBtn.x, prevBtn.y, prevBtn.w, prevBtn.h, 5);
            ctx.roundRect(nextBtn.x, nextBtn.y, nextBtn.w, nextBtn.h, 5);
            ctx.fill();

            ctx.fillStyle = "#FFF";
            ctx.fillText("<", prevBtn.x + 14, prevBtn.y + 20);
            ctx.fillText(">", nextBtn.x + 14, nextBtn.y + 20);

            ctx.fillStyle = "#FFD700";
            ctx.fillText(value, 260, y + 20);
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
            ctx.fillText(`Coins: 🟡 ${coins}`, 20, 60);

            // 게임 오버 레이어 및 선택 버튼
            if (gameState === 'GAMEOVER') {
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#FF1744";
                ctx.font = "bold 38px Arial";
                ctx.textAlign = "center";
                ctx.fillText("DESTROYED!", canvas.width / 2, canvas.height / 2 - 40);

                ctx.fillStyle = "#AAA";
                ctx.font = "16px Arial";
                ctx.fillText(`최종 점수: ${score}  |  코인: ${coins}`, canvas.width / 2, canvas.height / 2 - 5);

                // 1. 다시 시작 버튼
                const rBtn = gameOverButtons.retry;
                ctx.fillStyle = "#FF1744";
                ctx.beginPath();
                ctx.roundRect(rBtn.x, rBtn.y, rBtn.w, rBtn.h, 8);
                ctx.fill();

                ctx.fillStyle = "#FFF";
                ctx.font = "bold 16px Arial";
                ctx.fillText("🔄 다시 도전 (Space)", rBtn.x + 75, rBtn.y + 28);

                // 2. 캐릭터/배경 변경 메뉴 버튼
                const mBtn = gameOverButtons.menu;
                ctx.fillStyle = "#444";
                ctx.beginPath();
                ctx.roundRect(mBtn.x, mBtn.y, mBtn.w, mBtn.h, 8);
                ctx.fill();
                ctx.strokeStyle = "#888";
                ctx.lineWidth = 2;
                ctx.stroke();

                ctx.fillStyle = "#FFF";
                ctx.fillText("⚙️ 설정 변경 (M)", mBtn.x + 75, mBtn.y + 28);

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

st.markdown("""
---
### 🔄 변경 및 새로 적용된 기능
- **게임 오버 시 설정 변경 옵션 추가:**
  1. **`⚙️ 설정 변경` 버튼 클릭** 또는 **`M` 키 누르기** ➔ **시작 화면(메뉴)으로 이동**하여 배경과 캐릭터 변경
  2. **`🔄 다시 도전` 버튼 클릭** 또는 **`Space` 키 누르기** ➔ 바로 게임 재시작
""")
