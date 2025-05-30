from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, Optional

from webargs.flaskparser import parser, use_kwargs
from marshmallow import fields, validate

from .db import signed_in
from .data import social_links, later_than_now

import resend.exceptions
import resend

import markdown
from markupsafe import Markup
from bs4 import BeautifulSoup

import os
import re
import pytz

resend.api_key = os.environ.get("RESEND_KEY")

class MailingListForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(message='Subject must be specified')])
    content = TextAreaField('Content', validators=[Length(message='Content must be at least 5 characters', min=5)])
    datetime = DateTimeLocalField('Schedule Date', validators=[Optional(), later_than_now])
    confirm = BooleanField('Confirm')

bp = Blueprint('mailing_list', __name__, url_prefix='/mailing_list')

# HTML content of email given text content
# Replace google drive links with thumbnail links
def email_content(content):
    html_content = markdown.markdown(content)
    soup = BeautifulSoup(html_content, 'html.parser')
    drive_regex = r"https:\/\/drive.google.com\/file\/d\/([^\/]+)\/"
    for img in soup.find_all('img'):
        img['width'] = '100%'
        search = re.search(drive_regex, img["src"])
        if search is not None:
            src_id = search.group(1)
            img['src'] = f"https://drive.google.com/thumbnail?id={src_id}&sz=w1000"
    html_content = str(soup)
    return Markup(markdown.markdown(html_content))

# Send to list
@bp.route('/', methods=["GET", "POST"])
def mailing_list():
    # ensure user has access
    if not signed_in():
        return redirect(url_for("auth.login"))
    
    form = MailingListForm()

    # if form was submitted correctly
    if form.validate_on_submit():
        # create broadcast inputs
        html_content = email_content(form.content.data)
        params: resend.Broadcasts.CreateParams = {
            "audience_id": "a17a345c-1182-4915-a3b8-47121580b9a6",
            "from": "Freshta Taeb <news@taebforassembly.com>",
            "subject": form.subject.data,
            "name": form.subject.data,
            "html": render_template("email/mailing_list.html", html_content=html_content, social_links=social_links),
        }

        # try creating broadcast
        try:
            email = resend.Broadcasts.create(params)
        except resend.exceptions.ResendError as err:
            return render_template("forms/send_email.html", form=form, error=f"Error creating broadcast: {err}")

        # send broadcast inputs (taking id from response)
        params: resend.Broadcasts.SendParams = { "broadcast_id": email["id"] }
        if form.datetime.data is not None:
            params["scheduled_at"] = pytz.timezone("America/New_York").localize(form.datetime.data).isoformat()

        # try sending broadcast with id
        try:
            resend.Broadcasts.send(params)
        except resend.exceptions.ResendError as err:
            return render_template("forms/send_email.html", form=form, error=f"Error sending broadcast: {err}")
        
        # refresh with flashed method
        flash(f"Broadcast with id \"{email["id"]}\" successfully sent")
        return redirect(url_for("mailing_list.mailing_list"))

    # else return the corm
    return render_template("forms/send_email.html", form=form)

# Preview Email
class PreviewForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
preview_schema = {
    "subject" : fields.Str(required=True),
    "content" : fields.Str(required=True, validate=[validate.Length(min=5)])
}
@bp.route('/preview', methods=["GET", "POST"])
def check_email():
    # Perform validation on querystring
    try:
        args = parser.parse(preview_schema, location='querystring')
    except Exception as e:
        return f"Validation Error: {e}", 400
    
    # get inputs for operations
    content = args["content"]
    subject = args["subject"]
    html_content = email_content(content)
    
    form = PreviewForm()
    if form.validate_on_submit():
        params: resend.Emails.SendParams = {
            "from": "Freshta Taeb <test@taebforassembly.com>",
            "to": [form.email.data],
            "subject": f"[TEST]: {subject}",
            "html": render_template("email/mailing_list.html", html_content=html_content, social_links=social_links)
        }

        # Try sending the email to inputted email
        try:
            resend.Emails.send(params)
            flash("Email sent")
        except resend.exceptions.ResendError:
            flash("Email couldn't be sent")

    # Return preview and form to send preview to an email
    return render_template("email/mailing_list_preview.html", html_content=html_content, content=content, subject=subject, social_links=social_links, form=form)

# Add user to mailing list
@bp.route('/users', methods=["POST"])
@use_kwargs({ "email": fields.Email(required=True) }, location='form')
def add_user(email):
    # send to mailing list
    try:
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
    except resend.exceptions.ResendError:
        return {
            "message" : "Error adding user",
            "success" : False
        }
    
@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"success": False, "message" : "Error validating inputs", "errors": messages}), err.code, headers
    else:
        return jsonify({"success": False, "message" : "Error validating inputs", "errors": messages}), err.code