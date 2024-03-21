import datetime
import json
import authenticity
import requests
import os
from flask import Flask, send_from_directory, render_template, request, make_response, redirect, url_for, jsonify, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socket_server = SocketIO(app)


# Upon site entry, if the user still has their non-expired token, they will be
# automatically logged into the homepage, otherwise back to login.
@app.route("/")
def landing_page():
    token = request.cookies.get('token')
    if token and authenticity.user_authenticated(token):
        response = make_response(redirect('/home'))
        response.headers["X-Content-Type-Options"] = 'nosniff'
        expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
        response.set_cookie('token', token, max_age=3600, httponly=True, expires=expiration)
        return response
    response = make_response(render_template("index.html"))
    response.headers["X-Content-Type-Options"] = 'nosniff'
    return response


@app.route('/static/login.css')
def serve_logCSS():
    response = make_response(send_from_directory('static', 'login.css'))
    response.headers["X-Content-Type-Options"] = 'nosniff'
    return response


@app.route('/static/yo.jpg')
def serve_yo():
    response = make_response(send_from_directory('static', 'yo.jpg'))
    response.headers["X-Content-Type-Options"] = 'nosniff'
    return response


@app.route('/register', methods=["POST"])
def register():
    response = make_response(redirect('/'))
    username = request.form['username_reg']
    password = request.form["password_reg"]
    confirm_password = request.form["password_reg_2"]
    authenticity.user_registration(username, password, confirm_password)
    return response

app.secret_key = 'your_secret_key'  # Set a secret key for sessions.
# Creates a token that expires after an hour after successful login.
# This token will keep them logged in everytime they visit the base site,
# until they click logout.
@app.route("/login", methods=['POST'])
def login():
    response = make_response(redirect('/'))
    username = request.form['username_login']
    print(username)
    password = request.form["password_login"]
    result = authenticity.user_login(username, password)
    expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
    if result[0]: #user is valid 
        response2 = make_response(redirect('/home'))
        response2.set_cookie('token', result[1], max_age=3600, httponly=True, expires=expiration)
        session['user'] = username
        #generating xsrf
        xsrf_token = os.urandom(24).hex()
        session['xsrf_token'] = xsrf_token
        return response2
    return response


@app.route('/home')
def homepage():
    xsrf = session.get('xsrf_token', '')
    print(xsrf)
    response = make_response(render_template("home.html", xsrf_token=xsrf))
    return response

# New endpoint to display username on frontend
@app.route("/get-username")
def get_username():
    user = session.get('user')  # Use session to retrieve the username.
    if user:
        return jsonify(username=user)  # Return the username as a JSON object.
    else:
        return jsonify(error='User not logged in'), 401

@app.route("/logout", methods=['POST'])
def logout():
    response = make_response(redirect('/'))
    # token = request.get['token']
    response.delete_cookie('token')
    
    # authenticity.user_logout(token)
    return response

@app.route("/chat-messages", methods=['POST', "GET"])
def chatserver():
    if request.method == "POST":
        payload = request.get_json()
        print(payload)
        msg = payload['message']
        xsrf = payload['token']
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    socket_server.run(app, host="0.0.0.0", port=8080)
