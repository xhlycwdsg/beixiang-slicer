# 北向证券资格调整事件数据库与投资启示展示平台

本项目用于展示北向证券资格调整事件数据库、严格研究样本、论文核心实证结果以及事件信号的投资启示模拟。

## 功能模块

1. 项目首页：展示研究背景、核心结论和样本概况。
2. 事件库探索：基于原始事件库进行年份、事件类型、板块和股票关键词筛选。
3. 严格样本分析：展示 NEW_BUYABLE 与 SELL_ONLY 事件分布。
4. 核心实证结果：展示论文研究逻辑图、公告日 CAR 路径图、换手率机制图。
5. 投资启示模拟：展示 NEW 买入、高换手 NEW 筛选、SELL_ONLY 风险预警结果。
6. 数据下载：提供网页所用 CSV 数据下载。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Streamlit Cloud 部署

1. 将本文件夹上传至 GitHub 仓库。
2. 打开 Streamlit Community Cloud。
3. 选择 GitHub 仓库和 `streamlit_app.py`。
4. 点击 Deploy。

## 重要说明

本平台仅用于学术研究与数据展示，不构成任何投资建议。
