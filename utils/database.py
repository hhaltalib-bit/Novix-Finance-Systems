import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# ============================================================
# الاتصال بقاعدة البيانات
# ============================================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================================
# دوال المستخدمين
# ============================================================
def get_user(user_id: str):
    """جلب بيانات المستخدم"""
    try:
        res = supabase.table("users").select("*").eq("user_id", user_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        st.error(f"خطأ في جلب بيانات المستخدم: {e}")
        return None

def update_user(user_id: str, data: dict):
    """تحديث بيانات المستخدم"""
    try:
        supabase.table("users").update(data).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        st.error(f"خطأ في تحديث البيانات: {e}")
        return False

def refresh_user_session(user_id: str):
    """تحديث بيانات المستخدم في الـ session"""
    user = get_user(user_id)
    if user:
        st.session_state.user_info = user
        st.session_state.lang = user.get("preferred_language", "ar")
        st.session_state.theme = user.get("preferred_theme", "dark")
        st.session_state.currency = user.get("preferred_currency", "IQD")

# ============================================================
# دوال العمليات المالية
# ============================================================
def add_transaction(user_id: str, type: str, category: str, amount: float, note: str = "", quantity: int = 1):
    """إضافة عملية مالية جديدة"""
    try:
        now = datetime.now()
        supabase.table("transactions").insert({
            "user_id": user_id,
            "type": type,
            "category": category,
            "amount": amount,
            "quantity": quantity,
            "note": note,
            "date": now.isoformat()
        }).execute()
        # تحديث الملخص الشهري
        field = "total_spent" if type == "expense" else "total_income"
        update_monthly_summary(user_id, amount, field)
        return True
    except Exception as e:
        st.error(f"خطأ في إضافة العملية: {e}")
        return False

def get_transactions(user_id: str, limit: int = None, month: int = None, year: int = None,
                     category: str = None, type: str = None, search: str = None):
    """جلب العمليات المالية مع فلترة"""
    try:
        query = supabase.table("transactions").select("*").eq("user_id", user_id)
        if type:
            query = query.eq("type", type)
        if category:
            query = query.eq("category", category)
        query = query.order("date", desc=True)
        if limit:
            query = query.limit(limit)
        res = query.execute()
        data = res.data or []
        # فلترة بالشهر والسنة
        if month and year:
            data = [
                t for t in data
                if datetime.fromisoformat(t['date'].replace('Z', '')).month == month
                and datetime.fromisoformat(t['date'].replace('Z', '')).year == year
            ]
        # بحث نصي
        if search:
            search = search.lower()
            data = [
                t for t in data
                if search in t.get('note', '').lower()
                or search in t.get('category', '').lower()
            ]
        return data
    except Exception as e:
        st.error(f"خطأ في جلب العمليات: {e}")
        return []

# ============================================================
# دوال الرواتب
# ============================================================
def check_salary_received(user_id: str, month: int, year: int) -> bool:
    """تحقق إذا استلم الراتب هذا الشهر"""
    try:
        res = supabase.table("salary_log").select("*").eq(
            "user_id", user_id).eq("month", month).eq("year", year).execute()
        return len(res.data) > 0
    except:
        return False

def record_salary(user_id: str, month: int, year: int):
    """تسجيل استلام الراتب"""
    try:
        supabase.table("salary_log").insert({
            "user_id": user_id,
            "month": month,
            "year": year,
            "received_at": datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        st.error(f"خطأ في تسجيل الراتب: {e}")
        return False

# ============================================================
# دوال التحويلات
# ============================================================
def add_transfer(user_id: str, direction: str, amount: float):
    """إضافة تحويل بين المحفظة والمدخرات"""
    try:
        supabase.table("transfers").insert({
            "user_id": user_id,
            "direction": direction,
            "amount": amount,
            "date": datetime.now().isoformat()
        }).execute()
        if direction == "to_savings":
            update_monthly_summary(user_id, amount, "total_saved")
        return True
    except Exception as e:
        st.error(f"خطأ في التحويل: {e}")
        return False

def get_transfers(user_id: str, limit: int = 10):
    """جلب سجل التحويلات"""
    try:
        res = supabase.table("transfers").select("*").eq(
            "user_id", user_id).order("date", desc=True).limit(limit).execute()
        return res.data or []
    except:
        return []

# ============================================================
# دوال الملخص الشهري
# ============================================================
def update_monthly_summary(user_id: str, amount: float, field: str):
    """تحديث الملخص الشهري للشهر الحالي فقط"""
    now = datetime.now()
    month, year = now.month, now.year
    try:
        existing = supabase.table("monthly_summary").select("*").eq(
            "user_id", user_id).eq("month", month).eq("year", year).execute()
        if existing.data:
            current = existing.data[0].get(field, 0) or 0
            supabase.table("monthly_summary").update(
                {field: current + amount}
            ).eq("user_id", user_id).eq("month", month).eq("year", year).execute()
        else:
            data = {
                "user_id": user_id, "month": month, "year": year,
                "total_spent": 0, "total_income": 0, "total_saved": 0
            }
            data[field] = amount
            supabase.table("monthly_summary").insert(data).execute()
    except Exception as e:
        st.error(f"خطأ في تحديث الملخص: {e}")

def get_monthly_summary(user_id: str, month: int = None, year: int = None):
    """جلب الملخص الشهري"""
    now = datetime.now()
    month = month or now.month
    year = year or now.year
    try:
        res = supabase.table("monthly_summary").select("*").eq(
            "user_id", user_id).eq("month", month).eq("year", year).execute()
        if res.data:
            return res.data[0]
        return {"total_spent": 0, "total_income": 0, "total_saved": 0, "month": month, "year": year}
    except:
        return {"total_spent": 0, "total_income": 0, "total_saved": 0}

def get_all_summaries(user_id: str, year: int = None):
    """جلب كل الملخصات الشهرية لسنة معينة"""
    now = datetime.now()
    year = year or now.year
    try:
        res = supabase.table("monthly_summary").select("*").eq(
            "user_id", user_id).eq("year", year).order("month").execute()
        return res.data or []
    except:
        return []

def get_previous_month_summary(user_id: str):
    """جلب ملخص الشهر الماضي للمقارنة"""
    now = datetime.now()
    if now.month == 1:
        month, year = 12, now.year - 1
    else:
        month, year = now.month - 1, now.year
    return get_monthly_summary(user_id, month, year)
