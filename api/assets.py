from flask import Blueprint, send_file, send_from_directory, render_template, redirect, url_for
from .db import supabase, supabase_admin, signed_in
import requests
from io import BytesIO

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from wtforms import ValidationError

from supabase import StorageException

import re

bp = Blueprint('assets', __name__, url_prefix='/assets', static_folder='static/assets')

class UploadFileForm(FlaskForm):
    image = FileField(validators=[FileRequired()])

    def validate_image(form, field):
        if not re.search(r".(jpg|jpeg|webp|png|gif)$", field.data.filename):
            raise ValidationError("Invalid filename")
@bp.route('/upload', methods=["GET", "POST"])
def upload_file():
    # ensure user has access
    if not signed_in():
        return redirect(url_for("auth.login"))
    
    form = UploadFileForm()

    if form.validate_on_submit():
        f = form.image.data
        filename = secure_filename(f.filename)
        filetype = filename.split(".")[-1]
        filetype = filetype if filetype != "jpg" else "jpeg"
        try:
            (
                supabase_admin.storage
                .from_("assets")
                .upload(
                    file=f.read(),
                    path=filename,
                    file_options={"cache-control": "3600", "upsert": "false", "content-type": f"image/{filetype}"}
                )
            )
            return render_template('forms/upload_file.html', form=form, image_url=f"https://internal.taebforassembly.com/assets/{filename}")
        except StorageException as err:
            return render_template('forms/upload_file.html', form=form, error=err.message)

    return render_template('forms/upload_file.html', form=form)

def get_public_url(filename):
    return (
        supabase.storage
        .from_("assets")
        .get_public_url(filename)
    )

@bp.route('/')
def view_images():
    # ensure user has access
    if not signed_in():
        return redirect(url_for("auth.login"))

    response = (
        supabase_admin.storage
        .from_("assets")
        .list()
    )
    images = map(lambda image:
        {
            "filename" : image["name"],
            "image_url" : get_public_url(image["name"]),
            "asset_url" : f"https://internal.taebforassembly.com/assets/{image['name']}"
        }
    , response)
    return render_template("information/images_list.html", images=images)

@bp.route('/<filename>', methods=["GET"])
def base_static(filename):
    public_url = get_public_url(filename)
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

@bp.route('/<filename>', methods=["DELETE"])
def delete_static(filename):
    try:
        response = (
            supabase_admin.storage
            .from_("assets")
            .remove([filename])
        )
        if not len(response):
            raise StorageException
        return {
            "success" : True,
            "message" : "File deleted successfully"
        }
    except StorageException:
        return {
            "success" : False,
            "message" : f"File delete failed on {filename}"
        }