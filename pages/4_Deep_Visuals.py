import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Deep Visual Insight", layout="wide")

st.title("📊 데이터 입체 분석 & 인사이트")
st.markdown("단순 조회를 넘어 데이터 사이의 **상관관계와 분포**를 탐색합니다.")

if 'data' in st.session_state:
    df = st.session_state['data']

    # --- 1. 변수 간 상관관계 (Heatmap) ---
    st.subheader("🔗 변수 간 상관관계 분석")
    st.info("💡 어떤 요소(가격, 날씨, 공휴일 등)가 판매량과 가장 밀접하게 관련 있는지 보여줍니다.")
    
    # 상관계수 계산을 위해 숫자형 컬럼만 추출
    # 날씨나 공휴일이 문자열인 경우 숫자로 임시 변환하여 분석에 포함 가능
    corr_df = df.select_dtypes(include=['number']).corr()
    
    fig_corr = px.imshow(corr_df, 
                         text_auto='.2f', 
                         color_continuous_scale='RdBu_r',
                         aspect="auto",
                         title="데이터 상관관계 히트맵")
    st.plotly_chart(fig_corr, use_container_width=True)

    st.divider()

    # --- 2. 다차원 계층 구조 분석 (Sunburst Chart) ---
    st.subheader("🌳 지역 - 카테고리별 판매 계층 구조")
    st.markdown("원 안쪽에서 바깥쪽으로 클릭하며 상세 비중을 확인하세요.")
    
    fig_sun = px.sunburst(df, 
                          path=['Region', 'Category'], 
                          values='Units Sold',
                          color='Units Sold', 
                          color_continuous_scale='Viridis')
    st.plotly_chart(fig_sun, use_container_width=True)

    st.divider()

    # --- 3. 가격 vs 판매량 & 재고 (Bubble Chart) ---
    st.subheader("💰 가격과 수요의 상관관계 (버블 차트)")
    st.markdown("버블의 크기는 **재고 수준**을 의미합니다. 가격이 높을 때 판매가 줄어드는지 확인해 보세요.")
    
    # 데이터가 너무 많으면 점이 겹치므로 카테고리별 평균값으로 요약
    bubble_df = df.groupby(['Category', 'Product ID']).agg({
        'Price': 'mean',
        'Units Sold': 'sum',
        'Inventory Level': 'mean'
    }).reset_index()

    fig_bubble = px.scatter(bubble_df, 
                            x="Price", y="Units Sold",
                            size="Inventory Level", 
                            color="Category",
                            hover_name="Product ID", 
                            log_x=True, 
                            size_max=60,
                            title="가격 대비 판매량 (버블 크기 = 평균 재고)")
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.divider()

    # --- 4. 외부 요인 분석 (Box Plot) ---
    st.subheader("☁️ 외부 요인별 판매 분포 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**날씨(Weather)에 따른 판매량 분포**")
        if 'Weather Condition' in df.columns:
            fig_weather = px.box(df, x="Weather Condition", y="Units Sold", color="Weather Condition")
            st.plotly_chart(fig_weather, use_container_width=True)
        else:
            st.warning("데이터에 Weather Condition 컬럼이 없습니다.")

    with col2:
        st.write("**공휴일/프로모션 여부에 따른 판매량 분포**")
        if 'Holiday/Promotion' in df.columns:
            # 0/1 데이터라면 가독성을 위해 문자열로 변환
            df_promo = df.copy()
            df_promo['Promotion_Label'] = df_promo['Holiday/Promotion'].apply(lambda x: 'Promotion ON' if x == 1 else 'Normal Day')
            fig_promo = px.violin(df_promo, x="Promotion_Label", y="Units Sold", color="Promotion_Label", box=True, points="all")
            st.plotly_chart(fig_promo, use_container_width=True)
        else:
            st.warning("데이터에 Holiday/Promotion 컬럼이 없습니다.")

else:
    st.error("❌ 데이터가 없습니다. 메인 페이지에서 파일을 업로드해 주세요.")