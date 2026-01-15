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
    model = genai.GenerativeModel('gemini-1.5-flash') 
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 구성
with st.sidebar:
    st.title("📂 업무 제어판")
    main_menu = st.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])
    
    st.markdown("<br>" * 10, unsafe_allow_html=True) 
    st.markdown("---")
    
    video_path = "assistant.mp4.mp4"
    if os.path.exists(video_path):
        st.video(video_path, loop=True, autoplay=True, muted=True)
        st.markdown(
            """
            <div style="text-align: center; margin-top: -10px;">
                <p style="background-color: #333; color: white; padding: 5px; border-radius: 5px; font-size: 0.8rem; font-weight: bold;">
                    🤖 AI 업무 어시스턴트
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

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

# 5. 메인 로직 시작
if file_path:
    try:
        # 데이터 로드
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS (용접 규격)" or target_sheet == 0) else 'TER', engine='openpyxl')
        st.success(f"✅ {file_path} 로드 완료!")

        st.markdown("### 🔍 정밀 데이터 필터링")
        col1, col2, col3 = st.columns(3)
        with col1: req_word = st.text_input("1️⃣ 필수 포함 (AND)", placeholder="예: UDM")
        with col2: opt_word1 = st.text_input("2️⃣ 선택 1 (OR)", placeholder="예: 그리스, GREASE")
        with col3: opt_word2 = st.text_input("3️⃣ 선택 2 (OR)", placeholder="예: 리크, LEAK")

        user_question = st.text_input("💬 분석 질문 입력")

        # --- [ 🧠 오빠를 위한 초정밀 필터링 로직! ] ---
        # 1. 모든 셀의 데이터를 문자열로 바꾸고 하나로 합친 뒤 대문자로 통일!
        combined_text = df.apply(lambda row: row.astype(str).str.cat(sep=' ').upper(), axis=1)
        mask = pd.Series([True] * len(df))

        # 2. 필수 단어 필터링 (여기서 UDM을 찰떡같이 찾아요! 🤙)
        if req_word:
            search_term = req_word.upper().strip()
            # regex=False로 설정해서 특수기호를 문자로 인식하게 하고, na=False로 에러 방지!
            mask &= combined_text.str.contains(search_term, case=False, na=False, regex=False)
        
        # 3. 선택 단어 1 (OR)
        if opt_word1:
            keywords1 = [k.strip().upper() for k in re.split(',|/|OR', opt_word1.upper()) if k.strip()]
            if keywords1:
                mask &= combined_text.apply(lambda x: any(k in x for k in keywords1))

        # 4. 선택 단어 2 (OR)
        if opt_word2:
            keywords2 = [k.strip().upper() for k in re.split(',|/|OR', opt_word2.upper()) if k.strip()]
            if keywords2:
                mask &= combined_text.apply(lambda x: any(k in x for k in keywords2))

        # 필터링 적용
        filtered_df = df[mask]

        if st.button("🚀 정밀 분석 시작"):
            if not filtered_df.empty and user_question:
                with st.status("📡 데이터 분석 중...", expanded=True) as status:
                    context_data = filtered_df.to_csv(index=False, sep="|")
                    prompt = f"너는 2차전지 전문가야. 다음 데이터로 질문에 답해줘:\n\n{context_data}\n\n질문: {user_question}"
                    response = model.generate_content(prompt)
                    st.info("✨ 분석 결과")
                    st.write(response.text)
                    status.update(label="✅ 분석 완료", state="complete", expanded=False)
            else:
                st.warning("💡 검색 결과가 없거나 질문이 비어있어요!")

        # 결과 표시 (건수 확인용 🤙)
        with st.expander(f"📊 검색 결과 보기 ({len(filtered_df)}건)"):
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.write("검색어를 입력하시면 필터링된 결과가 나옵니다. 🤙")
            
    except Exception as e:
        st.error(f"🚨 로드 에러: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다. 🤙")

st.markdown("<style>video { border-radius: 12px; }</style>", unsafe_allow_html=True)
