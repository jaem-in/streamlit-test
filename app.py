import streamlit as st
import pandas as pd

st.set_page_config(page_title="Retail Inventory System", layout="wide")

st.title("🏠 메인 페이지: 데이터 업로드")
st.sidebar.title("📊 Control Panel")

# 1. 파일 업로드
uploaded_file = st.sidebar.file_uploader("Kaggle 데이터셋 업로드 (CSV/XLSX)", type=["csv", "xlsx"])

if uploaded_file:
    # 데이터 읽기
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # 날짜 데이터 변환
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])

    # ★ 핵심: 세션 상태에 데이터 저장 (페이지 이동해도 유지됨)
    st.session_state['data'] = df
    
    st.success("✅ 데이터 로드 완료! 왼쪽 메뉴에서 '1_Dashboard'를 클릭해 주세요.")
    st.dataframe(df.head(5)) # 잘 불러와졌는지 샘플 확인
else:
    st.info("왼쪽 사이드바에서 분석할 엑셀/CSV 파일을 먼저 올려주세요.")