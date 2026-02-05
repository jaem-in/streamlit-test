import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide") # 각 페이지 상단에 써주는 것이 좋습니다.

st.title("📊 재고 분석 대시보드")

# 1. 메인에서 저장한 데이터 불러오기
if 'data' in st.session_state:
    df = st.session_state['data']

    # --- 사이드바 필터 (기존 코드와 동일) ---
    st.sidebar.subheader("🔍 필터 설정")
    region = st.sidebar.multiselect("지역(Region) 선택", df['Region'].unique(), default=df['Region'].unique())
    category = st.sidebar.multiselect("카테고리 선택", df['Category'].unique(), default=df['Category'].unique())

    filtered_df = df[(df['Region'].isin(region)) & (df['Category'].isin(category))]

    # --- 메인 시각화 (기존 코드와 동일) ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("총 판매량", f"{filtered_df['Units Sold'].sum():,} EA")
    m2.metric("평균 재고 수준", f"{int(filtered_df['Inventory Level'].mean()):,} EA")
    
    stockout_risk = filtered_df[filtered_df['Inventory Level'] < filtered_df['Demand Forecast']]
    m3.metric("재고 부족 위험 품목", f"{len(stockout_risk)}건", delta="-위험", delta_color="inverse")
    
    avg_price = filtered_df['Price'].mean() if 'Price' in df.columns else 0
    m4.metric("평균 판매가", f"${avg_price:.2f}")

    st.divider()

    # 차트 섹션
    col1, col2 = st.columns(2)
    with col1:
        trend_df = filtered_df.groupby('Date')[['Units Sold', 'Inventory Level']].sum().reset_index()
        fig_trend = px.line(trend_df, x='Date', y=['Units Sold', 'Inventory Level'], color_discrete_map={"Units Sold": "#FF4B4B", "Inventory Level": "#1C83E1"})
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        fig_pie = px.pie(filtered_df, values='Units Sold', names='Category', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    # 상세 데이터 탭
    tab1, tab2 = st.tabs(["전체 데이터", "⚠️ 재고 보충 필요"])
    with tab1:
        st.dataframe(filtered_df, use_container_width=True)
    with tab2:
        st.dataframe(stockout_risk, use_container_width=True)

else:
    # 데이터가 없을 경우
    st.error("❌ 파일이 업로드되지 않았습니다. 메인 페이지로 돌아가서 파일을 업로드해 주세요.")