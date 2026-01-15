import streamlit as st
import os

# --- [ 1. 페이지 설정 ] ---
st.set_page_config(page_title="2차전지 장비 매니저 시스템", page_icon="🔋", layout="wide")

# --- [ 2. 사이드바 구성 ] ---
with st.sidebar:
    # (1) 원래 좌측에 있던 메뉴들 (예시로 넣어둘게요!)
    st.title("⚙️ 장비 관리 메뉴")
    st.selectbox("공정 선택", ["전극 공정", "조립 공정", "활성화 공정"])
    st.button("실시간 리포트 생성")
    
    st.markdown("---") # 구분선 하나 긋고!

    # (2) 비서 동영상을 메뉴 아래로 배치!
    video_path = "assistant.mp4.mp4" 
    
    if os.path.exists(video_path):
        # 글자 다 빼고 영상만 깔끔하게! 
        # width 조절로 사이드바에 딱 맞게 세팅했어요 🤙
        st.video(video_path, loop=True, autoplay=True, muted=True)
    else:
        st.caption("비서 영상 대기 중...")

    # (3) 시스템 정보는 맨 아래에 작게!
    st.markdown("---")
    st.caption("Windows 11 Pro | Office 2021 | ZWCAD 2024")

# --- [ 3. 메인 화면 ] ---
st.title("🔋 2차전지 장비 매니저 시스템")
st.subheader("실시간 모니터링 및 비서 지원")

# 대화 기록 및 채팅 기능
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 응답도 오빠 소리 빼고 깔끔하게!
    response = f"매니저님, 요청하신 '{prompt}'에 대한 데이터를 분석 중입니다."
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- [ 4. 스타일링 ] ---
st.markdown(
    """
    <style>
    /* 영상 모서리를 둥글게 만들어서 더 세련되게! */
    video {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
