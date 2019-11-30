from flask import render_template, request, flash

from app.users import users
from app.users.validators import is_user_exist
from flask import Blueprint


@users.route('/')
def none_route():
    return render_template("login.html")


@users.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        user_payload = request.json
        if is_user_exist(user_payload):
            flash("Welcome to our homepage!")
            return render_template("homepage.html")
        else:
            flash("Sorry! it seems to be you haven't registered yet.", "error")
            return render_template("signup.html")
