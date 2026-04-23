import streamlit as st
import pandas as pd
import io
from datetime import datetime
from config.translations import t
from utils.database import get_transactions
from utils.financial import CATEGORIES, CATEGORY_ICONS
from utils.currency import get_currency_display

def render(user, lang, theme, currency):
    user_id = user['user_id']

    st.markdown(f'<div class="novix-page-title anim-fade-up">{t("history", lang)}</div>', unsafe_allow_html=True)
    st.divider()

    # فلاتر
    st.markdown('<div class="novix-card">', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        type_options = [t('all_types', lang), t('expense', lang), t('income', lang)]
        sel_type = st.selectbox(t('filter_type', lang), type_options)

    with f2:
        cat_options = [t('all_types', lang)] + CATEGORIES
        sel_cat = st.selectbox(t('filter_category', lang), cat_options)

    with f3:
        now = datetime.now()
        months = t('months', lang)
        month_options = ['الكل'] + months
        sel_month_label = st.selectbox(t('filter_month', lang), month_options)
        sel_month = month_options.index(sel_month_label) if sel_month_label != 'الكل' else None

    with f4:
        search_term = st.text_input(t('search', lang), placeholder="🔍")

    st.markdown('</div>', unsafe_allow_html=True)

    # جلب البيانات مع الفلترة
    type_map = {t('expense', lang): 'expense', t('income', lang): 'income'}
    fetch_type = type_map.get(sel_type)
    fetch_cat = sel_cat if sel_cat != t('all_types', lang) else None

    txns = get_transactions(
        user_id,
        type=fetch_type,
        category=fetch_cat,
        month=sel_month,
        year=now.year if sel_month else None,
        search=search_term if search_term else None
    )

    if not txns:
        st.info(t('no_transactions', lang))
        return

    # عرض العمليات
    st.markdown(f"<div class='section-title'>{len(txns)} {'عملية' if lang == 'ar' else 'transactions'}</div>", unsafe_allow_html=True)

    for tx in txns:
        tt = tx.get('type', 'expense')
        cat = tx.get('category', '')
        icon = CATEGORY_ICONS.get(cat, '💰' if tt == 'income' else '📦')
        date_str = datetime.fromisoformat(tx['date'].replace('Z', '')).strftime('%Y/%m/%d — %H:%M')
        note = tx.get('note', '') or ''
        amount = tx.get('amount', 0)

        st.markdown(f"""
        <div class="novix-txn">
            <div class="novix-txn-icon {'inc' if tt=='income' else 'exp'}">{icon}</div>
            <div style="flex:1">
                <div class="novix-txn-name">{cat} {'— ' + note if note else ''}</div>
                <div class="novix-txn-date">{date_str}</div>
            </div>
            <div class="novix-txn-amt {'inc' if tt=='income' else 'exp'}">
                {'+' if tt=='income' else '-'}{get_currency_display(amount, currency)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # تصدير
    col_csv, col_pdf, _ = st.columns([1, 1, 3])

    with col_csv:
        df = pd.DataFrame(txns)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M')
            csv_data = df[['date', 'type', 'category', 'amount', 'note']].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label=t('export_csv', lang),
                data=csv_data.encode('utf-8-sig'),
                file_name=f"novix_transactions_{now.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col_pdf:
        if st.button(t('export_pdf', lang), use_container_width=True):
            st.info("PDF export — coming soon" if lang == 'en' else "تصدير PDF — قريباً")
