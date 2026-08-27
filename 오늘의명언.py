import random
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="오늘의 명언", page_icon="📜", layout="centered")

# 명언 데이터베이스 (리스트 형태)
QUOTES = [
    {
        "quote": "성공은 매일 반복되는 작은 노력의 합이다.",
        "author": "로버트 콜리어",
    },
    {"quote": "시작하는 방법은 말하기를 그만두고 행동하는 것이다.", "author": "월트 디즈니"},
    {
        "quote": "미래를 예측하는 가장 좋은 방법은 미래를 창조하는 것이다.",
        "author": "피터 드러커",
    },
    {
        "quote": "실패는 성공을 맛붙이는 양념이다.",
        "author": "트루먼 카포티",
    },
    {
        "quote": "행복은 이미 완성된 것이 아니라 당신의 행동에서 나온다.",
        "author": "달라이 라마",
    },
]

# 제목 영역
st.title("📜 오늘의 명언")
st.caption("버튼을 눌러 오늘의 동기부여 문구를 확인해보세요!")

st.divider()

# 세션 상태(Session State) 초기화
if "current_quote" not in st.session_state:
    st.session_state.current_quote = random.choice(QUOTES)

# 명언 출력 영역
quote_data = st.session_state.current_quote
st.subheader(f'"{quote_data["quote"]}"')
st.write(f"- **{quote_data["author"]}**")

st.divider()

# 새로운 명언 불러오기 버튼
if st.button("🎲 다른 명언 보기", use_container_width=True):
    st.session_state.current_quote = random.choice(QUOTES)
    st.rerun()
