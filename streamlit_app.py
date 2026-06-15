
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =============================
# 页面设置
# =============================

st.set_page_config(
    page_title="北向资格调整事件数据库",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
FIG_DIR = BASE_DIR / "figures"


# =============================
# 工具函数
# =============================

@st.cache_data(show_spinner=False)
def load_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="gbk", low_memory=False)


def to_date_safe(s):
    return pd.to_datetime(s, errors="coerce")


def pct_fmt(x, digits=2):
    try:
        if pd.isna(x):
            return ""
        return f"{float(x) * 100:.{digits}f}%"
    except Exception:
        return str(x)


def num_fmt(x, digits=4):
    try:
        if pd.isna(x):
            return ""
        return f"{float(x):.{digits}f}"
    except Exception:
        return str(x)


def normalize_code(x):
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if "." in s and s.replace(".", "", 1).isdigit():
        s = str(int(float(s)))
    return s.zfill(6)


def add_board(code: str) -> str:
    code = normalize_code(code)
    if code.startswith(("600", "601", "603", "605")):
        return "沪市主板"
    if code.startswith(("000", "001", "002", "003")):
        return "深市主板"
    if code.startswith(("300", "301")):
        return "创业板"
    if code.startswith("688"):
        return "科创板"
    return "其他"


def show_dataframe_download(df: pd.DataFrame, filename: str, label: str = "下载当前表格 CSV"):
    if df.empty:
        return
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


# =============================
# 数据加载
# =============================

events_base = load_csv("events_base_2014_2026.csv")
events_strict = load_csv("events_main_candidates_v2.csv")
strategy_summary = load_csv("strategy_summary_batch_weighted_v1.csv")
strategy_sell = load_csv("strategy_SELL_risk_warning_summary_v1.csv")
strategy_turnover = load_csv("strategy_high_turnover_NEW_comparison_v1.csv")

if not events_base.empty:
    events_base["stkcd"] = events_base["stkcd"].apply(normalize_code)
    events_base["eff_date"] = to_date_safe(events_base["eff_date"])
    events_base["ann_date"] = to_date_safe(events_base.get("ann_date"))
    events_base["year"] = events_base["eff_date"].dt.year
    events_base["month"] = events_base["eff_date"].dt.month
    events_base["board"] = events_base["stkcd"].apply(add_board)

if not events_strict.empty:
    events_strict["stkcd"] = events_strict["stkcd"].apply(normalize_code)
    events_strict["eff_date"] = to_date_safe(events_strict["eff_date"])
    events_strict["ann_date_batch"] = to_date_safe(events_strict.get("ann_date_batch"))
    events_strict["year"] = events_strict["eff_date"].dt.year
    events_strict["month"] = events_strict["eff_date"].dt.month
    events_strict["board"] = events_strict["stkcd"].apply(add_board)


# =============================
# 侧边栏
# =============================

st.sidebar.title("📌 北向资格调整研究")
st.sidebar.caption("事件数据库 · 实证结果 · 投资启示模拟")

st.sidebar.info(
    "本平台用于展示北向证券资格调整事件数据库与论文核心结果。"
    "策略模块仅用于学术研究与投资启示展示，不构成投资建议。"
)

st.sidebar.markdown("### 数据状态")
st.sidebar.write({
    "原始事件库": f"{len(events_base):,} 行" if not events_base.empty else "未找到",
    "严格研究样本": f"{len(events_strict):,} 行" if not events_strict.empty else "未找到",
    "策略结果": f"{len(strategy_summary):,} 行" if not strategy_summary.empty else "未找到",
})


# =============================
# 标题
# =============================

st.title("北向证券资格调整事件数据库与投资启示展示平台")
st.caption("从价格冲击到选择效应：北向证券资格调整的市场反应与机制非对称")


tab_home, tab_events, tab_strict, tab_results, tab_strategy, tab_download = st.tabs(
    ["项目首页", "事件库探索", "严格样本分析", "核心实证结果", "投资启示模拟", "数据下载"]
)


# =============================
# Tab 1: 首页
# =============================

with tab_home:
    st.subheader("项目简介")

    st.markdown(
        """
        本项目围绕港交所披露的沪股通、深股通证券名单调整，构建北向证券资格调整事件数据库，
        并将事件划分为 **新增可买（NEW_BUYABLE）** 与 **转为只可卖出（SELL_ONLY）** 两类核心资格变化。

        与一般北向资金流量研究不同，本项目关注的是“境外投资者能否通过北向渠道买入某只 A 股”的
        交易资格边界变化。研究发现，北向资格调整并不能简单理解为稳定的公告后价格冲击事件；
        其更重要的含义在于公告前选择效应和调入端、限制端筛选机制差异。
        """
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("原始事件记录", f"{len(events_base):,}" if not events_base.empty else "—")
    if not events_strict.empty and "event_class_v2" in events_strict.columns:
        c2.metric("NEW_BUYABLE", f"{(events_strict['event_class_v2'] == 'NEW_BUYABLE').sum():,}")
        c3.metric("SELL_ONLY", f"{(events_strict['event_class_v2'] == 'SELL_ONLY').sum():,}")
        c4.metric("公告批次数", f"{events_strict['ann_date_batch'].nunique():,}" if "ann_date_batch" in events_strict.columns else "—")
    else:
        c2.metric("NEW_BUYABLE", "—")
        c3.metric("SELL_ONLY", "—")
        c4.metric("公告批次数", "—")

    st.markdown("### 核心结论")
    st.success(
        "北向资格调整的非对称性并不稳定体现为公告后价格冲击幅度差异，"
        "而更主要体现为调入端与限制端的筛选机制差异。"
    )

    st.markdown(
        """
        - **价格反应层面**：B-MA 模型下公告后存在方向差异，但 B-MM 模型下明显减弱。
        - **选择效应层面**：两类事件在公告前长期收益和事件前 alpha 上已存在显著差异。
        - **筛选机制层面**：SELL_ONLY 更关联于公告前弱势收益特征；非科创板 NEW_BUYABLE 更关联于公告前高换手率。
        - **投资启示层面**：简单买入 NEW_BUYABLE 不稳健；SELL_ONLY 更适合作为短窗口风险预警信号。
        """
    )


# =============================
# Tab 2: 事件库探索
# =============================

with tab_events:
    st.subheader("原始事件库探索")

    if events_base.empty:
        st.warning("未找到 events_base_2014_2026.csv。请确认 data 文件夹中已放置该文件。")
    else:
        left, right = st.columns([1, 3])

        with left:
            years = sorted([int(y) for y in events_base["year"].dropna().unique()])
            if years:
                selected_years = st.slider("生效年份", min(years), max(years), (min(years), max(years)))
            else:
                selected_years = (None, None)

            event_types = sorted(events_base["event_type"].dropna().unique().tolist())
            selected_types = st.multiselect("事件类型", event_types, default=event_types)

            boards = sorted(events_base["board"].dropna().unique().tolist())
            selected_boards = st.multiselect("板块", boards, default=boards)

            keyword = st.text_input("股票代码 / 名称关键词", "")

        df = events_base.copy()
        if selected_years[0] is not None:
            df = df[(df["year"] >= selected_years[0]) & (df["year"] <= selected_years[1])]
        if selected_types:
            df = df[df["event_type"].isin(selected_types)]
        if selected_boards:
            df = df[df["board"].isin(selected_boards)]
        if keyword.strip():
            key = keyword.strip()
            name_col = "名稱" if "名稱" in df.columns else None
            mask = df["stkcd"].astype(str).str.contains(key, case=False, na=False)
            if name_col:
                mask = mask | df[name_col].astype(str).str.contains(key, case=False, na=False)
            df = df[mask]

        with right:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("筛选后事件数", f"{len(df):,}")
            m2.metric("股票数", f"{df['stkcd'].nunique():,}")
            m3.metric("覆盖年份", f"{int(df['year'].min()) if not df.empty and pd.notna(df['year'].min()) else '—'}—{int(df['year'].max()) if not df.empty and pd.notna(df['year'].max()) else '—'}")
            m4.metric("事件类型数", f"{df['event_type'].nunique():,}")

            if not df.empty:
                yearly = df.groupby(["year", "event_type"]).size().reset_index(name="事件数")
                fig = px.bar(yearly, x="year", y="事件数", color="event_type", barmode="stack", title="年度事件分布")
                st.plotly_chart(fig, use_container_width=True)

                monthly = df.groupby(["month", "event_type"]).size().reset_index(name="事件数")
                fig2 = px.line(monthly, x="month", y="事件数", color="event_type", markers=True, title="月份事件分布")
                st.plotly_chart(fig2, use_container_width=True)

            st.dataframe(df, use_container_width=True, height=360)
            show_dataframe_download(df, "filtered_events_base.csv")


# =============================
# Tab 3: 严格样本分析
# =============================

with tab_strict:
    st.subheader("严格研究样本：NEW_BUYABLE / SELL_ONLY")

    if events_strict.empty:
        st.warning("未找到 events_main_candidates_v2.csv。请确认 data 文件夹中已放置该文件。")
    else:
        col_a, col_b = st.columns([1, 3])

        with col_a:
            class_col = "event_class_v2" if "event_class_v2" in events_strict.columns else "event_class_v1"
            classes = sorted(events_strict[class_col].dropna().unique().tolist())
            selected_classes = st.multiselect("事件类别", classes, default=classes)

            strict_options = []
            if "baseline_candidate_v2" in events_strict.columns:
                strict_options = sorted(events_strict["baseline_candidate_v2"].dropna().unique().tolist())
                selected_candidate = st.multiselect("是否严格样本", strict_options, default=strict_options)
            else:
                selected_candidate = []

            boards = sorted(events_strict["board"].dropna().unique().tolist())
            selected_boards = st.multiselect("板块", boards, default=boards, key="strict_board")

        df2 = events_strict.copy()
        if selected_classes:
            df2 = df2[df2[class_col].isin(selected_classes)]
        if selected_candidate and "baseline_candidate_v2" in df2.columns:
            df2 = df2[df2["baseline_candidate_v2"].isin(selected_candidate)]
        if selected_boards:
            df2 = df2[df2["board"].isin(selected_boards)]

        with col_b:
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("样本事件数", f"{len(df2):,}")
            k2.metric("股票数", f"{df2['stkcd'].nunique():,}")
            k3.metric("NEW_BUYABLE", f"{(df2[class_col] == 'NEW_BUYABLE').sum():,}")
            k4.metric("SELL_ONLY", f"{(df2[class_col] == 'SELL_ONLY').sum():,}")

            if not df2.empty:
                board_class = df2.groupby(["board", class_col]).size().reset_index(name="事件数")
                fig = px.bar(board_class, x="board", y="事件数", color=class_col, barmode="group", title="板块 × 严格事件类别")
                st.plotly_chart(fig, use_container_width=True)

                year_class = df2.groupby(["year", class_col]).size().reset_index(name="事件数")
                fig2 = px.bar(year_class, x="year", y="事件数", color=class_col, barmode="stack", title="严格样本年度分布")
                st.plotly_chart(fig2, use_container_width=True)

            st.dataframe(df2, use_container_width=True, height=360)
            show_dataframe_download(df2, "filtered_strict_events.csv")


# =============================
# Tab 4: 核心实证结果
# =============================

with tab_results:
    st.subheader("核心实证结果展示")

    st.markdown(
        """
        本页展示论文中的三张核心图。它们分别对应研究逻辑、公告日事件反应和调入端换手率机制。
        """
    )

    fig_files = [
        ("图 1 研究逻辑框架图", "fig1_research_framework.png"),
        ("图 2 公告日锚点下两类资格调整事件的累计异常收益路径", "fig2_car_announcement_path.png"),
        ("图 3 非科创板新增可买事件的换手率机制示意图", "fig3_turnover_mechanism_or.png"),
    ]

    for title, fname in fig_files:
        path = FIG_DIR / fname
        st.markdown(f"### {title}")
        if path.exists():
            st.image(str(path), use_container_width=True)
        else:
            st.warning(f"未找到图片：{path}")

    st.markdown("### 结果解释")
    st.info(
        "B-MA 下公告后短窗口存在 NEW_BUYABLE 与 SELL_ONLY 的方向差异；"
        "但在 B-MM 中控制公告前正常收益特征后差异明显减弱。"
        "这提示资格调整公告效应受到公告前选择效应影响。"
    )
    st.info(
        "风险集合结果进一步显示：SELL_ONLY 更关联于公告前弱势收益特征；"
        "非科创板 NEW_BUYABLE 则更关联于公告前较高换手率，换手率能够吸收原先的高波动效应。"
    )


# =============================
# Tab 5: 投资启示模拟
# =============================

with tab_strategy:
    st.subheader("投资启示模拟：事件信号与风险预警")

    st.warning(
        "本模块仅用于展示北向资格调整事件的投资启示和风险预警价值，不构成投资建议。"
        "已有结果显示，简单买入 NEW_BUYABLE 不具备稳定显著收益；SELL_ONLY 更适合作为短窗口风险预警信号。"
    )

    selected_window = st.selectbox(
        "选择观察窗口",
        ["ANN_1_5", "ANN_1_20", "ANN_TO_EFF_PRE", "EFF_1_20"],
        index=0,
        help="ANN_1_5 表示公告后第 1 至第 5 个交易日；ANN_TO_EFF_PRE 表示公告后至生效日前。",
    )

    st.markdown("### 1. NEW_BUYABLE 简单买入策略")

    if strategy_summary.empty:
        st.warning("未找到 strategy_summary_batch_weighted_v1.csv。")
    else:
        ss = strategy_summary.copy()
        ss = ss[(ss["window"] == selected_window) & (ss["metric"].astype(str).str.contains("board_adj", na=False))]
        if ss.empty:
            st.info("该窗口下没有可展示的 NEW 策略结果。")
        else:
            display = ss[["strategy", "window", "N", "批次数", "均值", "胜率", "t_p", "Wilcoxon_p"]].copy()
            display["均值"] = display["均值"].apply(pct_fmt)
            display["胜率"] = display["胜率"].apply(pct_fmt)
            display["t_p"] = display["t_p"].apply(lambda x: num_fmt(x, 4))
            display["Wilcoxon_p"] = display["Wilcoxon_p"].apply(lambda x: num_fmt(x, 4))
            st.dataframe(display, use_container_width=True)

            fig = px.bar(
                ss,
                x="strategy",
                y="均值",
                text=ss["均值"].apply(lambda x: pct_fmt(x)),
                title=f"NEW 策略平均板块调整收益：{selected_window}",
            )
            fig.update_yaxes(tickformat=".1%")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 2. 高换手 NEW_BUYABLE 筛选")

    if strategy_turnover.empty:
        st.warning("未找到 strategy_high_turnover_NEW_comparison_v1.csv。")
    else:
        ht = strategy_turnover.copy()
        ht = ht[(ht["window"] == selected_window) & (ht["metric"].astype(str).str.contains("diff_ar", na=False))]
        if ht.empty:
            st.info("该窗口下没有可展示的高低换手对比结果。")
        else:
            display = ht[["comparison", "window", "N", "批次数", "均值", "胜率", "t_p", "Wilcoxon_p"]].copy()
            display["均值"] = display["均值"].apply(pct_fmt)
            display["胜率"] = display["胜率"].apply(pct_fmt)
            display["t_p"] = display["t_p"].apply(lambda x: num_fmt(x, 4))
            display["Wilcoxon_p"] = display["Wilcoxon_p"].apply(lambda x: num_fmt(x, 4))
            st.dataframe(display, use_container_width=True)

            fig = px.bar(
                ht,
                x="comparison",
                y="均值",
                text=ht["均值"].apply(lambda x: pct_fmt(x)),
                title=f"高换手 NEW 相对低换手 NEW 的收益差异：{selected_window}",
            )
            fig.update_yaxes(tickformat=".1%")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 3. SELL_ONLY 退出风险预警")

    if strategy_sell.empty:
        st.warning("未找到 strategy_SELL_risk_warning_summary_v1.csv。")
    else:
        se = strategy_sell.copy()
        se = se[se["window"] == selected_window]
        if se.empty:
            st.info("该窗口下没有可展示的 SELL 风险预警结果。")
        else:
            display = se[["window", "口径", "N", "批次数", "均值", "胜率", "t_p", "Wilcoxon_p"]].copy()
            display["均值"] = display["均值"].apply(pct_fmt)
            display["胜率"] = display["胜率"].apply(pct_fmt)
            display["t_p"] = display["t_p"].apply(lambda x: num_fmt(x, 4))
            display["Wilcoxon_p"] = display["Wilcoxon_p"].apply(lambda x: num_fmt(x, 4))
            st.dataframe(display, use_container_width=True)

            fig = px.bar(
                se,
                x="口径",
                y="均值",
                text=se["均值"].apply(lambda x: pct_fmt(x)),
                title=f"SELL_ONLY 风险预警收益：{selected_window}",
            )
            fig.update_yaxes(tickformat=".1%")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 结论提示")
    st.write(
        "策略模块的核心用途是展示事件信号的现实含义。"
        "当前结果更支持将 SELL_ONLY 理解为短窗口风险预警信号，"
        "而不是将 NEW_BUYABLE 机械地解释为稳定买入机会。"
    )


# =============================
# Tab 6: 数据下载
# =============================

with tab_download:
    st.subheader("数据文件下载")

    st.markdown("下列数据文件用于本网页展示。下载后可在本地复核或二次分析。")

    for fname in [
        "events_base_2014_2026.csv",
        "events_main_candidates_v2.csv",
        "strategy_summary_batch_weighted_v1.csv",
        "strategy_high_turnover_NEW_comparison_v1.csv",
        "strategy_SELL_risk_warning_summary_v1.csv",
    ]:
        path = DATA_DIR / fname
        if path.exists():
            st.download_button(
                label=f"下载 {fname}",
                data=path.read_bytes(),
                file_name=fname,
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info(f"未找到 {fname}")

    st.markdown("### 部署说明")
    st.code(
        """
        # GitHub 项目结构建议
        northbound-event-app/
        ├── streamlit_app.py
        ├── requirements.txt
        ├── README.md
        ├── data/
        │   ├── events_base_2014_2026.csv
        │   ├── events_main_candidates_v2.csv
        │   ├── strategy_summary_batch_weighted_v1.csv
        │   ├── strategy_high_turnover_NEW_comparison_v1.csv
        │   └── strategy_SELL_risk_warning_summary_v1.csv
        └── figures/
            ├── fig1_research_framework.png
            ├── fig2_car_announcement_path.png
            └── fig3_turnover_mechanism_or.png
        """,
        language="text",
    )
