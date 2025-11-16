import os
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy import true
from werkzeug.utils import secure_filename
from models.models import db, BirdPictures
from login.login_register import current_user
from utils.decorators import login_required

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

photo_uploader = Blueprint(
    "photo_uploader", __name__, static_folder="static", template_folder="template"
)
s3_bucket = os.environ.get("S3_BUCKET")
s3_region = os.environ.get("S3_REGION")

s3_client = boto3.client("s3", region_name=s3_region)

user = current_user


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def make_unique(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name, extension = os.path.splitext(filename)
    return f"{name}_{timestamp}{extension}"


def upload_file_to_s3(file, bucket, object_name=None):
    """Download file to s3"""
    if object_name is None:
        object_name = file.filename

    try:
        s3_client.upload_fileobj(file, bucket, object_name)
        return True
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False


def delete_file_from_s3(bucket, object_name):
    """delete file from s3"""
    try:
        s3_client.delete_object(Bucket=bucket, Key=object_name)
        return True
    except ClientError as e:
        print(f"Error deleting from S3: {e}")
        return False


def generate_s3_url(bucket, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object"""
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": object_name},
            ExpiresIn=expiration,
        )
        return response
    except ClientError as e:
        print(f"Error generating S3 URL: {e}")
        return None


@photo_uploader.route("/gallery", methods=["GET", "POST"])
@login_required
def index():
    pictures = BirdPictures.query.with_entities(
        BirdPictures.picture,
        BirdPictures.location,
        BirdPictures.id,
        BirdPictures.is_protected,
    ).all()

    unlocked_locations = set()

    if request.method == "POST":
        image_id = request.form["image_id"]
        password = request.form["password"]
        picture = BirdPictures.query.filter_by(id=image_id).first()
        if picture and picture.is_protected and picture.check_password(password):
            flash("Access granted!", "success")
            unlocked_locations.add(picture.id)
        else:
            flash("Wrong password!", "error")

    pictures_with_urls = []
    for pic in pictures:
        if pic.is_protected and pic.id not in unlocked_locations:
            location_display = "Protected!"
        else:
            location_display = pic.location

        s3_url = generate_s3_url(s3_bucket, pic.picture)
        pictures_with_urls.append(
            {
                "picture": pic.picture,
                "location": location_display,
                "id": pic.id,
                "s3_url": s3_url,
                "is_protected": pic.is_protected,
            }
        )
    return render_template("index.html", pictures=pictures_with_urls)


@photo_uploader.route("/upload/", methods=("GET", "POST"))
@login_required
def upload():
    if (
        request.method == "POST"
        and "file" in request.files
        and "location" in request.form
    ):
        file = request.files["file"]
        location = request.form["location"]

        protect_option = request.form.get("protect") == "yes"
        password = request.form.get("password") if protect_option else None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # make a unique file name
            unique_filename = make_unique(filename)

            if upload_file_to_s3(file, s3_bucket, unique_filename):
                new_picture = BirdPictures(
                    location=location,
                    picture=unique_filename,
                    user_id=current_user["id"],
                    is_protected=protect_option,
                )

                if protect_option and password:
                    new_picture.set_password(password)

                db.session.add(new_picture)
                db.session.commit()

                flash("Photo successfully uploaded!", "success")
                return redirect(url_for("photo_uploader.index"))
            else:
                flash("Error when upload photo", "error")
        else:
            flash("Wrong photo format", "error")

    return render_template("upload.html")


@photo_uploader.route("/delete_photo/<image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    can_delete = verify_allowed_to_edit_image(image_id)
    if not can_delete:
        flash("You do not have permission to delete this image", "error")
        return redirect(
            url_for(request.form.get("redirect_page", "dashboard.user_dashboard"))
        )

    picture = BirdPictures.query.filter_by(id=image_id).first()
    if picture:
        # delete from s3
        if delete_file_from_s3(s3_bucket, picture.picture):
            db.session.delete(picture)
            db.session.commit()
            flash("Delete is successful ", "success")
        else:
            flash("Error when delete photo", "error")
    else:
        flash("Someone miss your photo, photo not found", "error")

    return redirect(url_for(request.form.get("redirect_page")))


@photo_uploader.route("/update_location/<image_id>", methods=["POST"])
@login_required
def update_image_location(image_id):
    can_edit = verify_allowed_to_edit_image(image_id)
    if not can_edit:
        flash("You do not have permission to edit this image", "error")
        return redirect(
            url_for(request.form.get("redirect_page", "dashboard.user_dashboard"))
        )

    new_location_name = request.form.get("new_location")

    if not new_location_name:
        flash("Location name is required", "error")
        return redirect(url_for(request.form.get("redirect_page")))

    picture = BirdPictures.query.filter_by(id=image_id).first()
    if picture:
        picture.location = new_location_name.strip()  # Remove whitespace
        db.session.commit()
        flash("Location updated successfully", "success")
    else:
        flash("Image not found", "error")

    return redirect(url_for(request.form.get("redirect_page")))


def verify_allowed_to_edit_image(image_id):
    user_role = session.get("role", "user")
    if user_role == "admin":
        return True
    cur_user_id = session.get("id")
    doesExist = (
        BirdPictures.query.filter_by(id=image_id, user_id=cur_user_id).first()
        is not None
    )
    return doesExist
