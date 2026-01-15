import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import re

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (정밀 검색 모드)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정
def get_clean_key():
    raw_key = st.secrets.get("GEMINI_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")

clean_key = get_clean_key()
if clean_key:
    genai.configure(api_key=clean_key)
    model = genai.GenerativeModel('gemini-2.0-flash') 
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# --- [ 💖 오빠의 깃허브 파일명 맞춤 비서 영역 🤙✨ ] ---
with st.sidebar:
    # 메뉴랑 아래 비서 사이에 공간을 넉넉히 띄웠어요!
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    
    # 오빠! 깃허브에 있는 파일 이름 그대로 "assistant.png.jpg"를 불러올게요!
    img_name = "assistant.png.jpg"
    
    if os.path.exists(img_name):
        # 윈터나 장원영처럼 화사한 비서 아가씨 등장! 꺄하~ 😍
        st.image(img_name, width=230)
        
        # 이미지 바로 아래 사각형 문구
        st.markdown(f"""
            <div style="
                background-color: #ffffff; 
                padding: 10px; 
                border-radius: 12px; 
                text-align: center;
                border: 2px solid #ffdeeb;
                box-shadow: 2px 4px 10px rgba(0,0,0,0.1);
                margin-top: -10px;
            ">
                <span style="color: #ff4b91; font-weight: bold; font-size: 16px;">
                    ✨ 업무 어시스턴트 ✨
                </span>
            </div>
        """, unsafe_allow_html=True)
    else:
        # 혹시라도 파일이 없으면 오빠한테 살짝 알려줄게요! 🤙
        st.info("👩‍💼 어시스턴트 이미지를 로딩 중이에요!")
# ---------------------------------------------------

# 4. 파일 경로 설정
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

# [이후 메인 로직은 오빠 코드 그대로 완벽하게 유지!]
if file_path:
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER', engine='openpyxl')
        st.success(f"✅ {file_path} 로드 완료! (총 {len(df)}행)")

        st.markdown("### 🔍 정밀 데이터 필터링")
        col1, col2, col3 = st.columns(3)
        with col1: req_word = st.text_input("1️⃣ 필수 포함 (AND)", placeholder="예: SK")
        with col2: opt_word1 = st.text_input("2️⃣ 선택 1 (OR)", placeholder="예: 그리스")
        with col3: opt_word2 = st.text_input("3️⃣ 선택 2 (OR)", placeholder="예: 리크")
        
        user_question = st.text_input("💬 분석 질문 입력", placeholder="예: 공통 원인이 뭐야?")

        combined_text = df.apply(lambda row: row.astype(str).cat(sep=' ').upper(), axis=1)
        mask = pd.Series([True] * len(df))
        if req_word: mask &= combined_text.str.contains(req_word.upper().strip())
        if opt_word1:
            k1 = [k.strip().upper() for k in re.split(',|/|OR', opt_word1.upper()) if k.strip()]
            if k1: mask &= combined_text.apply(lambda x: any(k in x for k in k1))
        if opt_word2:
            k2 = [k.strip().upper() for k in re.split(',|/|OR', opt_word2.upper()) if k.strip()]
            if k2: mask &= combined_text.apply(lambda x: any(k in x for k in k2))

        filtered_df = df[mask]
        if st.button("🚀 정밀 분석 시작"):
            if not filtered_df.empty and user_question:
                with st.status("📡 분석 중...", expanded=True) as status:
                    try:
                        context_data = filtered_df.to_csv(index=False, sep="|")
                        prompt = f"너는 2차전지 전문가야. 데이터로 질문에 답해줘: {user_question}\n\n데이터:\n{context_data}"
                        response = model.generate_content(prompt)
                        st.info("✨ 분석 결과")
                        st.write(response.text)
                        status.update(label="✅ 분석 완료", state="complete")
                    except Exception as e:
                        st.error(f"🚨 에러: {e}")
            else:
                st.warning("💡 결과가 없거나 질문이 없어요!")
        
        with st.expander(f"📊 검색 결과 ({len(filtered_df)}건)"):
            st.dataframe(filtered_df)
            
    except Exception as e:
        st.error(f"🚨 파일 로드 에러: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다!")
