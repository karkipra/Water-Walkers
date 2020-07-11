from flask import Flask, render_template, request, session, redirect
from forms import LoginForm
from flask_bootstrap import Bootstrap

# Initializing app
app = Flask(__name__)
# Initializing bootstrap
bootstrap = Bootstrap(app)

import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)