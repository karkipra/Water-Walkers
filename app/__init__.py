from flask import Flask
from flask_session import Session
#from flask-login import LoginManager

# Initializing app
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize login
# login = LoginManager(app)

#from app import helpers
from app import routes
#from helpers import login_required