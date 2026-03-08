"""Write benchmark results to the GitHub Actions job summary.

Reads benchmark-results.json (always present) and appends
a markdown summary to $GITHUB_STEP_SUMMARY.
"""
import json
import os
import pathlib
import sys


def _benchmark_table(data: dict) -> list[str]:
    lines = [
        "## Benchmark Results\n",
        "| Test | Mean (ms) | Min (ms) | Max (ms) | Rounds |",
        "|------|-----------|----------|----------|--------|",
    ]
    for b in data["benchmarks"]:
        s = b["stats"]
        lines.append(
            f"| {b['name']} "
            f"| {s['mean'] * 1000:.2f} "
            f"| {s['min'] * 1000:.2f} "
            f"| {s['max'] * 1000:.2f} "
            f"| {s['rounds']} |"
        )
    return lines


def main() -> None:
    """Build and write the job summary."""
    benchmark_path = pathlib.Path("benchmark-results.json")
    if not benchmark_path.exists():
        print(
            "benchmark-results.json not found — skipping summary.",
            file=sys.stderr,
        )
        return

    with benchmark_path.open() as f:
        data = json.load(f)

    lines = _benchmark_table(data)

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        print("\n".join(lines))
        return

    with open(summary_file, "a") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
