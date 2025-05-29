from flask import Blueprint, request, jsonify
from webargs.flaskparser import abort, parser, use_args, use_kwargs
from .data import state_dict, activities, trim_inputs, no_duplicates
from marshmallow import Schema, fields, validate, pre_load, ValidationError
from .db import supabase_admin
from supabase import PostgrestAPIError

bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')

class VolunteerSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))

    # address
    address1 = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    address2 = fields.Str(validate=validate.Length(min=1, max=100))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    state = fields.Str(required=True, validate=validate.OneOf(state_dict.keys()))
    zip = fields.Str(required=True, validate=validate.Regexp(r"\d{5}(-\d{4})?"))

    # contact information
    email = fields.Email(required=True, validate=validate.Length(max=254))
    phone = fields.Str(required=True, validate=validate.Regexp(r"[0-9]{10}"))

    # about
    personal = fields.Str(validate=validate.Length(max=2000))
    availability = fields.Str(required=True, validate=validate.Length(max=2000))
    tasks = fields.List(fields.Str(validate=validate.OneOf(activities)), required=True, validate=[validate.Length(min=1), no_duplicates])

    @pre_load
    def trim_load(self, in_data, **kwargs):
        return trim_inputs(in_data)

@bp.route('/', methods=["POST"])
@use_args(VolunteerSchema(), location='form')
def add_volunteer(args):
    response = (
        supabase_admin.table("volunteers")
        .insert(args)
        .execute()
    )
    
    return {
        "success" : True,
        "data" : response.data
    }

@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"success": False, "message" : "Error validating inputs", "errors": messages}), err.code, headers
    else:
        return jsonify({"success": False, "message" : "Error validating inputs", "errors": messages}), err.code

@bp.errorhandler(PostgrestAPIError)
def handle_supabase_err(err):
    err_dict = err.json()
    err_dict["success"] = False

    if err.code == "23505":
        err_dict["message"] = "Duplicate email found, please use a unique email"
    elif err.details is not None:
        err_dict["message"] = f"Server Error: {err.details}"
    else:
        err_dict["message"] = "Error submitting to our database, try again later!"

    return jsonify(err_dict), 500