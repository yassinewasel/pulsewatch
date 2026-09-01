import httpx


def create_service(client, name="Example", url="https://example.com/health"):
    return client.post("/api/services", json={"name": name, "url": url})


def test_create_list_and_delete_service(client) -> None:
    created = create_service(client)

    assert created.status_code == 201
    assert created.json()["name"] == "Example"
    service_id = created.json()["id"]

    listed = client.get("/api/services")
    assert listed.status_code == 200
    assert [service["id"] for service in listed.json()] == [service_id]

    deleted = client.delete(f"/api/services/{service_id}")
    assert deleted.status_code == 204
    assert client.get("/api/services").json() == []


def test_successful_check_is_stored(client, monkeypatch) -> None:
    service_id = create_service(client).json()["id"]
    monkeypatch.setattr(
        "app.services.monitoring.httpx.get",
        lambda *args, **kwargs: httpx.Response(204),
    )

    response = client.post(f"/api/services/{service_id}/check")

    assert response.status_code == 200
    assert response.json()["status"] == "UP"
    assert response.json()["status_code"] == 204
    assert response.json()["response_time_ms"] is not None

    history = client.get(f"/api/services/{service_id}/checks")
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["status"] == "UP"


def test_network_failure_is_stored_as_down(client, monkeypatch) -> None:
    service_id = create_service(client).json()["id"]

    def fail(*args, **kwargs):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr("app.services.monitoring.httpx.get", fail)
    response = client.post(f"/api/services/{service_id}/check")

    assert response.status_code == 200
    assert response.json()["status"] == "DOWN"
    assert response.json()["status_code"] is None
    assert "connection refused" in response.json()["error_message"]
    assert len(client.get(f"/api/services/{service_id}/checks").json()) == 1


def test_timeout_is_stored_as_down(client, monkeypatch) -> None:
    service_id = create_service(client).json()["id"]

    def timeout(*args, **kwargs):
        raise httpx.ReadTimeout("request timed out")

    monkeypatch.setattr("app.services.monitoring.httpx.get", timeout)
    response = client.post(f"/api/services/{service_id}/check")

    assert response.status_code == 200
    assert response.json()["status"] == "DOWN"
    assert "request timed out" in response.json()["error_message"]


def test_http_error_status_is_down(client, monkeypatch) -> None:
    service_id = create_service(client).json()["id"]
    monkeypatch.setattr(
        "app.services.monitoring.httpx.get",
        lambda *args, **kwargs: httpx.Response(503),
    )

    response = client.post(f"/api/services/{service_id}/check")

    assert response.status_code == 200
    assert response.json()["status"] == "DOWN"
    assert response.json()["status_code"] == 503


def test_check_all_checks_every_service(client, monkeypatch) -> None:
    create_service(client, "One", "https://one.example")
    create_service(client, "Two", "https://two.example")
    monkeypatch.setattr(
        "app.services.monitoring.httpx.get",
        lambda *args, **kwargs: httpx.Response(302),
    )

    response = client.post("/api/services/check-all")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(result["status"] == "UP" for result in response.json())


def test_missing_service_returns_not_found(client) -> None:
    assert client.post("/api/services/999/check").status_code == 404
    assert client.get("/api/services/999/checks").status_code == 404
    assert client.delete("/api/services/999").status_code == 404


def test_dashboard_displays_service_and_recent_status(client, monkeypatch) -> None:
    service_id = create_service(client).json()["id"]
    monkeypatch.setattr(
        "app.services.monitoring.httpx.get",
        lambda *args, **kwargs: httpx.Response(200),
    )
    client.post(f"/api/services/{service_id}/check")

    response = client.get("/")

    assert response.status_code == 200
    assert "Example" in response.text
    assert "https://example.com/health" in response.text
    assert "UP" in response.text
