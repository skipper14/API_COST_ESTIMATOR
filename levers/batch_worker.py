"""Offline batch worker fixture for non-interactive routing jobs."""

import argparse
import json
from pathlib import Path
import sys
from typing import Any


FIXTURE_JOBS = [
    {"job_id": "job-001", "urgency": "routine"},
    {"job_id": "job-002", "urgency": "review"},
    {"job_id": "job-003", "urgency": "routine"},
    {"job_id": "job-004", "urgency": "urgent"},
    {"job_id": "job-005", "urgency": "routine"},
    {"job_id": "job-006", "urgency": "review"},
    {"job_id": "job-007", "urgency": "routine"},
]


def read_jobs(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as source:
        jobs = [json.loads(line) for line in source if line.strip()]
    return jobs


def process_jobs(jobs: list[dict[str, Any]], batch_size: int) -> list[dict[str, str]]:
    if batch_size < 1:
        raise ValueError("batch_size must be at least one")
    results = []
    for start in range(0, len(jobs), batch_size):
        batch_number = start // batch_size + 1
        for job in jobs[start : start + batch_size]:
            if not job.get("job_id") or job.get("urgency") not in {
                "routine",
                "review",
                "urgent",
            }:
                raise ValueError("each job requires job_id and a supported urgency")
            result = "human_review" if job["urgency"] in {"review", "urgent"} else "routine_queue"
            results.append(
                {
                    "job_id": str(job["job_id"]),
                    "result": result,
                    "batch_number": str(batch_number),
                }
            )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="JSONL jobs; defaults to built-in fixtures")
    parser.add_argument("--output", type=Path, help="write JSONL results to this path")
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()

    jobs = read_jobs(args.input) if args.input else FIXTURE_JOBS
    results = process_jobs(jobs, args.batch_size)
    output = "\n".join(json.dumps(item, sort_keys=True) for item in results) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    print(
        f"processed={len(results)} batches={(len(results) + args.batch_size - 1) // args.batch_size} "
        "mode=fixture-no-model-calls",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()