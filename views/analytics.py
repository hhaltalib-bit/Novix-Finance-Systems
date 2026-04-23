import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from config.translations import t
from utils.database import get_transactions, get_all_summaries, get_monthly_summary, get_previous_month_summary
from utils.financial import CATEGORY_ICONS, compare_months, generate_month_end_report
from utils.currency import get_currency_display

CHART_COLORS = ['#00e5ff','#7c4dff','#00e676','#ffd740','#ff5252',
                '#ff6b35','#a8ff78','#f8cdda','#1d976c','#93f9b9',
                '#c471ed','#f64f59','#43cea2','#185a9d','#43c6ac']

def chart_layout(fig, theme):
    is_dark = theme == 'dark'
    bg = 'rgba(0,0,0,0)'
    font_color = '#e8eaf6' if is_dark else '#1a1a2e'
    grid_color = '#ffffff11' if is_dark else '#00000011'
    fig.update_layout(
        paper_bgcolor=bg, plot_bgcolor=bg,
        font_color=font_color, font_family='Tajawal',
        xaxis=dict(gridcolor=grid_color, showgrid=True),
        yaxis=dict(gridcolor=grid_color, showgrid=True),
        margin=dict(t=30, b=10, l=10, r=10)
    )
    return fig

def render(user, lang, theme, currency):
    user_id = user['user_id']
    now = datetime.now()
    months_labels = t('months', lang)

    st.markdown(f'<div class="novix-page-title anim-fade-up">{t("analytics", lang)}</div>', unsafe_allow_html=True)
    st.divider()

    all_txns = get_transactions(user_id)
    all_summary = get_all_summaries(user_id, now.year)
    curr_summary = get_monthly_summary(user_id, now.month, now.year)
    prev_summary = get_previous_month_summary(user_id)

    # --- رسم 1: توزيع المصاريف حسب الصنف ---
    st.markdown(f'<div class="section-title">{t("chart_expenses_cat", lang)}</div>', unsafe_allow_html=True)
    expenses = [tx for tx in all_txns if tx.get('type') == 'expense']
    if expenses:
        df_exp = pd.DataFrame(expenses)
        cat_group = df_exp.groupby('category')['amount'].sum().reset_index()
        cat_group['icon'] = cat_group['category'].map(lambda x: CATEGORY_ICONS.get(x, '📦'))
        cat_group['label'] = cat_group.apply(lambda r: f"{r['icon']} {r['category']}", axis=1)
        fig1 = px.pie(cat_group, values='amount', names='label',
                      color_discrete_sequence=CHART_COLORS, hole=0.45)
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(chart_layout(fig1, theme), use_container_width=True)
    else:
        st.info(t('no_data', lang))

    st.divider()

    # --- رسم 2: الدخل مقابل المصروف شهرياً ---
    st.markdown(f'<div class="section-title">{t("chart_monthly", lang)}</div>', unsafe_allow_html=True)
    if all_summary:
        df_sum = pd.DataFrame(all_summary)
        df_sum['month_label'] = df_sum['month'].apply(lambda m: months_labels[m-1])
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_sum['month_label'], y=df_sum['total_income'],
                              name='دخل' if lang == 'ar' else 'Income',
                              marker_color='#00e676', text=df_sum['total_income'],
                              texttemplate='%{text:,.0f}', textposition='outside'))
        fig2.add_trace(go.Bar(x=df_sum['month_label'], y=df_sum['total_spent'],
                              name='مصروف' if lang == 'ar' else 'Expenses',
                              marker_color='#ff5252', text=df_sum['total_spent'],
                              texttemplate='%{text:,.0f}', textposition='outside'))
        fig2.update_layout(barmode='group')
        st.plotly_chart(chart_layout(fig2, theme), use_container_width=True)
    else:
        st.info(t('no_data', lang))

    st.divider()

    # --- رسم 3: معدل الادخار ---
    st.markdown(f'<div class="section-title">{t("chart_savings_rate", lang)}</div>', unsafe_allow_html=True)
    if all_summary:
        df_sum = pd.DataFrame(all_summary)
        df_sum['month_label'] = df_sum['month'].apply(lambda m: months_labels[m-1])
        df_sum['savings_rate'] = df_sum.apply(
            lambda r: round((r['total_saved'] / r['total_income'] * 100), 1)
            if r['total_income'] > 0 else 0, axis=1)
        fig3 = px.line(df_sum, x='month_label', y='savings_rate',
                       markers=True, color_discrete_sequence=['#00e5ff'])
        fig3.update_traces(line=dict(width=3), marker=dict(size=9, color='#7c4dff',
                                                            line=dict(width=2, color='#00e5ff')))
        fig3.update_layout(yaxis_title='%')
        st.plotly_chart(chart_layout(fig3, theme), use_container_width=True)
    else:
        st.info(t('no_data', lang))

    st.divider()

    # --- مقارنة الأشهر ---
    st.markdown(f'<div class="section-title">{t("month_comparison", lang)}</div>', unsafe_allow_html=True)
    comparison = compare_months(curr_summary, prev_summary)
    curr_month = months_labels[now.month - 1]
    prev_month_idx = (now.month - 2) % 12
    prev_month = months_labels[prev_month_idx]

    for key, label in [('spent', t('spent_card', lang)), ('income', t('salary_card', lang)), ('saved', t('savings_card', lang))]:
        data = comparison[key]
        change = data['change']
        pct = data['pct']
        color = 'success' if (key == 'income' or key == 'saved') and change >= 0 else 'danger' if change < 0 else 'warning'
        arrow = '▲' if change >= 0 else '▼'
        st.markdown(f"""
        <div class="novix-card" style="padding:14px 20px; margin-bottom:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:0.78rem; opacity:0.5;">{label}</div>
                    <div style="font-size:1rem; font-weight:700;">{get_currency_display(data['current'], currency)}</div>
                </div>
                <div style="text-align:center; opacity:0.5; font-size:0.75rem;">{prev_month} → {curr_month}</div>
                <div class="kpi-change-{'up' if change >= 0 else 'down'}" style="font-size:0.9rem; font-weight:700;">
                    {arrow} {abs(pct)}%
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- التقرير السنوي ---
    st.markdown(f'<div class="section-title">{t("chart_annual", lang)}</div>', unsafe_allow_html=True)
    if all_summary:
        df_year = pd.DataFrame(all_summary)
        total_income = df_year['total_income'].sum()
        total_spent = df_year['total_spent'].sum()
        total_saved = df_year['total_saved'].sum()

        c1, c2, c3 = st.columns(3)
        for col, label, val, color in [
            (c1, '💰 إجمالي الدخل' if lang == 'ar' else '💰 Total Income', total_income, 'success'),
            (c2, '📉 إجمالي المصاريف' if lang == 'ar' else '📉 Total Expenses', total_spent, 'danger'),
            (c3, '🏦 إجمالي الادخار' if lang == 'ar' else '🏦 Total Saved', total_saved, 'warning'),
        ]:
            with col:
                st.markdown(f"""
                <div class="novix-kpi">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value {color}">{get_currency_display(val, currency)}</div>
                </div>""", unsafe_allow_html=True)

        # Sunburst
        fig4 = go.Figure(go.Sunburst(
            labels=['Year', 'Income', 'Expenses', 'Savings'],
            parents=['', 'Year', 'Year', 'Year'],
            values=[0, total_income, total_spent, total_saved],
            branchvalues='total',
            marker=dict(colors=['#0d0e14', '#00e676', '#ff5252', '#00e5ff'])
        ))
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e8eaf6')
        st.plotly_chart(fig4, use_container_width=True)

        # تقرير نهاية الشهر
        if now.day >= 25:
            st.divider()
            st.markdown(f'<div class="section-title">{t("month_report", lang)}</div>', unsafe_allow_html=True)
            report = generate_month_end_report(user, curr_summary, [tx for tx in all_txns
                                                                      if datetime.fromisoformat(tx['date'].replace('Z','')).month == now.month], lang)
            st.markdown(f"""
            <div class="strength-badge">
                <div style="font-size:1rem; font-weight:700;">📊 {months_labels[now.month-1]} {now.year}</div>
                <div style="margin-top:12px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; text-align:center;">
                    <div><div style="font-size:0.7rem; opacity:0.6;">{'صرفت' if lang=='ar' else 'Spent'}</div><div style="font-weight:700; color:#ff5252;">{get_currency_display(report['total_spent'], currency)}</div></div>
                    <div><div style="font-size:0.7rem; opacity:0.6;">{'ادخرت' if lang=='ar' else 'Saved'}</div><div style="font-weight:700; color:#00e676;">{get_currency_display(report['total_saved'], currency)}</div></div>
                    <div><div style="font-size:0.7rem; opacity:0.6;">{'معدل الادخار' if lang=='ar' else 'Savings Rate'}</div><div style="font-weight:700; color:#ffd740;">{report['savings_rate']}%</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(t('no_data', lang))
