import streamlit as st
from datetime import datetime
from config.translations import t
from utils.database import update_user, add_transfer, get_transfers, refresh_user_session
from utils.currency import get_currency_display

def render(user, lang, theme, currency):
    user_id = user['user_id']
    wallet = user.get('current_wallet', 0) or 0
    savings = user.get('savings_balance', 0) or 0

    st.markdown(f'<div class="novix-page-title anim-fade-up">{t("transfer", lang)}</div>', unsafe_allow_html=True)
    st.divider()

    # عرض الأرصدة
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="novix-kpi anim-fade-up-1">
            <div class="kpi-label">{t('wallet_card', lang)}</div>
            <div class="kpi-value success">{get_currency_display(wallet, currency)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="novix-kpi anim-fade-up-2">
            <div class="kpi-label">{t('savings_card', lang)}</div>
            <div class="kpi-value warning">{get_currency_display(savings, currency)}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # نموذج التحويل
    st.markdown('<div class="novix-card anim-fade-up">', unsafe_allow_html=True)
    with st.form("transfer_form"):
        direction = st.radio(
            t('transfer_direction', lang),
            [t('to_savings', lang), t('to_wallet', lang)],
            horizontal=True
        )
        tr_amount = st.number_input(t('amount', lang), min_value=1, step=1000)

        # معاينة
        is_to_savings = direction == t('to_savings', lang)
        if is_to_savings:
            available = wallet
            st.caption(f"الرصيد المتاح للتحويل: {get_currency_display(available, currency)}")
        else:
            available = savings
            st.caption(f"الرصيد المتاح للسحب: {get_currency_display(available, currency)}")

        submitted = st.form_submit_button(t('transfer_btn', lang), use_container_width=True)

    if submitted:
        # أنيميشن التحويل
        with st.spinner(t('transfer_anim', lang)):
            import time
            time.sleep(0.8)

        if is_to_savings:
            if wallet >= tr_amount:
                update_user(user_id, {
                    "current_wallet": wallet - tr_amount,
                    "savings_balance": savings + tr_amount
                })
                add_transfer(user_id, "to_savings", tr_amount)
                st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
                st.success(t('transfer_success', lang))
                st.markdown(f"""
                <div class="notif-card success" style="text-align:center; font-size:1rem;">
                    👛 → 🏦<br>
                    <strong>{get_currency_display(tr_amount, currency)}</strong>
                </div>
                """, unsafe_allow_html=True)
                refresh_user_session(user_id)
                st.rerun()
            else:
                st.error(t('insufficient_wallet', lang))
        else:
            if savings >= tr_amount:
                update_user(user_id, {
                    "savings_balance": savings - tr_amount,
                    "current_wallet": wallet + tr_amount
                })
                add_transfer(user_id, "to_wallet", tr_amount)
                st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
                st.success(t('transfer_success', lang))
                st.markdown(f"""
                <div class="notif-card success" style="text-align:center; font-size:1rem;">
                    🏦 → 👛<br>
                    <strong>{get_currency_display(tr_amount, currency)}</strong>
                </div>
                """, unsafe_allow_html=True)
                refresh_user_session(user_id)
                st.rerun()
            else:
                st.error(t('insufficient_savings', lang))

    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # سجل التحويلات
    st.markdown(f'<div class="section-title">{t("transfer_history", lang)}</div>', unsafe_allow_html=True)
    transfers = get_transfers(user_id, limit=15)
    if transfers:
        for tr in transfers:
            direction_key = tr.get('direction', 'to_savings')
            is_saving = direction_key == 'to_savings'
            icon = '👛→🏦' if is_saving else '🏦→👛'
            label = t('to_savings', lang) if is_saving else t('to_wallet', lang)
            date_str = datetime.fromisoformat(tr['date'].replace('Z', '')).strftime('%Y/%m/%d — %H:%M')
            st.markdown(f"""
            <div class="novix-txn">
                <div class="novix-txn-icon {'inc' if is_saving else 'exp'}" style="font-size:0.85rem;">{icon}</div>
                <div style="flex:1">
                    <div class="novix-txn-name">{label}</div>
                    <div class="novix-txn-date">{date_str}</div>
                </div>
                <div class="novix-txn-amt {'inc' if is_saving else 'exp'}">{get_currency_display(tr['amount'], currency)}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(t('no_transactions', lang))
