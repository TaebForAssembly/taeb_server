from flask import Blueprint, render_template, request
from .data import state_dict

bp = Blueprint('embed', __name__, url_prefix='/embed')

@bp.route('/mailing_list_form', methods=["GET"])
def mailing_list_form_oembed():
    preview = request.args.get("preview") is not None
    return render_template('embeds/mailing_list_embed.html', preview=preview)

@bp.route('/volunteer_form', methods=["GET"])
def volunteer_form_oembed():
    preview = request.args.get("preview") is not None
    return render_template('embeds/volunteer_embed.html', preview=preview, states=state_dict)