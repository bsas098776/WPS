import streamlit as st
import os

# --- [ 1. 페이지 기본 설정 ] ---
st.set_page_config(page_title="2차전지 장비 매니저 전용 비서", page_icon="🔋", layout="wide")

# --- [ 2. 사이드바 - 오빠의 전담 비서님 👩‍💼 ] ---
with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff4b91;'>💖 MY SECRETARY</h2>", unsafe_allow_html=True)
    
    # 깃허브에 올린 동영상 파일 이름
    video_path = "assistant.mp4"
    
    if os.path.exists(video_path):
        # 💡 오빠! 비서님이 무한 반복(loop)하면서 자동 재생(autoplay)되게 설정했어요!
        st.video(video_path, loop=True, autoplay=True, muted=True)
        st.markdown(
            """
            <div style="text-align: center; background-color: #fff0f5; padding: 10px; border-radius: 15px; border: 2px solid #ff4b91;">
                <p style="margin: 0; color: #ff4b91; font-weight: bold;">🌸 오빠, 오늘도 화이팅! 🌸</p>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">안성 공도읍 블루밍 오피스</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # 파일이 없을 경우를 대비한 귀여운 안내문! 잉잉..
        st.warning("🚨 'assistant.mp4' 파일을 찾을 수 없어요! 깃허브에 파일을 꼭 올려주세요, 오빠! 🤙")

    st.markdown("---")
    st.write("🔧 **시스템 정보**")
    st.caption("OS: Windows 11 Pro (24H2)")
    st.caption("Soft: ZWCAD 2024 / Office 2021")

# --- [ 3. 메인 화면 - 오빠와의 대화창 ] ---
st.title("🔋 2차전지 장비 매니저 시스템")
st.subheader(f"환영합니다, 매니저 오빠! 👋")

# 세션 상태 초기화 (대화 기록용)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력창
if prompt := st.chat_input("비서에게 궁금한 점을 물어보세요!"):
    # 오빠의 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 비서의 응답 (여기서는 예시 응답이에요!)
    response = f"네, 오빠! '{prompt}'에 대해 알아볼까요? 제가 안성 블루밍 아파트 서재에서 바로 도와드릴게요! 꺄하~ 😍"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- [ 4. 하단 스타일링 ] ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #fafafa;
    }
    [data-testid="stSidebar"] {
        background-color: #fff9fb;
    }
    </style>
    """,
    unsafe_allow_html=True
)
