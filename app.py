from flask import Flask, render_template, request, session, redirect
from flask_bootstrap import Bootstrap
import sqlite3

# Initializing app
app = Flask(__name__)
# Initializing bootstrap
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    # Dummy data
    user = {'username': 'Pratik'}
    events = [
        {
            'event': 'Activity 1',
            'date': 'Jan 1',
            'body': 'Description!'
        },
        {
            'event': 'Activity 2',
            'date': 'Feb 1',
            'body': 'Description!'
        }
    ]
    return render_template('index.html', title='Water Walkers', user=user, events=events)

# consider adding login_required aspect (http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/)
@app.route('/login', methods=["GET", "POST"])
def login():
    # setup login page
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        return "TODO"

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method =="GET":
        return render_template("register.html")
    else:
        # get values from form
        name = request.form.get("name")
        age = request.form.get("age")
        grade = request.form.get("grade")
        dob = request.form.get("dob")
        email = request.form.get("email")
        parent1 = request.form.get("parent1")
        parent2 = request.form.get("parent2")
        emergency = request.form.get("econtact")
        allergies = request.form.get("allergies")
        needs = request.form.get("needs")
        meds = request.form.get("medications")
        notes = request.form.get("notes")

        return "TODO"

@app.route('/calendar')
def calendar():
    return render_template("json.html")


@app.route('/data')
def return_data():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    # You'd normally use the variables above to limit the data returned
    # you don't want to return ALL events like in this code
    # but since no db or any real storage is implemented I'm just
    # returning data from a text file that contains json elements

    with open("events.json", "r") as input_data:
        # you should use something else here than just plaintext
        # check out jsonfiy method or the built in json module
        # http://flask.pocoo.org/docs/0.10/api/#module-flask.json
        return input_data.read()

if __name__ == '__main__':
    app.run(debug=True)
