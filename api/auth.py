from flask import Blueprint, render_template, redirect
from .db import get_db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email
from gotrue.errors import AuthApiError

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(message='Email input must be an email')])
    password = PasswordField('Password', validators=[DataRequired(message='Password must be specified')])

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=["GET", "POST"])
def login():
    supabase = get_db()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            supabase.auth.sign_in_with_password(
                {
                    "email": email, 
                    "password": password,
                }
            )
            return redirect("/mailing_list")
        except AuthApiError:
            return render_template('authentication/login.html', form=form, error="Login Error", signed_out=True)
    return render_template('authentication/login.html', form=form, signed_out=True)

@bp.route('/logout', methods=["POST"])
def logout():
    supabase = get_db()
    supabase.auth.sign_out()
    return redirect("/login")