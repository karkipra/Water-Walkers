from flask import Flask
from flask_session import Session

# Initializing app
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# App is in testing mode, no emails acutally sent
# TODO - turn me off once we're ready to deploy
app.config["TESTING"] = True

from app import routes
