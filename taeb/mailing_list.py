from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from .db import signed_in, get_db
import resend

class MailingListForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(message='Subject must be specified')])
    content = TextAreaField('Content', validators=[Length(message='Content must be at least 5 characters', min=5)])

bp = Blueprint('mailing_list', __name__, url_prefix='/mailing_list')

@bp.route('/', methods=["GET", "POST"])
def mailing_list():
    if not signed_in():
        return redirect(url_for("login"))
    form = MailingListForm()
    if form.validate_on_submit():
        supabase = get_db()
        response = (
            supabase.table("mailing_list")
            .select("email")
            .execute()
        )
        email_list = list(map(lambda point: point["email"], response.data))
        '''
            TODO: Setup Resend
            params = [{
                "from": "Freshta Taeb <onboarding@taebforassembly.com>",
                "to": email,
                "subject" : form.subject.data,
                "html": render_template("email/mailing_list.html", name="John Smith", content=form.content.data)
            } for email in email_list]

            email = resend.Emails.send(params)
            return jsonify(email)
        '''
    return render_template("forms/send_email.html", form=form)

@bp.route('/preview', methods=["GET"])
def check_email():
    content = request.args.get("content")
    return render_template("email/mailing_list.html", name="John Smith", content=content)