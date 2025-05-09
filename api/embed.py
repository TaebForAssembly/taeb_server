from flask import Blueprint, render_template, request, redirect, url_for, jsonify

bp = Blueprint('embed', __name__, url_prefix='/embed')

@bp.route('/mailing_list_form', methods=["GET", "POST"])
def mailing_list_form():
    print(f"{request.url_root}embed/oembed/mailing_list_form")
    return f'<iframe src="{request.url_root}embed/oembed/mailing_list_form" title="Mailing List Form"></iframe>'
    
    
    return {
        "success": "true",
        "type": "rich",
        "version": "1.0",
        "html": f'<iframe src="{request.url_root}embed/oembed/mailing_list_form" title="Mailing List Form"></iframe>',
        "width": 480,
        "height": 480
    }

@bp.route('/oembed/mailing_list_form', methods=["GET", "POST"])
def mailing_list_form_oembed():
    return render_template('embeds/mailing_list_embed.html')