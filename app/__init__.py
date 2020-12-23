from flask import Flask
from flask_session import Session
from flask_mail import Mail

# Initializing app
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Setup flask mail stuff (for forgot_pwd only, not general emails)
mail = Mail(app)

from app import routes
