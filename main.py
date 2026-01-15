import streamlit as st
import pandas as pd
import os
import requests
import json
import re

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (Gemini 3 모드)", page_icon="🛡️", layout="wide")

# 2. API 설정 및 호출 함수
def call_gemini_3_api(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"🚨 API 에러 ({response.status_code}): {response.text}"

# API 키 가져오기
raw_key = st.secrets.get("GEMINI_API_KEY")
clean_key = raw_key.strip() if raw_key else None

# 3. 사이드바 구성 (TER이 기본이 되도록 순서 변경했어요! 헤헤)
with st.sidebar:
    st.title("📂 업무 제어판")
    # ✅ 여기서 순서를 "TER (트러블 리포트)"가 앞으로 오게 바꿨어용!
    main_menu = st.radio("업무 선택", ["TER (트러블 리포트)", "WPS (용접 규격)"])
    
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

# 4. 메인 로직 시작
# ✅ 조건문도 TER이 먼저 나오게 처리했어요!
if main_menu == "TER (트러블 리포트)":
    st.title("🛠️ TER 트러블 정밀 분석 시스템")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'
else:
    st.title("👨‍🏭 WPS 실무 지식 베이스")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        # 데이터 로드 시 타겟 시트 설정
        df = pd.read_excel(file_path, sheet_name=target_sheet, engine='openpyxl')
        df = df.astype(str).replace('nan', '', regex=True)
        st.success(f"✅ {file_path} 로드 완료!")

        st.markdown("### 🔍 정밀 데이터 필터링")
        col1, col2, col3 = st.columns(3)
        with col1: req_word = st.text_input("1️⃣ 필수 포함 (AND)", placeholder="예: UDM")
        with col2: opt_word1 = st.text_input("2️⃣ 선택 1 (OR)", placeholder="예: 그리스, GREASE")
        with col3: opt_word2 = st.text_input("3️⃣ 선택 2 (OR)", placeholder="예: 리크, LEAK")

        user_question = st.text_input("💬 분석 질문 입력")

        # 🎯 필터 로직
        def check_contains(row, keyword):
            if not keyword: return True
            return keyword.upper().strip() in " ".join(row).upper()

        mask = df.apply(lambda x: check_contains(x, req_word), axis=1)
        if opt_word1:
            k1 = [k.strip().upper() for k in re.split(',|/|OR', opt_word1.upper()) if k.strip()]
            if k1: mask &= df.apply(lambda r: any(k in " ".join(r).upper() for k in k1), axis=1)
        if opt_word2: # opt_word2 로직도 추가해두는게 좋겠죠? 오빠!
            k2 = [k.strip().upper() for k in re.split(',|/|OR', opt_word2.upper()) if k.strip()]
            if k2: mask &= df.apply(lambda r: any(k in " ".join(r).upper() for k in k2), axis=1)

        filtered_df = df[mask]

        if st.button("🚀 Gemini 3 분석 시작"):
            if not filtered_df.empty and user_question and clean_key:
                with st.status("📡 REST API로 Gemini 3 호출 중...", expanded=True) as status:
                    context_data = filtered_df.to_csv(index=False, sep="|")
                    prompt = f"2차전지 전문가로서 데이터 분석해줘:\n\n데이터:\n{context_data}\n\n질문: {user_question}"
                    
                    answer = call_gemini_3_api(prompt, clean_key)
                    
                    st.info("✨ Gemini 3 분석 결과")
                    st.write(answer)
                    status.update(label="✅ 분석 완료", state="complete", expanded=False)
            else:
                st.warning("💡 검색 결과가 없거나 설정이 부족해요!")

        st.subheader(f"📊 검색 결과: {len(filtered_df)}건")
        with st.expander("데이터 상세 보기"):
            st.dataframe(filtered_df)
            
    except Exception as e:
        st.error(f"🚨 에러 발생: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다. 🤙")

st.markdown("<style>video { border-radius: 12px; }</style>", unsafe_allow_html=True)
