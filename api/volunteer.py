from flask import Blueprint, request
from webargs.flaskparser import abort, parser, use_args, use_kwargs
from webargs import fields, validate
from .data import state_dict

bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')

user_args = {
    #  name
    "first_name" : fields.Str(required=True),
    "last_name" : fields.Str(required=True),

    # address
    "address1" : fields.Str(required=True),
    "address2" : fields.Str(),
    "city" : fields.Str(required=True),
    "state" : fields.Str(required=True, validate=validate.OneOf(state_dict.keys())),
    "zip" : fields.Str(required=True),

    # contact information
    "email" : fields.Email(required=True),
    "phone" : fields.Str(required=True),

    # about
    "personal" : fields.Str(required=True),
    "availability" : fields.Str(required=True),
    "tasks": fields.List(fields.Str())
}

@bp.route('/', methods=["POST"])
@use_args(user_args, location='form')
def add_volunteer(args):
    return args

@parser.error_handler
def handle_request_parsing_error(err, req, schema, *, error_status_code, error_headers):
    abort(error_status_code, errors=err.messages)