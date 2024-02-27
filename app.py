import json
import authenticity
from flask import Flask, send_from_directory, render_template, request, make_response
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socket_server = SocketIO(app)

@app.route("/")
def login():
    return render_template("index.html")


@app.route('/register', method=["POST"])
def register():
    username = request.form['username_reg']
    password = request.form["password_reg"]
    result = authenticity.takethis(username, password)
    return

@app.route("/login", method=['POST'])
def login():
    username = request.form['username_login']
    password = request.form["password_login"]
    result = authenticity.takethat(username, password)
    return 

if __name__ == '__main__':
    socket_server.run(app, host="0.0.0.0", port=8080)