from flask import Blueprint, send_file, send_from_directory
from os import path
from .db import supabase
import requests
from io import BytesIO

bp = Blueprint('assets', __name__, url_prefix='/assets', static_folder='static/assets')

@bp.route('/<filename>')
def base_static(filename):
    public_url = (
        supabase.storage
        .from_("assets")
        .get_public_url(filename)
    )
    response = requests.get(public_url)

    try:
        # if response is json serializable, it's an error message
        # send "not found" image in response
        response.json()
        return send_from_directory("static/assets", "not_found.png")
    except requests.exceptions.JSONDecodeError:
        return send_file(
            BytesIO(response.content),
            download_name='logo.png',
            mimetype='image/png'
        )