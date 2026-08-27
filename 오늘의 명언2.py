import random
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="오늘의 명언 - 영감을 주는 한 줄",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 사용자 지정 Custom CSS (커스텀 카드 디자인 및 애니메이션 효과)
st.markdown(
    """
<style>
    /* 전체 배경 및 폰트 개선 */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* 카드 컨테이너 스타일 */
    .quote-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%);
        border: 1px solid #E2E8F0;
        border-left: 6px solid #6366F1;
        border-radius: 16px;
        padding: 32px 28px;
        margin: 24px 0;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        transition: all 0.3s ease-in-out;
        position: relative;
    }
    
    .quote-icon {
        font-size: 2.5rem;
        color: #C7D2FE;
        line-height: 1;
        margin-bottom: 12px;
        font-family: Georgia, serif;
    }

    .quote-text {
        color: #1E293B;
        font-size: 1.35rem;
        font-weight: 600;
        line-height: 1.6;
        letter-spacing: -0.02em;
        margin-bottom: 20px;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }

    .quote-author {
        color: #64748B;
        font-size: 1.05rem;
        font-weight: 500;
        text-align: right;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 8px;
    }
    
    .quote-author::before {
        content: "";
        display: inline-block;
        width: 20px;
        height: 2px;
        background-color: #94A3B8;
    }

    /* 초기 안내 상자 커스텀 */
    .welcome-card {
        background-color: #EFF6FF;
        border: 1px dashed #93C5FD;
        border-radius: 14px;
        padding: 28px;
        text-align: center;
        color: #1E40AF;
        margin: 24px 0;
    }
    
    .welcome-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    
    .welcome-desc {
        font-size: 0.95rem;
        color: #3B82F6;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 풍부해진 명언 데이터베이스 (20개)
QUOTES = [
    {"quote": "성공은 매일 반복되는 작은 노력의 합이다.", "author": "로버트 콜리어"},
    {"quote": "시작하는 방법은 말하기를 그만두고 행동하는 것이다.", "author": "월트 디즈니"},
    {
        "quote": "미래를 예측하는 가장 좋은 방법은 미래를 창조하는 것이다.",
        "author": "피터 드러커",
    },
    {"quote": "실패는 성공을 맛붙이는 양념이다.", "author": "트루먼 카포티"},
    {
        "quote": "행복은 이미 완성된 것이 아니라 당신의 행동에서 나온다.",
        "author": "달라이 라마",
    },
    {
        "quote": "당신이 할 수 있다고 믿든 할 수 없다고 믿든, 당신이 옳다.",
        "author": "헨리 포드",
    },
    {"quote": "바람이 불지 않을 때 노를 저어라.", "author": "윈스턴 처칠"},
    {
        "quote": "위대한 일을 하는 유일한 방법은 당신이 하는 일을 사랑하는 것이다.",
        "author": "스티브 잡스",
    },
    {
        "quote": "꿈을 실현하는 가장 좋은 방법은 깨어있는 것이다.",
        "author": "폴 발레리",
    },
    {
        "quote": "위험을 무릅쓰지 않는 것이야말로 가장 큰 위험이다.",
        "author": "마크 저커버그",
    },
    {
        "quote": "어제와 똑같은 삶을 살면서 다른 미래를 기대하는 것은 정신병이다.",
        "author": "알베르트 아인슈타인",
    },
    {"quote": "행동은 모든 성공의 열쇠이다.", "author": "파블로 피카소"},
    {
        "quote": "가장 큰 영광은 넘어지지 않는 것이 아니라 넘어질 때마다 일어서는 것이다.",
        "author": "넬슨 만델라",
    },
    {"quote": "나중은 없다. 지금 하라.", "author": "작자 미상"},
    {
        "quote": "인생은 10%의 사건과 90%의 반응으로 이루어진다.",
        "author": "찰스 스윈돌",
    },
    {"quote": "단 하나의 촛불로 수천 개의 촛불을 켤 수 있다.", "author": "부처"},
    {"quote": "탁월함은 행동이 아니라 습관이다.", "author": "아리스토텔레스"},
    {
        "quote": "당신의 시간은 한정되어 있으니 다른 사람의 삶을 살며 낭비하지 마라.",
        "author": "스티브 잡스",
    },
    {"quote": "배움에는 끝이 없다.", "author": "레오나르도 다 빈치"},
    {
        "quote": "가장 아름다운 꿈은 실행에 옮겨진 꿈이다.",
        "author": "알렉산더 그레이엄 벨",
    },
]

# 헤더 영역
st.title("✨ 오늘의 명언")
st.caption("버튼을 누를 때마다 당신에게 영감을 주는 문장을 찾아드립니다.")

# 세션 상태 초기화
if "current_quote" not in st.session_state:
    st.session_state.current_quote = None

# 명언 보기 / 다시 뽑기 버튼
button_label = (
    "🎲 오늘의 명언 뽑기"
    if st.session_state.current_quote is None
    else "🔄 다른 명언 뽑기"
)

if st.button(button_label, use_container_width=True, type="primary"):
    st.session_state.current_quote = random.choice(QUOTES)

# 화면 출력 로직
if st.session_state.current_quote is None:
    st.markdown(
        """
        <div class="welcome-card">
            <div class="welcome-title">💡 준비되셨나요?</div>
            <div class="welcome-desc">상단의 버튼을 눌러 오늘의 마음을 깨우는 명언을 뽑아보세요!</div>
        </div>
    """,
        unsafe_allow_html=True,
    )
else:
    quote_data = st.session_state.current_quote

    # 세련된 CSS 커스텀 카드 출력
    st.markdown(
        f"""
        <div class="quote-card">
            <div class="quote-icon">“</div>
            <div class="quote-text">{quote_data['quote']}</div>
            <div class="quote-author">{quote_data['author']}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # st.toast를 이용한 알림 효과
    st.toast("새로운 명언이 전달되었습니다! 🎁")
