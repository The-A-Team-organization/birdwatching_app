import re
import os
from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from models.models import db, User, HunterIP

url_for_hunters="https://zakon.rada.gov.ua/laws/show/2341-14#n1669"


login_register = Blueprint(
    "login_register", __name__, static_folder="static", template_folder="template"
)  # still relative to module
bcrypt = Bcrypt()

def get_user_ip():
    if request.environ.get("HTTP_X_FORWARDED_FOR"):
        return request.environ["HTTP_X_FORWARDED_FOR"].split(",")[0].strip()
    return request.environ.get("REMOTE_ADDR")

@login_register.before_app_request
def redirect_hunter_ips():
    user_ip = get_user_ip()
    exist_ips = HunterIP.query.all()
    for exist_ip in exist_ips:
        if exist_ip.check_ip(user_ip):
            return redirect(url_for_hunters, code=302)

@login_register.route("/")
@login_register.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["loggedin"] = True
            session["id"] = user.id
            session["username"] = user.username
            session["role"] = user.role
            return redirect(url_for("dashboard.user_dashboard"))
        else:
            msg = "Incorrect username/password!"
    return render_template("login.html", msg=msg)


@login_register.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("role", None)
    return redirect(url_for("login_register.login"))


@login_register.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            msg = "Account already exists!"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username must contain only letters and numbers!"
        elif " " in password:
            msg = "Password must not contain spaces!"
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            new_user.set_role(role="user")

            db.session.add(new_user)
            db.session.commit()

            session["loggedin"] = True
            session["id"] = new_user.id
            session["username"] = new_user.username
            session["role"] = new_user.role
        return redirect(url_for("dashboard.user_dashboard"))
    return render_template("register.html", msg=msg)


current_user = session
