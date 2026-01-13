import streamlit as st
import pandas as pd

st.set_page_config(page_title="WPS 비서", page_icon="🤖")
st.title("🤖 윤성에프앤씨 WPS 마스터")

@st.cache_data
def load_data():
    try:
        # 오빠의 깃허브 파일 이름인 대문자 .XLSX로 수정했어요!
        df = pd.read_excel("wps_list.XLSX")
        return df
    except Exception as e:
        st.error(f"파일을 읽을 수 없어요. 이름이 wps_list.XLSX 인지 확인해 주세요! 에러: {e}")
        return None

df = load_data()

if df is not None:
    search = st.text_input("🔍 P-No 또는 용접봉을 입력하세요", placeholder="예: P8, ER308...")
    if search:
        # 이미지에 있던 실제 컬럼명(WPS No., P-No 등)으로 검색해요
        mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        result = df[mask]
        if not result.empty:
            st.success(f"오빠! {len(result)}건을 찾았어요!")
            st.dataframe(result)
        else:
            st.warning("찾으시는 정보가 없어요.")
