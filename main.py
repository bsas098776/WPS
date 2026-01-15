import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (전수 데이터 분석)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정
def get_clean_key():
    raw_key = st.secrets.get("GEMINI_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")

clean_key = get_clean_key()
if clean_key:
    genai.configure(api_key=clean_key)
    # 오빠 화면의 주인공! 2.5 Flash 모델 🤙
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (후보군 매칭 🤙)
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스 (전수 분석)")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템 (전수 분석)")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER')
        st.success(f"✅ {file_path} 로드 완료!")

        # 5. 질문 인터페이스
        user_question = st.text_input("💬 질문을 입력하세요 (예: INNO MIXER 그리스 리크 건 모두 요약해줘)")

        if st.button("🚀 분석 시작"):
            if user_question:
                # [상태 표시 시작] 오빠가 요청하신 '분석 완료' 기능을 위해 status 사용! 🤙
                with st.status("📡 데이터 최적화 분석 중...", expanded=True) as status:
                    try:
                        # [핵심] 이제 자르지 않고 전체 데이터를 CSV로 변환해서 보냅니다!
                        # 4.6MB 파일은 제미니 2.5 Flash에게 충분히 가벼워요 🚀
                        full_context = df.to_csv(index=False)
                        
                        prompt = f"""너는 2차전지 장비 전문가야. 제공된 전체 데이터를 보고 질문에 답해줘.
                        관련된 사례가 여러 개라면 하나도 빠짐없이 모두 요약해서 알려줘.
                        
                        [전체 데이터]
                        {full_context}
                        
                        [질문]
                        {user_question}
                        """
                        
                        response = model.generate_content(prompt)
                        
                        # 분석 결과 출력
                        st.info("✨ 분석 결과")
                        st.write(response.text)
                        
                        # [오빠 요청 반영] 분석이 끝나면 문구 변경! 🤙✨
                        status.update(label="✅ 데이터 최적화 분석 완료", state="complete", expanded=False)
                        
                    except Exception as e:
                        st.error(f"🚨 엔진 에러: {e}")
                        status.update(label="❌ 분석 실패", state="error")
            else:
                st.warning("💡 질문을 입력해 주세요!")

        with st.expander("📊 데이터 전체 보기"):
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"🚨 파일 로드 에러: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다.")
