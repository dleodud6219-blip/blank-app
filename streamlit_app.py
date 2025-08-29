#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")



#######################
# Background + Colors
st.markdown("""
<style>
/* 전체 앱 배경: 타이타닉 사진 */
[data-testid="stAppViewContainer"] {
  background: url("https://upload.wikimedia.org/wikipedia/commons/f/fd/RMS_Titanic_3.jpg") no-repeat center center fixed;
  background-size: cover;
  color: #FFFFFF;  /* 기본 텍스트 흰색 */
}

/* 사이드바 */
[data-testid="stSidebar"] {
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(5px);
  color: #FFFFFF;  /* 사이드바 텍스트 흰색 */
}

/* 메인 컨텐츠 블록 */
[data-testid="block-container"] {
  background: rgba(17,18,22,0.80);  /* 반투명 블랙 */
  border-radius: 18px;
  padding: 2rem;
  color: #FFFFFF;  /* 기본 텍스트 흰색 */
}

/* 헤더/제목 */
h1, h2, h3, h4, h5, h6 {
  color: #FFD700 !important;   /* 골드 노랑 */
}

/* metric 카드 */
[data-testid="stMetricLabel"] {
  color: #FFD700 !important;   /* 라벨 = 노랑 */
}
[data-testid="stMetricValue"] {
  color: #00FF7F !important;   /* 값 = 에메랄드 그린 */
  font-weight: bold;
}
[data-testid="stMetricDelta"] {
  color: #00FF7F !important;   /* 증감 = 에메랄드 그린 */
}

/* 설명/캡션/보조 */
.stCaption, .stMarkdown p, span, label {
  color: #C0C0C0 !important;   /* 은은한 회색 */
}

/* selectbox 내부 글자 */
div[data-baseweb="select"] > div {
    color: #000000 !important;   /* 선택된 값 = 검정 */
}
div[data-baseweb="select"] span {
    color: #000000 !important;   /* 드롭다운 목록 = 검정 */
}
</style>
""", unsafe_allow_html=True)




#######################
# Load data
df_reshaped = pd.read_csv('titanic.csv') ## 분석 데이터 넣기


#######################
# Sidebar
with st.sidebar:
    st.title("⚓ Titanic Dashboard")
    st.markdown("탑승객 생존 데이터 분석")

    # 성별 선택
    gender_filter = st.multiselect(
        "성별 선택:",
        options=df_reshaped['Sex'].unique(),
        default=df_reshaped['Sex'].unique()
    )

    # 선실 등급 선택
    pclass_filter = st.multiselect(
        "선실 등급 선택:",
        options=sorted(df_reshaped['Pclass'].unique()),
        default=sorted(df_reshaped['Pclass'].unique())
    )

    # 탑승 항구 선택
    embarked_filter = st.multiselect(
        "탑승 항구 선택:",
        options=df_reshaped['Embarked'].dropna().unique(),
        default=df_reshaped['Embarked'].dropna().unique()
    )

    # 색상 테마 선택
    color_theme = st.selectbox(
        "색상 테마 선택:",
        options=["Blues", "Viridis", "Plasma", "Cividis"]
    )

    # 연령 구간화 여부
    age_binning = st.checkbox("연령 구간화 (0–12, 13–18, 19–30, 31–50, 51+)", value=True)



#######################
# Plots

# — 공통: 필터 적용 데이터 ---
df_filtered = df_reshaped[
    (df_reshaped['Sex'].isin(gender_filter)) &
    (df_reshaped['Pclass'].isin(pclass_filter)) &
    (df_reshaped['Embarked'].isin(embarked_filter))
].copy()

# Survived 라벨 컬럼
df_filtered['Survived_label'] = df_filtered['Survived'].map({0: 'Died', 1: 'Survived'})

# 색상 스킴 매핑 (Altair)
scheme_map = {
    "Blues": "blues",
    "Viridis": "viridis",
    "Plasma": "plasma",
    "Cividis": "cividis"
}
scheme = scheme_map.get(color_theme, "blues")

# — 1) Age × Sex 생존률 히트맵 (Altair) ---
# 연령 구간화 옵션 적용
if age_binning:
    bins = [0, 12, 18, 30, 50, 120]
    labels = ["0–12", "13–18", "19–30", "31–50", "51+"]
    df_filtered['AgeBin'] = pd.cut(df_filtered['Age'], bins=bins, labels=labels, right=True, include_lowest=True)
    x_enc = alt.X('AgeBin:O', sort=labels, title='Age (binned)')
else:
    x_enc = alt.X('Age:Q', bin=alt.Bin(maxbins=20), title='Age')

heatmap_chart = (
    alt.Chart(df_filtered)
    .mark_rect()
    .encode(
        x=x_enc,
        y=alt.Y('Sex:N', title='Sex'),
        color=alt.Color('mean(Survived):Q',
                        title='Survival Rate',
                        scale=alt.Scale(scheme=scheme)),
        tooltip=[
            alt.Tooltip('Sex:N', title='Sex'),
            alt.Tooltip('count():Q', title='Count'),
            alt.Tooltip('mean(Survived):Q', title='Survival Rate', format='.2f')
        ]
    )
    .properties(height=260)
)

# — 2) 연령 분포 히스토그램 (Plotly) ---
fig_age_hist = px.histogram(
    df_filtered,
    x='Age',
    color='Survived_label',
    nbins=30,
    opacity=0.75,
    barmode='overlay',
    labels={'Age': 'Age', 'Survived_label': 'Status'}
)
fig_age_hist.update_layout(
    margin=dict(l=10, r=10, t=30, b=10),
    title_text="Age Distribution by Survival",
    legend_title_text="Status"
)

# — 3) 탑승 항구별 인원/생존 분포 (Plotly) ---
df_emb = (
    df_filtered
    .groupby(['Embarked', 'Survived_label'])
    .size()
    .reset_index(name='count')
)

fig_embarked = px.bar(
    df_emb,
    x='Embarked',
    y='count',
    color='Survived_label',
    barmode='group',
    labels={'Embarked': 'Embarked Port', 'count': 'Passengers', 'Survived_label': 'Status'},
    title='Passengers by Embarkation Port & Survival'
)
fig_embarked.update_layout(margin=dict(l=10, r=10, t=30, b=10))

# (선택) 다음 단계에서 사용하기 쉽도록 딕셔너리로 묶어두기
plots = {
    "heatmap": heatmap_chart,
    "age_hist": fig_age_hist,
    "embarked_bar": fig_embarked
}



#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown("### 📊 주요 요약 지표")

    # 필터 적용된 데이터
    df_filtered = df_reshaped[
        (df_reshaped['Sex'].isin(gender_filter)) &
        (df_reshaped['Pclass'].isin(pclass_filter)) &
        (df_reshaped['Embarked'].isin(embarked_filter))
    ]

    total_passengers = len(df_filtered)
    survived_passengers = df_filtered['Survived'].sum()
    survival_rate = round((survived_passengers / total_passengers) * 100, 1) if total_passengers > 0 else 0

    # 전체 승객 수
    st.metric(label="전체 승객 수", value=f"{total_passengers}")

    # 생존자 수 및 비율
    st.metric(label="생존자 수", value=f"{survived_passengers}", delta=f"{survival_rate}%")

    # 성별별 생존률
    st.markdown("#### 성별별 생존률")
    gender_stats = df_filtered.groupby("Sex")["Survived"].mean().round(2) * 100
    for sex, rate in gender_stats.items():
        st.metric(label=f"{sex}", value=f"{rate:.1f}%")

    # 객실 등급별 생존률
    st.markdown("#### 등급별 생존률")
    pclass_stats = df_filtered.groupby("Pclass")["Survived"].mean().round(2) * 100
    for pclass, rate in pclass_stats.items():
        st.metric(label=f"{pclass}등급", value=f"{rate:.1f}%")



with col[1]:
    st.markdown("### 🎨 메인 시각화")

    # 1) Age × Sex 생존률 히트맵
    st.markdown("#### 나이 × 성별 생존률 히트맵")
    st.altair_chart(plots["heatmap"], use_container_width=True)

    # 2) 연령 분포 히스토그램
    st.markdown("#### 생존 여부별 연령 분포")
    st.plotly_chart(plots["age_hist"], use_container_width=True)


with col[2]:
    st.markdown("### 🔎 상세 분석")

    # 1) 탑승 항구별 생존 분포
    st.markdown("#### 탑승 항구별 생존 분포")
    st.plotly_chart(plots["embarked_bar"], use_container_width=True)

    # 2) Top 특징 요약 (간단히 텍스트/통계)
    st.markdown("#### Top 분석 인사이트")
    top_message = """
    - **성별**: 여성의 생존률이 남성보다 훨씬 높음  
    - **객실 등급**: 1등급 승객의 생존률이 가장 높음  
    - **연령대**: 어린이(0–12세)의 생존률이 상대적으로 높음  
    """
    st.markdown(top_message)

    # 3) 데이터 설명
    st.markdown("#### ℹ️ About")
    st.info(
        """
        데이터셋: Titanic (Kaggle 제공)  
        - 총 승객: 891명  
        - 주요 컬럼: Pclass, Sex, Age, Embarked, Survived 등  
        - 목표: 어떤 요인이 생존에 영향을 주었는지 탐색  
        """
    )
