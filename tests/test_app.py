from app import db
from app.models import ServiceRequest, AuditLog


def submit_request(client):
    return client.post(
        "/submit",
        data={
            "citizen_name": "Test Citizen",
            "email": "citizen@example.com",
            "category": "Street Lighting",
            "priority": "Medium",
            "description": "Street light is not working."
        },
        follow_redirects=True
    )


def admin_login(client):
    return client.post(
        "/admin/login",
        data={
            "username": "admin",
            "password": "Admin@123"
        },
        follow_redirects=True
    )


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Citizen Service Request Portal" in response.data


def test_submit_service_request(client, app):
    response = submit_request(client)

    assert response.status_code == 200
    assert b"Request Submitted Successfully" in response.data

    with app.app_context():
        service_request = ServiceRequest.query.first()

        assert service_request is not None
        assert service_request.citizen_name == "Test Citizen"
        assert service_request.status == "Submitted"


def test_reference_generation(client, app):
    submit_request(client)

    with app.app_context():
        service_request = ServiceRequest.query.first()

        assert service_request.reference.startswith("CSR-")
        assert service_request.reference.endswith("0001")


def test_track_request(client, app):
    submit_request(client)

    with app.app_context():
        service_request = ServiceRequest.query.first()
        reference = service_request.reference

    response = client.post(
        "/track",
        data={
            "reference": reference
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert reference.encode() in response.data
    assert b"Street Lighting" in response.data


def test_invalid_reference(client):
    response = client.post(
        "/track",
        data={
            "reference": "CSR-9999-9999"
        },
        follow_redirects=True
    )

    assert b"No service request was found" in response.data


def test_admin_login(client):
    response = admin_login(client)

    assert response.status_code == 200
    assert b"Administration Dashboard" in response.data


def test_admin_dashboard_requires_login(client):
    response = client.get(
        "/admin",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Administrator Login" in response.data


def test_admin_update_request(client, app):
    submit_request(client)
    admin_login(client)

    with app.app_context():
        service_request = ServiceRequest.query.first()
        request_id = service_request.id

    response = client.post(
        f"/admin/request/{request_id}/update",
        data={
            "priority": "High",
            "status": "Under Review"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Service request updated successfully" in response.data

    with app.app_context():
        updated_request = db.session.get(
            ServiceRequest,
            request_id
        )

        assert updated_request.priority == "High"
        assert updated_request.status == "Under Review"


def test_audit_log_created(client, app):
    submit_request(client)
    admin_login(client)

    with app.app_context():
        service_request = ServiceRequest.query.first()
        request_id = service_request.id

    client.post(
        f"/admin/request/{request_id}/update",
        data={
            "priority": "High",
            "status": "In Progress"
        },
        follow_redirects=True
    )

    with app.app_context():
        logs = AuditLog.query.all()

        assert len(logs) == 2

        actions = [log.action for log in logs]

        assert "Priority Updated" in actions
        assert "Status Updated" in actions


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["service"] == "citizen-service-portal"