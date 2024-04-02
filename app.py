import datetime
import json
import authenticity
import requests
import os
import html
import chat
import uuid
import logging
from flask import Flask, send_from_directory, render_template, request, make_response, redirect, url_for, jsonify, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socket_server = SocketIO(app)
UPLOAD_FOLDER = 'public/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}


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

@app.route('/static/login.js')
def serve_js():
    response = make_response(send_from_directory('static', 'login.js'))
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

#global variable for username, i need to access in in def homepage():

@app.route("/login", methods=['POST'])
def login():
    response = make_response(redirect('/'))
    username = request.form['username_login']
    password = request.form["password_login"]
    result = authenticity.user_login(username, password)
    expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
    if result[0]: #user is valid 
        response2 = make_response(redirect('/home'))
        response2.set_cookie('token', result[1], max_age=3600, httponly=True, expires=expiration)
        session['user'] = username
        #generating xsrf
        xsrf_token = os.urandom(24).hex()
        authenticity.xsrf_storage(username, xsrf_token)
        session['xsrf_token'] = xsrf_token
        return response2
    return response


@app.route('/home')
def homepage():
    xsrf = session.get('xsrf_token', '')
    print(request.cookies.get('token'))
    token = request.cookies.get('token')
    user = session.get('user')
    result = authenticity.check_authToken(user, token)
    if result == False:
        resp = make_response(redirect("/"))
        resp.delete_cookie('token')
        session.clear()
        authenticity.user_logout(token)
        return resp
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
    token = request.cookies.get('token')
    response.delete_cookie('token')
    session.clear()
    #delete
    authenticity.user_logout(token)
    return response

@app.route("/chat-messages", methods=['POST', "GET", "DELETE"])
def chatserver():
    if request.method == "POST":
        payload = request.get_json()
        msg = html.escape(payload['message'])  
        xsrf = html.escape(payload['token'])
        token = request.cookies.get('token')
        username = authenticity.findingUser(token)
        result = authenticity.xsrf_handler(username, xsrf) #return a boolean
        if result == False:
            return jsonify({"status": "f^&k you"}), 403
        chat.postmsg([username, msg])
        return jsonify({"status": "success"}), 200
    elif request.method == "GET":
        #find the msg
        msgBottle = chat.getmsg()
        return jsonify(msgBottle)
    elif request.method == "DELETE":
        payload = request.get_json()
        message_id = payload['id']
        token = request.cookies.get('token')
        username = authenticity.findingUser(token)

        # verify user
        auth_user = True
        message_data = chat.chat_collection.find_one({"id": message_id})
        if message_data and message_data['username'] == username:
            auth_user = True
        else:
            auth_user = False

        if auth_user == False:
            return jsonify({"status":"fail"}), 401

        #delete chat
        result = chat.chat_collection.delete_one({"id": message_id})
        #return appropriate response based on attempted deletion
        if result.deleted_count > 0:
            return jsonify({"status":"success"}), 200
        else:
            return jsonify({"status":"fail"}), 404
        
# Function stores user image uploads in chat database
@app.route("/upload-image", methods=['POST'])
def upload_image():
    file = request.files['chatImage']
    if file:
        file_bytes = file.read(10)
        # .jpeg file
        filename = f""
        if file_bytes.startswith(b"\xff\xd8"):
            filename = f"image{str(uuid.uuid4())}.jpeg"
        # .gif file
        elif file_bytes.startswith(b'\x47\x49\x46\x38\x37\x61') or file_bytes.startswith(b'\x47\x49\x46\x38\x39\x61'):
            filename = f"image{str(uuid.uuid4())}.gif"
        # .png file
        elif file_bytes.startswith(b'\x89PNG'):
            filename = f"image{str(uuid.uuid4())}.png"
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.seek(0)  # Resets file pointer to beginning of file after file.read()
        file.save(file_path)
        img_src = f"/public/uploads/{filename}"
        message_html = f'<img src="{img_src}" alt="User Image" width="300" height="400">'
        username = session.get('user')
        data = [username, message_html, str(uuid.uuid4())]
        chat.postmsg(data)
    return redirect(url_for('homepage'))

# Function loads user uploads from disk
@app.route("/public/uploads/<filename>")
def serve_uploads(filename):
    filename = os.path.basename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'])
    return send_from_directory(file_path, filename)

# Function stores user video uploads in chat database
@app.route("/upload-video", methods=['POST'])
def upload_video():
    file = request.files['chatVideo']
    if file:
        filename = f"video{str(uuid.uuid4())}.mp4"
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        vid_src = f"/public/uploads/{filename}"
        message_html = f'<video src="{vid_src}" alt="User Video" controls width="400" height="300">'
        username = session.get('user')
        data = [username, message_html, str(uuid.uuid4())]
        chat.postmsg(data)
    return redirect(url_for('homepage'))
    

if __name__ == '__main__':
    socket_server.run(app, host="0.0.0.0", port=8080)
