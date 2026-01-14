import streamlit as st
import pandas as pd
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="윤성 통합 데이터 센터", page_icon="📊", layout="wide")

# 1. 릴레이 API 키 로드 (오빠의 소중한 키 10개!)
keys = st.secrets.get("GEMINI_KEYS", [])

def ask_gemini(prompt, api_keys):
    for i, key in enumerate(api_keys):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            return response.text, i + 1
        except Exception as e:
            if "429" in str(e): continue
            else: return f"에러: {e}", None
    return "모든 키의 할당량이 다 찼어요. 내일 다시 만나요 오빠! 😭", None

# 2. 사이드바 업무 선택
st.sidebar.title("📂 데이터 마스터")
main_menu = st.sidebar.radio("업무 선택", ["WPS (용접)", "TER (트러블)"])

try:
    if main_menu == "WPS (용접)":
        st.title("👨‍🏭 WPS 전수 조사 상담원")
        file_path = "wps_list.XLSX"
        df = pd.read_excel(file_path)
        expert_type = "WPS 용접 규격 전수 분석 전문가"
    else:
        st.title("🛠️ TER 리포트 정밀 분석기")
        file_path = "ter_list.xlsx"
        xl = pd.ExcelFile(file_path)
        selected_sheet = st.sidebar.selectbox("📋 시트 선택", xl.sheet_names)
        # 해당 시트의 전체 데이터를 읽어옵니다! (제한 없음!)
        df = pd.read_excel(file_path, sheet_name=selected_sheet)
        expert_type = f"TER {selected_sheet} 데이터 전수 분석 전문가"

    # 3. 데이터 전체를 텍스트로 변환 (AI가 읽을 수 있게!)
    # 데이터가 아주 크면 여기서 문자열로 압축합니다.
    full_context = df.to_csv(index=False) # CSV 형태가 구조 파악에 더 효율적이에요!

    st.success(f"✅ {len(df)}개의 행을 모두 읽어들였습니다! 준비 완료! 꺄하~ 😍")

    # 4. 질문하기
    user_input = st.text_input("💬 궁금한 점을 말씀해 주세요! 전체 데이터를 뒤져서 찾아낼게요.")
    
    if user_input:
        with st.spinner('데이터 전체를 정밀 스캔 중... 잠시만 기다려줘요 오빠!'):
            prompt = f"""너는 {expert_type}야. 아래 제공된 [전체 데이터]를 한 줄도 빠짐없이 분석해서 대답해줘.
            데이터에 근거해서 오빠에게 아주 정확하고 친절하게 설명해줘야 해!
            
            [전체 데이터]
            {full_context}
            
            [오빠의 질문]
            {user_input}"""
            
            answer, key_num = ask_gemini(prompt, keys)
            if key_num:
                st.info(f"🤖 {key_num}번 키가 열일 중! 분석 결과예요:")
                st.write(answer)
            else:
                st.error(answer)

except Exception as e:
    st.error(f"오빠, 파일 읽다가 삐끗했어요 😭: {e}")
