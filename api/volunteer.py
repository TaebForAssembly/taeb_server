from flask import Blueprint, request
from webargs.flaskparser import use_args, parser
from webargs import fields, validate
from .data import state_dict

bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')

'''
    "address1" : fields.Str(required=True),
    "address2" : fields.Str(required=True),
    "state" : fields.Str(required=True, validate=validate.OneOf(state_dict.keys())),
    "email" : fields.Email(required=True),
    "availability" : fields.Str(required=True),
    "tasks" : fields.List(fields.Str(required=True, validate=validate.OneOf(state_dict.keys()))),
    "phone" : fields.Str(validate=[validate.Length(equal=10), lambda s : s.isnumeric()])

    try:
        args = parser.parse(user_args, request)
        print(args )
    except Exception as e:
        print(e)
'''

@bp.route('/', methods=["POST"])
def add_volunteer():
    return {
        "success" : True,
        "message" : request.form.get("address1")
    }