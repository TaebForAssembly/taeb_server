from flask import g
from supabase import create_client, Client
from gotrue.errors import AuthApiError
import os

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

def get_db():
    if 'db' not in g:
        g.db = create_client(url, key)
    
    return g.db

def signed_in():
    supabase = get_db()
    try:
        supabase.auth.get_user()
        return True
    except AuthApiError:
        return False