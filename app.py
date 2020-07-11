from flask import Flask, render_template, request, session, redirect
from flask_bootstrap import Bootstrap

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

if __name__ == '__main__':
    app.run(debug=True)