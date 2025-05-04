import os
from flask import Flask, render_template, request, redirect, jsonify
from .db import get_db
import resend
from gotrue.errors import AuthApiError

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/', methods=["GET"])
    def email():
        content = request.args.get("content")
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
        response = (get_db().table("mailing_list").select("*").execute())
        print(list(map(lambda row: row["email"], response.data)))
        return render_template('email/mailing_list.html', name="John Smith", content=content, social_links=social_links)
    
    @app.route('/login', methods=["GET"])
    def login():
        return render_template('authentication/login.html')
    
    @app.route('/login', methods=["POST"])
    def login_post():
        # get data
        email = request.form.get("email")
        password = request.form.get("password")
        
        supabase = get_db()

        try:
            supabase.auth.sign_in_with_password(
                {
                    "email": email, 
                    "password": password,
                }
            )

            return redirect("/mailing_list")
        except AuthApiError:
            return {
                "success": False
            }

    @app.route('/mailing_list', methods=["GET"])
    def send_email():
        return render_template("forms/send_email.html")

    @app.route('/mailing_list/preview', methods=["POST"])
    def check_email():
        content = request.form.get("content")
        return render_template("email/mailing_list.html", name="John Smith", content=content)
    
    @app.route('/logout', methods=["POST"])
    def logout():
        supabase = get_db()
        supabase.auth.sign_out()
        return redirect("/login")

    return app