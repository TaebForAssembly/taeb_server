from flask import Blueprint, render_template, redirect, url_for
from .db import supabase_admin, signed_in, supabase
from supabase import PostgrestAPIError
from datetime import datetime

bp = Blueprint('view', __name__, url_prefix='/view')

def formatTasks(volunteer, show_time=True):
    volunteer["tasks"] = list(map(lambda t: t.replace("_", " ").title(), volunteer["tasks"]))
    time_string = "%m/%d/%Y at %I:%M %p" if show_time else "%m/%d/%Y"
    volunteer["created_at"] = datetime.strptime(volunteer["created_at"], "%Y-%m-%dT%H:%M:%S.%f+00:00").strftime(time_string)
    return volunteer

#Time formatting method for the following events:
# Canvassing
# Phone Banking
#Convert given event start and end time to 12 hr format and return it
def formatTimeTo12(event):
    time_12hr = "%I:%M %p" 
    start_time_12_hr  = datetime.strptime(event["start"], "%H:%M:%S").strftime(time_12hr)
    #Remove zeroes
    start_time_HOUR = int(start_time_12_hr[0:2])
    if start_time_HOUR < 10:
        event["start"] = str(start_time_HOUR) + datetime.strptime(event["start"], "%H:%M:%S").strftime(":%M %p")
    else:
        event["start"] = start_time_12_hr
    
    end_time_12_hr  = datetime.strptime(event["end"], "%H:%M:%S").strftime(time_12hr)
    #Remove zeroes
    end_time_HOUR = int(end_time_12_hr[0:2])
    if end_time_HOUR < 10:
        event["end"] = str(end_time_HOUR) + datetime.strptime(event["end"], "%H:%M:%S").strftime(":%M %p")
    else:
        event["end"] = end_time_12_hr
    return event

#Format the day properly...
def formatDay(event):
    default_day_format = "%m-%d"
    changed_day_format = "%b-%d"
    with_abbreviated_month = datetime.strptime(event["date"] , default_day_format).strftime(changed_day_format)
    #All month abbreviations are 3-characters long
    day_number = int(with_abbreviated_month[4:6])
    if day_number < 10:
        event["date"] = with_abbreviated_month[0:4] + str(day_number)
    else:
        event["date"] = with_abbreviated_month

    return event

#Simplify date format
def removeYear(event):
    time_wo_year = "%m-%d"
    event["date"] = datetime.strptime(event["date"], "%Y-%m-%d").strftime(time_wo_year)
    return event


#Volunteer Table
@bp.route("/volunteers", methods=["GET"])
def view_volunteers():
    # ensure user has access
    if not signed_in():
        return redirect(url_for("auth.login"))
    
    volunteers = []
    try:
        response = (
            supabase_admin.table("volunteers")
            .select("first_name, last_name, city, state, email, tasks, created_at, id, contacted")
            .order("created_at", desc=True)
            .execute()
        )
        volunteers = response.data
        volunteers = list(map(lambda v: formatTasks(v, False), volunteers))
    except PostgrestAPIError:
        return render_template("information/volunteer_table.html", error="Server Error: Volunteers not Found")

    return render_template("information/volunteer_table.html", volunteers=volunteers)

#Specific Volunteer Route
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
        if len(response.data) == 0:
            raise KeyError
        volunteer = response.data[0]
        volunteer = formatTasks(volunteer)
    except PostgrestAPIError:
        pass
    except KeyError:
        return render_template("information/volunteer_info.html", error="User not found")

    return render_template("information/volunteer_info.html", volunteer=volunteer)

#Canvassing
@bp.route("/canvassing", methods=["GET"]) #HTTP GET
def view_canvassing():
    # ensure user has access
    if not signed_in():
        return redirect(url_for("auth.login"))
    
    canvassing_events = []
    try:
        response = (
            supabase_admin.table("canvassing")
            .select("day, date, start, end, location, rsvp, created_at, id")
            .order("id", desc=False)
            .execute()
        )
        canvassing_events = response.data
        #Use a lambda expression to format time to 12 HR format
        canvassing_events = list(map(lambda e: formatTimeTo12(e), canvassing_events))
        canvassing_events = list(map(lambda e: removeYear(e), canvassing_events))
        canvassing_events = list(map(lambda e: formatDay(e) , canvassing_events))
    except PostgrestAPIError:
        return render_template("information/canvassing_table.html", error="Server Error: Volunteers not Found")

    return render_template("information/canvassing_table.html", canvassing_events=canvassing_events)

#Phone banking
@bp.route("/phone_banking", methods=["GET"]) #HTTP GET
def view_phone_banking():
    # ensure user has access
    if not signed_in():
        return redirect(url_for("auth.login"))
    
    phone_bankings = []
    try:
        response = (
            supabase_admin.table("phone_banking")
            .select("day, date, start, end, rsvp, created_at, id")
            .order("id", desc=False)
            .execute()
        )
        phone_bankings = response.data
        #Use a lambda expression to format time to 12 HR format
        phone_bankings = list(map(lambda e: formatTimeTo12(e), phone_bankings))
        phone_bankings = list(map(lambda e: removeYear(e), phone_bankings))
        phone_bankings = list(map(lambda e: formatDay(e) , phone_bankings))
    except PostgrestAPIError:
        return render_template("information/phone_banking_table.html", error="Server Error: Volunteers not Found")

    return render_template("information/phone_banking_table.html", phone_bankings=phone_bankings)



#No html associated here
@bp.route("/greeting", methods=["GET"])
def hello_world():
    try:
        response = (
            supabase_admin.table("content")
            .select("content")
            .eq("name", "greeting")
            .execute()
        )

        if len(response.data) == 0:
            return {
                "success": False,
                "message": "Data not found"
            }

        return {
            "success": True,
            "message": response.data[0]["content"]
        }
    except PostgrestAPIError:
        return {
            "success": False,
            "message": "Error fetching content"
        }