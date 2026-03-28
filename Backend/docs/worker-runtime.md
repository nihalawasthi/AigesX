# Worker Runtime (Phase 1)

## Queue + Worker Model

- Jobs are queued in Redis list `aigesx:scan_jobs`.
- API endpoint `POST /api/scan/start/` enqueues job IDs.
- Worker command consumes queued jobs:

```bash
python manage.py run_scan_worker
```

Run multiple worker processes for basic horizontal scaling.

## Execution Isolation and Limits

Execution supports two modes:

- `local` (default): direct subprocess execution with timeout.
- `docker`: container execution with `--cpus` and `--memory` limits.

Set environment variable:

```bash
AIGESX_EXECUTOR=docker
```

Optional Docker image override:

```bash
AIGESX_DOCKER_IMAGE=ubuntu:24.04
```

## Crash Persistence

- Crash inputs are stored in `CrashArtifact` records and written to `media/crashes/`.
- Crash metadata, hashes, grouping keys, and CVE match signals are persisted.
- Deduplication is enforced per job by unique `crash_hash`.

## Centralized Logs

- Structured worker/job events are persisted in `JobExecutionLog`.
- API endpoint to fetch logs:

`GET /api/scan/jobs/<job_id>/logs/`

- Backend logs are also written to `Backend/logs/aigesx_backend.log`.
