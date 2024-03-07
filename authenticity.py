# ray's file
import hashlib
import html
import secrets

import bcrypt
from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client["cse312_group"]
user_collection = db["users"]
token_collection = db["tokens"]


# Checks to see if the user has their token in the database
def user_authenticated(token):
    sha256 = hashlib.sha256()
    sha256.update(token.encode("utf-8"))
    user_info = token_collection.find_one({'token': sha256.hexdigest()})
    if user_info:
        return True
    else:
        return False


def user_registration(username, password, confirm_password):
    valid = check_password(password)
    username_fixed = html.escape(username)
    if valid and password == confirm_password:
        salt = bcrypt.gensalt()
        hashed_passwd = bcrypt.hashpw(password.encode("utf-8"), salt)
        user_collection.insert_one({'username': username_fixed, 'password': hashed_passwd, 'salt': salt})
    return


# Checking for a successful login. If the login is correct, will return a 2
# element list containing a boolean and their token, otherwise false and empty.
def user_login(username, password):
    user_info = user_collection.find_one({'username': username})
    if user_info:
        salt = user_info['salt'].decode('utf-8')
        hashed_passwd = bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8"))
        if hashed_passwd == user_info['password']:
            token = secrets.token_urlsafe(80)
            sha256 = hashlib.sha256()
            sha256.update(token.encode("utf-8"))
            token_collection.insert_one({'username': username, 'token': sha256.hexdigest()})
            return [True, token]
    return [False, '']


# Helper Functions

def check_password(password):
    uppercase = False
    lowercase = False
    valid_length = False
    special_char = False
    contains_num = False
    not_invalid = True

    if len(password) >= 8:
        valid_length = True

    for char in password:
        if char.islower():
            lowercase = True
        elif char.isupper():
            uppercase = True
        elif char.isdigit():
            contains_num = True
        elif char in '!@#$%^&()-_=':
            special_char = True
        else:
            not_invalid = False
    return lowercase and uppercase and contains_num and special_char and valid_length and not_invalid
