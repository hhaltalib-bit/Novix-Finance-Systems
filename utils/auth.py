import hashlib
import random
import string
from datetime import datetime
from utils.database import supabase

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id(name: str) -> str:
    prefix = name[:3].upper()
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}-{numbers}"

def register_user(name, surname, password, salary, savings, wallet, language='ar'):
    if len(name) < 3:
        return {"success": False, "error": "name_short"}
    if not name or not surname or not password:
        return {"success": False, "error": "fill_all"}
    try:
        while True:
            uid = generate_user_id(name)
            check = supabase.table("users").select("user_id").eq("user_id", uid).execute()
            if not check.data:
                break
        res = supabase.table("users").insert({
            "user_id": uid,
            "name": name,
            "surname": surname,
            "password": hash_password(password),
            "salary_amount": salary,
            "savings_balance": savings,
            "current_wallet": wallet,
            "preferred_language": language,
            "preferred_theme": "dark",
            "preferred_currency": "IQD",
            "join_date": datetime.now().isoformat()
        }).execute()
        if res.data:
            return {"success": True, "user_id": uid}
        return {"success": False, "error": "db_error"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_user(name, surname, user_id, password):
    if not name or not surname or not user_id or not password:
        return {"success": False, "error": "fill_all"}
    try:
        result = supabase.table("users").select("*").eq(
            "name", name).eq("surname", surname).eq(
            "user_id", user_id).eq("password", hash_password(password)).execute()
        if result.data:
            return {"success": True, "user": result.data[0]}
        return {"success": False, "error": "invalid_credentials"}
    except Exception as e:
        return {"success": False, "error": str(e)}
