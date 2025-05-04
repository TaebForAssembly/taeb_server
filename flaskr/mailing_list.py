from flask import Blueprint, render_template, request

bp = Blueprint('mailing_list', __name__, url_prefix='/mailing_list')

@bp.route('/mailing_list', methods=["GET"])
def send_email():
    return render_template("forms/send_email.html")

@bp.route('/mailing_list/preview', methods=["POST"])
def check_email():
    content = request.form.get("content")
    return render_template("email/mailing_list.html", name="John Smith", content=content)