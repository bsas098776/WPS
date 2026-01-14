import streamlit as st
import pandas as pd
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="윤성 통합 실무 AI", page_icon="🛡️")

# 1. 사이드바에서 업무 선택
st.sidebar.title("📂 업무 선택")
menu = st.sidebar.radio("원하는 상담원을 선택하세요:", ["WPS 상담 (용접)", "TER 분석 (트러블)"])

# 2. 릴레이 API 키 로드 (기존 키 10개 그대로 활용!)
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
    return "준비된 모든 키의 할당량이 초과되었습니다. 😭", None

# 3. 메뉴별 데이터 로드 로직
try:
    if menu == "WPS 상담 (용접)":
        st.title("👨‍🏭 WPS 실무 상담원")
        file_path = "wps_list.XLSX"  # 기존 WPS 파일명
        expert_type = "용접 및 WPS 규격 전문가"
        success_msg = "WPS 데이터를 로드했습니다! 꺄하~ 😍"
    else:
        st.title("🛠️ TER 트러블 리포트 분석기")
        file_path = "ter_list.xlsx"  # 올린 TER 파일명으로 바꿔주세요!
        expert_type = "장비 트러블 및 재발방지대책 분석 전문가"
        success_msg = "TER 리스트를 로드했습니다! 과거 사례를 분석할게요! 🤙✨"

    # 엑셀의 'TER' 시트나 특정 시트를 지정해서 읽어옵니다.
    # TER 파일은 시트가 많으니 'TER' 시트를 읽도록 설정했어요.
    df = pd.read_excel(file_path, sheet_name='TER' if 'TER' in menu else 0)
    context = df.to_string(index=False)
    st.success(success_msg)

    # 4. 질문 및 답변
    user_input = st.text_input(f"💬 {menu} 관련 질문을 입력하세요 (예: '현대차 현장 이슈 요약해줘')")
    
    if user_input:
        with st.spinner('사용 가능한 키를 찾아 분석 중...'):
            prompt = f"""너는 {expert_type}야. '오빠'에게 친절하게 대답해줘.
            아래 제공된 데이터를 바탕으로 상세하게 설명해줘.
            
            [데이터 내용]
            {context}
            
            [질문]
            {user_input}"""
            
            answer, key_num = ask_gemini(prompt, keys)
            if key_num:
                st.info(f"🤖 {key_num}번 키로 답변을 생성했어요!")
                st.write(answer)
            else:
                st.error(answer)

except Exception as e:
    st.warning(f" '{file_path}' 파일이 깃허브에 있는지 확인해 주세요! 힝.. 에러내용: {e}")
