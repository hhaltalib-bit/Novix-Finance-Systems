from datetime import datetime

# ============================================================
# الأصناف الـ 15
# ============================================================
CATEGORIES = [
    'طعام ومشروبات', 'مواصلات', 'إيجار', 'صحة', 'ترفيه',
    'ملابس', 'سفر', 'فواتير', 'تعليم', 'هدايا',
    'حيوانات أليفة', 'رياضة واشتراكات', 'تكنولوجيا واشتراكات',
    'صيانة وإصلاح', 'ديون وأقساط'
]

CATEGORY_ICONS = {
    'طعام ومشروبات': '🍔', 'مواصلات': '🚗', 'إيجار': '🏠',
    'صحة': '💊', 'ترفيه': '🎮', 'ملابس': '👕', 'سفر': '✈️',
    'فواتير': '📄', 'تعليم': '🎓', 'هدايا': '🎁',
    'حيوانات أليفة': '🐾', 'رياضة واشتراكات': '💪',
    'تكنولوجيا واشتراكات': '📱', 'صيانة وإصلاح': '🔧',
    'ديون وأقساط': '💰'
}

# ============================================================
# حسابات مالية
# ============================================================
def calculate_spending_percentage(spent: float, salary: float) -> float:
    """نسبة الصرف من الراتب"""
    if salary <= 0:
        return 0
    return round((spent / salary) * 100, 1)

def calculate_savings_goal_progress(current_savings: float, goal_amount: float) -> float:
    """نسبة التقدم نحو هدف الادخار"""
    if goal_amount <= 0:
        return 0
    return min(round((current_savings / goal_amount) * 100, 1), 100)

def calculate_budget_split(salary: float, splits: dict) -> dict:
    """حساب تقسيم الراتب حسب نسب الزبون"""
    result = {}
    for category, percentage in splits.items():
        result[category] = round(salary * (percentage / 100), 0)
    return result

def get_top_categories(transactions: list, top_n: int = 3) -> list:
    """أكثر الأصناف إنفاقاً"""
    category_totals = {}
    for t in transactions:
        if t.get('type') == 'expense':
            cat = t.get('category', 'أخرى')
            category_totals[cat] = category_totals.get(cat, 0) + t.get('amount', 0)
    sorted_cats = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    return sorted_cats[:top_n]

def compare_months(current: dict, previous: dict) -> dict:
    """مقارنة شهرين"""
    def diff(curr, prev, key):
        c = curr.get(key, 0) or 0
        p = prev.get(key, 0) or 0
        change = c - p
        pct = round((change / p * 100), 1) if p > 0 else 0
        return {"current": c, "previous": p, "change": change, "pct": pct}
    return {
        "spent": diff(current, previous, "total_spent"),
        "income": diff(current, previous, "total_income"),
        "saved": diff(current, previous, "total_saved"),
    }

def generate_smart_notifications(user: dict, summary: dict, transactions: list, lang: str = 'ar') -> list:
    """توليد إشعارات ذكية بناءً على بيانات المستخدم"""
    notifications = []
    now = datetime.now()
    days_left = (datetime(now.year, now.month % 12 + 1 if now.month < 12 else 1,
                          1) - now).days if now.month < 12 else (datetime(now.year + 1, 1, 1) - now).days

    salary = user.get('salary_amount', 0) or 0
    spent = summary.get('total_spent', 0) or 0
    saved = summary.get('total_saved', 0) or 0

    if salary > 0:
        pct = (spent / salary) * 100
        # تنبيه إنفاق زائد
        if pct >= 80:
            notifications.append({
                "type": "warning",
                "icon": "⚠️",
                "msg_ar": f"صرفت {pct:.0f}% من راتبك وما زال {days_left} يوم بالشهر!",
                "msg_en": f"You've spent {pct:.0f}% of your salary with {days_left} days left!"
            })
        elif pct >= 50:
            notifications.append({
                "type": "info",
                "icon": "💡",
                "msg_ar": f"صرفت نصف راتبك تقريباً ({pct:.0f}%) — راقب إنفاقك",
                "msg_en": f"You've spent about half your salary ({pct:.0f}%) — watch your spending"
            })

        # تنبيه ادخار ممتاز
        savings_rate = (saved / salary) * 100 if salary > 0 else 0
        if savings_rate >= 20:
            notifications.append({
                "type": "success",
                "icon": "🏆",
                "msg_ar": f"ممتاز! ادخرت {savings_rate:.0f}% من راتبك هذا الشهر",
                "msg_en": f"Excellent! You saved {savings_rate:.0f}% of your salary this month"
            })

    # نصيحة أكثر صنف إنفاق
    top = get_top_categories(transactions, 1)
    if top:
        cat, amount = top[0]
        icon = CATEGORY_ICONS.get(cat, '📦')
        notifications.append({
            "type": "tip",
            "icon": "💡",
            "msg_ar": f"أنت تصرف أكثر على {icon} {cat} — حاول تقلل بعض الشيء",
            "msg_en": f"You spend most on {icon} {cat} — try to reduce a bit"
        })

    return notifications

def generate_financial_tips(user: dict, summary: dict, transactions: list, lang: str = 'ar') -> list:
    """نصائح مالية تلقائية"""
    tips = []
    salary = user.get('salary_amount', 0) or 0
    spent = summary.get('total_spent', 0) or 0
    saved = summary.get('total_saved', 0) or 0
    wallet = user.get('current_wallet', 0) or 0

    if salary > 0:
        # نصيحة قاعدة 50/30/20
        needs_budget = salary * 0.5
        wants_budget = salary * 0.3
        savings_budget = salary * 0.2

        tips.append({
            "icon": "📊",
            "title_ar": "قاعدة 50/30/20",
            "title_en": "50/30/20 Rule",
            "msg_ar": f"ضروريات: {needs_budget:,.0f} | ترفيه: {wants_budget:,.0f} | ادخار: {savings_budget:,.0f}",
            "msg_en": f"Needs: {needs_budget:,.0f} | Wants: {wants_budget:,.0f} | Savings: {savings_budget:,.0f}"
        })

        # نصيحة بناءً على الإنفاق
        top_cats = get_top_categories(transactions, 3)
        for cat, amount in top_cats:
            pct = (amount / salary) * 100
            if cat == 'طعام ومشروبات' and pct > 25:
                tips.append({
                    "icon": "🍔",
                    "title_ar": "إنفاقك على الطعام مرتفع",
                    "title_en": "High Food Spending",
                    "msg_ar": f"تصرف {pct:.0f}% من راتبك على الطعام — المعدل الصحي 15-20%",
                    "msg_en": f"You spend {pct:.0f}% on food — healthy average is 15-20%"
                })
            elif cat == 'ترفيه' and pct > 15:
                tips.append({
                    "icon": "🎮",
                    "title_ar": "إنفاقك على الترفيه مرتفع",
                    "title_en": "High Entertainment Spending",
                    "msg_ar": f"تصرف {pct:.0f}% على الترفيه — حاول تقلل لـ 10%",
                    "msg_en": f"You spend {pct:.0f}% on entertainment — try to reduce to 10%"
                })

    # نصيحة المحفظة
    if wallet < salary * 0.1 and salary > 0:
        tips.append({
            "icon": "👛",
            "title_ar": "رصيد المحفظة منخفض",
            "title_en": "Low Wallet Balance",
            "msg_ar": "رصيد محفظتك أقل من 10% من راتبك — فكر بتحويل من المدخرات",
            "msg_en": "Your wallet is below 10% of salary — consider transferring from savings"
        })

    return tips

def generate_month_end_report(user: dict, summary: dict, transactions: list, lang: str = 'ar') -> dict:
    """تقرير نهاية الشهر"""
    salary = user.get('salary_amount', 0) or 0
    spent = summary.get('total_spent', 0) or 0
    saved = summary.get('total_saved', 0) or 0
    income = summary.get('total_income', 0) or 0
    top_cats = get_top_categories(transactions, 3)

    return {
        "salary": salary,
        "total_income": income,
        "total_spent": spent,
        "total_saved": saved,
        "remaining": salary + income - spent,
        "spending_pct": calculate_spending_percentage(spent, salary),
        "savings_rate": round((saved / salary * 100), 1) if salary > 0 else 0,
        "top_categories": top_cats,
        "transactions_count": len(transactions)
    }

def generate_strength_badge(saved: float, salary: float, consecutive_months: int = 0) -> dict:
    """نقاط القوة المالية"""
    if salary <= 0:
        return None
    rate = (saved / salary) * 100
    if rate >= 30:
        return {"icon": "🏆", "level": "ذهبي" if True else "Gold", "msg_ar": "مدخر ممتاز! وفرت أكثر من 30% من راتبك", "msg_en": "Excellent saver! You saved over 30% of your salary"}
    elif rate >= 20:
        return {"icon": "🥈", "level": "فضي" if True else "Silver", "msg_ar": "مدخر جيد! وفرت أكثر من 20% من راتبك", "msg_en": "Good saver! You saved over 20% of your salary"}
    elif rate >= 10:
        return {"icon": "🥉", "level": "برونزي" if True else "Bronze", "msg_ar": "بداية جيدة! وفرت أكثر من 10% من راتبك", "msg_en": "Good start! You saved over 10% of your salary"}
    return None
