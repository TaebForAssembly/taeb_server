from flask import g
from supabase import create_client, Client, ClientOptions
from gotrue.errors import AuthApiError
import os

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
admin_key: str = os.environ.get("SUPABASE_ADMIN_KEY")
supabase = create_client(url, key)
supabase_admin = create_client(url, admin_key, options=ClientOptions(auto_refresh_token=False, persist_session=False))

def get_db():
    return supabase

def signed_in():
    supabase = get_db()
    try:
        user = supabase.auth.get_user()
        return user is not None
    except AuthApiError:
        return False