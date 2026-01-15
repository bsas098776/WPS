import streamlit as st
import pandas as pd
import os
import google.generativeai as genai # 제미니 엔진 장착! 🤙

# 1. 페이지 설정
st.set_page_config(page_title="윤성 AI (Gemini 2.5 무적 모드)", page_icon="🛡️", layout="wide")

# 2. Gemini API 설정
def get_clean_key():
    raw_key = st.secrets.get("GEMINI_API_KEY") # Secrets 이름 확인!
    if not raw_key: return None
    return raw_key.strip().replace("\n", "").replace("\r", "").replace(" ", "").strip('"').strip("'")

clean_key = get_clean_key()
if clean_key:
    genai.configure(api_key=clean_key)
    # 오빠 화면에서 확인한 가장 최신 모델! 🤙
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.error("🔑 Secrets에 GEMINI_API_KEY를 등록해주세요!")
    st.stop()

# 3. 사이드바 업무 선택
st.sidebar.title("📂 업무 제어판")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접 규격)", "TER (트러블 리포트)"])

# 4. 파일 로드 (오빠의 파일명 후보들 🤙)
if main_menu == "WPS (용접 규격)":
    st.title("👨‍🏭 WPS 실무 지식 베이스 (Gemini)")
    candidates = ["wps_list.XLSX", "wps_list.xlsx"]
    target_sheet = 0
else:
    st.title("🛠️ TER 트러블 정밀 분석 시스템 (Gemini)")
    candidates = ["ter_list.xlsx.xlsx", "ter_list.xlsx", "ter_list.XLSX", "TER LIST.XLSX"]
    target_sheet = 'TER'

file_path = next((f for f in candidates if os.path.exists(f)), None)

if file_path:
    try:
        # 엑셀 읽기
        df = pd.read_excel(file_path, sheet_name=target_sheet if (main_menu == "WPS" or target_sheet == 0) else 'TER')
        st.success(f"✅ {file_path} 로드 완료!")

        # 5. [안전 밸브] 검색 및 질문 🤙
        search_keyword = st.text_input("🔍 찾고 싶은 핵심 단어 하나만 입력 (예: INNO, 그리스, 리크)")
        user_question = st.text_input("💬 질문을 입력하세요")

        if st.button("🚀 분석 시작"):
            if search_keyword and user_question:
                with st.status("📡 제미니가 데이터 정밀 여과 중..."):
                    # 1. 키워드 포함 행 찾기
                    mask = df.apply(lambda row: row.astype(str).str.contains(search_keyword, case=False).any(), axis=1)
                    filtered_df = df[mask]

                    if not filtered_df.empty:
                        # [핵심] 제미니 2.5 Flash 한도에 맞춰 상위 20개까지는 넉넉하게 보낼 수 있어요! 🤙
                        # 그록보다 입이 커서 20개도 충분해요!
                        small_context = filtered_df.head(20).to_csv(index=False)
                        
                        try:
                            # 제미니 프롬프트 구성
                            prompt = f"""너는 2차전지 장비 전문 업체 '윤성'의 전문가야. 
                            제공된 검색 결과 데이터를 바탕으로 질문에 짧고 명확하게 답해줘.
                            
                            [검색된 데이터]
                            {small_context}
                            
                            [질문]
                            {user_question}
                            """
                            
                            response = model.generate_content(prompt)
                            st.info(f"✨ '{search_keyword}' 관련 제미니 분석 결과")
                            st.write(response.text)
                            
                        except Exception as e:
                            st.error(f"🚨 제미니 엔진 에러: {e}")
                    else:
                        st.warning(f"😭 '{search_keyword}'를 찾을 수 없어요. 단어를 바꿔볼까요?")
            else:
                st.warning("💡 키워드와 질문을 모두 입력해 주세요!")

        with st.expander("📊 데이터 전체 보기 (직접 확인용)"):
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"🚨 파일 로드 에러: {e}")
else:
    st.error("❌ 파일을 찾을 수 없습니다.")
