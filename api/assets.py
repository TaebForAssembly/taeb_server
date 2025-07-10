from flask import Blueprint, send_from_directory
from os import path

bp = Blueprint('assets', __name__, url_prefix='/assets', static_folder='static/assets')

@bp.route('/<filename>')
def base_static(filename):
    filepath = path.join(bp.root_path, 'static/assets')
    return send_from_directory(filepath, filename)