from flask import Blueprint, jsonify
import resend.exceptions
from webargs.flaskparser import abort, parser, use_args, use_kwargs
from .data import state_dict, activities, trim_inputs, no_duplicates, rendered_email
from marshmallow import Schema, fields, validate, pre_load, ValidationError
from .db import supabase_admin
from supabase import PostgrestAPIError
import resend

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
    # add volunteer to database
    response = (
        supabase_admin.table("volunteers")
        .insert(args)
        .execute()
    )
    
    # get contents of email from database and add in user's name
    content_response = (
        supabase_admin.table("content")
        .select("content")
        .eq("name", "volunteer_form")
        .execute()
    )
    email_content = content_response.data[0]["content"]
    email_content = email_content.replace("_name_", f"{args["first_name"]} {args["last_name"]}")

    # Send email to user
    params: resend.Emails.SendParams = {
        "from": "Freshta Taeb <events@taebforassembly.com>",
        "to": [args["email"]],
        "subject": "Volunteer Onboarding",
        "html": rendered_email(email_content, unsubscribe=False)
    }
    email_success = True
    try:
        resend.Emails.send(params)
    except resend.exceptions.ResendError:
        email_success = False

    # send email notification to Frank
    email_content = f"""<p>The volunteer form has been filled out by {args["first_name"]} {args["last_name"]}</p>
    <p><b>Email:</b> {args["email"]}</p>
    <p><b>Phone:</b> {args["email"]}</p>
    <a href="https://taeb-server.vercel.app/view/volunteers/{response.data[0]["id"]}">More info</a>
    """
    params: resend.Emails.SendParams = {
        "from": "Onboarding <events@taebforassembly.com>",
        "to": ["frankb.ogrod@gmail.com"],
        "subject": f"{args["first_name"]} {args["last_name"]} has filled out the Volunteer Form",
        "html": email_content
    }
    notification_success = True
    try:
        resend.Emails.send(params)
    except resend.exceptions.ResendError:
        notification_success = False

    # send back response
    return {
        "success" : True,
        "email_success": email_success,
        "notification_success": notification_success,
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