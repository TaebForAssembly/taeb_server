from flask import g
from supabase import create_client, Client
from gotrue.errors import AuthApiError
import os

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def get_db():
    return supabase

def signed_in():
    supabase = get_db()
    try:
        user = supabase.auth.get_user()
        return user is not None
    except AuthApiError:
        return False