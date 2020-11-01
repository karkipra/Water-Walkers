from app import app

from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
#from flask.ext.sqlalchemy import SQLAlchemy
import sqlite3
from datetime import datetime 
import json
from mailchimp_marketing import Client

# Initializing bootstrap
bootstrap = Bootstrap(app)

"""
# Initializing mailchimp
# NOTE - these values depend on the account - don't forget to change them if you move to a different one
mailchimp = Client()
mailchimp.set_config({
    "api_key": "FIXME",
    "server" : "us17"
})

# test that mailchimp is working correctly - should print "everything's chimpy!"
response = mailchimp.ping.get()
print(response)
"""

@app.route('/')
def index():
    if not LOGGED_IN:
        return redirect("/login")

    # SQLite query to add username and password into database
    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()
    if USER_TYPE == 1:
        db.execute("SELECT * FROM STUDENTS where user_id=?", (USER_ID,))
    elif USER_TYPE == 2:
        db.execute("SELECT * FROM STAFF where user_id=?", (USER_ID,))

    user = db.fetchone()

    # ADD CHECK IF NAME IS NONE
    firstname = user[1]

    events = db.execute("SELECT * FROM EVENTS")
    conn.commit()
        
    return render_template('index.html', name=firstname, events=events, user_type=USER_TYPE)

# consider adding login_required aspect (http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/)
@app.route('/login', methods=["GET", "POST"])
def login():  
    global LOGGED_IN
    global USER_ID
    global USER_TYPE
    
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
        db.execute("SELECT * FROM MAIN WHERE username=? AND password=?", (username, password))
        data = db.fetchall()
        conn.commit() # is this line needed? not editing anything in db, just looking

        if len(data) != 1:
            # TODO - add way for user to see that they've added in the wrong info
            return redirect("/login")
        else:
            LOGGED_IN = True
            USER_ID = data[0][0]
            USER_TYPE = data[0][1]
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
        fname = request.form.get("fname")
        lname = request.form.get("lname")

        password = request.form.get("password")
        confirm = request.form.get("passwordconfirm")
        
        # TODO - show users that password doesn't match
        if password != confirm:
            return redirect("/register")
        
        age = request.form.get("age")
        grade = request.form.get("grade")
        dob = request.form.get("dob")
        email = request.form.get("email")

        # NEW - not added to the html in this order
        school = request.form.get("school")
        gender = request.form.get("gender")
        ethnicity = request.form.get("ethnicity")
        immunizations = request.form.get("immunizations")
        
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
        student_info = (str(user_id), fname, lname, age, grade, dob, parent1, parent2, emergency, allergies, meds, parent1phone, parent2phone, emergency_phone, gender, school, ethnicity, immunizations, notes)
        db.execute("INSERT INTO STUDENTS (user_id, firstname, lastname, age, grade, dob, parent1, parent2, econtact, diet, meds, parent1phone, parent2phone, emergencyphone, gender, school, ethnicity, immunizations, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", student_info)
        conn.commit()
        
        return redirect("/")

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

# TODO - take photo of user
@app.route('/profile/<index>')
def profile(index):

    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()

    # prevent students from accessing profiles other than their own
    if index == 0 or USER_TYPE == 1:
        index = USER_ID

    #show the past events and profile page for students
    if USER_TYPE == 1:
        db.execute("SELECT * FROM STUDENTS where user_id=?", (index,))
        student = db.fetchone()

        db.execute("SELECT * FROM ATTENDEES where student_id=?", (index,))
        pastEvents = db.fetchall()

        event_info = []
        for event in pastEvents: 
            db.execute("SELECT * FROM EVENTS where event_id=?", (event[0],))
            event_info.append(db.fetchone())

        events = db.execute("SELECT * FROM EVENTS")
        events = db.fetchall()

        return render_template('profile.html', student=student, pastEvents=pastEvents, event_info=event_info, events=events)
    
    #directs to profile page for the staff
    db.execute("SELECT * FROM STAFF where user_id=?", (index,))
    staff = db.fetchone()
    return render_template('prof_staff.html', staff=staff)

@app.route('/edit_student', methods=['GET', 'POST'])
def edit_student():
    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()

    db.execute("SELECT * FROM STUDENTS where user_id=?", (USER_ID,))
    student = db.fetchone()

    if request.method =="GET":
        return render_template('edit_student.html', student = student)
    
    #gets all info after user edits the form
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    age = request.form.get("age")
    grade = request.form.get("grade")
    dob = request.form.get("dob")
    parent1 = request.form.get("parent1")
    parent2 = request.form.get("parent2")
    emergency = request.form.get("econtact") 
    allergies = request.form.get("allergies")
    meds = request.form.get("medications")
    parent1phone = request.form.get("parent1phone")
    parent2phone = request.form.get("parent2phone")
    emergency_phone = request.form.get("econtactphone")
    gender = request.form.get("gender")
    school = request.form.get("school")
    ethnicity = request.form.get("ethnicity")
    immunizations = request.form.get("immunization")   
    notes = request.form.get("notes")
    
    student_info = (fname, lname, age, grade, dob, parent1, parent2, emergency, allergies, meds, parent1phone, parent2phone, emergency_phone, gender, school, ethnicity, immunizations, notes, student[0])

    db.execute("UPDATE STUDENTS SET firstname = ?, lastname = ?, age = ?, grade = ?, dob = ?, parent1 = ?, parent2 = ?, econtact = ?, diet = ?, meds = ?, parent1phone = ?, parent2phone = ?, emergencyphone = ?, gender = ?, school = ?, ethnicity = ?, immunizations = ?, notes = ? WHERE user_id = ?", (student_info))
    conn.commit()

    #get the new value for student before passing it
    db.execute("SELECT * FROM STUDENTS where user_id=?", (student[0],))
    student = db.fetchone()
    return render_template('edit_student.html', student=student)

@app.route('/edit_staff', methods=['GET', 'POST'])
def edit_staff():
    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()

    db.execute("SELECT * FROM STAFF where user_id=?", (USER_ID,))
    staff = db.fetchone()

    if request.method =="GET":
        return render_template('prof_staff.html', staff = staff)
   
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    emergency = request.form.get("econtact")
    meds = request.form.get("medications")
    gender = request.form.get("gender")
    allergies = request.form.get("allergies")
    immunizations = request.form.get("immunization")
    
    db.execute("UPDATE STAFF SET firstname = ?, lastname = ?, econtact = ?, meds = ?, gender = ?, allergies = ?, immunizations = ? WHERE user_id = ?", (fname, lname, emergency, meds, gender, allergies, immunizations, staff[0]))
    conn.commit()
    db.execute("SELECT * FROM STAFF where user_id=?", (staff[0],))
    staff = db.fetchone()
    return render_template('prof_staff.html', staff=staff)

@app.route('/data')
def return_data():
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
            'address': event[5],
            # adding url for that particular page for calendar.html
            'url': url_for('Event1', index=event[0]) 
        }
        js.append(d)

    with open('events.json', 'w') as outfile:
        json.dump(js, outfile)    

    with open("events.json", "r") as input_data:
        return input_data.read()

@app.route('/add', methods=["GET", "POST"])
def add_event():
    if request.method == "GET":
        return render_template("add_event.html")
    else:
        name = request.form.get("name")
        descrip = request.form.get("descrip")
        start = request.form.get("start")
        end = request.form.get("end")
        address = request.form.get("address")

        # IMPORTANT - for now this needs to run locally on someone's machine. 
        # remember to change this per your db's path!
        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()

        # SQLite query to add username and password into database
        # events that haven't started are represented with a 0 - after the first attendance pass this is changed to 1
        db.execute("INSERT INTO EVENTS (event_name, event_descrip, start, end, address, started) VALUES (?, ?, ?, ?, ?, ?)", (name, descrip, start, end, address, 0))
        #event_id = db.execute("SELECT event_id FROM EVENTS WHERE event_name=?", (name,))

        conn.commit()

        return redirect("/")

# TODO - make this page hidden for students
@app.route('/delete_event', methods=["GET", "POST"])
def delete_event():
    if request.method == "POST":
        index = request.form.get('event_id')
        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()

        # delete event 
        db.execute("DELETE FROM EVENTS WHERE event_id=?", (index,))
        conn.commit()

        return redirect("/")

@app.route('/take_attendance/<index>', methods=['GET', 'POST'])
def take_attendance(index):
    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()

    # select students who have expressed interest (or if after the fact, actually attended) a given event
    db.execute("SELECT * FROM ATTENDEES WHERE event_id=?", (index,))
    data = db.fetchall()
    
    # if no one is interested, generate all students by default
    if len(data) == 0:
        db.execute("SELECT * FROM STUDENTS")
        attendees = db.fetchall()
    else:
        attendees = []
        for row in data:
            student_id = row[1]

            db.execute("SELECT firstname FROM STUDENTS WHERE user_id=?", (student_id,))
            fname = db.fetchone()

            db.execute("SELECT lastname FROM STUDENTS WHERE user_id=?", (student_id,))
            lname = db.fetchone()

            db.execute("SELECT grade FROM STUDENTS WHERE user_id=?", (student_id,))
            grade = db.fetchone()

            attendees.append((student_id, fname[0], lname[0], grade[0]))

    # sort students by last name
    # students is a list of tuples (each student is a tuple)
    attendees.sort(key = lambda x: x[2])

    if request.method == 'POST':
        db.execute("SELECT * FROM EVENTS WHERE event_id=?", (index,))
        event_data = db.fetchall()

        # first pass just made, filtering out no shows
        if event_data[0][6] == 0:
            # first, update the event as started so this block doesn't fire again
            db.execute("UPDATE EVENTS SET started=? WHERE event_id=?", (1, index,))
            conn.commit()

            # next, remove no shows from database OR in the case if no interested students, add to database
            for student in attendees:
                # check if student is present
                present = request.form.get(str(student[0]) + "p")

                # check if student was initially interested in the event
                db.execute("SELECT * FROM ATTENDEES WHERE event_id=? AND student_id=?", (index, student[0],))
                initially_interested = len(db.fetchall()) > 0

                # in case of no show, remove from database
                if not present and initially_interested:
                    db.execute("DELETE FROM ATTENDEES WHERE event_id=? AND student_id=?", (index, student[0],))
                # in case of random show up for event with no interest, insert into database
                elif present and not initially_interested:
                    db.execute("INSERT INTO ATTENDEES (event_id, student_id, late, left_early, behavior_issue) VALUES (?,?,?,?,?)", (index, student[0], 0, 0, 0,))

                conn.commit()

        # update attendance details if first pass has already been made
        else:
            # check to see if on time or late
            for student in attendees:
                attendance_data = [ request.form.get(str(student[0]) + "o"),
                                    request.form.get(str(student[0]) + "l"),
                                    request.form.get(str(student[0]) + "le"),
                                    request.form.get(str(student[0]) + "b"), ]

                # since sqlite can't handle booleans, we have to convert them to integers (0=T, 1=F)
                # the default value is a student isn't present at the event
                db_values = [1, 1, 1, 1]

                for i in range(len(attendance_data)):
                    if attendance_data[i]:
                        db_values[i] -= 1

                # only insert students who have at least one checkmark in some field
                if sum(db_values) != 4:
                    db.execute("SELECT * FROM ATTENDEES WHERE event_id=? AND student_id=?", (index, student[0]))
                    data = db.fetchall()

                    # check to see if it's an update for attendance (eg. leaving early) or a new record
                    if len(data) == 0:
                        db.execute("INSERT INTO ATTENDEES (event_id, student_id, late, left_early, behavior_issue) VALUES (?,?,?,?,?)", (index, student[0], db_values[1], db_values[2], db_values[3]))
                    else:
                        db.execute("UPDATE ATTENDEES SET late = ?, left_early = ?, behavior_issue = ? WHERE event_id = ? and student_id = ?", (db_values[1], db_values[2], db_values[3], index, student[0]))

                    conn.commit()

        return redirect("/")
    else:
        db.execute("SELECT * FROM EVENTS WHERE event_id=?", (index,))
        event_data = db.fetchall()
        started = event_data[0][6]
        return render_template('attendance.html', students=attendees, index=index, started=started)
        
# TODO - this could be modified to add students to a seperate db table rather than attendees
@app.route('/signup_student', methods=['GET', 'POST'])
def signup_student():
    if request.method == "POST":
        index = request.form.get('event_id')
        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()

        # insert student and event data into database
        # TODO - replace with INSERT OR IGNORE at some point
        db.execute("SELECT * FROM ATTENDEES WHERE event_id=? AND student_id=?", (index, USER_ID))
        data = db.fetchall()

        # Don't insert if already present
        if len(data) == 0:
            db.execute("INSERT INTO ATTENDEES (event_id, student_id) VALUES (?,?)", (index, USER_ID,))
            conn.commit()

        return redirect("/")

@app.route('/Event1/<index>')
def Event1(index):
    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()

    # select event object
    db.execute("SELECT * FROM EVENTS WHERE event_id=?", (index,))
    event = db.fetchone()

    # select students who have expressed interest (or if after the fact, actually attended) a given event
    db.execute("SELECT * FROM ATTENDEES WHERE event_id=?", (index,))
    data = db.fetchall()

    attendees = []
    for row in data:
        student_id = row[1]

        db.execute("SELECT firstname FROM STUDENTS WHERE user_id=?", (student_id,))
        fname = db.fetchone()

        db.execute("SELECT lastname FROM STUDENTS WHERE user_id=?", (student_id,))
        lname = db.fetchone()

        db.execute("SELECT grade FROM STUDENTS WHERE user_id=?", (student_id,))
        grade = db.fetchone()

        attendees.append((fname[0], lname[0], grade[0]))

    # pass in user type in order to only show interested students to staff accounts
    return render_template('Event1.html', attendees=attendees, event=event, user_type=USER_TYPE)

@app.route('/RegisterStaff', methods=['GET', 'POST'])
def RegisterStaff():
    if request.method =="GET":
        return render_template('reg_staff.html')
    else:
        # get values from form
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        
        password = request.form.get("password")
        confirm = request.form.get("passwordconfirm")

        # TODO - show users that password doesn't match
        if password != confirm:
            return redirect("/RegisterStaff")
        
        emergency = request.form.get("contact")
        meds = request.form.get("medical")
        email = request.form.get("email")

        # NEW - not in this order
        gender = request.form.get("gender")
        allergies = request.form.get("allergies")
        immunizations = request.form.get("immunizations")

        main_info = (2, email, password)

        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()
        
        # main table updated
        db.execute("INSERT INTO MAIN (user_type, username, password) VALUES (?,?,?)", main_info)
        conn.commit()
        
        # get staff's user_id
        db.execute("SELECT * FROM MAIN WHERE username=?", (email,))
        data = db.fetchall()
        user_id = data[0][0]

         # TODO - edit db to have parent phone numbers
        staff_info = (str(user_id), fname, lname, emergency, meds, gender, allergies, immunizations)
        db.execute("INSERT INTO STAFF (user_id, firstname, lastname, econtact, meds, gender, allergies, immunizations) VALUES (?,?,?,?,?,?,?,?)", staff_info)
        conn.commit()
        
        return redirect("/")

@app.route('/forgot_pwd')
def forgot_pwd():
    return render_template('forgot_pwd.html')

# TODO - replace this unsecure login mechanic
LOGGED_IN = False
USER_ID = None 
USER_TYPE = 0 

