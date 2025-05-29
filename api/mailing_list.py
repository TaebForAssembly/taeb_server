from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_wtf import FlaskForm
import resend.exceptions
from wtforms import StringField, TextAreaField, DateTimeLocalField, ValidationError
from wtforms.validators import DataRequired, Length, Optional
from .db import signed_in, get_db
import resend
import markdown
from markupsafe import Markup
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import pytz

resend.api_key = os.environ.get("RESEND_KEY")

social_links = [
    # facebook
    {
        "url": "https://www.facebook.com/people/Freshta-Taeb/pfbid0pbEhVeAoyC1zNs4txi2AXAyxEFzweoWXjc68M7W6dDjDsDycDqwCqJaZCSGrsS7hl/",
        "image": "https://img.icons8.com/?size=30&id=118466&format=png&color=012852"
    },
    # instagram
    {
        "url": "https://www.instagram.com/taeb4assembly/",
        "image": "https://img.icons8.com/?size=30&id=32309&format=png&color=012852"
    },
    # linkedin
    {
        "url": "https://www.linkedin.com/company/taeb-for-assembly/posts/?feedView=all",
        "image": "https://img.icons8.com/?size=30&id=8808&format=png&color=012852"
    },
    # tiktok
    {
        "url": "https://www.tiktok.com/@taeb4assembly",
        "image": "https://img.icons8.com/?size=30&id=118638&format=png&color=012852"
    },
    # X
    {
        "url": "https://www.tiktok.com/@taeb4assembly",
        "image": "https://img.icons8.com/?size=30&id=phOKFKYpe00C&format=png&color=012852"
    },
]

def later_than_now(_form, field):
    our_timezone = pytz.timezone("America/New_York")
    if datetime.now().astimezone(our_timezone) > our_timezone.localize(field.data):
        raise ValidationError("Date must be later than now")

class MailingListForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(message='Subject must be specified')])
    content = TextAreaField('Content', validators=[Length(message='Content must be at least 5 characters', min=5)])
    datetime = DateTimeLocalField('Schedule Date', validators=[Optional(), later_than_now])

bp = Blueprint('mailing_list', __name__, url_prefix='/mailing_list')

def email_content(content):
    html_content = markdown.markdown(content)
    soup = BeautifulSoup(html_content, 'html.parser')
    for img in soup.find_all('img'):
        img['width'] = '100%'
    html_content = str(soup)
    return Markup(markdown.markdown(html_content))

@bp.route('/', methods=["GET", "POST"])
def mailing_list():
    # ensure user has access
    if not signed_in():
        return redirect(url_for("auth.login"))
    
    form = MailingListForm()

    # if form was submitted correctly
    if form.validate_on_submit():
        html_content = email_content(form.content.d)
        params: resend.Broadcasts.CreateParams = {
            "audience_id": "a17a345c-1182-4915-a3b8-47121580b9a6",
            "from": "Freshta Taeb <news@taebforassembly.com>",
            "subject": form.subject.data,
            "name": form.subject.data,
            "html": render_template("email/mailing_list_full.html", html_content=html_content, social_links=social_links),
        }

        try:
            email = resend.Broadcasts.create(params)
        except resend.exceptions.ResendError as err:
            flash(f"Error sending broadcast: {err}")
            return render_template("forms/send_email.html", form=form)

        params: resend.Broadcasts.SendParams = {
            "broadcast_id": email["id"]
        }
        if form.datetime.data is not None:
            params["scheduled_at"] = pytz.timezone("America/New_York").localize(form.datetime.data).isoformat()

        try:
            resend.Broadcasts.send(params)
        except resend.exceptions.ResendError as err:
            flash(f"Error sending broadcast: {err}")
            return render_template("forms/send_email.html", form=form)
        
        flash(f"Broadcast with id \"{email["id"]}\" successfully sent")
        return redirect(url_for("mailing_list.mailing_list"))

    # else return the corm
    return render_template("forms/send_email.html", form=form)

@bp.route('/preview', methods=["GET"])
def check_email():
    content = request.args.get("content")
    subject = request.args.get("subject")
    html_content = email_content(content)
    return render_template("email/mailing_list_preview.html", html_content=html_content, content=content, subject=subject, social_links=social_links)

@bp.route('/users', methods=["POST"])
def add_user():
    # error testing
    email = request.form.get("email")
    email_regex = r".+@.+"
    if email is None:
        return { "success" : False, "message": "Email must be supplied" }, 400
    elif re.search(email_regex, email) is None:
        return { "success" : False, "message": "Email must be in \"_@_\" format" }, 400
    
    # send to mailing list
    params: resend.Contacts.CreateParams = {
        "email": email,
        "unsubscribed": False,
        "audience_id": "a17a345c-1182-4915-a3b8-47121580b9a6",
    }
    response = resend.Contacts.create(params)
    return {
        "response" : response,
        "success" : True
    }