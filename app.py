from flask import Flask, render_template, request, session, redirect
app = Flask(__name__)

@app.route('/')
def index():
    # stuff
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()