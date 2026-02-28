"""Write benchmark results to the GitHub Actions job summary.

Reads benchmark-results.json (always present) and per-phase-results.json
(written by the per-phase benchmark tests when available) and appends
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


_PHASES = [
    "main_query_s",
    "agency_suggestions_s",
    "location_suggestions_s",
    "name_suggestions_s",
    "batch_info_s",
    "format_s",
]


def _per_phase_table(per_phase: dict) -> list[str]:
    datasets = list(per_phase.keys())
    lines = [
        "\n## Per-Phase Averages\n",
        "| Phase | " + " | ".join(datasets) + " |",
        "|-------|" + "|".join("---:" for _ in datasets) + "|",
    ]
    for phase in _PHASES:
        label = phase.removesuffix("_s").replace("_", " ")
        vals = " | ".join(
            f"{per_phase[k].get(phase, 0) * 1000:.2f} ms" for k in datasets
        )
        lines.append(f"| {label} | {vals} |")
    return lines


def main() -> None:
    """Build and write the job summary."""
    benchmark_path = pathlib.Path("benchmark-results.json")
    if not benchmark_path.exists():
        print("benchmark-results.json not found — skipping summary.", file=sys.stderr)
        return

    with benchmark_path.open() as f:
        data = json.load(f)

    lines = _benchmark_table(data)

    per_phase_path = pathlib.Path("per-phase-results.json")
    if per_phase_path.exists():
        with per_phase_path.open() as f:
            per_phase = json.load(f)
        lines += _per_phase_table(per_phase)

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_file:
        print("\n".join(lines))
        return

    with open(summary_file, "a") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
