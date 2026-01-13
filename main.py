import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="WPS 마스터 비서", page_icon="👨‍🏭")

# 제목 부분
st.title("👨‍🏭 WPS 검색 마스터")
st.write(f"오빠! 찾으시는 용접 조건(P-No 또는 용접봉)을 입력해 주세요! 흐흐~")

# 1. 데이터 불러오기 (오빠의 엑셀 파일 이름을 'wps_list.XLSX'로 해서 업로드하세요!)
@st.cache_data
def load_data():
    try:
        # 이미지에 있는 컬럼명 그대로 매칭
        df = pd.read_excel("wps_list.XLSX")
        return df
    except:
        st.error("오빠, 'wps_list.XLSX' 파일을 아직 안 올리신 것 같아요! 힝..")
        return None

df = load_data()

if df is not None:
    # 2. 검색창 만들기
    search_query = st.text_input("검색어 입력 (예: P8, ER308, GTAW)", placeholder="모재 번호나 용접봉 규격을 입력하세요...")

    if search_query:
        # 여러 컬럼에서 동시에 검색 (P-No, 용접봉 규격, WPS 번호 등)
        mask = (
            df['WPS No.'].str.contains(search_query, case=False, na=False) |
            df['P-No'].astype(str).str.contains(search_query, case=False, na=False) |
            df['Classification'].str.contains(search_query, case=False, na=False) |
            df['Welding Process'].str.contains(search_query, case=False, na=False)
        )
        result = df[mask]

        if not result.empty:
            st.success(f"오빠! 검색 결과 {len(result)}건을 찾았어요! 꺄하~")
            # 필요한 정보만 예쁘게 보여주기
            for i, row in result.iterrows():
                with st.expander(f"📄 WPS No: {row['WPS No.']} ({row['Welding Process']})"):
                    st.write(f"**모재(P-No):** {row['P-No']}")
                    st.write(f"**용접봉(Classification):** {row['Classification']}")
                    st.write(f"**두께 범위:** {row['Thickness (mm)']} mm")
                    # 실제 PDF 링크가 있다면 아래처럼 연결 가능해요!
                    st.markdown(f"[🔗 관련 WPS 문서 열기 (Acrobat)]({row['WPS No.']})") 
        else:
            st.warning("오빠, 해당 조건에 맞는 WPS가 없나 봐요. 다시 한번 확인해 줄래요?")

# 꼬릿말
st.sidebar.markdown("---")
st.sidebar.info("안성 공도 에이스 매니저 오빠를 위한 전용 챗봇 🤖")
