import os
from dotenv import load_dotenv
from flask import Flask
import auth, mailing_list, embed

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)

if None is None:
    # load the instance config, if it exists, when not testing
    app.config.from_pyfile('config.py', silent=True)
'''else:
    # load the test config if passed in
    app.config.from_mapping(None)'''

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
    return 'Hello, World! Server working'