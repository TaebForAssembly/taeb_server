from wtforms import ValidationError
import pytz
from datetime import datetime, timedelta
import markdown
from markupsafe import Markup
from bs4 import BeautifulSoup
import re
from flask import render_template

state_dict : dict[str, str] = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
    "DC": "District of Columbia",
    "AS": "American Samoa",
    "GU": "Guam GU",
    "MP": "Northern Mariana Islands",
    "PR": "Puerto Rico PR",
    "VI": "U.S. Virgin Islands",
}

activities = [
    "phone_banking",
    "event_coordination",
    "lawn_sign_delivery",
    "meet_and_greet_host",
    "canvassing",
]

social_links = [
    # facebook
    {
        "url": "https://www.facebook.com/people/Freshta-Taeb/pfbid0pbEhVeAoyC1zNs4txi2AXAyxEFzweoWXjc68M7W6dDjDsDycDqwCqJaZCSGrsS7hl/",
        "image": "https://img.icons8.com/?size=30&id=118466&format=png&color=012852"
    },
    # instagram
    {
        "url": "https://www.instagram.com/taeb4assembly/",
        "image": "https://img.icons8.com/?size=30&id=32309&format=png&color=012852"
    },
    # linkedin
    {
        "url": "https://www.linkedin.com/company/taeb-for-assembly/posts/?feedView=all",
        "image": "https://img.icons8.com/?size=30&id=8808&format=png&color=012852"
    },
    # tiktok
    {
        "url": "https://www.tiktok.com/@taeb4assembly",
        "image": "https://img.icons8.com/?size=30&id=118638&format=png&color=012852"
    },
    # X
    {
        "url": "https://www.tiktok.com/@taeb4assembly",
        "image": "https://img.icons8.com/?size=30&id=phOKFKYpe00C&format=png&color=012852"
    },
]

def trim_inputs(in_data):
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

def no_duplicates(v):
    if len(v) != len(set(v)):
        raise ValidationError("List must not contain duplicate items")

def later_than_now(_form, field):
    our_timezone = pytz.timezone("America/New_York")
    if datetime.now().astimezone(our_timezone) + timedelta(minutes=5) > our_timezone.localize(field.data):
        raise ValidationError("Date must be later than 5 minutes from now")

# HTML content of email given text content
# Replace google drive links with thumbnail links
def email_content(content):
    html_content = markdown.markdown(content)
    soup = BeautifulSoup(html_content, 'html.parser')
    drive_regex = r"https:\/\/drive.google.com\/file\/d\/([^\/]+)\/"
    for img in soup.find_all('img'):
        img['width'] = '100%'
        search = re.search(drive_regex, img["src"])
        if search is not None:
            src_id = search.group(1)
            img['src'] = f"https://drive.google.com/thumbnail?id={src_id}&sz=w1000"
    html_content = str(soup)
    return Markup(markdown.markdown(html_content))

def rendered_email(content, unsubscribe=True):
    html_content = email_content(content)
    return render_template("email/mailing_list.html", html_content=html_content, social_links=social_links, unsubscribe=unsubscribe)