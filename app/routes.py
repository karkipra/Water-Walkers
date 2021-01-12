from app import app

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
#from flask.ext.sqlalchemy import SQLAlchemy
import sqlite3
from datetime import datetime 
import json
import mailchimp_marketing as MailchimpMarketing
from mailchimp_marketing.api_client import ApiClientError
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
from functools import wraps
# Initializing bootstrap
bootstrap = Bootstrap(app)

# Setup flask mail stuff (for forgot_pwd only, not general emails)
mail = Mail(app)

# NOTE - To test mailchimp, turn this to True, fill in api_key and LIST_ID
TESTING_MAILCHIMP = False

if TESTING_MAILCHIMP:
    # Initializing mailchimp
    # NOTE - these values depend on the account - don't forget to change them if you move to a different one
    mailchimp = MailchimpMarketing.Client()
    mailchimp.set_config({
        "api_key": "FIXME",
        "server" : "us17"
    })

    # test that mailchimp is working correctly - should print "everything's chimpy!"
    response = mailchimp.ping.get()
    print(response)

LIST_ID = "FIXME"

# this code is used to CREATE an audience programmatically. Since this only needs to happen once, it's commented out
"""
body = {
  "permission_reminder": "You signed up for updates on our website",
  "email_type_option": False,
  "campaign_defaults": {
    "from_name": "FIXME",
    "from_email": "test@gmail.com",
    "subject": "Contact - Water Walkers",
    "language": "EN_US"
  },
  "name": "Water Walkers",
  "contact": {
    "company": "FIXME",
    "address1": "FIXME",
    "address2": "FIXME",
    "city": "Nashville",
    "state": "TN",
    "zip": "FIXME",
    "country": "US"
  }
}

try:
  response = mailchimp.lists.create_list(body)
  print("Response: {}".format(response))
except ApiClientError as error:
  print("An exception occurred: {}".format(error.text))
"""

# this is the logic behind the login_required decorator
# https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    # fetch basic user info
    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()
    if session["user_type"] == 1:
        db.execute("SELECT * FROM STUDENTS where user_id=?", (session["user_id"],))
    elif session["user_type"] == 2:
        db.execute("SELECT * FROM STAFF where user_id=?", (session["user_id"],))

    user = db.fetchone()

    # ADD CHECK IF NAME IS NONE
    firstname = user[1]

    events = db.execute("SELECT * FROM EVENTS")
    conn.commit()
        
    return render_template('index.html', name=firstname, events=events, user_type=session["user_type"])

@app.route('/login', methods=["GET", "POST"])
def login():  
    # forgets and previous user info
    session.clear()

    # setup login page
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("email")
        password = request.form.get("password")
        
        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()
        
        # look for username and password in database
        db.execute("SELECT * FROM MAIN WHERE username=?", (username,))
        data = db.fetchall()
        conn.commit() # is this line needed? not editing anything in db, just looking
        error = None

        # use werkzeug function to check password hash - NOTE - you cannot just compare using
        # generate_password_hash since that produces different strings each time
        if len(data) != 1 or not check_password_hash(data[0][3], password):
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
        else:
            session["user_id"] = data[0][0]
            session["user_type"] = data[0][1]
         
            return redirect("/")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")

    
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method =="GET":
        return render_template("register.html")
    else:
        # get values from form
        fname = request.form.get("fname")
        lname = request.form.get("lname")

        password = generate_password_hash(request.form.get("password"))
        confirm = request.form.get("passwordconfirm")
        
        # TODO - show users that password doesn't match
        # NOTE - must use this function, cannot string compare - see note in login about this function
        if not check_password_hash(password, confirm):
            return redirect("/register")
        
        age = request.form.get("age")
        grade = request.form.get("grade")
        dob = request.form.get("dob")
        email = request.form.get("email")

        # NOTE this stuff was added later and is not added to the html in this order
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
        needs = request.form.get("needs") # TODO - figure out if we need this ;)
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

        if TESTING_MAILCHIMP:
            # add user to mailchimp master audience
            member_info = {
                "email_address": email,
                "status": "subscribed",
                "merge_fields": {
                "FNAME": fname,
                "LNAME": lname
                }
            }

            try:
                response = mailchimp.lists.add_list_member(LIST_ID, member_info)
                print("response: {}".format(response))
            except ApiClientError as error:
                print("An exception occurred: {}".format(error.text))

            # tag user if indicated
            tags = [["adventure", request.form.get("adventure")],["tutoring", request.form.get("tutoring")]]

            # check responses to each tag and add them if checked off on registration form
            for tag in tags:
                if tag[1]:
                    # boilerplate from https://mailchimp.com/developer/guides/organize-contacts-with-tags/
                    SUBSCRIBER_HASH = hashlib.md5(email.encode('utf-8')).hexdigest()
                    try:
                        response = mailchimp.lists.update_list_member_tags(LIST_ID, SUBSCRIBER_HASH, body={
                            "tags": [{
                                "name": tag[0],
                                "status": "active"
                            }]
                        })
                        print("client.lists.update_list_member_tags() response: {}".format(response))
                    except ApiClientError as error:
                        print("An exception occurred: {}".format(error.text))

        return redirect("/")

@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

# TODO - take photo of user
@app.route('/profile/<index>')
@login_required
def profile(index):

    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()

    #directs to profile page for the staff
    if index == '0' and session["user_type"] == 2:
        index = session["user_id"]
        db.execute("SELECT * FROM STAFF where user_id=?", (index,))
        staff = db.fetchone()
        return render_template('prof_staff.html', staff=staff)

    #show the past events and profile page for students
    else:
        # prevent students from accessing other student profiles
        if session["user_type"] == 1:
            index = session["user_id"]

        # get student and events they've attended
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

        # analyze attendance data for % no show and behavioral issues
        # start with % no show
        db.execute("SELECT * FROM NOSHOWS WHERE student_id=?", (index,))
        noShows = db.fetchall()

        # catch edge case where student hasn't attended any events
        if len(pastEvents) == 0 and len(noShows) == 0:
            noShowPercentage = 0
        else:
            # need to account for rows removed from attendees table in denominator by readding no show length
            noShowPercentage = round(100 * len(noShows) / (len(noShows) + len(pastEvents)))

        # get % behavioral issues
        db.execute("SELECT * FROM ATTENDEES WHERE student_id=? and behavior_issue=?",(index, 0))
        behavioralIssues = db.fetchall()

        if len(pastEvents) == 0:
            behavioralPercentage = 0
        else:
            behavioralPercentage = round(100 * len(behavioralIssues) / len(pastEvents))

        return render_template('profile.html', student=student, pastEvents=pastEvents, event_info=event_info, events=events, noShow=noShowPercentage, behavior=behavioralPercentage)

@app.route('/edit_student', methods=['GET', 'POST'])
@login_required
def edit_student():
    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()

    db.execute("SELECT * FROM STUDENTS where user_id=?", (session["user_id"],))
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

    # UPDATE EMAIL TAGS
    # get current tags
    if TESTING_MAILCHIMP:
        db.execute("SELECT username FROM MAIN WHERE user_id=?", (session["user_id"],))
        email = db.fetchone()[0]

        SUBSCRIBER_HASH = hashlib.md5(email.encode('utf-8')).hexdigest()
        active_tags = {}

        try:
            response = mailchimp.lists.get_list_member_tags(LIST_ID, SUBSCRIBER_HASH)
            print("client.ping.get() response: {}".format(response))
            
            # fill active_tags with info from response(json)
            for tag in response["tags"]:
                active_tags.setdefault(tag["name"])

        except ApiClientError as error:
            print("An exception occurred: {}".format(error.text))

        # add tags
        tags_to_add = []

        # manual check of all tags that exist, add the names of those that do to tags_to_add
        if request.form.get("adventure"):
            tags_to_add.append("adventure")
        if request.form.get("tutoring"):
            tags_to_add.append("tutoring")

        # tag users if they don't already have given tag
        for tag in tags_to_add:
            if tag not in active_tags:
                try:
                    response = mailchimp.lists.update_list_member_tags(LIST_ID, SUBSCRIBER_HASH, body={
                        "tags": [{
                            "name": tag,
                            "status": "active"
                        }]
                    })
                    print("client.lists.update_list_member_tags() response: {}".format(response))
                except ApiClientError as error:
                    print("An exception occurred: {}".format(error.text))
        
        # remove tags
        tags_to_remove = []
        
        # same procedure as above
        if request.form.get("adventure_stop"):
            tags_to_remove.append("adventure")
        if request.form.get("tutoring_stop"):
            tags_to_remove.append("tutoring")

        # remove tag is user has given tag
        for tag in tags_to_remove:
            if tag in active_tags:
                try:
                    response = mailchimp.lists.update_list_member_tags(LIST_ID, SUBSCRIBER_HASH, body={
                        "tags": [{
                            "name": tag,
                            "status": "inactive"
                        }]
                    })
                    print("client.lists.update_list_member_tags() response: {}".format(response))
                except ApiClientError as error:
                    print("An exception occurred: {}".format(error.text))

    # get the new value for student before passing it
    db.execute("SELECT * FROM STUDENTS where user_id=?", (session["user_id"],))
    student = db.fetchone()
    return render_template('edit_student.html', student=student)

@app.route('/edit_staff', methods=['GET', 'POST'])
@login_required
def edit_staff():
    conn = sqlite3.connect('database/database.db')
    db = conn.cursor()

    db.execute("SELECT * FROM STAFF where user_id=?", (session["user_id"],))
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
                    db.execute("INSERT INTO NOSHOWS (student_id, event_id) VALUES (?,?)", (student[0], index))
                # in case of random show up for event with no interest, insert into database
                elif present and not initially_interested:
                    db.execute("INSERT INTO ATTENDEES (event_id, student_id, late, left_early, behavior_issue) VALUES (?,?,?,?,?)", (index, student[0], 1, 1, 1,))

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
@login_required
def signup_student():
    if request.method == "POST":
        index = request.form.get('event_id')
        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()

        # insert student and event data into database
        # TODO - replace with INSERT OR IGNORE at some point
        db.execute("SELECT * FROM ATTENDEES WHERE event_id=? AND student_id=?", (index, session["user_id"]))
        data = db.fetchall()

        # Don't insert if already present
        if len(data) == 0:
            db.execute("INSERT INTO ATTENDEES (event_id, student_id) VALUES (?,?)", (index, session["user_id"],))
            conn.commit()

        return redirect("/")

@app.route('/Event1/<index>')
@login_required
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
    return render_template('Event1.html', attendees=attendees, event=event, user_type=session["user_type"])

@app.route('/RegisterStaff', methods=['GET', 'POST'])
def RegisterStaff():
    if request.method =="GET":
        return render_template('reg_staff.html')
    else:
        # get values from form
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        
        password = generate_password_hash(request.form.get("password"))
        confirm = request.form.get("passwordconfirm")

        # TODO - show users that password doesn't match
        # NOTE - must use this function, cannot string compare - see note in login about this function
        if not check_password_hash(password, confirm):
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

@app.route('/forgot_pwd', methods=['GET', 'POST'])
def forgot_pwd():
    if request.method == 'GET':
        return render_template('forgot_pwd.html')
    else:
        recovery = request.form.get("recovery")

        # send recovery email
        # NOTE - IMPORTANT!!! CREATE TESTING EMAIL, DO NOT USE YOUR OWN!!!
        # user email should be protected but we need a dummy "noreply" email
        # TODO - send user link to reset password with index as user_id
        with mail.record_messages() as outbox:
            # test to see that mail "sent"
            msg = Message(subject = "Water Walkers Password Recovery",
                          body = "This is a test.", 
                          sender = "FIXME", 
                          recipients = ["FIXME"])

            mail.send(msg)

            assert len(outbox) == 1
            assert outbox[0].subject == "Water Walkers Password Recovery"
            assert outbox[0].body == "This is a test."


        return render_template("confirmation.html")

@app.route('/reset_password/<index>', methods=['GET', 'POST'])
def reset_password(index):
    if request.method == 'GET':
        return render_template("reset.html", index=index)
    else:
        new_password = generate_password_hash(request.form.get("new_password"))
        confirm_new_password = request.form.get("confirm_new_password")

        # TODO - show user that passwords do not match
        if not check_password_hash(new_password, confirm_new_password):
            return redirect(url_for('reset_password', index=index))

        # connect to database
        conn = sqlite3.connect('database/database.db')
        db = conn.cursor()

        db.execute("UPDATE MAIN SET password=?", (new_password,))
        conn.commit()

        return redirect('/login')

@app.route('/mass_email', methods=['GET', 'POST'])
def mass_email():
    if request.method == 'GET':
        return render_template("email.html")
    else:
        campaign_name = request.form.get("campaign_name")
        subject = request.form.get("subject")
        body = request.form.get("body")
        tag_name = None
        tag_number = -1

        #  get response from tags in form
        try:
            tag_name = request.form["tags"]
        except:
            print("Error with radio buttons occured")

        # determine tag id
        # TODO - figure out how to get tag_id without subscriber email
        if tag_name:
            SUBSCRIBER_HASH = hashlib.md5(EMAIL.encode('utf-8')).hexdigest()
            try:
                response = mailchimp.lists.get_list_member_tags(LIST_ID, SUBSCRIBER_HASH)
                print("client.ping.get() response: {}".format(response))

                for tag in response["tags"]:
                    if tag["name"] == tag_name:
                        tag_number = tag["id"]

            except ApiClientError as error:
                print("An exception occurred: {}".format(error.text))

        # send email to students
        # TODO - remember to setup proper reply to email before deployment
        if TESTING_MAILCHIMP:
            # basic campaign info https://mailchimp.com/developer/api/marketing/campaigns/add-campaign/
            campaign = {
                "type": "plaintext",
                "recipients": {
                    "list_id": LIST_ID
                },
                "settings": {
                    "subject_line": subject,
                    "preview_text": body,
                    "title": campaign_name,
                    "from_name": "Water Walkers Staff",
                    "reply_to": "test@gmail.com"
                }
            }

            content = {
                "plaintext": body
            }

            # FIXME
            if tag_name:
                recipients = {
                    "segment_opts": {
                        "saved_segment_id": tag_number
                    },
                    "list_id": LIST_ID
                }
                print(recipients)

            try:
                # create campaign
                response = mailchimp.campaigns.create(campaign)
                campaign_id = response["id"]
                print(campaign_id)

                # TODO - append to dict or use update function to add tags if specified

                # set campaign content and send mass email
                mailchimp.campaigns.set_content(campaign_id, content)
                send_receipt = mailchimp.campaigns.send(campaign_id)

                # should print 204 HTML code
                print(send_receipt)
            except ApiClientError as error:
                print("An exception occurred: {}".format(error.text))

        return redirect("/")

