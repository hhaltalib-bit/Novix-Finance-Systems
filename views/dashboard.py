import streamlit as st
from datetime import datetime
from config.translations import t
from utils.database import (get_transactions, get_monthly_summary, get_previous_month_summary,
                             check_salary_received, record_salary, update_user,
                             add_transaction, refresh_user_session, update_monthly_summary)
from utils.financial import (calculate_spending_percentage, get_top_categories,
                              generate_smart_notifications, generate_financial_tips,
                              generate_strength_badge, CATEGORY_ICONS, CATEGORIES)
from utils.currency import get_currency_display

def render(user, lang, theme, currency):
    now = datetime.now()
    user_id = user['user_id']
    month_name = t('months', lang)[now.month - 1]
    summary = get_monthly_summary(user_id, now.month, now.year)
    prev_summary = get_previous_month_summary(user_id)
    txns = get_transactions(user_id, month=now.month, year=now.year)
    recent_txns = get_transactions(user_id, limit=5)

    salary = user.get('salary_amount', 0) or 0
    wallet = user.get('current_wallet', 0) or 0
    savings = user.get('savings_balance', 0) or 0
    spent = summary.get('total_spent', 0) or 0
    prev_spent = prev_summary.get('total_spent', 0) or 0
    wallet_change = spent - prev_spent

    # Header
    st.markdown(f"""
    <div class="anim-fade-up">
        <div class="novix-page-title">{t('dashboard', lang)}</div>
        <div class="novix-page-sub">{t('welcome_back', lang)}, {user['name']} — {month_name} {now.year}</div>
    </div>
    """, unsafe_allow_html=True)

    # إشعارات ذكية
    notifications = generate_smart_notifications(user, summary, txns, lang)
    if notifications:
        with st.expander(f"🔔 {t('notifications', lang)} ({len(notifications)})", expanded=True):
            for n in notifications:
                msg = n['msg_ar'] if lang == 'ar' else n['msg_en']
                st.markdown(f'<div class="notif-card {n["type"]}">{n["icon"]} {msg}</div>', unsafe_allow_html=True)

    st.divider()

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, color, change_txt, anim in [
        (c1, t('salary_card', lang), salary, 'primary', '', 'anim-fade-up-1'),
        (c2, t('wallet_card', lang), wallet, 'success',
         f"{'▲' if wallet_change <= 0 else '▼'} {t('vs_last_month', lang)}", 'anim-fade-up-2'),
        (c3, t('savings_card', lang), savings, 'warning', '', 'anim-fade-up-3'),
        (c4, t('spent_card', lang), spent, 'danger',
         f"▼ {calculate_spending_percentage(spent, salary)}%", 'anim-fade-up-4'),
    ]:
        with col:
            change_html = f"<div class='kpi-change-{'up' if '▲' in change_txt else 'down'}'>{change_txt}</div>" if change_txt else ""
            st.markdown(f"""
            <div class="novix-kpi {anim}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value {color}">{get_currency_display(value, currency)}</div>
                {change_html}
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # زر الراتب
    col_s, _ = st.columns([2, 3])
    with col_s:
        if check_salary_received(user_id, now.month, now.year):
            st.info(t('salary_already', lang))
        else:
            if st.button(t('receive_salary', lang), use_container_width=True):
                update_user(user_id, {"current_wallet": wallet + salary})
                record_salary(user_id, now.month, now.year)
                update_monthly_summary(user_id, salary, "total_income")
                st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
                st.success(t('salary_received', lang))
                refresh_user_session(user_id)
                st.rerun()

    st.divider()

    # Row 2
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="novix-card anim-fade-up">', unsafe_allow_html=True)
        pct = calculate_spending_percentage(spent, salary)
        st.markdown(f"""
        <div class="novix-progress-info">
            <span>{t('spending_pct', lang)}</span>
            <span style="color:{'#ff5252' if pct>=80 else '#ffd740' if pct>=50 else 'inherit'}; font-weight:700;">{pct}%</span>
        </div>
        <div class="novix-progress-bar">
            <div class="novix-progress-fill {'warning' if pct>=80 else ''}" style="width:{min(pct,100)}%"></div>
        </div>
        """, unsafe_allow_html=True)

        goal = user.get('savings_goal_amount', 0) or 0
        if goal > 0:
            gp = min(int((savings / goal) * 10), 10)
            segs = ''.join([f'<div class="goal-seg {"filled" if i < gp else ""}"></div>' for i in range(10)])
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;font-size:0.75rem;opacity:0.6;margin-top:10px;margin-bottom:4px;">
                <span>{t('savings_goal', lang)}</span><span style="color:#ffd740;">{gp*10}%</span>
            </div>
            <div class="goal-segs" style="margin-bottom:16px;">{segs}</div>
            """, unsafe_allow_html=True)

        st.markdown(f'<div class="section-title">{t("top_categories", lang)}</div>', unsafe_allow_html=True)
        top_cats = get_top_categories(txns, 3)
        if top_cats:
            mx = top_cats[0][1]
            for cat, amt in top_cats:
                icon = CATEGORY_ICONS.get(cat, '📦')
                bp = int((amt / mx) * 100)
                st.markdown(f"""
                <div class="novix-cat-row">
                    <div class="novix-cat-emoji">{icon}</div>
                    <div style="flex:1">
                        <div class="novix-cat-name">{cat}</div>
                        <div class="novix-cat-bar"><div class="novix-cat-bar-fill" style="width:{bp}%"></div></div>
                    </div>
                    <div class="novix-cat-amount">-{get_currency_display(amt, currency)}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(t('no_data', lang))
        st.markdown('</div>', unsafe_allow_html=True)

        # اختصارات سريعة
        st.markdown(f'<div class="section-title">{t("quick_expense", lang)}</div>', unsafe_allow_html=True)
        quick_cats = ['طعام ومشروبات', 'مواصلات', 'ترفيه', 'فواتير']
        qc1, qc2 = st.columns(2)
        for i, cat in enumerate(quick_cats):
            icon = CATEGORY_ICONS.get(cat, '📦')
            with (qc1 if i % 2 == 0 else qc2):
                if st.button(f"{icon} {cat}", key=f"qk_{cat}", use_container_width=True):
                    st.session_state.quick_cat = cat
                    st.session_state.show_quick = True

        if st.session_state.get('show_quick'):
            qcat = st.session_state.get('quick_cat', '')
            with st.form("quick_form"):
                qa = st.number_input(t('amount', lang), min_value=1, step=1000)
                qn = st.text_input(t('note', lang))
                if st.form_submit_button(t('save', lang)):
                    if wallet >= qa:
                        update_user(user_id, {"current_wallet": wallet - qa})
                        add_transaction(user_id, "expense", qcat, qa, qn)
                        st.session_state.show_quick = False
                        st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
                        st.success(t('expense_success', lang))
                        refresh_user_session(user_id)
                        st.rerun()
                    else:
                        st.error(t('insufficient_wallet', lang))

    with col_r:
        st.markdown('<div class="novix-card anim-fade-up-2">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{t("wallet_balance", lang)} & {t("savings_balance", lang)}</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            st.markdown(f"""
            <div class="novix-bal-item">
                <div class="novix-bal-label">{t('wallet_card', lang)}</div>
                <div class="novix-bal-val">{get_currency_display(wallet, currency)}</div>
                <div class="novix-bal-change">{'▲' if wallet_change <= 0 else '▼'} {t('vs_last_month', lang)}</div>
            </div>""", unsafe_allow_html=True)
        with b2:
            st.markdown(f"""
            <div class="novix-bal-item">
                <div class="novix-bal-label">{t('savings_card', lang)}</div>
                <div class="novix-bal-val savings">{get_currency_display(savings, currency)}</div>
                <div class="novix-bal-change" style="opacity:0.4;">—</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="section-title" style="margin-top:16px;">{t("recent_txns", lang)}</div>', unsafe_allow_html=True)
        if recent_txns:
            for tx in recent_txns[:5]:
                tt = tx.get('type', 'expense')
                cat = tx.get('category', '')
                icon = CATEGORY_ICONS.get(cat, '💰' if tt == 'income' else '📦')
                ds = datetime.fromisoformat(tx['date'].replace('Z', '')).strftime('%d/%m — %H:%M')
                st.markdown(f"""
                <div class="novix-txn">
                    <div class="novix-txn-icon {'inc' if tt=='income' else 'exp'}">{icon}</div>
                    <div style="flex:1">
                        <div class="novix-txn-name">{cat}</div>
                        <div class="novix-txn-date">{ds}</div>
                    </div>
                    <div class="novix-txn-amt {'inc' if tt=='income' else 'exp'}">{'+' if tt=='income' else '-'}{get_currency_display(tx['amount'], currency)}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info(t('no_transactions', lang))
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # تسجيل العمليات
    tab_e, tab_i = st.tabs([t('add_expense', lang), t('add_income', lang)])

    with tab_e:
        # CSS القائمة المنسدلة حسب الثيم
        if theme in ("light", "green"):
            dropdown_bg = "#ffffff"
            dropdown_text = "#0f172a"
            dropdown_hover = "#e2e8f0"
        else:
            dropdown_bg = "#1a1b27"
            dropdown_text = "#e8eaf6"
            dropdown_hover = "#00e5ff20"

        st.markdown(f"""
        <style>
        ul[data-testid="stSelectboxVirtualDropdown"] {{
            background: {dropdown_bg} !important;
        }}
        ul[data-testid="stSelectboxVirtualDropdown"] li {{
            background: {dropdown_bg} !important;
            color: {dropdown_text} !important;
        }}
        ul[data-testid="stSelectboxVirtualDropdown"] li:hover {{
            background: {dropdown_hover} !important;
            color: {dropdown_text} !important;
        }}
        ul[data-testid="stSelectboxVirtualDropdown"] li[aria-selected="true"] {{
            background: {dropdown_hover} !important;
            color: {dropdown_text} !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        # بدون form حتى يتحدث المجموع لحظياً
        cat_labels = [f"{CATEGORY_ICONS.get(c, chr(128230))} {c}" for c in CATEGORIES]
        sel = st.selectbox(t("category", lang), cat_labels, key="exp_cat")
        sel_cat = CATEGORIES[cat_labels.index(sel)]

        c_price, c_qty = st.columns(2)
        with c_price:
            unit_price = st.number_input(
                ("💵 سعر الوحدة" if lang == "ar" else "💵 Unit Price"),
                min_value=0, step=500, value=0, key="exp_price"
            )
        with c_qty:
            qty = st.number_input(
                ("🔢 الكمية" if lang == "ar" else "🔢 Quantity"),
                min_value=1, step=1, value=1, key="exp_qty"
            )

        # المجموع يتحدث فوراً مع كل تغيير
        total = unit_price * qty
        total_color = "#ff5252" if total > 0 else "#94a3b8"
        total_bg = "#ff525210" if total > 0 else "transparent"
        total_border = "#ff525240" if total > 0 else "#ffffff15"
        st.markdown(f"""
        <div style="padding:16px 20px;border-radius:12px;border:2px solid {total_border};
                    background:{total_bg};display:flex;justify-content:space-between;
                    align-items:center;margin:10px 0;">
            <span style="font-size:13px;font-weight:700;color:{total_color};">
                💰 {"المجموع الكلي" if lang == "ar" else "Total Amount"}
            </span>
            <span style="font-size:20px;font-weight:800;font-family:monospace;color:{total_color};">
                {get_currency_display(total, currency)}
            </span>
        </div>
        """, unsafe_allow_html=True)

        en = st.text_input(t("note", lang), key="exp_note")

        if st.button(
            f"💾 {'حفظ' if lang == 'ar' else 'Save'} — {get_currency_display(total, currency)}",
            use_container_width=True, key="exp_save", type="primary"
        ):
            if total <= 0:
                st.error("⚠️ " + ("أدخل السعر والكمية" if lang == "ar" else "Enter price and quantity"))
            elif wallet >= total:
                update_user(user_id, {"current_wallet": wallet - total})
                add_transaction(user_id, "expense", sel_cat, total, en, qty)
                st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
                st.success(t("expense_success", lang))
                refresh_user_session(user_id)
                st.rerun()
            else:
                st.error(t("insufficient_wallet", lang))

    with tab_i:
        ia = st.number_input(t("amount", lang), min_value=1, step=500, key="inc_amt")
        in_ = st.text_input(t("note", lang), key="inc_note")

        if st.button(
            f"💾 {t('save', lang)}",
            use_container_width=True, key="inc_save", type="primary"
        ):
            update_user(user_id, {"current_wallet": wallet + ia})
            add_transaction(user_id, "income", "دخل إضافي", ia, in_)
            st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
            st.success(t("income_success", lang))
            refresh_user_session(user_id)
            st.rerun()

    # نصائح مالية
    tips = generate_financial_tips(user, summary, txns, lang)
    if tips:
        st.divider()
        with st.expander(f"💡 {t('tips', lang)}"):
            for tip in tips:
                title = tip['title_ar'] if lang == 'ar' else tip['title_en']
                msg = tip['msg_ar'] if lang == 'ar' else tip['msg_en']
                st.markdown(f'<div class="notif-card info">{tip["icon"]} <strong>{title}</strong><br><span style="font-size:0.82rem;opacity:0.85;">{msg}</span></div>', unsafe_allow_html=True)

    # نقاط القوة
    saved = summary.get('total_saved', 0) or 0
    badge = generate_strength_badge(saved, salary)
    if badge:
        msg = badge['msg_ar'] if lang == 'ar' else badge['msg_en']
        st.markdown(f'<div class="strength-badge anim-fade-up"><div class="strength-icon">{badge["icon"]}</div><div class="strength-msg">{msg}</div></div>', unsafe_allow_html=True)
