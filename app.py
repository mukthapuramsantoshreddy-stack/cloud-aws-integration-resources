
import os
import re
import json
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "change-this-development-key"
)

AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
S3_BUCKET = os.environ.get("S3_BUCKET", "").strip()

PHOTO_PREFIX = os.environ.get(
    "S3_PHOTO_PREFIX", "student-photos"
).strip("/") + "/"

RECORD_PREFIX = os.environ.get(
    "S3_RECORD_PREFIX", "student-records"
).strip("/") + "/"

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Uses the EC2 instance IAM role automatically.
s3 = boto3.client("s3", region_name=AWS_REGION)


def allowed_image(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def get_students():
    """Read JSON student records from private S3."""
    students = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(
        Bucket=S3_BUCKET, Prefix=RECORD_PREFIX
    ):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            if not key.endswith(".json"):
                continue

            response = s3.get_object(
                Bucket=S3_BUCKET, Key=key
            )
            student = json.loads(
                response["Body"].read().decode("utf-8")
            )

            photo_key = student.get("photo_key")
            student["photo_url"] = None

            if photo_key:
                student["photo_url"] = s3.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": S3_BUCKET,
                        "Key": photo_key
                    },
                    ExpiresIn=900
                )

            students.append(student)

    students.sort(
        key=lambda item: item.get("created_at", ""),
        reverse=True
    )
    return students


@app.route("/", methods=["GET", "POST"])
def index():
    if not S3_BUCKET:
        return (
            "S3_BUCKET is missing. Set the exact S3 bucket name "
            "in the EC2 terminal.",
            500
        )

    if request.method == "POST":
        student = {
            "student_name": request.form.get(
                "student_name", ""
            ).strip(),
            "roll_number": request.form.get(
                "roll_number", ""
            ).strip(),
            "phone_number": request.form.get(
                "phone_number", ""
            ).strip(),
            "college_name": request.form.get(
                "college_name", ""
            ).strip(),
            "email": request.form.get("email", "").strip(),
            "course_branch": request.form.get(
                "course_branch", ""
            ).strip(),
            "year_of_study": request.form.get(
                "year_of_study", ""
            ).strip(),
        }

        if not all(student.values()):
            flash("Please fill in all student details.", "error")
            return redirect(url_for("index"))

        if not re.fullmatch(
            r"[0-9+() .-]{7,20}", student["phone_number"]
        ):
            flash("Please enter a valid phone number.", "error")
            return redirect(url_for("index"))

        email = student["email"]
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("index"))

        photo = request.files.get("student_photo")

        if not photo or not photo.filename:
            flash("Please select a student photo.", "error")
            return redirect(url_for("index"))

        filename = secure_filename(photo.filename)

        if not filename or not allowed_image(filename):
            flash(
                "Only JPG, JPEG, PNG, GIF, and WEBP images are allowed.",
                "error"
            )
            return redirect(url_for("index"))

        student_id = uuid.uuid4().hex
        photo_key = f"{PHOTO_PREFIX}{student_id}_{filename}"
        record_key = f"{RECORD_PREFIX}{student_id}.json"

        student["student_id"] = student_id
        student["photo_key"] = photo_key
        student["created_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        photo_uploaded = False

        try:
            # 1. Upload the image to S3.
            s3.upload_fileobj(
                photo,
                S3_BUCKET,
                photo_key,
                ExtraArgs={
                    "ContentType": photo.mimetype
                    or "application/octet-stream"
                }
            )
            photo_uploaded = True

            # 2. Save student details as JSON in S3.
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=record_key,
                Body=json.dumps(
                    student, ensure_ascii=False, indent=2
                ).encode("utf-8"),
                ContentType="application/json"
            )

            flash(
                "Student details and photo saved successfully!",
                "success"
            )

        except NoCredentialsError:
            flash(
                "AWS credentials not found. Attach an IAM role "
                "to your EC2 instance.",
                "error"
            )

        except ClientError as exc:
            app.logger.exception("S3 operation failed")

            # Clean up the photo if saving its record failed.
            if photo_uploaded:
                try:
                    s3.delete_object(
                        Bucket=S3_BUCKET, Key=photo_key
                    )
                except ClientError:
                    app.logger.exception("Photo cleanup failed")

            error_code = exc.response.get(
                "Error", {}
            ).get("Code", "Unknown")

            flash(
                f"S3 error: {error_code}. Check the bucket name, "
                "region, and IAM permissions.",
                "error"
            )

        return redirect(url_for("index"))

    try:
        students = get_students()
        return render_template(
            "index.html", students=students
        )

    except (NoCredentialsError, ClientError):
        app.logger.exception("Could not read student records from S3")
        flash(
            "Could not load records from S3. Check the EC2 IAM role "
            "and bucket configuration.",
            "error"
        )
        return render_template("index.html", students=[])


@app.errorhandler(413)
def file_too_large(error):
    flash("Photo must be no larger than 10 MB.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False
    )
