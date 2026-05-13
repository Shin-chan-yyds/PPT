import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="凤竹 EaaS 投资级决策沙盘", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border-radius: 8px; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #0056b3; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 凤竹纺织 EaaS 模式动态对标与风险压测沙盘 (V3.1)")
st.caption("核心逻辑：将【碳排放负债】计入总成本，揭示 EaaS 模式的【风险隔离】金融价值")

# --- 侧边栏：核心变量调节 ---
with st.sidebar:
    st.header("⚙️ 动态参数沙盘")

    with st.expander("🌍 宏观市场与政策波动", expanded=True):
        p_ng = st.slider("天然气当前市价 (元/m³)", 2.0, 6.0, 3.5, 0.1)
        carbon_tax = st.slider("全国碳市场交易价/碳税 (元/吨CO₂)", 0, 300, 80, 10)

    with st.expander("🏭 凤竹自营现状 (Baseline)", expanded=True):
        q_annual = st.number_input("年总蒸汽需求 (万吨)", value=80.0)
        eta_now = st.slider("自营锅炉效率 (%)", 75, 95, 88) / 100
        r_now = st.slider("自营孤岛余热回收率 (%)", 0, 15, 8) / 100
        om_now = st.number_input("自营年运维及折旧 (万元)", value=600)

    with st.expander("🛡️ EaaS 深度托管方案", expanded=True):
        r_eaas = st.slider("管家系统级回收率 (%)", 10, 30, 18) / 100
        p_settle = st.slider("EaaS 合同结算报价 (元/吨)", 250, 320, 285)
        asset_buyback = st.number_input("盘活沉淀资产(一次性回笼万元)", value=3500)

# --- 核心底层物理与财务算法 ---
base_gas_needed = 70.6
co2_factor = 1.9

# 1. 凤竹自营物理与财务模型
gas_per_ton_now = (base_gas_needed / eta_now) * (1 - r_now)
annual_gas_cost_now = gas_per_ton_now * p_ng * q_annual
annual_co2_now = (gas_per_ton_now * q_annual * 10000 * co2_factor) / 1000
carbon_cost_now = annual_co2_now * carbon_tax / 10000
total_cost_now = annual_gas_cost_now + om_now + carbon_cost_now
unit_cost_now = total_cost_now / q_annual

# 2. EaaS 托管模式模型
gas_per_ton_eaas = (base_gas_needed / 0.95) * (1 - r_eaas)
annual_co2_eaas = (gas_per_ton_eaas * q_annual * 10000 * co2_factor) / 1000
total_cost_eaas = p_settle * q_annual

# --- UI 展示区 ---
tab1, tab2, tab3 = st.tabs(["💰 真实 LCOE 与成本解构", "📉 能源与碳价双重风险压测", "🌿 绿色资产负债表"])

with tab1:
    st.subheader("当我们将『碳排放』计入成本后，凤竹真实的吨汽成本是多少？")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("凤竹自营真实吨汽成本", f"{unit_cost_now:.1f} 元", help="包含燃料、运维折旧及碳税")
    with col2:
        diff = p_settle - unit_cost_now
        st.metric("EaaS 锁定结算报价", f"{p_settle} 元", delta=f"{diff:.1f} 元", delta_color="inverse")
    with col3:
        st.metric("企业年化净利润增加", f"{total_cost_now - total_cost_eaas:.0f} 万元", help="自营总支出 - EaaS总支出")
    with col4:
        st.metric("首期现金流注入", f"+ {asset_buyback} 万元", help="通过设备回租/收购盘活的资金")

    st.divider()

    # 【核心视觉优化区】：将一张图拆分为左右两部分
    c_left, c_right = st.columns(2)

    with c_left:
        # 左图：用环形图展示内部结构，规避绝对值量级差异导致的不可见
        labels = ['天然气硬支出', '设备运维与折旧', '碳排放隐性负债']
        values = [annual_gas_cost_now, om_now, carbon_cost_now]
        fig_donut = px.pie(values=values, names=labels, hole=0.45,
                           title="凤竹现状：真实用能成本结构拆解",
                           color_discrete_sequence=['#1f77b4', '#ff7f0e', '#d62728'])
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)

    with c_right:
        # 右图：用极简的柱状图直接对比双方总账，直截了当
        df_compare = pd.DataFrame({
            '模式': ['凤竹当前自营总成本', 'EaaS深度托管总价'],
            '总成本 (万元)': [total_cost_now, total_cost_eaas]
        })
        fig_bar = px.bar(df_compare, x='模式', y='总成本 (万元)', text='总成本 (万元)',
                         color='模式',
                         color_discrete_map={'凤竹当前自营总成本': '#6c757d', 'EaaS深度托管总价': '#2ca02c'})
        fig_bar.update_traces(texttemplate='%{text:.0f} 万', textposition='outside')
        fig_bar.update_layout(title="宏观对决：年度总支出规模对比", showlegend=False,
                              yaxis_range=[0, max(total_cost_now, total_cost_eaas) * 1.2])
        st.plotly_chart(fig_bar, use_container_width=True)

    # 底部补充精确的数据透视表，弥补图形在极小数值上的读取困难
    st.markdown("#### 📝 年度用能支出明细账单 (单位：万元)")
    df_details = pd.DataFrame({
        "成本科目": ["天然气燃料支出", "设备运维、人工与折旧", "碳排放配额/碳税成本", "**年度综合总支出**"],
        "凤竹自营模式": [f"{annual_gas_cost_now:.0f}", f"{om_now:.0f}", f"{carbon_cost_now:.0f}",
                         f"**{total_cost_now:.0f}**"],
        "EaaS 深度托管": ["(由管家承担)", "(由管家承担)", "(由管家承担)", f"**{total_cost_eaas:.0f}**"]
    })
    st.table(df_details.set_index("成本科目"))

with tab2:
    st.subheader("⚖️ 宏观风险隔离：天然气暴涨时，谁在替凤竹扛雷？")
    gas_range = np.arange(2.5, 6.5, 0.5)
    cost_now_range = [(((gas_per_ton_now * p * q_annual)) + om_now + carbon_cost_now) for p in gas_range]
    cost_eaas_range = [total_cost_eaas for _ in gas_range]

    df_risk = pd.DataFrame({
        '极端气价模拟 (元/m³)': gas_range,
        '凤竹自营总敞口': cost_now_range,
        'EaaS 固定支出': cost_eaas_range
    })

    fig_risk = px.line(df_risk, x='极端气价模拟 (元/m³)', y=['凤竹自营总敞口', 'EaaS 固定支出'],
                       color_discrete_map={'凤竹自营总敞口': '#e63946', 'EaaS 固定支出': '#2a9d8f'},
                       markers=True)
    fig_risk.update_layout(yaxis_title="企业年度能源总支出 (万元)", hovermode="x unified")
    fig_risk.add_trace(
        go.Scatter(x=gas_range, y=cost_now_range, fill='tonexty', mode='none', fillcolor='rgba(230, 57, 70, 0.1)',
                   name='规避的亏损风险区'))
    st.plotly_chart(fig_risk, use_container_width=True)

with tab3:
    st.subheader("🍀 碳资产增量：从成本中心到利润中心")
    co2_diff = annual_co2_now - annual_co2_eaas

    c1, c2 = st.columns([1, 1])
    with c1:
        st.write("得益于管家将余热回收率从现状的极值拉升，每年额外减少碳排放：")
        st.title(f"↓ {co2_diff:.0f} 吨 CO₂")
        st.write("按照当前的碳交易价格，这相当于为凤竹/管家共同创造了：")
        st.subheader(f"{co2_diff * carbon_tax / 10000:.1f} 万元 的额外碳资产红利")

    with c2:
        labels = ['燃气直接排放', '余热逃逸等效排放']
        values_now = [annual_co2_now * 0.9, annual_co2_now * 0.1]
        fig_pie = px.pie(values=values_now, names=labels, title="凤竹当前碳排放结构分析", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)