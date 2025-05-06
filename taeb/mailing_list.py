from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from .db import signed_in, get_db
import resend
import markdown
from markupsafe import Markup
from bs4 import BeautifulSoup

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

class MailingListForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(message='Subject must be specified')])
    content = TextAreaField('Content', validators=[Length(message='Content must be at least 5 characters', min=5)])

bp = Blueprint('mailing_list', __name__, url_prefix='/mailing_list')

def render_email(content, name="Mailing List Member"):
    html_content = markdown.markdown(content)
    soup = BeautifulSoup(html_content, 'html.parser')
    for img in soup.find_all('img'):
        img['width'] = '100%'
    html_content = str(soup)
    return render_template("email/mailing_list_preview.html", name=name, content=Markup(markdown.markdown(html_content)), social_links=social_links)

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

            params: resend.Broadcasts.CreateParams = {
                "audience_id": "a17a345c-1182-4915-a3b8-47121580b9a6",
                "from": "Freshta Taeb <onboarding@taebforassembly.com>",
                "subject": form.subject.data,
                "html": render_template("email/mailing_list.html", content=form.content.data),
            }

            email = resend.Emails.send(params)
            return jsonify(email)
        '''
    return render_template("forms/send_email.html", form=form)

@bp.route('/preview', methods=["GET"])
def check_email():
    content = request.args.get("content")
    return render_email(content)

@bp.route('/users', methods=["POST"])
def add_user():
    pass