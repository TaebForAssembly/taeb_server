import os
from flask import Flask, redirect
from . import auth, mailing_list, embed
from .db import signed_in
from flask_cors import CORS

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, origins=["https://www.taebforassembly.com/"])
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
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

    app.register_blueprint(auth.bp)
    app.register_blueprint(mailing_list.bp)
    app.register_blueprint(embed.bp)

    # a simple page that says hello
    @app.route('/')
    def root():
        if signed_in():
            return redirect("/mailing_list")
        else:
            return redirect("/login")

    return app

app = create_app()