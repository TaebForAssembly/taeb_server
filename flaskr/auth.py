from flask import Blueprint, render_template, request, g
from supabase import create_client, Client
from .db import get_db

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=["GET"])
def login():
    return render_template('authentication/login.html')

@bp.route('/login', methods=["POST"])
def login_post():
    # get data
    email = request.form.get("email")
    password = request.form.get("password")
    
    supabase = get_db()

    try:
        supabase.auth.sign_in_with_password(
            {
                "email": email, 
                "password": password,
            }
        )

        return redirect("/mailing_list")
    except AuthApiError:
        return {
            "success": False
        }

@bp.route('/logout', methods=["POST"])
def logout():
    supabase = get_db()
    supabase.auth.sign_out()
    return redirect("/login")