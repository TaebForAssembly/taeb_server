from flask import Blueprint, render_template, request, redirect
from supabase import create_client, Client
from gotrue.errors import AuthApiError
from .db import get_db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        supabase = get_db()
        supabase.auth.sign_in_with_password(
            {
                "email": email, 
                "password": password,
            }
        )
        return redirect("/mailing_list")
    return render_template('authentication/login.html', form=form)

@bp.route('/logout', methods=["POST"])
def logout():
    supabase = get_db()
    supabase.auth.sign_out()
    return redirect("/login")