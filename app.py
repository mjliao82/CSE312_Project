import datetime
import json
import authenticity
from flask import Flask, send_from_directory, render_template, request, make_response
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socket_server = SocketIO(app)


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route('/register', methods=["POST"])
def register():
    response = make_response(render_template("index.html"))
    username = request.form['username_reg']
    password = request.form["password_reg"]
    confirm_password = request.form["password_reg_2"]
    authenticity.user_registration(username, password, confirm_password)
    return response


@app.route("/login", methods=['POST'])
def login():
    response = make_response(render_template("index.html"))
    username = request.form['username_login']
    password = request.form["password_login"]
    result = authenticity.user_login(username, password)
    expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
    if result[0]:
        response.set_cookie('token', result[1], max_age=3600, httponly=True, expires=expiration)
    return response



if __name__ == '__main__':
    socket_server.run(app, host="0.0.0.0", port=8080)