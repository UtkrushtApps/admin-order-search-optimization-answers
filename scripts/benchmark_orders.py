import statistics
import time

import requests

BASE_URL = "http://127.0.0.1:8000"
PARAMS = {"status": "paid", "from": "2026-01-01", "limit": 100, "offset": 0}


def main() -> None:
    timings: list[float] = []
    statement_counts: list[int] = []

    for _ in range(5):
        started = time.perf_counter()
        response = requests.get(f"{BASE_URL}/api/orders", params=PARAMS, timeout=30)
        elapsed_ms = (time.perf_counter() - started) * 1000
        response.raise_for_status()
        payload = response.json()
        timings.append(elapsed_ms)
        statement_counts.append(int(response.headers.get("X-SQL-Statements", "0")))
        print(
            f"rows={len(payload)} elapsed_ms={elapsed_ms:.1f} "
            f"sql_statements={statement_counts[-1]}"
        )

    print(
        f"median_elapsed_ms={statistics.median(timings):.1f} "
        f"max_sql_statements={max(statement_counts)}"
    )


if __name__ == "__main__":
    main()
