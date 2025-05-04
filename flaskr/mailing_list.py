from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length

class MailingListForm(FlaskForm):
    subject = StringField('Subject', validators=[Email()])
    content = PasswordField('Content', validators=[Length(min=5)])

bp = Blueprint('mailing_list', __name__, url_prefix='/mailing_list')

@bp.route('/', methods=["GET", "POST"])
def send_email():
    form = MailingListForm()
    if form.validate_on_submit():
        print("valid")
    return render_template("forms/send_email.html", form=form)

@bp.route('/preview', methods=["GET"])
def check_email():
    content = request.args.get("content")
    return render_template("email/mailing_list.html", name="John Smith", content=content)