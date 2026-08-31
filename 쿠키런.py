import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="스트림릿 쿠키런", page_icon="🍪", layout="centered")

st.title("🍪 Streamlit Cookie Run (슬라이딩 추가판)")
st.caption("Space / 클릭으로 점프 | Down 화살표 / S 키로 슬라이딩!")

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
            background-color: #1e1e2f;
            font-family: Arial, sans-serif;
            color: white;
            user-select: none;
        }
        #gameContainer {
            text-align: center;
            position: relative;
        }
        canvas {
            border: 4px solid #fff;
            border-radius: 12px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
            background: linear-gradient(to bottom, #87CEEB, #E0F6FF);
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="700" height="350"></canvas>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // 게임 변수
        let score = 0;
        let coins = 0;
        let gameOver = false;
        let frameCount = 0;

        const groundY = 280;

        // 쿠키(플레이어) 크기 정의
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

        // 키보드 입력 처리
        window.addEventListener("keydown", function (e) {
            if (["Space", "ArrowDown", "KeyS", "ArrowUp"].includes(e.code)) {
                e.preventDefault();
            }
            keys[e.code] = true;

            if (e.code === "Space" || e.code === "ArrowUp") {
                jump();
            }
        });

        window.addEventListener("keyup", function (e) {
            keys[e.code] = false;
        });

        // 마우스 클릭 (점프)
        canvas.addEventListener("mousedown", function () {
            jump();
        });

        function jump() {
            if (gameOver) {
                resetGame();
                return;
            }
            // 슬라이딩 중에는 점프 불가
            if (cookie.isSliding) return;

            if (cookie.jumpCount < cookie.maxJumps) {
                cookie.dy = cookie.jumpPower;
                cookie.jumpCount++;
            }
        }

        function resetGame() {
            score = 0;
            coins = 0;
            gameOver = false;
            obstacles.length = 0;
            coinItems.length = 0;
            cookie.height = NORMAL_HEIGHT;
            cookie.y = groundY - NORMAL_HEIGHT;
            cookie.dy = 0;
            cookie.jumpCount = 0;
            cookie.isSliding = false;
            animate();
        }

        // 장애물 생성 (지상 장애물 vs 슬라이딩 장애물)
        function spawnObstacle() {
            const isHigh = Math.random() < 0.4; // 40% 확률로 슬라이딩 장애물 생성

            if (isHigh) {
                // 슬라이딩으로 피해야 하는 공중 장애물
                obstacles.push({
                    x: canvas.width,
                    y: groundY - 85, // 숙이면 안 닿는 높이
                    width: 30,
                    height: 50,
                    type: "high"
                });
            } else {
                // 점프로 넘어야 하는 지상 장애물
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

        // 코인 생성
        function spawnCoin() {
            // 지상/공중 다양한 위치에 코인 배치
            const coinY = groundY - (Math.floor(Math.random() * 3) + 1) * 40;
            coinItems.push({
                x: canvas.width,
                y: coinY,
                radius: 12
            });
        }

        function update() {
            if (gameOver) return;

            frameCount++;
            score++;

            // 슬라이딩 상태 체크 (Down 화살표 또는 S키 누르고 있고, 땅에 있을 때만)
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

            // 착지 판정
            if (cookie.y + cookie.height >= groundY) {
                cookie.y = groundY - cookie.height;
                cookie.dy = 0;
                cookie.jumpCount = 0;
            }

            // 장애물 & 코인 생성 주기
            if (frameCount % 90 === 0) spawnObstacle();
            if (frameCount % 50 === 0) spawnCoin();

            // 장애물 이동 및 충돌 체크
            for (let i = obstacles.length - 1; i >= 0; i--) {
                const obs = obstacles[i];
                obs.x -= 6.5; // 속도 약간 상승

                // 충돌 감지 (AABB)
                if (
                    cookie.x < obs.x + obs.width &&
                    cookie.x + cookie.width > obs.x &&
                    cookie.y < obs.y + obs.height &&
                    cookie.y + cookie.height > obs.y
                ) {
                    gameOver = true;
                }

                if (obs.x + obs.width < 0) {
                    obstacles.splice(i, 1);
                }
            }

            // 코인 이동 및 획득 체크
            for (let i = coinItems.length - 1; i >= 0; i--) {
                const c = coinItems[i];
                c.x -= 6.5;

                const distX = (cookie.x + cookie.width / 2) - c.x;
                const distY = (cookie.y + cookie.height / 2) - c.y;
                const distance = Math.sqrt(distX * distX + distY * distY);

                if (distance < cookie.width / 2 + c.radius) {
                    coins += 10;
                    score += 50;
                    coinItems.splice(i, 1);
                } else if (c.x + c.radius < 0) {
                    coinItems.splice(i, 1);
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // 1. 바닥
            ctx.fillStyle = "#654321";
            ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);
            ctx.fillStyle = "#228B22";
            ctx.fillRect(0, groundY, canvas.width, 15);

            // 2. 쿠키(플레이어)
            ctx.fillStyle = "#D2691E";
            ctx.beginPath();
            ctx.roundRect(cookie.x, cookie.y, cookie.width, cookie.height, 8);
            ctx.fill();

            // 쿠키 눈 표현 (슬라이딩 시 표정 변화)
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

            // 3. 장애물 (유형별 색상 다르게 표시)
            obstacles.forEach(obs => {
                if (obs.type === "high") {
                    // 공중 장애물 (보라색/어두운 톤)
                    ctx.fillStyle = "#8A2BE2";
                    ctx.beginPath();
                    ctx.roundRect(obs.x, obs.y, obs.width, obs.height, [0, 0, 10, 10]);
                    ctx.fill();
                    // 경고 표시 텍스트
                    ctx.fillStyle = "#FFF";
                    ctx.font = "bold 12px Arial";
                    ctx.fillText("LOW", obs.x + 1, obs.y + 30);
                } else {
                    // 지상 장애물 (빨간색)
                    ctx.fillStyle = "#FF4500";
                    ctx.beginPath();
                    ctx.roundRect(obs.x, obs.y, obs.width, obs.height, [8, 8, 0, 0]);
                    ctx.fill();
                }
            });

            // 4. 코인
            ctx.fillStyle = "#FFD700";
            coinItems.forEach(c => {
                ctx.beginPath();
                ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = "#DAA520";
                ctx.lineWidth = 2;
                ctx.stroke();
            });

            // 5. UI
            ctx.fillStyle = "#222";
            ctx.font = "bold 18px Arial";
            ctx.fillText(`Score: ${score}`, 20, 35);
            ctx.fillText(`Coins: 🟡 ${coins}`, 20, 60);

            // 슬라이딩 상태 가이드 표시
            if (cookie.isSliding) {
                ctx.fillStyle = "#FF1493";
                ctx.font = "bold 14px Arial";
                ctx.fillText("SLIDE!", cookie.x, cookie.y - 10);
            }

            // 6. 게임 오버
            if (gameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#FFF";
                ctx.font = "bold 36px Arial";
                ctx.textAlign = "center";
                ctx.fillText("GAME OVER", canvas.width / 2, canvas.height / 2 - 20);

                ctx.font = "20px Arial";
                ctx.fillText("Space 또는 클릭으로 다시 시작", canvas.width / 2, canvas.height / 2 + 20);
                ctx.textAlign = "left";
            }
        }

        function animate() {
            update();
            draw();
            if (!gameOver) {
                requestAnimationFrame(animate);
            }
        }

        animate();
    </script>
</body>
</html>
"""

components.html(game_html, height=400)

st.markdown("---")
st.markdown("""
### 🎮 변경된 조작법
- **점프 / 2단 점프:** `Space` 또는 `↑(위 화살표)` 키 / 화면 마우스 클릭
- **슬라이딩:** `↓(아래 화살표)` 또는 `S` 키 누르고 있기
- **장애물 구분:**
  - 🔴 **빨간색 장애물:** 바닥 장애물 ➔ **점프**해서 회피
  - 🟣 **보라색 장애물(LOW):** 천장 장애물 ➔ **슬라이딩**해서 회피
""")
