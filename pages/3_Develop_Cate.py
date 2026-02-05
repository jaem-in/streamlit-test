import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Advanced Data Explorer", layout="wide")

st.title("🔍 멀티 조건 상세 탐색기")
st.markdown("글자 데이터는 **선택박스**로, 숫자 데이터는 **퍼센트 슬라이더**로 자유롭게 필터링하세요.")

if 'data' in st.session_state:
    df = st.session_state['data'].copy()

    # --- 사이드바: 필터 컨트롤 패널 ---
    st.sidebar.title("🛠️ 필터 설정")
    
    # 1. 글자(Categorical) 데이터 필터링
    st.sidebar.subheader("🔤 카테고리 필터 (글자)")
    text_cols = ['Region', 'Category', 'Product ID', 'Weather Condition']
    
    # 데이터에 실제 존재하는 컬럼만 추출
    available_text_cols = [col for col in text_cols if col in df.columns]
    
    filters = {}
    for col in available_text_cols:
        unique_vals = sorted(df[col].unique().tolist())
        selected = st.sidebar.multiselect(f"{col} 선택", unique_vals, default=unique_vals)
        filters[col] = selected

    st.sidebar.divider()

    # 2. 숫자(Numerical) 데이터 필터링 (0~100% 범위)
    st.sidebar.subheader("🔢 수치 필터 (퍼센트 범위)")
    num_cols = ['Inventory Level', 'Units Sold', 'Price', 'Demand Forecast']
    available_num_cols = [col for col in num_cols if col in df.columns]

    num_filters = {}
    for col in available_num_cols:
        st.sidebar.write(f"**{col}**")
        # 0~100 사이의 범위 슬라이더
        percent_range = st.sidebar.slider(
            f"{col} 퍼센트 범위", 
            0, 100, (0, 100), 
            key=f"slider_{col}",
            help="전체 데이터 중 해당 퍼센트 범위에 속하는 값만 보여줍니다."
        )
        num_filters[col] = percent_range

    # --- 데이터 필터링 로직 적용 ---
    filtered_df = df.copy()

    # 글자 필터 적용
    for col, values in filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(values)]

    # 숫자 퍼센트 필터 적용 (Percentile 기준)
    for col, p_range in num_filters.items():
        low_val = np.percentile(df[col], p_range[0])
        high_val = np.percentile(df[col], p_range[1])
        filtered_df = filtered_df[(filtered_df[col] >= low_val) & (filtered_df[col] <= high_val)]

    # --- 결과 화면 출력 ---
    st.info(f"💡 현재 조건에 맞는 데이터: **{len(filtered_df):,}** 건 (전체의 {len(filtered_df)/len(df)*100:.1f}%)")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📋 필터링된 데이터 결과")
        st.dataframe(filtered_df, use_container_width=True, height=500)

    with col2:
        st.subheader("📊 필터 결과 요약")
        if not filtered_df.empty:
            # 1. 판매량 Top 10 제품 (기존)
            top_products = filtered_df.groupby('Product ID')['Units Sold'].sum().nlargest(10).reset_index()
            fig1 = px.bar(top_products, x='Units Sold', y='Product ID', orientation='h', 
                          title="판매 Top 10 제품", color='Units Sold', color_continuous_scale='Reds')
            fig1.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig1, use_container_width=True)
            
            # 2. 카테고리별 비중 (추가 - 도넛 차트)
            cat_dist = filtered_df.groupby('Category')['Units Sold'].sum().reset_index()
            fig2 = px.pie(cat_dist, values='Units Sold', names='Category', hole=0.4, title="카테고리별 판매 비중")
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("조건에 맞는 데이터가 없습니다.")

    st.divider()

    # --- 하단 추가 시각화 섹션 (새로운 행) ---
    if not filtered_df.empty:
        col3, col4 = st.columns(2)

        with col3:
            # 3. 시간 흐름에 따른 판매 vs 예측 (추가 - 선 그래프)
            st.subheader("📈 판매량 및 수요 예측 추이")
            if 'Date' in filtered_df.columns:
                time_df = filtered_df.groupby('Date')[['Units Sold', 'Demand Forecast']].sum().reset_index()
                fig3 = px.line(time_df, x='Date', y=['Units Sold', 'Demand Forecast'],
                               title="일별 실적 vs 예측 트렌드",
                               color_discrete_map={"Units Sold": "#EF553B", "Demand Forecast": "#636EFA"})
                st.plotly_chart(fig3, use_container_width=True)

        with col4:
            # 4. 가격 대비 판매량 상관관계 (추가 - 산점도)
            st.subheader("💰 가격 대비 판매량 분포")
            fig4 = px.scatter(filtered_df, x='Price', y='Units Sold', color='Category',
                              size='Inventory Level', hover_name='Product ID',
                              title="가격과 판매의 상관관계 (점 크기=재고)")
            st.plotly_chart(fig4, use_container_width=True)

else:
    st.error("❌ 데이터가 없습니다. 메인 페이지에서 파일을 업로드해 주세요.")