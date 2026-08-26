"""Check p99 latency from Locust stats CSV."""

import sys
import csv


def check_p99_latency(csv_file: str, max_p99_ms: int) -> bool:
    """
    Check if p99 latency is below threshold.

    Args:
        csv_file: Path to Locust stats CSV file
        max_p99_ms: Maximum allowed p99 latency in milliseconds

    Returns:
        True if p99 is below threshold, False otherwise
    """
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Name"] == "Aggregated":
                p99 = float(row["99%"])
                p50 = float(row["50%"])
                avg = float(row["Average response time"])
                num_requests = int(row["# requests"])
                num_failures = int(row["# failures"])

                print(f"Load Test Results:")
                print(f"  Requests: {num_requests}")
                print(f"  Failures: {num_failures}")
                print(f"  Average:  {avg:.1f}ms")
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
