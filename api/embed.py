from flask import Blueprint, render_template, request, redirect, url_for, jsonify

bp = Blueprint('embed', __name__, url_prefix='/embed')

@bp.route('/mailing_list_form', methods=["GET", "POST"])
def mailing_list_form_oembed():
    preview = request.args.get("preview") is not None
    return render_template('embeds/mailing_list_embed.html', preview=preview)