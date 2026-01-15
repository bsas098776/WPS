import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# 1. 페이지 설정 (매니저님 오빠를 위한 깔끔한 레이아웃 🤙)
st.set_page_config(page_title="윤성 AI (전수 데이터 분석)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정 (Secrets 관리 필수!)
def get_clean_key():
    raw_key = st.secrets.get("GEMINI_API_KEY")
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")

clean_key = get_clean_key()
if clean_key:
    genai.configure(api_key=clean_key)
    # 오빠 화면에 떠 있는 그 모델! gemini-2.5-flash 🤙
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.error("🔑 Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 제어판
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (Zip 에러 방지 및 엔진 최적화 🛠️)
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
        # engine='openpyxl' 추가로 파일 로드 안정성 강화! 🤙
        df = pd.read_excel(file_path, 
                           sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER',
                           engine='openpyxl')
        st.success(f"✅ {file_path} 로드 완료! (데이터 수: {len(df)}행)")

        # 5. 질문 인터페이스
        user_question = st.text_input("💬 질문을 입력하세요 (예: INNO MIXER 그리스 리크 건 모두 요약해줘)")

        if st.button("🚀 분석 시작"):
            if user_question:
                # 상태 표시 시작!
                with st.status("📡 데이터 최적화 분석 중...", expanded=True) as status:
                    try:
                        # [데이터 다이어트] 토큰 절약을 위해 불필요한 공백 제거
                        cleaned_df = df.dropna(how='all')
                        # CSV 압축형태로 제미니에게 전달 (전수 분석용)
                        full_context = cleaned_df.to_csv(index=False, sep="|")
                        
                        prompt = f"""너는 2차전지 장비 전문가야. 제공된 데이터를 분석해서 질문에 답해줘.
                        관련된 사례가 여러 개라면 빠짐없이 모두 요약해줘야 해.
                        
                        [데이터베이스]
                        {full_context}
                        
                        [질문]
                        {user_question}
                        """
                        
                        # 제미니 답변 생성
                        response = model.generate_content(prompt)
                        
                        st.info("✨ 분석 결과")
                        st.write(response.text)
                        
                        # 오빠가 요청한 문구로 상태 업데이트! 🤙✨
                        status.update(label="✅ 데이터 최적화 분석 완료", state="complete", expanded=False)
                        
                    except Exception as e:
                        # 429 에러(한도 초과) 발생 시 친절하게 안내
                        if "429" in str(e):
                            st.error("🚨 제미니가 지금 너무 바빠요(분당 한도 초과)! 무료 버전은 1분에 한 번만 전수 분석이 가능하니 1분 뒤에 다시 시도해 주세요. 😭")
                        else:
                            st.error(f"🚨 엔진 에러: {e}")
                        status.update(label="❌ 분석 실패", state="error")
            else:
                st.warning("💡 분석하고 싶은 질문을 입력해 주세요!")

        with st.expander("📊 데이터 전체 보기 (원본 확인용)"):
            st.dataframe(df)
            
    except Exception as e:
        # "File is not a zip file" 에러 등이 나면 여기서 잡혀요!
        st.error(f"🚨 파일 로드 에러: {e}")
        st.info("💡 팁: 엑셀 파일을 'Excel 통합 문서(.xlsx)' 형식으로 다시 저장해서 올려보세요!")
else:
    st.error("❌ 분석할 엑셀 파일을 찾을 수 없습니다. 파일명을 확인해 주세요!")
