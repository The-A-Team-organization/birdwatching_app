from flask import Blueprint, render_template, redirect, url_for, session, request, flash
import re
from models.models import db, BirdPictures, User, HunterIP
from utils.decorators import login_required, admin_required
from images.photo_uploader import s3_client, generate_s3_url, s3_bucket

dashboard = Blueprint(
    "dashboard", __name__, static_folder="static", template_folder="template"
)


@dashboard.route("/dashboard")
@login_required
def user_dashboard():
    # user_role = session.get("role", "user")
    user_id = session.get("id")

    # if user_role == "admin":
    #     return admin_dashboard()
    # else:
    # if we want to redirect admin roles to admin dashboard uncomment this if statement and user_role variable
    pictures = (
        BirdPictures.query.filter_by(user_id=user_id)
        .with_entities(BirdPictures.picture, BirdPictures.location, BirdPictures.id)
        .all()
    )
    pictures_with_urls = []
    for pic in pictures:
        s3_url = generate_s3_url(s3_bucket, pic.picture)
        pictures_with_urls.append({
            'picture': pic.picture,
            'location': pic.location,
            'id': pic.id,
            's3_url': s3_url
        })

    return render_template("user_dashboard.html", pictures=pictures_with_urls)


@dashboard.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    pictures = (
        db.session.query(
            BirdPictures.picture, BirdPictures.location, User.username, BirdPictures.id
        )
        .join(User, BirdPictures.user_id == User.id)
        .all()
    )

    pictures_with_urls = []
    for pic in pictures:
        s3_url = generate_s3_url(s3_bucket, pic.picture)
        pictures_with_urls.append({
            'picture': pic.picture,
            'location': pic.location,
            'username': pic.username,
            'id': pic.id,
            's3_url': s3_url
        })

    return render_template("admin_dashboard.html", pictures=pictures_with_urls)


@dashboard.route("/dashboard/add_ip", methods=["POST"])
@login_required
def add_ip():
    ip = request.form.get("ip")
    user_id = session.get("id")

    ip_regex = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    if not ip or not re.match(ip_regex, ip):
        flash("Invalid IP", "error")
        return redirect(url_for("dashboard.user_dashboard") + "#ip-modal")

    exist_ips = HunterIP.query.all()
    for exist_ip in exist_ips:
        if exist_ip.check_ip(ip):
            flash("This IP already exist", "error")
            return redirect(url_for("dashboard.user_dashboard") + "#ip-modal")

    hunter_ip = HunterIP(added_by=user_id)
    hunter_ip.set_ip(ip)
    db.session.add(hunter_ip)
    db.session.commit()
    flash("IP save successfully", "success")
    return redirect(url_for("dashboard.user_dashboard") + "#ip-modal")
