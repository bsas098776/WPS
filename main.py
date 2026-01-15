import streamlit as st
import os

# --- [ 1. 페이지 설정 ] ---
st.set_page_config(page_title="2차전지 장비 매니저 전용 비서", page_icon="🔋", layout="wide")

# --- [ 2. 사이드바 - 오빠의 전담 비서님 👩‍💼 ] ---
with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff4b91;'>💖 MY SECRETARY</h2>", unsafe_allow_html=True)
    
    # 💡 오빠! 파일 이름을 오빠가 말씀하신 대로 바꿨어요!
    video_path = "assistant.mp4.mp4" 
    
    if os.path.exists(video_path):
        # 무한 반복(loop), 자동 재생(autoplay), 소리 끔(muted) 🤙
        st.video(video_path, loop=True, autoplay=True, muted=True)
        st.markdown(
            """
            <div style="text-align: center; background-color: #fff0f5; padding: 10px; border-radius: 15px; border: 2px solid #ff4b91;">
                <p style="margin: 0; color: #ff4b91; font-weight: bold;">🌸 오빠, 비서님 출근했어요! 🌸</p>
                <p style="margin: 0; font-size: 0.8rem; color: #666;">안성 공도읍 블루밍 오피스</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # 파일이 없을 때 오빠를 위한 친절한 안내! 잉잉..
        st.error(f"🚨 '{video_path}' 파일을 찾을 수 없어요!")
        st.info("💡 깃허브에 올린 파일 이름이 'assistant.mp4.mp4'가 맞는지 다시 한 번만 봐주세요, 오빠! 🤙")

    st.markdown("---")
    st.caption("OS: Windows 11 Pro / Soft: Office 2021")

# --- [ 3. 메인 화면 - 오빠와의 대화창 ] ---
st.title("🔋 2차전지 장비 매니저 시스템")
st.subheader(f"환영합니다, 매니저 오빠! 👋")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("비서에게 궁금한 점을 물어보세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = f"네, 오빠! 안성 블루밍 아파트 서재에서 제가 바로 알아볼게요! 꺄하~ 😍"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- [ 4. 배경 스타일링 ] ---
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #fff9fb;
    }
    </style>
    """,
    unsafe_allow_html=True
)
