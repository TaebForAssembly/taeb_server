from flask import g
from supabase import create_client, Client

url: str = "https://vdktuvrsapclxnmqdieg.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZka3R1dnJzYXBjbHhubXFkaWVnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYzODA2MTgsImV4cCI6MjA2MTk1NjYxOH0.iQwdvRGT0eOcnZe9Fyv9oFLNLF2CyleEdCjxBqxdbag"

def get_db():
    if 'db' not in g:
        g.db = create_client(url, key)
    
    return g.db