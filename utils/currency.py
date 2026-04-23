import requests
import streamlit as st
from datetime import datetime

CURRENCIES = {
    "IQD": {"name_ar": "دينار عراقي", "name_en": "Iraqi Dinar", "symbol": "د.ع", "flag": "🇮🇶"},
    "USD": {"name_ar": "دولار أمريكي", "name_en": "US Dollar", "symbol": "$", "flag": "🇺🇸"},
    "EUR": {"name_ar": "يورو", "name_en": "Euro", "symbol": "€", "flag": "🇪🇺"},
    "GBP": {"name_ar": "جنيه إسترليني", "name_en": "British Pound", "symbol": "£", "flag": "🇬🇧"},
    "SAR": {"name_ar": "ريال سعودي", "name_en": "Saudi Riyal", "symbol": "ر.س", "flag": "🇸🇦"},
    "AED": {"name_ar": "درهم إماراتي", "name_en": "UAE Dirham", "symbol": "د.إ", "flag": "🇦🇪"},
    "TRY": {"name_ar": "ليرة تركية", "name_en": "Turkish Lira", "symbol": "₺", "flag": "🇹🇷"},
}

@st.cache_data(ttl=3600)  # كاش ساعة واحدة
def get_exchange_rates(base: str = "IQD") -> dict:
    """جلب أسعار الصرف من API"""
    try:
        # API مجاني - exchangerate-api
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("rates", {})
    except:
        pass
    # أسعار احتياطية تقريبية لو فشل الـ API
    fallback = {
        "IQD": {"USD": 0.00076, "EUR": 0.00070, "GBP": 0.00060, "SAR": 0.00286, "AED": 0.00280, "TRY": 0.0245},
        "USD": {"IQD": 1310, "EUR": 0.92, "GBP": 0.79, "SAR": 3.75, "AED": 3.67, "TRY": 32.1},
    }
    return fallback.get(base, {})

def convert_amount(amount: float, from_currency: str, to_currency: str) -> float:
    """تحويل مبلغ من عملة لأخرى"""
    if from_currency == to_currency:
        return amount
    try:
        rates = get_exchange_rates(from_currency)
        rate = rates.get(to_currency, 1)
        return round(amount * rate, 2)
    except:
        return amount

def format_currency(amount: float, currency: str = "IQD") -> str:
    """تنسيق المبلغ مع رمز العملة"""
    info = CURRENCIES.get(currency, CURRENCIES["IQD"])
    symbol = info["symbol"]
    if currency == "IQD":
        return f"{amount:,.0f} {symbol}"
    elif currency in ["USD", "EUR", "GBP"]:
        return f"{symbol}{amount:,.2f}"
    else:
        return f"{amount:,.2f} {symbol}"

def get_currency_display(user_amount: float, user_currency: str = "IQD") -> str:
    """عرض المبلغ بعملة المستخدم"""
    converted = convert_amount(user_amount, "IQD", user_currency)
    return format_currency(converted, user_currency)
