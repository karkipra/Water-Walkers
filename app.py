from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
import sqlite3
from datetime import datetime 
import json

# Initializing app
app = Flask(__name__)
# Initializing bootstrap
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    if not LOGGED_IN:
        return redirect("/login")

    user = {'username': 'Pratik'}

    # SQLite query to add username and password into database
    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()
    events = db.execute("SELECT * FROM EVENTS")
    conn.commit()
        
    return render_template('index.html', user=user, events=events)

# consider adding login_required aspect (http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/)
@app.route('/login', methods=["GET", "POST"])
def login():  
    global LOGGED_IN
    if LOGGED_IN:
        return redirect("/")

    # setup login page
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("email")
        password = request.form.get("password")
        
        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()
        
        # look for username and password in database
        # TODO - check parenthesis
        db.execute("SELECT * FROM MAIN WHERE username=? AND password=?", (username, password))
        data = db.fetchall()
        conn.commit()

        if len(data) != 1:
            # TODO - add way for user to see that they've added in the wrong info
            return redirect("/login")
        else:
            LOGGED_IN = True
            return redirect("/")

@app.route('/logout')
def logout():
    global LOGGED_IN
    LOGGED_IN = False
    return redirect("/login")
    
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method =="GET":
        return render_template("register.html")
    else:
        # get values from form
        name = request.form.get("name")
        
        password = request.form.get("password")
        confirm = request.form.get("passwordconfirm")
        
        # TODO - show users that password doesn't match
        if password != confirm:
            return redirect("/register")
        
        age = request.form.get("age")
        grade = request.form.get("grade")
        dob = request.form.get("dob")
        email = request.form.get("email")
        
        parent1 = request.form.get("parent1")
        parent1phone = request.form.get("parent1phone")
        parent2 = request.form.get("parent2")
        parent2phone = request.form.get("parent2phone")
        emergency = request.form.get("econtact")
        emergency_phone = request.form.get("econtactphone")
        
        allergies = request.form.get("allergies")
        needs = request.form.get("needs")
        meds = request.form.get("medications")
        notes = request.form.get("notes")
        
        # fill tuple with ordered col info
        # NOTE - students are user type 1
        main_info = (1, email, password)
        
        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()
        
        # main table updated
        db.execute("INSERT INTO MAIN (user_type, username, password) VALUES (?,?,?)", main_info)
        conn.commit()
        
        # get student's user_id
        db.execute("SELECT * FROM MAIN WHERE username=?", (email,))
        data = db.fetchall()
        user_id = data[0][0]
        
        # TODO - edit db to have parent phone numbers
        student_info = (str(user_id), name, age, grade, dob, parent1, parent2, emergency, allergies, meds, parent1phone, parent2phone, emergency_phone)
        db.execute("INSERT INTO STUDENTS (user_id, name, age, grade, dob, parent1, parent2, econtact, diet, meds, parent1phone, parent2phone, emergencyphone) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", student_info)
        conn.commit()
        
        return redirect("/")

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/profile')
def profile():

    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()

    # SQLite query to add username and password into database
    db.execute("SELECT * FROM STUDENTS") # user_id should be logged in user's id

    student = db.fetchone()
    
    return render_template('profile.html', student=student)

@app.route('/data')
def return_data():
    # SQLite query to add username and password into database
    conn = sqlite3.connect('database/database.db')
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

        # these variables are unused for now
        start = request.form.get("start")
        end = request.form.get("end")
        url = request.form.get("url")

        # IMPORTANT - for now this needs to run locally on someone's machine. 
        # remember to change this per your db's path!
        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()

        # SQLite query to add username and password into database
        db.execute("INSERT INTO EVENTS (event_name, event_descrip, start, end, url) VALUES (?, ?, ?, ?, ?)", (name, descrip, start, end, url))
        conn.commit()

        return redirect("/")

@app.route('/Event1')
def Event1():
    return render_template('Event1.html')
        
LOGGED_IN = False
    
if __name__ == '__main__':
    app.run(debug=True)