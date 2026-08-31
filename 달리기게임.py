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
        // 테마 및 사람 캐릭터 색상
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
        let sawRotation = 0; // 톱날 회전각

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

        const buttons = {
            bgPrev: { x: 200, y: 130, w: 40, h: 30 },
            bgNext: { x: 460, y: 130, w: 40, h: 30 },
            runnerPrev: { x: 200, y: 190, w: 40, h: 30 },
            runnerNext: { x: 460, y: 190, w: 40, h: 30 },
            play: { x: 275, y: 250, w: 150, h: 50 }
        };

        // -------------------------------------------------------------------
        // 이벤트
        // -------------------------------------------------------------------
        window.addEventListener("keydown", function (e) {
            if (["Space", "ArrowDown", "KeyS", "ArrowUp"].includes(e.code)) {
                e.preventDefault();
            }
            keys[e.code] = true;

            if (gameState === 'PLAYING' && (e.code === "Space" || e.code === "ArrowUp")) {
                jump();
            } else if (gameState === 'GAMEOVER' && e.code === "Space") {
                resetGame();
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
                resetGame();
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
        // 장애물 생성 (위험한 톱날 / 날카로운 가시)
        // -------------------------------------------------------------------
        function spawnObstacle() {
            const isDoubleJump = Math.random() < 0.5;

            if (isDoubleJump) {
                // 🔥 회전하는 대형 위협 톱날 (2단 점프 전용, 너비 230px)
                obstacles.push({
                    x: canvas.width,
                    y: groundY - 45,
                    width: 230,
                    height: 45,
                    type: "double_jump_saw"
                });
            } else {
                // 🟣 천장 가시 트랩 (슬라이딩 전용)
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
            sawRotation += 0.2; // 톱날 회전 애니메이션

            // 슬라이딩 동작
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

            // 중력 및 좌표 연산
            runner.dy += runner.gravity;
            runner.y += runner.dy;

            if (runner.y + runner.height >= groundY) {
                runner.y = groundY - runner.height;
                runner.dy = 0;
                runner.jumpCount = 0;
            }

            if (frameCount % 90 === 0) spawnObstacle();
            if (frameCount % 45 === 0) spawnCoin();

            // 장애물 이동 및 히트박스 판정
            for (let i = obstacles.length - 1; i >= 0; i--) {
                const obs = obstacles[i];
                obs.x -= 7.5;

                // 충돌 검사
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

            // 코인
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
        // 렌더링 (사람 관절 캐릭터 & 위험 장애물)
        // -------------------------------------------------------------------
        function drawBackground() {
            const currentBg = bgThemes[selectedBgIdx];
            const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
            grad.addColorStop(0, currentBg.sky[0]);
            grad.addColorStop(1, currentBg.sky[1]);
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 바닥
            ctx.fillStyle = currentBg.ground;
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.fillStyle = currentBg.top;
            ctx.fillRect(0, groundY, canvas.width, 10);
        }

        // 🚶 사람 형태(Stickman / Human Runner) 그리기
        function drawHumanRunner() {
            const theme = runnerThemes[selectedRunnerIdx];
            const rx = runner.x + 15; // 중심 X
            const ry = runner.y;

            ctx.lineWidth = 4;
            ctx.strokeStyle = theme.skin;
            ctx.fillStyle = theme.skin;

            if (runner.isSliding) {
                // 엎드려서 슬라이딩하는 사람 포즈
                // 머리
                ctx.beginPath();
                ctx.arc(rx + 15, ry + 10, 7, 0, Math.PI * 2);
                ctx.fill();
                // 몸통
                ctx.beginPath();
                ctx.moveTo(rx - 10, ry + 18);
                ctx.lineTo(rx + 10, ry + 18);
                ctx.stroke();
                // 다리
                ctx.beginPath();
                ctx.moveTo(rx - 10, ry + 18);
                ctx.lineTo(rx - 22, ry + 25);
                ctx.stroke();
            } else {
                // 달리기/점프하는 사람 포즈
                const legSwing = Math.sin(frameCount * 0.3) * 12; // 달리 모션 연산

                // 1. 머리
                ctx.beginPath();
                ctx.arc(rx, ry + 8, 8, 0, Math.PI * 2);
                ctx.fill();

                // 2. 몸통 (슈트 스틸)
                ctx.beginPath();
                ctx.moveTo(rx, ry + 16);
                ctx.lineTo(rx, ry + 38);
                ctx.strokeStyle = theme.suit;
                ctx.lineWidth = 6;
                ctx.stroke();

                ctx.strokeStyle = theme.skin;
                ctx.lineWidth = 4;

                // 3. 다리 모션 (공중에 떠있으면 점프 포즈, 땅에서는 달리기 포즈)
                if (runner.jumpCount > 0) {
                    // 점프 포즈 (무릎을 구부림)
                    ctx.beginPath();
                    ctx.moveTo(rx, ry + 38);
                    ctx.lineTo(rx - 10, ry + 48);
                    ctx.lineTo(rx - 5, ry + 58);
                    ctx.moveTo(rx, ry + 38);
                    ctx.lineTo(rx + 12, ry + 48);
                    ctx.lineTo(rx + 8, ry + 58);
                    ctx.stroke();
                } else {
                    // 달리기 연산
                    ctx.beginPath();
                    ctx.moveTo(rx, ry + 38);
                    ctx.lineTo(rx + legSwing, ry + 48);
                    ctx.lineTo(rx + legSwing * 1.2, ry + 58);

                    ctx.moveTo(rx, ry + 38);
                    ctx.lineTo(rx - legSwing, ry + 48);
                    ctx.lineTo(rx - legSwing * 1.2, ry + 58);
                    ctx.stroke();
                }

                // 4. 팔 모션
                ctx.beginPath();
                ctx.moveTo(rx, ry + 20);
                ctx.lineTo(rx - legSwing, ry + 30);
                ctx.moveTo(rx, ry + 20);
                ctx.lineTo(rx + legSwing, ry + 30);
                ctx.stroke();
            }
        }

        // ⚙️ 위험한 장애물 (회전 톱날 & 가시 트랩) 그리기
        function drawDangerousObstacles() {
            obstacles.forEach(obs => {
                if (obs.type === "double_jump_saw") {
                    // 💥 위험한 연쇄 회전 톱날 (3개 톱날 배치)
                    const sawCount = 3;
                    const radius = 22;
                    const spacing = obs.width / sawCount;

                    for (let i = 0; i < sawCount; i++) {
                        const cx = obs.x + radius + (i * spacing);
                        const cy = obs.y + radius;

                        ctx.save();
                        ctx.translate(cx, cy);
                        ctx.rotate(sawRotation + i);

                        // 톱날 외형
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

                        // 중심 휠
                        ctx.fillStyle = "#FFF";
                        ctx.beginPath();
                        ctx.arc(0, 0, 5, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.restore();
                    }

                    // 경고 텍스트
                    ctx.fillStyle = "#FF1744";
                    ctx.font = "bold 13px Arial";
                    ctx.fillText("⚠️ DANGER: 2단 점프!", obs.x + 35, obs.y - 8);

                } else if (obs.type === "spike_ceiling") {
                    // 💥 날카로운 천장 가시 트랩
                    ctx.fillStyle = "#D500F9";
                    const spikeWidth = 10;
                    const numSpikes = obs.width / spikeWidth;

                    // 위쪽 지지대
                    ctx.fillRect(obs.x, obs.y, obs.width, 10);

                    // 삼각 가시 그리기
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

            // 관절 캐릭터 그리기
            drawHumanRunner();

            // 위험 장애물 그리기
            drawDangerousObstacles();

            // 코인
            ctx.fillStyle = "#FFD700";
            coinItems.forEach(c => {
                ctx.beginPath();
                ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
                ctx.fill();
            });

            // 점수 UI
            ctx.fillStyle = "#FFF";
            ctx.font = "bold 18px Arial";
            ctx.fillText(`Score: ${score}`, 20, 35);
            ctx.fillText(`Coins: 🟡 ${coins}`, 20, 60);

            // 게임 오버
            if (gameState === 'GAMEOVER') {
                ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#FF1744";
                ctx.font = "bold 40px Arial";
                ctx.textAlign = "center";
                ctx.fillText("DESTROYED!", canvas.width / 2, canvas.height / 2 - 20);

                ctx.fillStyle = "#FFF";
                ctx.font = "18px Arial";
                ctx.fillText("Space 키를 눌러 재도전", canvas.width / 2, canvas.height / 2 + 20);
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
### 🎮 업데이트 요소
1. **사람 형태 러너 (Stickman / Human Runner):** 
   - 러닝 애니메이션, 점프 포즈, 슬라이딩 포즈가 실시간으로 적용됩니다.
2. **위험한 장애물 비주얼:**
   - ⚙️ **회전하는 대형 톱날 트랩:** $230\text{px}$ 너비의 붉은색 톱날로, 최고점에서 정확히 **2단 점프**를 해야 넘을 수 있습니다.
   - 💜 **날카로운 가시 천장 트랩:** **`↓(아래 화살표)`** / **`S`** 키로 엎드려 통과해야 합니다.
""")
