# Water-Walkers Event Attendance Tracker

## Description
Partnered with Water Walkers for VandyHacks 2020, we designed a web application for easy, quick, and convenient check-in for attendance tracking. It allows for students to sign up, sign in, and register for events, while staff members can keep track of student profiles and event attendance.

Please find the deployed version at https://water-walkers.herokuapp.com/.

## Contributors 
* Annie Zhou
* Pratik Karki
* Nick Patilsen
* Ayushi Sharma

## Features
- [x] Allow parents and students to register personal accounts
- [x] Allow parents and students to log in to their accounts
- [x] Easy to navigate UI
- [x] Provides a calendar view to keep track of events
- [x] Allow staff members to add events
- [x] Allow staff members to keep track of student attendance to events

## Demo

![](demo.gif)

## Installation Guide

```bash
# clone the repo
$ git clone https://github.com/karkipra/Water-Walkers.git
$ cd Water-Walkers

# create a virtual env named 'venv'
$ python3 -m venv venv

# activate the venv (if not already activated)
$ source venv/bin/activate

# recursively install all the requirements 
$ pip install -r requirements.txt

# run the app!
$ flask run
```

## Requirements
See requirements.txt

## Future Updates

- Add more functionality with volunteers, parents
- Optimize the storage and efficiency of the program
- Integrate with Docusign to effectively sign waivers
- Integrate Mailchip for email communication
- Ensure responsiveness of pages on mobile view
