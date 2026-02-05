import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Category Analysis", layout="wide")

st.title("📂 카테고리별 상세 분석")

# 1. 메인에서 저장한 데이터 불러오기
if 'data' in st.session_state:
    df = st.session_state['data']

    # --- 상단 드롭박스 설정 ---
    st.markdown("### 🔍 분석할 카테고리를 선택하세요")
    
    # 드롭박스(Selectbox) 생성
    categories = sorted(df['Category'].unique())
    selected_category = st.selectbox("카테고리 목록", categories)

    # 선택된 카테고리에 맞게 데이터 필터링
    category_df = df[df['Category'] == selected_category]

    st.divider()

    # --- 해당 카테고리 요약 정보 (KPI) ---
    st.subheader(f"✨ {selected_category} 카테고리 요약")
    m1, m2, m3, m4 = st.columns(4)
    
    total_sales = category_df['Units Sold'].sum()
    avg_inventory = category_df['Inventory Level'].mean()
    total_revenue = (category_df['Units Sold'] * category_df['Price']).sum() if 'Price' in df.columns else 0
    
    m1.metric("총 판매량", f"{total_sales:,} EA")
    m2.metric("평균 재고", f"{int(avg_inventory):,} EA")
    m3.metric("총 매출액", f"${total_revenue:,.2f}")
    m4.metric("데이터 레코드 수", f"{len(category_df):,}건")

    st.divider()

    # --- 시각화 섹션 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 시간 흐름별 판매 추이")
        # 날짜별로 그룹화하여 판매량 합산
        trend_df = category_df.groupby('Date')['Units Sold'].sum().reset_index()
        fig_line = px.line(trend_df, x='Date', y='Units Sold', 
                           title=f"{selected_category} 일별 판매량 변화",
                           line_shape='spline', render_mode='svg')
        fig_line.update_traces(line_color='#FF4B4B')
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader("🌎 지역별 판매 비중")
        # 지역별로 그룹화하여 판매량 합산
        region_df = category_df.groupby('Region')['Units Sold'].sum().reset_index()
        fig_pie = px.pie(region_df, values='Units Sold', names='Region', 
                         title=f"{selected_category}의 지역별 판매 분포",
                         hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- 상세 데이터 테이블 ---
    st.divider()
    st.subheader(f"📋 {selected_category} 상세 데이터 리스트")
    st.dataframe(category_df, use_container_width=True)

else:
    st.error("❌ 데이터가 없습니다. 메인 페이지에서 파일을 먼저 업로드해 주세요.")