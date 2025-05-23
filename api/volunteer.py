from flask import Blueprint, request, jsonify
from webargs.flaskparser import abort, parser, use_args, use_kwargs
from .data import state_dict, activities
from marshmallow import Schema, fields, validate, pre_load, ValidationError
from .db import supabase
from supabase import PostgrestAPIError

bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')

def no_duplicates(v):
    if len(v) != len(set(v)):
        raise ValidationError("List must not contain duplicate items")

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
    def trim_inputs(self, in_data, **kwargs):
        out = {}
        for k,v in in_data.items():
            # if string, strip it
            # if stripped is empty, don't add to out
            if isinstance(v, str):
                if v.strip():
                    out[k] = v.strip()
            # else if a list of strings, map strings to trimmed strings
            elif isinstance(v, list) and all(isinstance(v_item, str) for v_item in v):
                out[k] = [v_item.strip() for v_item in v]
            # Otherwise, add as is to outputS
            else:
                out[k] = v
        return out

@bp.route('/', methods=["POST"])
@use_args(VolunteerSchema(), location='form')
def add_volunteer(args):
    response = (
        supabase.table("volunteers")
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
        return jsonify({"success": False, "errors": messages}), err.code, headers
    else:
        return jsonify({"success": False, "errors": messages}), err.code

@bp.errorhandler(PostgrestAPIError)
def handle_supabase_err(err):
    err_dict = err.json()
    err_dict["success"] = False
    return jsonify(err_dict), 400