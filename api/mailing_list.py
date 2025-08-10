from flask import Blueprint, render_template, redirect, url_for, flash, jsonify

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from webargs.flaskparser import parser, use_kwargs
from marshmallow import fields, validate, Schema, pre_load

from .db import signed_in
from .data import social_links, later_than_now, email_content, trim_inputs

import resend.exceptions
import resend

import os
import pytz

resend.api_key = os.environ.get("RESEND_KEY")

class MailingListForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(message='Subject must be specified')])
    content = TextAreaField('Content', validators=[DataRequired(message='Content must be specified'), Length(message='Content must be at least 5 characters', min=5)])
    datetime = DateTimeLocalField('Schedule Date', validators=[Optional(), later_than_now])
    confirm = BooleanField('Confirm')

bp = Blueprint('mailing_list', __name__, url_prefix='/mailing_list')

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
    email = EmailField('Email', validators=[DataRequired(), Regexp(r".+@.+\..+")])
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
            "subject": f"{subject}",
            "html": render_template("email/mailing_list.html", html_content=html_content, social_links=social_links)
        }

        # Try sending the email to inputted email
        try:
            resend.Emails.send(params)
            flash("Email sent")
        except resend.exceptions.ResendError as e:
            flash(f"Email couldn't be sent: {e}")

    # Return preview and form to send preview to an email
    return render_template("email/mailing_list_preview.html", html_content=html_content, content=content, subject=subject, social_links=social_links, form=form)

# Add user to mailing list
class MailingListUserSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    email = fields.Email(required=True)

    @pre_load
    def trim_load(self, in_data, **kwargs):
        return trim_inputs(in_data)

@bp.route('/users', methods=["POST"])
@use_kwargs(MailingListUserSchema(), location='form')
def add_user(first_name, last_name, email):
    # send to mailing list
    try:
        params: resend.Contacts.CreateParams = {
            "first_name" : first_name,
            "last_name" : last_name,
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