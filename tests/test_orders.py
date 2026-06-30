import time

import requests

BASE_URL = "http://127.0.0.1:8000"


def test_orders_response_shape_and_limit() -> None:
    response = requests.get(
        f"{BASE_URL}/api/orders",
        params={"status": "paid", "from": "2026-01-01", "limit": 10, "offset": 0},
        timeout=15,
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 10

    expected_keys = {
        "id",
        "order_number",
        "status",
        "created_at",
        "total_amount",
        "currency",
        "customer_email",
    }
    assert set(payload[0].keys()) == expected_keys
    assert payload[0]["status"] == "paid"
    assert payload[0]["customer_email"].endswith("@example.com")


def test_orders_pagination_window_is_stable() -> None:
    first = requests.get(
        f"{BASE_URL}/api/orders",
        params={"status": "paid", "from": "2026-01-01", "limit": 5, "offset": 0},
        timeout=15,
    )
    second = requests.get(
        f"{BASE_URL}/api/orders",
        params={"status": "paid", "from": "2026-01-01", "limit": 5, "offset": 5},
        timeout=15,
    )

    assert first.status_code == 200
    assert second.status_code == 200
    first_ids = [item["id"] for item in first.json()]
    second_ids = [item["id"] for item in second.json()]
    assert len(first_ids) == 5
    assert len(second_ids) == 5
    assert set(first_ids).isdisjoint(second_ids)


def test_orders_request_uses_bounded_database_work() -> None:
    started = time.perf_counter()
    response = requests.get(
        f"{BASE_URL}/api/orders",
        params={"status": "paid", "from": "2026-01-01", "limit": 100, "offset": 0},
        timeout=20,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000

    assert response.status_code == 200
    assert len(response.json()) == 100
    assert int(response.headers["X-SQL-Statements"]) <= 3
    assert elapsed_ms < 1200
