import streamlit as st
from datetime import datetime
from config.translations import t
from config.themes import THEMES
from utils.database import update_user, refresh_user_session, supabase
from utils.auth import hash_password
from utils.currency import CURRENCIES, get_exchange_rates, format_currency, convert_amount
import json

# ============================================================
# دالة تغيير كلمة السر
# ============================================================
def change_password(user_id, current_pwd, new_pwd):
    try:
        check = supabase.table("users").select("user_id").eq(
            "user_id", user_id).eq("password", hash_password(current_pwd)).execute()
        if not check.data:
            return {"success": False, "error": "wrong_password"}
        supabase.table("users").update(
            {"password": hash_password(new_pwd)}
        ).eq("user_id", user_id).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
# الواجهة الرئيسية
# ============================================================
def render(user, lang, theme, currency):
    user_id = user['user_id']
    th = THEMES.get(theme, THEMES["dark"])

    # CSS الواجهة
    st.markdown(f"""
    <style>
    .s-page-title {{
        font-size: 1.5rem; font-weight: 800;
        color: {th['text_primary']}; margin-bottom: 4px;
    }}
    .s-page-sub {{
        font-size: 0.82rem; color: {th['text_secondary']}; margin-bottom: 24px;
    }}
    .s-section-label {{
        font-size: 0.7rem; font-weight: 700; letter-spacing: 2px;
        text-transform: uppercase; color: {th['text_muted']};
        margin: 20px 0 8px; padding-bottom: 6px;
        border-bottom: 1px solid {th['border']};
    }}
    .s-row {{
        display: flex; align-items: center; gap: 14px;
        padding: 14px 16px;
        background: {th['card_bg']};
        border: 1px solid {th['border']};
        border-radius: 12px; margin-bottom: 7px;
        transition: all 0.2s; cursor: pointer;
    }}
    .s-row:hover {{
        border-color: {th['accent']}40;
        box-shadow: 0 2px 12px {th['accent']}10;
    }}
    .s-row-icon {{
        width: 42px; height: 42px; border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size: 19px; flex-shrink: 0;
    }}
    .s-row-text {{ flex: 1; }}
    .s-row-name {{
        font-size: 13px; font-weight: 700; color: {th['text_primary']};
    }}
    .s-row-desc {{
        font-size: 10px; color: {th['text_muted']}; margin-top: 2px;
    }}
    .s-row-val {{
        font-size: 11px; font-weight: 600;
        padding: 4px 12px; border-radius: 20px;
        border: 1px solid; white-space: nowrap;
    }}
    .s-row-val.cyan {{
        color: {th['accent']};
        background: {th['accent']}12;
        border-color: {th['accent']}30;
    }}
    .s-row-val.green {{
        color: {th['success']};
        background: {th['success']}12;
        border-color: {th['success']}30;
    }}
    .s-row-val.yellow {{
        color: {th['warning']};
        background: {th['warning']}12;
        border-color: {th['warning']}30;
    }}
    .s-row-val.red {{
        color: {th['danger']};
        background: {th['danger']}12;
        border-color: {th['danger']}30;
    }}
    .s-row-arr {{
        color: {th['text_muted']}; font-size: 14px; margin-right: 4px;
    }}
    .s-modal {{
        background: {th['card_bg']};
        border: 1px solid {th['accent']}25;
        border-radius: 14px; padding: 20px; margin-top: 12px;
    }}
    .s-modal-bar {{
        height: 4px; background: {th['progress_bg']};
        border-radius: 2px; overflow: hidden; margin-bottom: 18px;
    }}
    .s-modal-bar-fill {{
        height: 100%; background: {th['accent']}; border-radius: 2px;
        transition: width 0.3s;
    }}
    .s-acct-grid {{
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 6px;
    }}
    .s-acct-item {{
        background: {th['progress_bg']};
        border: 1px solid {th['border']};
        border-radius: 10px; padding: 12px 14px;
    }}
    .s-acct-label {{
        font-size: 9px; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; color: {th['text_muted']};
        margin-bottom: 5px;
    }}
    .s-acct-val {{
        font-size: 14px; font-weight: 700; color: {th['text_primary']};
    }}
    .s-acct-val.mono {{
        font-family: monospace; letter-spacing: 1px; color: {th['accent']};
    }}
    .s-pwd-strength {{
        display: flex; align-items: center; gap: 8px; margin: 6px 0 12px;
    }}
    .s-pwd-bar {{
        flex: 1; height: 4px; background: {th['progress_bg']};
        border-radius: 2px; overflow: hidden;
    }}
    </style>
    """, unsafe_allow_html=True)

    # العنوان
    st.markdown(f"""
    <div class="s-page-title">⚙️ {t('settings', lang)}</div>
    <div class="s-page-sub">
        {'تخصيص تجربتك — التغييرات تُطبق فوراً' if lang == 'ar'
         else 'Customize your experience — changes apply instantly'}
    </div>
    """, unsafe_allow_html=True)

    # ============================================================
    # Section 1: التخصيص
    # ============================================================
    st.markdown(f"""
    <div class="s-section-label">
        {'🎨 التخصيص' if lang == 'ar' else '🎨 Customization'}
    </div>
    """, unsafe_allow_html=True)

    # اللغة
    lang_label = '🇮🇶 العربية' if lang == 'ar' else '🇬🇧 English'
    st.markdown(f"""
    <div class="s-row">
        <div class="s-row-icon" style="background:{th['accent']}12">🌐</div>
        <div class="s-row-text">
            <div class="s-row-name">{'اللغة' if lang == 'ar' else 'Language'}</div>
            <div class="s-row-desc">{'لغة واجهة النظام بالكامل' if lang == 'ar' else 'System interface language'}</div>
        </div>
        <div class="s-row-val cyan">{lang_label}</div>
    </div>
    """, unsafe_allow_html=True)

    lang_options = {'ar': 'العربية 🇮🇶', 'en': 'English 🇬🇧'}
    sel_lang = st.radio(
        'lang', list(lang_options.keys()),
        format_func=lambda x: lang_options[x],
        index=0 if lang == 'ar' else 1,
        horizontal=True, label_visibility='collapsed'
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # الثيم
    theme_name = THEMES.get(theme, {}).get(f'name_{"ar" if lang == "ar" else "en"}', theme)
    st.markdown(f"""
    <div class="s-row">
        <div class="s-row-icon" style="background:#7c4dff15">🎨</div>
        <div class="s-row-text">
            <div class="s-row-name">{'الثيم' if lang == 'ar' else 'Theme'}</div>
            <div class="s-row-desc">{'مظهر واجهة النظام والألوان' if lang == 'ar' else 'Interface appearance and colors'}</div>
        </div>
        <div class="s-row-val cyan">{theme_name}</div>
    </div>
    """, unsafe_allow_html=True)

    theme_options = {k: v[f'name_{"ar" if lang == "ar" else "en"}'] for k, v in THEMES.items()}
    sel_theme = st.radio(
        'theme', list(theme_options.keys()),
        format_func=lambda x: theme_options[x],
        index=list(theme_options.keys()).index(theme),
        horizontal=True, label_visibility='collapsed'
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # العملة
    curr_info = CURRENCIES.get(currency, {})
    curr_label = f"{curr_info.get('flag','')} {curr_info.get('name_ar' if lang == 'ar' else 'name_en', currency)}"
    st.markdown(f"""
    <div class="s-row">
        <div class="s-row-icon" style="background:{th['warning']}15">💱</div>
        <div class="s-row-text">
            <div class="s-row-name">{'العملة' if lang == 'ar' else 'Currency'}</div>
            <div class="s-row-desc">{'عملة عرض المبالغ والأرقام' if lang == 'ar' else 'Currency for displaying amounts'}</div>
        </div>
        <div class="s-row-val green">{curr_label}</div>
    </div>
    """, unsafe_allow_html=True)

    curr_options = {k: f"{v['flag']} {v['name_ar' if lang == 'ar' else 'name_en']} ({v['symbol']})"
                    for k, v in CURRENCIES.items()}
    sel_currency = st.radio(
        'currency', list(curr_options.keys()),
        format_func=lambda x: curr_options[x],
        index=list(curr_options.keys()).index(currency) if currency in curr_options else 0,
        horizontal=True, label_visibility='collapsed'
    )

    # زر حفظ التخصيص
    if st.button('💾 ' + ('حفظ التخصيص' if lang == 'ar' else 'Save Customization'),
                 use_container_width=True):
        update_user(user_id, {
            'preferred_language': sel_lang,
            'preferred_theme': sel_theme,
            'preferred_currency': sel_currency,
        })
        st.session_state.lang = sel_lang
        st.session_state.theme = sel_theme
        st.session_state.currency = sel_currency
        st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
        st.success(t('settings_saved', lang))
        refresh_user_session(user_id)
        st.rerun()

    # ============================================================
    # Section 2: الحساب
    # ============================================================
    st.markdown(f"""
    <div class="s-section-label">
        {'👤 الحساب' if lang == 'ar' else '👤 Account'}
    </div>
    """, unsafe_allow_html=True)

    # معلومات الحساب — صف قابل للنقر
    join_date = user.get('join_date', '')
    if join_date:
        try:
            join_date = datetime.fromisoformat(join_date.replace('Z', '')).strftime('%Y/%m/%d')
        except:
            join_date = join_date[:10]

    show_acct = st.session_state.get('show_acct_info', False)

    st.markdown(f"""
    <div class="s-row" onclick="">
        <div class="s-row-icon" style="background:{th['success']}12">👤</div>
        <div class="s-row-text">
            <div class="s-row-name">{'معلومات الحساب' if lang == 'ar' else 'Account Info'}</div>
            <div class="s-row-desc">{user.get('name','')} {user.get('surname','')} — {user.get('user_id','')}</div>
        </div>
        <div class="s-row-val green">{'عرض' if lang == 'ar' else 'View'}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(('▼ إخفاء المعلومات' if show_acct else '▶ عرض المعلومات') if lang == 'ar'
                 else ('▼ Hide Info' if show_acct else '▶ Show Info'),
                 key='toggle_acct', use_container_width=False):
        st.session_state.show_acct_info = not show_acct
        st.rerun()

    if show_acct:
        st.markdown(f"""
        <div class="s-acct-grid">
            <div class="s-acct-item">
                <div class="s-acct-label">{'الاسم الأول' if lang == 'ar' else 'First Name'}</div>
                <div class="s-acct-val">{user.get('name', '—')}</div>
            </div>
            <div class="s-acct-item">
                <div class="s-acct-label">{'اللقب' if lang == 'ar' else 'Surname'}</div>
                <div class="s-acct-val">{user.get('surname', '—')}</div>
            </div>
            <div class="s-acct-item">
                <div class="s-acct-label">{'الرقم التعريفي' if lang == 'ar' else 'User ID'}</div>
                <div class="s-acct-val mono">{user.get('user_id', '—')}</div>
            </div>
            <div class="s-acct-item">
                <div class="s-acct-label">{'تاريخ الانضمام' if lang == 'ar' else 'Join Date'}</div>
                <div class="s-acct-val mono" style="font-size:12px">{join_date}</div>
            </div>
            <div class="s-acct-item">
                <div class="s-acct-label">{'الراتب الشهري' if lang == 'ar' else 'Monthly Salary'}</div>
                <div class="s-acct-val" style="font-family:monospace;font-size:12px">
                    {user.get('salary_amount', 0):,.0f} {'د.ع' if lang == 'ar' else 'IQD'}
                </div>
            </div>
            <div class="s-acct-item">
                <div class="s-acct-label">{'اللغة المفضلة' if lang == 'ar' else 'Language'}</div>
                <div class="s-acct-val">
                    {'🇮🇶 العربية' if user.get('preferred_language') == 'ar' else '🇬🇧 English'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # تغيير كلمة السر
    show_pwd = st.session_state.get('show_pwd_modal', False)
    pwd_step = st.session_state.get('pwd_step', 1)

    st.markdown(f"""
    <div class="s-row">
        <div class="s-row-icon" style="background:{th['danger']}12">🔐</div>
        <div class="s-row-text">
            <div class="s-row-name">{'تغيير كلمة السر' if lang == 'ar' else 'Change Password'}</div>
            <div class="s-row-desc">{'3 خطوات للتحقق والتغيير الآمن' if lang == 'ar' else '3 steps for secure verification and change'}</div>
        </div>
        <div class="s-row-val red">{'تغيير' if lang == 'ar' else 'Change'}</div>
    </div>
    """, unsafe_allow_html=True)

    if not show_pwd:
        if st.button('🔐 ' + ('تغيير كلمة السر' if lang == 'ar' else 'Change Password'),
                     use_container_width=True):
            st.session_state.show_pwd_modal = True
            st.session_state.pwd_step = 1
            st.rerun()
    else:
        progress = {1: 33, 2: 66, 3: 100}.get(pwd_step, 33)
        step_label = {
            1: ('الخطوة 1 من 3 — التحقق من الـ ID' if lang == 'ar' else 'Step 1 of 3 — Verify ID'),
            2: ('الخطوة 2 من 3 — كلمة السر الحالية' if lang == 'ar' else 'Step 2 of 3 — Current Password'),
            3: ('الخطوة 3 من 3 — كلمة السر الجديدة' if lang == 'ar' else 'Step 3 of 3 — New Password'),
        }.get(pwd_step, '')

        st.markdown(f"""
        <div class="s-modal">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <span style="font-size:12px;font-weight:700;color:{th['text_secondary']}">{step_label}</span>
            </div>
            <div class="s-modal-bar">
                <div class="s-modal-bar-fill" style="width:{progress}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if pwd_step == 1:
            entered_id = st.text_input(
                t('user_id', lang), placeholder="AHM-4821", key="pwd_id"
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button('❌ ' + ('إلغاء' if lang == 'ar' else 'Cancel'),
                             use_container_width=True):
                    st.session_state.show_pwd_modal = False
                    st.rerun()
            with c2:
                if st.button('← ' + ('التالي' if lang == 'ar' else 'Next'),
                             use_container_width=True, type="primary"):
                    if entered_id.strip() == user_id:
                        st.session_state.pwd_step = 2
                        st.rerun()
                    else:
                        st.error('❌ ' + ('الـ ID غير صحيح' if lang == 'ar' else 'Incorrect ID'))

        elif pwd_step == 2:
            current_pwd = st.text_input(
                ('كلمة السر الحالية' if lang == 'ar' else 'Current Password'),
                type="password", key="pwd_current"
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button('→ ' + ('السابق' if lang == 'ar' else 'Back'),
                             use_container_width=True):
                    st.session_state.pwd_step = 1
                    st.rerun()
            with c2:
                if st.button('← ' + ('التالي' if lang == 'ar' else 'Next'),
                             use_container_width=True, type="primary"):
                    if not current_pwd:
                        st.error('⚠️ ' + ('أدخل كلمة السر الحالية' if lang == 'ar' else 'Enter current password'))
                    else:
                        check = supabase.table("users").select("user_id").eq(
                            "user_id", user_id).eq(
                            "password", hash_password(current_pwd)).execute()
                        if check.data:
                            st.session_state.pwd_step = 3
                            st.session_state.verified_pwd = current_pwd
                            st.rerun()
                        else:
                            st.error('❌ ' + ('كلمة السر الحالية غير صحيحة' if lang == 'ar' else 'Incorrect current password'))

        elif pwd_step == 3:
            new_pwd = st.text_input(
                ('كلمة السر الجديدة' if lang == 'ar' else 'New Password'),
                type="password", key="pwd_new"
            )
            confirm_pwd = st.text_input(
                ('تأكيد كلمة السر الجديدة' if lang == 'ar' else 'Confirm New Password'),
                type="password", key="pwd_confirm"
            )

            if new_pwd:
                strength = sum([
                    len(new_pwd) >= 8,
                    any(c.isupper() for c in new_pwd),
                    any(c.isdigit() for c in new_pwd),
                ])
                colors = ['#ff5252', '#ffd740', '#00e676']
                labels = ['ضعيفة' if lang == 'ar' else 'Weak',
                          'متوسطة' if lang == 'ar' else 'Medium',
                          'قوية' if lang == 'ar' else 'Strong']
                idx = min(strength - 1, 2) if strength > 0 else 0
                st.markdown(f"""
                <div class="s-pwd-strength">
                    <div class="s-pwd-bar">
                        <div style="width:{(strength/3)*100}%;height:100%;
                                    background:{colors[idx]};border-radius:2px;transition:width .3s"></div>
                    </div>
                    <span style="font-size:10px;font-weight:700;color:{colors[idx]}">{labels[idx]}</span>
                </div>
                """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button('→ ' + ('السابق' if lang == 'ar' else 'Back'),
                             use_container_width=True):
                    st.session_state.pwd_step = 2
                    st.rerun()
            with c2:
                if st.button('💾 ' + ('حفظ' if lang == 'ar' else 'Save'),
                             use_container_width=True, type="primary"):
                    if not new_pwd or not confirm_pwd:
                        st.error('⚠️ ' + ('أكمل جميع الحقول' if lang == 'ar' else 'Fill all fields'))
                    elif len(new_pwd) < 6:
                        st.error('⚠️ ' + ('6 أحرف على الأقل' if lang == 'ar' else 'Minimum 6 characters'))
                    elif new_pwd != confirm_pwd:
                        st.error('❌ ' + ('كلمتا السر غير متطابقتين' if lang == 'ar' else 'Passwords do not match'))
                    else:
                        result = change_password(user_id, st.session_state.get('verified_pwd',''), new_pwd)
                        if result['success']:
                            st.session_state.show_pwd_modal = False
                            st.session_state.pwd_step = 1
                            st.session_state.pop('verified_pwd', None)
                            st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
                            st.success('✅ ' + ('تم تغيير كلمة السر!' if lang == 'ar' else 'Password changed!'))
                        else:
                            st.error('❌ ' + ('حدث خطأ' if lang == 'ar' else 'An error occurred'))

    # ============================================================
    # Section 3: المالية
    # ============================================================
    st.markdown(f"""
    <div class="s-section-label">
        {'💰 المالية' if lang == 'ar' else '💰 Financial'}
    </div>
    """, unsafe_allow_html=True)

    # هدف الادخار
    savings = user.get('savings_balance', 0) or 0
    goal = user.get('savings_goal_amount', 0) or 0
    goal_months = user.get('savings_goal_months', 12) or 12
    goal_pct = min(int((savings / goal) * 100), 100) if goal > 0 else 0

    st.markdown(f"""
    <div class="s-row">
        <div class="s-row-icon" style="background:{th['warning']}15">🎯</div>
        <div class="s-row-text">
            <div class="s-row-name">{'هدف الادخار' if lang == 'ar' else 'Savings Goal'}</div>
            <div class="s-row-desc">
                {f'{goal:,.0f} د.ع — {goal_pct}% مكتمل' if goal > 0
                 else ('لم يُحدد بعد' if lang == 'ar' else 'Not set yet')}
            </div>
        </div>
        <div class="s-row-val yellow">{'تعديل' if lang == 'ar' else 'Edit'}</div>
    </div>
    """, unsafe_allow_html=True)

    show_goal = st.session_state.get('show_goal', False)
    if st.button('🎯 ' + ('تعديل هدف الادخار' if lang == 'ar' else 'Edit Savings Goal'),
                 key='btn_goal', use_container_width=False):
        st.session_state.show_goal = not show_goal
        st.rerun()

    if st.session_state.get('show_goal', False):
        with st.form("goal_form"):
            new_goal = st.number_input(
                t('goal_amount', lang), min_value=0, step=50000, value=int(goal)
            )
            new_months = st.number_input(
                t('goal_months', lang), min_value=1, max_value=120,
                value=int(goal_months), step=1
            )
            if new_goal > 0:
                monthly = (new_goal - savings) / new_months if new_months > 0 else 0
                progress = min((savings / new_goal) * 100, 100)
                st.markdown(f"""
                <div class="novix-progress-info">
                    <span>{'التقدم' if lang == 'ar' else 'Progress'}</span>
                    <span style="color:{th['warning']};font-weight:700">{progress:.1f}%</span>
                </div>
                <div class="novix-progress-bar">
                    <div class="novix-progress-fill warning" style="width:{progress}%"></div>
                </div>
                """, unsafe_allow_html=True)
            if st.form_submit_button('💾 ' + ('حفظ' if lang == 'ar' else 'Save'),
                                     use_container_width=True, type="primary"):
                update_user(user_id, {
                    'savings_goal_amount': new_goal,
                    'savings_goal_months': new_months
                })
                st.session_state.show_goal = False
                st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
                st.success(t('settings_saved', lang))
                refresh_user_session(user_id)
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # تقسيم الراتب
    salary = user.get('salary_amount', 0) or 0
    current_split = user.get('budget_split') or {}
    if isinstance(current_split, str):
        try: current_split = json.loads(current_split)
        except: current_split = {}
    split_desc = ' — '.join([f"{v}% {k}" for k, v in list(current_split.items())[:3]]) if current_split else ('لم يُحدد' if lang == 'ar' else 'Not set')

    st.markdown(f"""
    <div class="s-row">
        <div class="s-row-icon" style="background:{th['accent']}12">📊</div>
        <div class="s-row-text">
            <div class="s-row-name">{'تقسيم الراتب' if lang == 'ar' else 'Budget Split'}</div>
            <div class="s-row-desc">{split_desc}</div>
        </div>
        <div class="s-row-val cyan">{'تعديل' if lang == 'ar' else 'Edit'}</div>
    </div>
    """, unsafe_allow_html=True)

    show_budget = st.session_state.get('show_budget', False)
    if st.button('📊 ' + ('تعديل تقسيم الراتب' if lang == 'ar' else 'Edit Budget Split'),
                 key='btn_budget', use_container_width=False):
        st.session_state.show_budget = not show_budget
        st.rerun()

    if st.session_state.get('show_budget', False):
        st.markdown(f'<div class="notif-card info">💡 {"مجموع النسب يجب أن يساوي 100%" if lang == "ar" else "Percentages must total 100%"}</div>',
                    unsafe_allow_html=True)
        budget_categories = [
            ('ضروريات' if lang == 'ar' else 'Necessities', '🏠', 50),
            ('طعام' if lang == 'ar' else 'Food', '🍔', 20),
            ('مواصلات' if lang == 'ar' else 'Transport', '🚗', 10),
            ('ترفيه' if lang == 'ar' else 'Entertainment', '🎮', 10),
            ('ادخار' if lang == 'ar' else 'Savings', '🏦', 10),
        ]
        total_pct = 0
        new_split = {}
        cols = st.columns(len(budget_categories))
        for i, (name, icon, default) in enumerate(budget_categories):
            with cols[i]:
                val = st.number_input(
                    f"{icon} {name}", min_value=0, max_value=100,
                    value=int(current_split.get(name, default)),
                    step=5, key=f"bgt_{name}"
                )
                new_split[name] = val
                total_pct += val
                if salary > 0:
                    st.caption(f"{salary * val / 100:,.0f}")

        color = th['success'] if total_pct == 100 else th['danger']
        st.markdown(f"""
        <div style="text-align:center;margin:12px 0;font-size:1rem;font-weight:700;color:{color}">
            {'المجموع' if lang == 'ar' else 'Total'}: {total_pct}%
            {'✅' if total_pct == 100 else '❌'}
        </div>
        """, unsafe_allow_html=True)

        if st.button('💾 ' + ('حفظ التقسيم' if lang == 'ar' else 'Save Split'),
                     use_container_width=True, disabled=total_pct != 100):
            update_user(user_id, {'budget_split': json.dumps(new_split, ensure_ascii=False)})
            st.markdown("<script>playSuccess()</script>", unsafe_allow_html=True)
            st.success(t('settings_saved', lang))
            refresh_user_session(user_id)

    # ============================================================
    # Section 4: أسعار الصرف
    # ============================================================
    st.markdown(f"""
    <div class="s-section-label">
        {'📈 أسعار الصرف' if lang == 'ar' else '📈 Exchange Rates'}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="s-row">
        <div class="s-row-icon" style="background:#7c4dff15">📈</div>
        <div class="s-row-text">
            <div class="s-row-name">{'أسعار حية' if lang == 'ar' else 'Live Rates'}</div>
            <div class="s-row-desc">{'يتحدث كل ساعة تلقائياً' if lang == 'ar' else 'Updates automatically every hour'}</div>
        </div>
        <div class="s-row-val cyan">{'عرض' if lang == 'ar' else 'View'}</div>
    </div>
    """, unsafe_allow_html=True)

    show_rates = st.session_state.get('show_rates', False)
    if st.button('📈 ' + ('أسعار الصرف وحاسبة التحويل' if lang == 'ar' else 'Exchange Rates & Calculator'),
                 key='btn_rates', use_container_width=False):
        st.session_state.show_rates = not show_rates
        st.rerun()

    if st.session_state.get('show_rates', False):
        # أسعار احتياطية ثابتة + API
        FALLBACK_RATES = {
            "USD": 1310, "EUR": 1425, "GBP": 1661,
            "SAR": 349,  "AED": 357,  "TRY": 40
        }
        with st.spinner('جاري جلب الأسعار...' if lang == 'ar' else 'Fetching rates...'):
            rates_raw = get_exchange_rates("IQD")

        # استخدم الـ API لو نجح، وإلا الأسعار الاحتياطية
        display_rates = {}
        if rates_raw:
            for code in FALLBACK_RATES:
                r = rates_raw.get(code, 0)
                display_rates[code] = round(1/r) if r > 0 else FALLBACK_RATES[code]
        else:
            display_rates = FALLBACK_RATES

        now = datetime.now()
        source = ('أسعار تقريبية' if not rates_raw else 'أسعار حية') if lang == 'ar' else ('Approximate rates' if not rates_raw else 'Live rates')
        st.caption(f"{source} — {now.strftime('%H:%M:%S')}")

        target = ['USD', 'EUR', 'GBP', 'SAR', 'AED', 'TRY']
        cols = st.columns(3)
        for i, code in enumerate(target):
            info = CURRENCIES.get(code, {})
            inverse = display_rates.get(code, 0)
            with cols[i % 3]:
                st.markdown(f"""
                <div class="novix-kpi" style="margin-bottom:8px;">
                    <div class="kpi-label">{info.get('flag','')} {info.get('name_ar' if lang=='ar' else 'name_en','')}</div>
                    <div class="kpi-value primary" style="font-size:1rem;">
                        1 {info.get('symbol','')} = {inverse:,} {'د.ع' if lang=='ar' else 'IQD'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1:
            amt = st.number_input('المبلغ' if lang == 'ar' else 'Amount',
                                  min_value=0.0, value=1000.0, step=1000.0, key='rates_amt')
        with c2:
            fc = st.selectbox('من' if lang == 'ar' else 'From', list(CURRENCIES.keys()),
                              index=list(CURRENCIES.keys()).index('IQD'), key='rates_from')
        with c3:
            tc = st.selectbox('إلى' if lang == 'ar' else 'To', list(CURRENCIES.keys()),
                              index=list(CURRENCIES.keys()).index('USD'), key='rates_to')
        if amt > 0:
            res = convert_amount(amt, fc, tc)
            fi = CURRENCIES.get(fc, {})
            ti = CURRENCIES.get(tc, {})
            st.markdown(f"""
            <div class="notif-card success" style="text-align:center;font-size:1.1rem;font-weight:700;">
                {fi.get('flag','')} {format_currency(amt, fc)} = {ti.get('flag','')} {format_currency(res, tc)}
            </div>
            """, unsafe_allow_html=True)
