from flask import Blueprint, send_file, send_from_directory, render_template, request, flash, redirect
from os import path
from .db import supabase, supabase_admin
import requests
from io import BytesIO

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

bp = Blueprint('assets', __name__, url_prefix='/assets', static_folder='static/assets')

class UploadFileForm(FlaskForm):
    image = FileField(validators=[FileRequired()])
@bp.route('/', methods=["GET", "POST"])
def upload_file():
    form = UploadFileForm()

    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        filetype = filename.split(".")[-1]
        (
            supabase_admin.storage
            .from_("assets")
            .upload(
                file=f.read(),
                path=filename,
                file_options={"cache-control": "3600", "upsert": "true", "content-type": f"image/{filetype}"}
            )
        )
        return render_template('forms/upload_file.html', form=form, image_url=f"https://internal.taebforassembly.com/assets/get/{filename}")

    return render_template('forms/upload_file.html', form=form)

@bp.route('/get/<filename>')
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