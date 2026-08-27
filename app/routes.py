from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from app import db
from app.models import ServiceRequest


main = Blueprint("main", __name__)


def generate_reference():
    year = datetime.now().year

    latest_request = ServiceRequest.query.order_by(
        ServiceRequest.id.desc()
    ).first()

    if latest_request:
        next_number = latest_request.id + 1
    else:
        next_number = 1

    return f"CSR-{year}-{next_number:04d}"


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/submit", methods=["GET", "POST"])
def submit_request():
    if request.method == "POST":

        citizen_name = request.form.get("citizen_name")
        email = request.form.get("email")
        category = request.form.get("category")
        description = request.form.get("description")
        priority = request.form.get("priority")

        if not citizen_name or not email or not category or not description:
            flash("Please complete all required fields.")
            return redirect(url_for("main.submit_request"))

        reference = generate_reference()

        service_request = ServiceRequest(
            reference=reference,
            citizen_name=citizen_name,
            email=email,
            category=category,
            description=description,
            priority=priority,
            status="Submitted"
        )

        db.session.add(service_request)
        db.session.commit()

        return render_template(
            "submission_success.html",
            service_request=service_request
        )

    return render_template("submit_request.html")


@main.route("/track", methods=["GET", "POST"])
def track_request():
    service_request = None

    if request.method == "POST":

        reference = request.form.get("reference")

        service_request = ServiceRequest.query.filter_by(
            reference=reference
        ).first()

        if not service_request:
            flash("No service request was found with that reference number.")

    return render_template(
        "track_request.html",
        service_request=service_request
    )