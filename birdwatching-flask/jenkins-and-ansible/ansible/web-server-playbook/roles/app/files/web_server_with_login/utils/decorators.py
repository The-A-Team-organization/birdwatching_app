from functools import wraps
from flask import redirect, url_for, session, flash


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("loggedin"):
            flash("Please log in to access this page", "warning")
            return redirect(url_for("login_register.login"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_role = session.get("role", "user")
        if user_role != "admin":
            flash("Access denied. Admin privileges required", "error")
            return redirect(url_for("dashboard.user_dashboard"))

        return f(*args, **kwargs)

    return decorated_function

