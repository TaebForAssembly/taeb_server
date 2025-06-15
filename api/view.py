from flask import Blueprint, render_template, redirect, url_for
from .db import supabase_admin, signed_in
from supabase import PostgrestAPIError
from datetime import datetime

bp = Blueprint('view', __name__, url_prefix='/view')

def formatTasks(volunteer):
    volunteer["tasks"] = list(map(lambda t: t.replace("_", " ").title(), volunteer["tasks"]))
    volunteer["created_at"] = datetime.strptime(volunteer["created_at"], "%Y-%m-%dT%H:%M:%S.%f+00:00").strftime("%m/%d/%Y at %I:%M %p")
    return volunteer

@bp.route("/volunteers", methods=["GET"])
def view_volunteers():
    # ensure user has access
    if not signed_in():
        return redirect(url_for("auth.login"))
    
    volunteers = []
    try:
        response = (
            supabase_admin.table("volunteers")
            .select("*")
            .execute()
        )
        volunteers = response.data
        volunteers = list(map(formatTasks, volunteers))
    except PostgrestAPIError:
        pass

    return render_template("information/volunteer_table.html", volunteers=volunteers)

@bp.route("/volunteers/<id>", methods=["GET"])
def view_volunteer(id):
    # ensure user has access
    if not signed_in():
        return redirect(url_for("auth.login"))
    
    volunteer = None
    try:
        response = (
            supabase_admin.table("volunteers")
            .select("*")
            .eq("id", id)
            .execute()
        )
        volunteer = response.data[0]
        volunteer = formatTasks(volunteer)
    except PostgrestAPIError:
        pass

    return render_template("information/volunteer_info.html", volunteer=volunteer)