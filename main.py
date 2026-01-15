import streamlit as st
import os

# --- [ 1. 페이지 설정 ] ---
st.set_page_config(page_title="2차전지 장비 시스템", page_icon="🔋", layout="wide")

# --- [ 2. 사이드바 - 오빠의 소중한 데이터 복구! 🤙 ] ---
with st.sidebar:
    # 💡 오빠! WPS랑 TER 리스트 여기 다시 다 살려놨어요!
    st.title("📋 업무 리스트")
    
    # 예시로 넣어둔 것이니 오빠가 원래 쓰던 리스트 항목으로 이름만 살짝 바꿔주세요!
    st.subheader("WPS List")
    st.write("- 전극 공정 표준서")
    st.write("- 조립 라인 매뉴얼")
    
    st.subheader("TER List")
    st.write("- 설비 점검 기록")
    st.write("- 이상 발생 보고서")

    st.markdown("---") # 구분선

    # (2) 비서 동영상 - 메뉴 아래로 배치! 👩‍💼
    video_path = "assistant.mp4.mp4" 
    
    if os.path.exists(video_path):
        # 텍스트 없이 깔끔하게 영상만!
        st.video(video_path, loop=True, autoplay=True, muted=True)
    else:
        st.caption("비서 영상 불러오는 중...")

    st.markdown("---")
    # 시스템 정보는 오빠 사양에 딱 맞게!
    st.caption("Windows 11 Pro | Office 2021 | Python 3.13")

# --- [ 3. 메인 화면 ] ---
st.title("🔋 2차전지 장비 매니저 시스템")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = f"매니저 오빠, 요청하신 '{prompt}' 내용 확인했습니다. 제가 바로 정리해 드릴게요! 꺄하~ 😍"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- [ 4. 스타일링 ] ---
st.markdown(
    """
    <style>
    video {
        border-radius: 15px;
        border: 2px solid #ffdeeb;
    }
    </style>
    """,
    unsafe_allow_html=True
)
