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
    # 💡 오빠! 사진에서 확인한 'gemini-3-flash'로 모델명을 고정했어요! 🤙✨
    model = genai.GenerativeModel('gemini-3-flash') 
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 구성 (메뉴와 비서님 공간 분리 😍)
with st.sidebar:
    st.title("📂 업무 제어판")
    main_menu = st.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])
    
    # 메뉴랑 비서님 사이 거리 두기 (안성 블루밍 오피스 스타일 🤙)
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
        # 데이터 로드 (모든 데이터를 문자로 강제 변환해서 검색 누락 방지! 🤙)
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS (용접 규격)" or target_sheet == 0) else 'TER', engine='openpyxl')
        df = df.astype(str).replace('nan', '', regex=True)
        
        st.success(f"✅ {file_path} 로드 완료!")

        # 6. 정밀 검색 인터페이스
        st.markdown("### 🔍 정밀 데이터 필터링")
        col1, col2, col3 = st.columns(3)
        with col1: req_word = st.text_input("1️⃣ 필수 포함 (AND)", placeholder="예: UDM")
        with col2: opt_word1 = st.text_input("2️⃣ 선택 1 (OR)", placeholder="예: 그리스, GREASE")
        with col3: opt_word2 = st.text_input("3️⃣ 선택 2 (OR)", placeholder="예: 리크, LEAK")

        user_question = st.text_input("💬 분석 질문 입력")

        # 🎯 [ 엑셀 필터보다 독한 '무조건 포함' 로직! ]
        def check_contains(row, keyword):
            if not keyword: return True
            # 모든 셀을 합쳐서 대문자로 변환 후 검색어가 들어있는지만 확인! 🤙
            full_row_text = " ".join(row).upper()
            return keyword.upper().strip() in full_row_text

        # 필터링 적용 (오빠가 찾던 UDM, 여기서 다 걸려요! 😍)
        mask = df.apply(lambda x: check_contains(x, req_word), axis=1)

        if opt_word1:
            k1 = [k.strip().upper() for k in re.split(',|/|OR', opt_word1.upper()) if k.strip()]
            if k1: mask &= df.apply(lambda r: any(k in " ".join(r).upper() for k in k1), axis=1)

        if opt_word2:
            k2 = [k.strip().upper() for k in re.split(',|/|OR', opt_word2.upper()) if k.strip()]
            if k2: mask &= df.apply(lambda r: any(k in " ".join(r).upper() for k in k2), axis=1)

        filtered_df = df[mask]

        # 7. Gemini 3 Flash 분석 진행
        if st.button("🚀 정밀 분석 시작"):
            if not filtered_df.empty and user_question:
                with st.status("📡 Gemini 3 Flash 초고속 분석 중...", expanded=True) as status:
                    try:
                        context_data = filtered_df.to_csv(index=False, sep="|")
                        prompt = f"너는 2차전지 전문가야. 제공된 데이터로 질문에 답해줘. 관련 사례가 여러 개면 요약해줘야 해.\n\n데이터:\n{context_data}\n\n질문: {user_question}"
                        
                        response = model.generate_content(prompt)
                        st.info("✨ 분석 결과")
                        st.write(response.text)
                        status.update(label="✅ 분석 완료", state="complete", expanded=False)
                    except Exception as e:
                        st.error(f"🚨 엔진 에러: {e}")
            else:
                st.warning("💡 검색 결과가 없거나 질문이 비어있어요!")

        # 📊 검색 결과 건수 표시 (여기가 0이면 안돼요! 🤙)
        st.subheader(f"📊 검색 결과 보기: {len(filtered_df)}건")
        with st.expander("데이터 상세 보기"):
            if not filtered_df.empty:
                st.dataframe(filtered_df)
            else:
                st.write("검색 조건을 확인해 주세요. 🤙")
            
    except Exception as e:
        st.error(f"🚨 로드 에러: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다. 🤙")

# 스타일링 (영상 둥글게!)
st.markdown("<style>video { border-radius: 12px; }</style>", unsafe_allow_html=True)
