import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import re

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (정밀 검색 모드)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정 (오빠의 소중한 API 키!)
def get_clean_key():
    raw_key = st.secrets.get("GEMINI_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")

clean_key = get_clean_key()
if clean_key:
    genai.configure(api_key=clean_key)
    model = genai.GenerativeModel('gemini-1.5-flash') 
else:
    st.error("🔑 Secrets에 키를 등록해주세요!")
    st.stop()

# 3. 사이드바 구성 (비서님은 아래로 쏙! 🤙)
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
        # 💡 오빠! 데이터 로드할 때 모든 값을 문자열로 미리 바꿔버릴게요 (검색 누락 방지!)
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS (용접 규격)" or target_sheet == 0) else 'TER', engine='openpyxl')
        df = df.fillna("") # 빈 칸 때문에 에러나는 거 방지!
        
        st.success(f"✅ {file_path} 로드 완료!")

        st.markdown("### 🔍 정밀 데이터 필터링")
        col1, col2, col3 = st.columns(3)
        with col1: req_word = st.text_input("1️⃣ 필수 포함 (AND)", placeholder="예: UDM")
        with col2: opt_word1 = st.text_input("2️⃣ 선택 1 (OR)", placeholder="예: 그리스, GREASE")
        with col3: opt_word2 = st.text_input("3️⃣ 선택 2 (OR)", placeholder="예: 리크, LEAK")

        user_question = st.text_input("💬 분석 질문 입력")

        # --- [ 🧠 엑셀 필터보다 더 독한 '포함' 로직! ] ---
        # 1. 각 행의 모든 데이터를 '그냥 하나의 긴 글자'로 합쳐버려요.
        #    (이렇게 하면 UDM이 어디에 박혀있든 무조건 걸려요! 🤙)
        def check_row(row, keyword):
            if not keyword: return True
            target = keyword.upper().strip()
            # 행 전체를 하나의 문자열로 합쳐서 대문자로 변환 후 포함 여부 확인
            row_content = " ".join(row.astype(str)).upper()
            return target in row_content

        # 필터링 시작
        mask = df.apply(lambda x: check_row(x, req_word), axis=1)

        # 선택 조건들 (OR)
        if opt_word1:
            k1_list = [k.strip().upper() for k in re.split(',|/|OR', opt_word1.upper()) if k.strip()]
            if k1_list:
                mask &= df.apply(lambda row: any(k in " ".join(row.astype(str)).upper() for k in k1_list), axis=1)

        if opt_word2:
            k2_list = [k.strip().upper() for k in re.split(',|/|OR', opt_word2.upper()) if k.strip()]
            if k2_list:
                mask &= df.apply(lambda row: any(k in " ".join(row.astype(str)).upper() for k in k2_list), axis=1)

        filtered_df = df[mask]

        # 6. 분석 및 결과 표시
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

        # 📊 건수 확인 (여기가 0이면 안돼요 오빠! 🤙)
        st.subheader(f"📊 검색 결과: {len(filtered_df)}건")
        with st.expander("데이터 상세 보기"):
            st.dataframe(filtered_df)
            
    except Exception as e:
        st.error(f"🚨 로드 에러: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다. 🤙")

st.markdown("<style>video { border-radius: 12px; }</style>", unsafe_allow_html=True)
