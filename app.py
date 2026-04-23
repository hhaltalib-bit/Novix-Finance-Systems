import streamlit as st
from config.themes import get_theme_css
from config.translations import t
from utils.database import refresh_user_session
from utils.auth import register_user, login_user

st.set_page_config(
    page_title="NOVIX Systems",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}  # ✅ يشيل أيقونات GitHub والقلم والـ Deploy
)

# ============================================================
# إدارة الجلسة
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.session_state.lang = 'ar'
    st.session_state.theme = 'dark'
    st.session_state.currency = 'IQD'
    st.session_state.page = 'dashboard'
    st.session_state.show_splash = True

# تطبيق الثيم
theme = st.session_state.get('theme', 'dark')
lang = st.session_state.get('lang', 'ar')
st.markdown(get_theme_css(theme), unsafe_allow_html=True)

# ✅ إخفاء شريط Streamlit العلوي بالكامل
st.markdown("""<style>header[data-testid=\"stHeader\"]{display:none!important;}div[data-testid=\"stToolbar\"]{display:none!important;}#MainMenu{display:none!important;}footer{display:none!important;}.stDeployButton{display:none!important;}</style>""", unsafe_allow_html=True)

# ============================================================
# شاشة التحميل (Splash Screen)
# ============================================================
if st.session_state.get('show_splash') and st.session_state.logged_in:
    st.markdown("""
    <div style="text-align:center; padding: 80px 0;">
        <div class="novix-logo-text" style="font-size:3.5rem; letter-spacing:6px;">NOVIX</div>
        <div style="font-size:0.7rem; letter-spacing:4px; opacity:0.4; margin-top:8px;">FINANCIAL SYSTEM</div>
        <div style="margin-top:24px; font-size:0.9rem; opacity:0.5;">جاري التحميل...</div>
    </div>
    """, unsafe_allow_html=True)
    import time
    time.sleep(1.2)
    st.session_state.show_splash = False
    st.rerun()

# ============================================================
# واجهة التسجيل والدخول
# ============================================================
if not st.session_state.logged_in:

    # ✅ إخفاء السايدبار فقط في صفحة الدخول
    st.markdown("""
    <style>
        div[data-testid="stSidebar"] { display: none !important; }
        div[data-testid="collapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # اختيار اللغة
    col_space, col_lang = st.columns([4, 1])
    with col_lang:
        lang_choice = st.selectbox("🌐", ["العربية", "English"], label_visibility="collapsed")
        st.session_state.lang = 'ar' if lang_choice == "العربية" else 'en'
    lang = st.session_state.lang

    # Header
    st.markdown(f"""
    <div style="text-align:center; padding: 32px 0 24px;">
        <div class="novix-logo-text" style="font-size:2.8rem;">NOVIX</div>
        <div class="novix-logo-sub" style="font-size:0.75rem; margin-top:4px;">
            {'نظام إدارة مالية ذكي' if lang == 'ar' else 'Smart Financial Management System'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs([t('login_tab', lang), t('signup_tab', lang)])

    # --- تبويب الدخول ---
    with tab_login:
        st.markdown(f"<p class='section-title'>{t('login_title', lang)}</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            c1, c2 = st.columns(2)
            l_name = c1.text_input(t('first_name', lang))
            l_surname = c2.text_input(t('surname', lang))
            l_id = st.text_input(t('user_id', lang))
            l_pwd = st.text_input(t('password', lang), type="password")
            submitted = st.form_submit_button(t('login_btn', lang), use_container_width=True)

        if submitted:
            result = login_user(l_name, l_surname, l_id, l_pwd)
            if result["success"]:
                st.session_state.logged_in = True
                st.session_state.user_info = result["user"]
                st.session_state.lang = result["user"].get("preferred_language", "ar")
                st.session_state.theme = result["user"].get("preferred_theme", "dark")
                st.session_state.currency = result["user"].get("preferred_currency", "IQD")
                st.session_state.show_splash = True
                st.rerun()
            else:
                st.error(t('login_error', lang))

    # --- تبويب التسجيل ---
    with tab_signup:
        st.markdown(f"<p class='section-title'>{t('signup_title', lang)}</p>", unsafe_allow_html=True)

        # ✅ حالة: تم التسجيل — نعرض الـ ID وزر دخول مباشر
        if st.session_state.get('just_registered'):
            reg_user = st.session_state.just_registered
            uid = reg_user['user_id']

            st.success(t('signup_success', lang))
            st.markdown(f"""
            <div style="text-align:center; padding:24px; background:#00e67610;
                        border:1px solid #00e67640; border-radius:16px; margin:16px 0;">
                <div style="font-size:0.8rem; opacity:0.6; margin-bottom:10px;">
                    {'رقمك التعريفي — احفظه!' if lang == 'ar' else 'Your ID — Save it!'}
                </div>
                <div style="font-size:2.2rem; font-weight:800; letter-spacing:6px;
                            color:#00e5ff; font-family:monospace;">
                    {uid}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.warning(t('save_id_warning', lang))
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button(
                '🚀 ' + ('دخول المنصة الآن' if lang == 'ar' else 'Enter Platform Now'),
                use_container_width=True,
                type="primary"
            ):
                st.session_state.logged_in = True
                st.session_state.user_info = reg_user
                st.session_state.lang = reg_user.get('preferred_language', lang)
                st.session_state.theme = reg_user.get('preferred_theme', 'dark')
                st.session_state.currency = reg_user.get('preferred_currency', 'IQD')
                st.session_state.show_splash = True
                del st.session_state['just_registered']
                st.rerun()

        else:
            with st.form("signup_form"):
                c1, c2 = st.columns(2)
                new_name = c1.text_input(t('first_name', lang))
                new_surname = c2.text_input(t('surname', lang))
                new_pwd = st.text_input(t('password', lang), type="password")
                c3, c4, c5 = st.columns(3)
                s_salary = c3.number_input(t('salary', lang), min_value=0, step=10000)
                s_savings = c4.number_input(t('savings', lang), min_value=0, step=10000)
                s_wallet = c5.number_input(t('wallet', lang), min_value=0, step=10000)
                submitted2 = st.form_submit_button(t('create_account', lang), use_container_width=True)

            if submitted2:
                result = register_user(new_name, new_surname, new_pwd, s_salary, s_savings, s_wallet, lang)
                if result["success"]:
                    from utils.database import get_user
                    new_user_data = get_user(result["user_id"])
                    st.session_state.just_registered = new_user_data
                    st.rerun()
                else:
                    err = result.get("error", "")
                    if err == "name_short":
                        st.error(t('name_short', lang))
                    elif err == "fill_all":
                        st.error(t('fill_all', lang))
                    else:
                        st.error(f"خطأ: {err}")

# ============================================================
# واجهة النظام الرئيسية
# ============================================================
else:
    user = st.session_state.user_info
    lang = st.session_state.lang
    theme = st.session_state.theme
    currency = st.session_state.get('currency', 'IQD')
    user_id = user['user_id']

    refresh_user_session(user_id)
    user = st.session_state.user_info

    # --- الشريط الجانبي ---
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 8px 0 20px;">
            <div class="novix-logo-text">NOVIX</div>
            <div class="novix-logo-sub">FINANCIAL SYSTEM</div>
        </div>
        <div style="padding: 16px 0;
                    border-top: 1px solid {('#ffffff08' if theme == 'dark' else '#ffffff15')};
                    border-bottom: 1px solid {('#ffffff08' if theme == 'dark' else '#ffffff15')};
                    margin-bottom: 16px;">
            <div style="font-size:1.8rem; margin-bottom:6px;">👤</div>
            <div style="font-weight:700; font-size:1rem;">{user['name']} {user['surname']}</div>
            <div style="font-size:0.72rem; opacity:0.5; font-family:monospace;">{user_id}</div>
        </div>
        """, unsafe_allow_html=True)

        pages = {
            'dashboard': t('dashboard', lang),
            'transfer': t('transfer', lang),
            'history': t('history', lang),
            'analytics': t('analytics', lang),
            'settings': t('settings', lang),
        }

        current_page = st.session_state.get('page', 'dashboard')
        for page_key, page_label in pages.items():
            is_active = current_page == page_key
            if st.button(
                page_label,
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.page = page_key
                st.rerun()

        st.divider()
        if st.button(t('logout_btn', lang), use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- تحميل الصفحة --- مستوردة من views مو pages
    page = st.session_state.get('page', 'dashboard')

    if page == 'dashboard':
        from views.dashboard import render
        render(user, lang, theme, currency)
    elif page == 'transfer':
        from views.transfers import render
        render(user, lang, theme, currency)
    elif page == 'history':
        from views.history import render
        render(user, lang, theme, currency)
    elif page == 'analytics':
        from views.analytics import render
        render(user, lang, theme, currency)
    elif page == 'settings':
        from views.settings import render
        render(user, lang, theme, currency)
