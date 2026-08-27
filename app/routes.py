from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import db, login_manager
from app.models import ServiceRequest, Admin, AuditLog


main = Blueprint("main", __name__)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))


def generate_reference():
    year = datetime.now().year

    latest_request = ServiceRequest.query.order_by(
        ServiceRequest.id.desc()
    ).first()

    next_number = latest_request.id + 1 if latest_request else 1

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


@main.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("main.admin_dashboard"))

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if admin and check_password_hash(
            admin.password_hash,
            password
        ):
            login_user(admin)
            return redirect(url_for("main.admin_dashboard"))

        flash("Invalid administrator username or password.")

    return render_template("admin_login.html")


@main.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()

    return redirect(url_for("main.admin_login"))


@main.route("/admin")
@login_required
def admin_dashboard():

    requests = ServiceRequest.query.order_by(
        ServiceRequest.created_at.desc()
    ).all()

    total_requests = len(requests)

    submitted = sum(
        1 for item in requests
        if item.status == "Submitted"
    )

    under_review = sum(
        1 for item in requests
        if item.status == "Under Review"
    )

    in_progress = sum(
        1 for item in requests
        if item.status == "In Progress"
    )

    resolved = sum(
        1 for item in requests
        if item.status == "Resolved"
    )

    return render_template(
        "admin_dashboard.html",
        requests=requests,
        total_requests=total_requests,
        submitted=submitted,
        under_review=under_review,
        in_progress=in_progress,
        resolved=resolved
    )

@main.route("/admin/audit-logs")
@login_required
def audit_logs():

    logs = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).all()

    return render_template(
        "audit_logs.html",
        logs=logs
    )


@main.route(
    "/admin/request/<int:request_id>/update",
    methods=["GET", "POST"]
)
@login_required
def update_request(request_id):

    service_request = ServiceRequest.query.get_or_404(
        request_id
    )

    if request.method == "POST":

        old_priority = service_request.priority
        old_status = service_request.status

        new_priority = request.form.get("priority")
        new_status = request.form.get("status")

        service_request.priority = new_priority
        service_request.status = new_status
        service_request.updated_at = datetime.utcnow()

        if old_priority != new_priority:

            priority_log = AuditLog(
                admin_username=current_user.username,
                request_reference=service_request.reference,
                action="Priority Updated",
                old_value=old_priority,
                new_value=new_priority
            )

            db.session.add(priority_log)

        if old_status != new_status:

            status_log = AuditLog(
                admin_username=current_user.username,
                request_reference=service_request.reference,
                action="Status Updated",
                old_value=old_status,
                new_value=new_status
            )

            db.session.add(status_log)

        db.session.commit()

        flash("Service request updated successfully.")

        return redirect(
            url_for("main.admin_dashboard")
        )

    return render_template(
        "admin_update_request.html",
        service_request=service_request
    )


