from flask import Flask, render_template, request, session, redirect
import datetime
from flask_bootstrap import Bootstrap
import sqlite3
from datetime import datetime 
from flask import jsonify
import json

# Initializing app
app = Flask(__name__)
# Initializing bootstrap
bootstrap = Bootstrap(app)

@app.route('/')
def index():

    user = {'username': 'Pratik'}

    # SQLite query to add username and password into database
    conn = sqlite3.connect('database/updated_db.db')
    db = conn.cursor()
    events = db.execute("SELECT * FROM EVENTS")
    conn.commit()

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
    return render_template('calendar.html')


@app.route('/data')
def return_data():
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    # You'd normally use the variables above to limit the data returned
    # you don't want to return ALL events like in this code
    # but since no db or any real storage is implemented I'm just
    # returning data from a text file that contains json elements

    # SQLite query to add username and password into database
    conn = sqlite3.connect('database/updated_db.db')
    db = conn.cursor()
    events = db.execute("SELECT * FROM EVENTS")
    conn.commit()

    # Pretty sure all of this can be written better but at least it works
    js = []

    for event in events:
        d = {
            'title': event[1],
            'start': event[3],
            'end': event[4],
            'url': event[5]
        }
        js.append(d)

    with open('events.json', 'w') as outfile:
        json.dump(js, outfile)    

    with open("events.json", "r") as input_data:
        return input_data.read()

@app.route('/add', methods=["GET", "POST"])
def add_event():
    # setup login page
    if request.method == "GET":
        return render_template("add_event.html")
    else:
        name = request.form.get("name")
        descrip = request.form.get("descrip")
        start = request.form.get('start')
        end = request.form.get("end")
        url = request.form.get("url")

        print(type(start))

        # IMPORTANT - for now this needs to run locally on someone's machine. 
        # remember to change this per your db's path!
        conn = sqlite3.connect('database/updated_db.db')
        db = conn.cursor()

        # SQLite query to add username and password into database
        db.execute("INSERT INTO EVENTS (event_name, event_descrip, start, end, url) VALUES (?, ?, ?, ?, ?)", (name, descrip, start, end, url))
        conn.commit()

        return redirect("/")
        
    
if __name__ == '__main__':
    app.run(debug=True)
