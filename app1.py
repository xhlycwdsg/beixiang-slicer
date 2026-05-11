import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. 网页全局设置 ---
st.set_page_config(page_title="北向标的调整事件探索器", page_icon="📈", layout="wide")

# --- 2. 加载数据 (利用缓存机制，极速加载) ---
@st.cache_data
def load_data():
    # 替换为你刚才清洗好的事件库路径
    file_path = "/Users/xuhanle/Downloads/调整名单/events_base_2014_2026.csv"
    df = pd.read_csv(file_path)
    df['eff_date'] = pd.to_datetime(df['eff_date'])
    df['year'] = df['eff_date'].dt.year
    df['month'] = df['eff_date'].dt.month
    return df

df = load_data()

# --- 3. 侧边栏：交互筛选器 ---
st.sidebar.header("🔍 交互式时空切片引擎")
st.sidebar.markdown("请选择您要探索的参数：")

# 年份双滑块
min_year, max_year = int(df['year'].min()), int(df['year'].max())
selected_years = st.sidebar.slider("📅 选择时间跨度", min_year, max_year, (min_year, max_year))

# 事件类型多选框
event_types = df['event_type'].unique().tolist()
selected_types = st.sidebar.multiselect("📊 选择事件类型", event_types, default=event_types)

# 数据过滤引擎
filtered_df = df[
    (df['year'] >= selected_years[0]) & 
    (df['year'] <= selected_years[1]) & 
    (df['event_type'].isin(selected_types))
]

# --- 4. 主页面：核心指标区 ---
st.title("🚀 互联互通机制：北向资金标的调整微观事件探索器")
st.markdown("本系统依托 Python 自动化引擎与 NLP 技术，从近十年港交所非结构化披露文件中提取并重构了 **9000+** 次外资调仓事件。")

col1, col2, col3, col4 = st.columns(4)
col1.metric("📌 当前筛选事件总数", f"{len(filtered_df)} 次")
col2.metric("🟢 调入 (In) 事件", f"{len(filtered_df[filtered_df['event_type'] == 'In'])} 次")
col3.metric("🔴 调出 (Out) 事件", f"{len(filtered_df[filtered_df['event_type'] == 'Out'])} 次")
col4.metric("⚠️ 特别名单 (Special)", f"{len(filtered_df[filtered_df['event_type'] == 'Special'])} 次")

st.divider()

# --- 5. 动态可视化图表 ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📈 事件年度分布规律")
    # 按年和事件类型统计
    yearly_counts = filtered_df.groupby(['year', 'event_type']).size().reset_index(name='count')
    fig_year = px.bar(yearly_counts, x='year', y='count', color='event_type', 
                      title="历年标的调整频次", barmode='stack', text_auto=True)
    st.plotly_chart(fig_year, use_container_width=True)

with col_chart2:
    st.subheader("🗓️ 季节性特征 (月份分布)")
    # 按月统计，寻找定期调整的规律
    monthly_counts = filtered_df.groupby(['month', 'event_type']).size().reset_index(name='count')
    fig_month = px.bar(monthly_counts, x='month', y='count', color='event_type', 
                       title="不同月份调整频率分布", barmode='group')
    st.plotly_chart(fig_month, use_container_width=True)

st.divider()

# --- 6. 数据穿透展示 ---
st.subheader("🗄️ 底层微观事件清单透视")
st.dataframe(filtered_df[['stkcd', '名稱', 'event_type', 'eff_date', 'ann_date']].sort_values('eff_date', ascending=False), use_container_width=True)

st.caption("© 2026 量化事件驱动项目组 | Powered by Streamlit & Pandas")