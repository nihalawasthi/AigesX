from __future__ import annotations

import time
from django.core.management.base import BaseCommand

from reports.executor import execute_scan_job
from reports.queue import dequeue_scan_job_blocking


class Command(BaseCommand):
    help = "Run Redis-backed scan worker for queued jobs"

    def add_arguments(self, parser):
        parser.add_argument("--sleep", type=int, default=2, help="Sleep seconds when queue is empty")

    def handle(self, *args, **options):
        sleep_seconds = max(1, int(options["sleep"]))
        self.stdout.write(self.style.SUCCESS("Scan worker started."))

        while True:
            job_id = dequeue_scan_job_blocking(timeout_seconds=sleep_seconds)
            if not job_id:
                time.sleep(sleep_seconds)
                continue

            self.stdout.write(f"Processing queued job: {job_id}")
            execute_scan_job(job_id)
