from sqlalchemy.exc import OperationalError

from app.database import get_db
from app.main import app


def test_health(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready_when_database_is_available(client) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_is_unavailable_but_health_stays_healthy_when_database_is_down(client) -> None:
    class UnavailableDatabase:
        def execute(self, statement):
            raise OperationalError("SELECT 1", {}, Exception("database is down"))

    def override_unavailable_database():
        yield UnavailableDatabase()

    app.dependency_overrides[get_db] = override_unavailable_database

    readiness_response = client.get("/ready")
    liveness_response = client.get("/health")

    assert readiness_response.status_code == 503
    assert readiness_response.json() == {"detail": "Database unavailable"}
    assert liveness_response.status_code == 200
    assert liveness_response.json() == {"status": "healthy"}
