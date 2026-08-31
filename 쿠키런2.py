import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="스트림릿 쿠키런", page_icon="🍪", layout="centered")

st.title("🍪 Streamlit Cookie Run")

# HTML / JS 게임 엔진
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
            border: 4px solid #fff;
            border-radius: 12px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
            background: linear-gradient(to bottom, #87CEEB, #E0F6FF);
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
            { name: "캔디 랜드 🍭", sky: ["#87CEEB", "#E0F6FF"], ground: "#654321", top: "#228B22" },
            { name: "용암 동굴 🌋", sky: ["#2b0000", "#4a0e0e"], ground: "#1a0f0f", top: "#ff3300" },
            { name: "밤하늘 🌙", sky: ["#0f2027", "#2c5364"], ground: "#1f1c2c", top: "#928dab" }
        ];

        const charThemes = [
            { name: "용감한 쿠키 🍪", color: "#D2691E" },
            { name: "딸기 맛 쿠키 🍓", color: "#FF69B4" },
            { name: "용사 맛 쿠키 ⚔️", color: "#4682B4" }
        ];

        let selectedBgIdx = 0;
        let selectedCharIdx = 0;

        // 게임 상태: 'START' | 'PLAYING' | 'GAMEOVER'
        let gameState = 'START';

        let score = 0;
        let coins = 0;
        let frameCount = 0;

        const groundY = 280;
        const NORMAL_HEIGHT = 50;
        const SLIDE_HEIGHT = 25;
        const COOKIE_WIDTH = 40;

        const cookie = {
            x: 80,
            y: groundY - NORMAL_HEIGHT,
            width: COOKIE_WIDTH,
            height: NORMAL_HEIGHT,
            dy: 0,
            gravity: 0.6,
            jumpPower: -12,
            jumpCount: 0,
            maxJumps: 2,
            isSliding: false
        };

        const obstacles = [];
        const coinItems = [];
        const keys = {};

        // UI 버튼 위치 정보 (시작 화면 클릭 처리용)
        const buttons = {
            bgPrev: { x: 200, y: 130, w: 40, h: 30 },
            bgNext: { x: 460, y: 130, w: 40, h: 30 },
            charPrev: { x: 200, y: 190, w: 40, h: 30 },
            charNext: { x: 460, y: 190, w: 40, h: 30 },
            play: { x: 275, y: 250, w: 150, h: 50 }
        };

        // -------------------------------------------------------------------
        // 이벤트 리스너
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
            // 배경 선택 화살표
            if (isInside(x, y, buttons.bgPrev)) {
                selectedBgIdx = (selectedBgIdx - 1 + bgThemes.length) % bgThemes.length;
            } else if (isInside(x, y, buttons.bgNext)) {
                selectedBgIdx = (selectedBgIdx + 1) % bgThemes.length;
            }
            // 캐릭터 선택 화살표
            else if (isInside(x, y, buttons.charPrev)) {
                selectedCharIdx = (selectedCharIdx - 1 + charThemes.length) % charThemes.length;
            } else if (isInside(x, y, buttons.charNext)) {
                selectedCharIdx = (selectedCharIdx + 1) % charThemes.length;
            }
            // PLAY 버튼
            else if (isInside(x, y, buttons.play)) {
                startGame();
            }
        }

        function isInside(x, y, btn) {
            return x >= btn.x && x <= btn.x + btn.w && y >= btn.y && y <= btn.y + btn.h;
        }

        function jump() {
            if (cookie.isSliding) return;
            if (cookie.jumpCount < cookie.maxJumps) {
                cookie.dy = cookie.jumpPower;
                cookie.jumpCount++;
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
            cookie.height = NORMAL_HEIGHT;
            cookie.y = groundY - NORMAL_HEIGHT;
            cookie.dy = 0;
            cookie.jumpCount = 0;
            cookie.isSliding = false;
        }

        // -------------------------------------------------------------------
        // 로직 및 장애물 생성
        // -------------------------------------------------------------------
        function spawnObstacle() {
            const rand = Math.random();

            if (rand < 0.25) {
                // 2단 점프 필수 대형 장애물
                obstacles.push({
                    x: canvas.width,
                    y: groundY - 45,
                    width: 140,
                    height: 45,
                    type: "double_jump"
                });
            } else if (rand < 0.6) {
                // 슬라이딩 전용 공중 장애물
                obstacles.push({
                    x: canvas.width,
                    y: groundY - 85,
                    width: 30,
                    height: 50,
                    type: "high"
                });
            } else {
                // 일반 점프 장애물
                const height = Math.random() * 20 + 35;
                obstacles.push({
                    x: canvas.width,
                    y: groundY - height,
                    width: 25,
                    height: height,
                    type: "low"
                });
            }
        }

        function spawnCoin() {
            const coinY = groundY - (Math.floor(Math.random() * 3) + 1) * 40;
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

            // 슬라이딩 판정
            const isDownPressed = keys["ArrowDown"] || keys["KeyS"];
            const isGrounded = cookie.y + cookie.height >= groundY - 1;

            if (isDownPressed && isGrounded) {
                if (!cookie.isSliding) {
                    cookie.isSliding = true;
                    cookie.height = SLIDE_HEIGHT;
                    cookie.y = groundY - SLIDE_HEIGHT;
                }
            } else {
                if (cookie.isSliding) {
                    cookie.isSliding = false;
                    cookie.height = NORMAL_HEIGHT;
                    cookie.y = groundY - NORMAL_HEIGHT;
                }
            }

            // 중력 적용
            cookie.dy += cookie.gravity;
            cookie.y += cookie.dy;

            if (cookie.y + cookie.height >= groundY) {
                cookie.y = groundY - cookie.height;
                cookie.dy = 0;
                cookie.jumpCount = 0;
            }

            if (frameCount % 90 === 0) spawnObstacle();
            if (frameCount % 50 === 0) spawnCoin();

            // 장애물 이동 및 충돌
            for (let i = obstacles.length - 1; i >= 0; i--) {
                const obs = obstacles[i];
                obs.x -= 6.5;

                if (
                    cookie.x < obs.x + obs.width &&
                    cookie.x + cookie.width > obs.x &&
                    cookie.y < obs.y + obs.height &&
                    cookie.y + cookie.height > obs.y
                ) {
                    gameState = 'GAMEOVER';
                }

                if (obs.x + obs.width < 0) obstacles.splice(i, 1);
            }

            // 코인 이동 및 획득
            for (let i = coinItems.length - 1; i >= 0; i--) {
                const c = coinItems[i];
                c.x -= 6.5;

                const distX = (cookie.x + cookie.width / 2) - c.x;
                const distY = (cookie.y + cookie.height / 2) - c.y;
                if (Math.sqrt(distX * distX + distY * distY) < cookie.width / 2 + c.radius) {
                    coins += 10;
                    score += 50;
                    coinItems.splice(i, 1);
                } else if (c.x + c.radius < 0) {
                    coinItems.splice(i, 1);
                }
            }
        }

        // -------------------------------------------------------------------
        // 렌더링 함수
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
            ctx.fillRect(0, groundY, canvas.width, 15);
        }

        function drawStartMenu() {
            drawBackground();

            // 오버레이 레이어
            ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // 타이틀
            ctx.fillStyle = "#FFD700";
            ctx.font = "bold 34px Arial";
            ctx.textAlign = "center";
            ctx.fillText("🍪 COOKIE RUN 🍪", canvas.width / 2, 70);

            ctx.font = "bold 16px Arial";
            ctx.fillStyle = "#FFF";

            // 1. 배경 선택 UI
            drawSelector("배경", bgThemes[selectedBgIdx].name, 130, buttons.bgPrev, buttons.bgNext);

            // 2. 캐릭터 선택 UI
            drawSelector("캐릭터", charThemes[selectedCharIdx].name, 190, buttons.charPrev, buttons.charNext);

            // 3. PLAY 버튼
            const btn = buttons.play;
            ctx.fillStyle = "#FF4500";
            ctx.beginPath();
            ctx.roundRect(btn.x, btn.y, btn.w, btn.h, 12);
            ctx.fill();
            ctx.strokeStyle = "#FFF";
            ctx.lineWidth = 3;
            ctx.stroke();

            ctx.fillStyle = "#FFF";
            ctx.font = "bold 24px Arial";
            ctx.fillText("▶ PLAY", canvas.width / 2, btn.y + 33);

            ctx.textAlign = "left";
        }

        function drawSelector(label, value, y, prevBtn, nextBtn) {
            ctx.fillStyle = "#FFF";
            ctx.font = "bold 16px Arial";
            ctx.fillText(`${label}:`, 140, y + 20);

            // 이전/다음 버튼
            ctx.fillStyle = "#444";
            ctx.beginPath();
            ctx.roundRect(prevBtn.x, prevBtn.y, prevBtn.w, prevBtn.h, 5);
            ctx.roundRect(nextBtn.x, nextBtn.y, nextBtn.w, nextBtn.h, 5);
            ctx.fill();

            ctx.fillStyle = "#FFF";
            ctx.fillText("<", prevBtn.x + 14, prevBtn.y + 20);
            ctx.fillText(">", nextBtn.x + 14, nextBtn.y + 20);

            // 선택된 항목명
            ctx.fillStyle = "#FFD700";
            ctx.fillText(value, 260, y + 20);
        }

        function drawGame() {
            drawBackground();

            // 쿠키 그리기
            const currentChar = charThemes[selectedCharIdx];
            ctx.fillStyle = currentChar.color;
            ctx.beginPath();
            ctx.roundRect(cookie.x, cookie.y, cookie.width, cookie.height, 8);
            ctx.fill();

            // 쿠키 눈
            ctx.fillStyle = "#FFF";
            const eyeX = cookie.x + (cookie.isSliding ? 30 : 28);
            const eyeY = cookie.y + (cookie.isSliding ? 8 : 15);
            ctx.beginPath();
            ctx.arc(eyeX, eyeY, 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#000";
            ctx.beginPath();
            ctx.arc(eyeX + 1, eyeY, 2, 0, Math.PI * 2);
            ctx.fill();

            // 장애물
            obstacles.forEach(obs => {
                if (obs.type === "double_jump") {
                    ctx.fillStyle = "#FF1493";
                    ctx.beginPath();
                    ctx.roundRect(obs.x, obs.y, obs.width, obs.height, 6);
                    ctx.fill();

                    ctx.fillStyle = "#FFF";
                    ctx.font = "bold 13px Arial";
                    ctx.fillText("⚠️ 2단 점프!", obs.x + 25, obs.y + 26);
                } else if (obs.type === "high") {
                    ctx.fillStyle = "#8A2BE2";
                    ctx.beginPath();
                    ctx.roundRect(obs.x, obs.y, obs.width, obs.height, [0, 0, 10, 10]);
                    ctx.fill();

                    ctx.fillStyle = "#FFF";
                    ctx.font = "bold 11px Arial";
                    ctx.fillText("LOW", obs.x + 2, obs.y + 30);
                } else {
                    ctx.fillStyle = "#FF4500";
                    ctx.beginPath();
                    ctx.roundRect(obs.x, obs.y, obs.width, obs.height, [8, 8, 0, 0]);
                    ctx.fill();
                }
            });

            // 코인
            ctx.fillStyle = "#FFD700";
            coinItems.forEach(c => {
                ctx.beginPath();
                ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
                ctx.fill();
            });

            // UI (점수)
            ctx.fillStyle = "#FFF";
            ctx.font = "bold 18px Arial";
            ctx.fillText(`Score: ${score}`, 20, 35);
            ctx.fillText(`Coins: 🟡 ${coins}`, 20, 60);

            if (cookie.isSliding) {
                ctx.fillStyle = "#FFD700";
                ctx.font = "bold 14px Arial";
                ctx.fillText("SLIDE!", cookie.x, cookie.y - 10);
            }

            // 게임 오버 화면
            if (gameState === 'GAMEOVER') {
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#FFF";
                ctx.font = "bold 36px Arial";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);

                ctx.font = "18px Arial";
                ctx.fillText("Space 키 또는 클릭으로 재시작", canvas.width / 2, canvas.height / 2 + 20);
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
### 🎮 플레이 안내
- **시작 화면:** Canvas 내 **`<` / `>`** 화살표 버튼으로 배경과 캐릭터 변경 ➔ **`▶ PLAY`** 버튼을 눌러 출발
- **점프 / 2단 점프:** `Space` 키 / `↑(위 화살표)` / 마우스 클릭
- **슬라이딩:** `↓(아래 화살표)` 키 또는 `S` 키 누르고 있기
""")
