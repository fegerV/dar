"""Check p99 latency from Locust stats CSV."""

import csv
import sys

# Locust renamed these columns in 2.x ("# requests" -> "Request Count", etc.).
# The workflow installs locust unpinned, so accept both spellings.
REQUEST_COUNT_COLUMNS = ("Request Count", "# requests")
FAILURE_COUNT_COLUMNS = ("Failure Count", "# failures")
AVERAGE_COLUMNS = ("Average Response Time", "Average response time")


def _column(row: dict[str, str], candidates: tuple[str, ...]) -> str:
    """Return the first candidate column that exists in the CSV header."""
    for name in candidates:
        if name in row:
            return row[name]
    raise KeyError(f"none of {list(candidates)} found in CSV header: {sorted(row)}")


def _as_float(value: str) -> float | None:
    """Parse a numeric CSV cell, returning None for Locust's "N/A" placeholder."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def check_p99_latency(csv_file: str, max_p99_ms: int) -> bool:
    """
    Check if p99 latency is below threshold.

    Args:
        csv_file: Path to Locust stats CSV file
        max_p99_ms: Maximum allowed p99 latency in milliseconds

    Returns:
        True if p99 is below threshold, False otherwise
    """
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Name"] == "Aggregated":
                p99 = _as_float(_column(row, ("99%",)))
                if p99 is None:
                    print("ERROR: p99 is not numeric - no successful requests were recorded")
                    return False

                p50 = _as_float(_column(row, ("50%",)))
                avg = _as_float(_column(row, AVERAGE_COLUMNS))
                num_requests = int(_as_float(_column(row, REQUEST_COUNT_COLUMNS)) or 0)
                num_failures = int(_as_float(_column(row, FAILURE_COUNT_COLUMNS)) or 0)

                print("Load Test Results:")
                print(f"  Requests: {num_requests}")
                print(f"  Failures: {num_failures}")
                if avg is not None:
                    print(f"  Average:  {avg:.1f}ms")
                if p50 is not None:
                    print(f"  p50:      {p50:.1f}ms")
                print(f"  p99:      {p99:.1f}ms")
                print(f"  Threshold: {max_p99_ms}ms")

                if p99 > max_p99_ms:
                    print(f"\nFAILED: p99 latency {p99:.1f}ms exceeds threshold {max_p99_ms}ms")
                    return False

                print(f"\nPASSED: p99 latency {p99:.1f}ms is within threshold {max_p99_ms}ms")
                return True

    print("ERROR: Could not find 'Aggregated' row in CSV")
    return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <csv_file> <max_p99_ms>")
        sys.exit(1)

    csv_file = sys.argv[1]
    max_p99_ms = int(sys.argv[2])

    passed = check_p99_latency(csv_file, max_p99_ms)
    sys.exit(0 if passed else 1)
