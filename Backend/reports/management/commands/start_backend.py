from __future__ import annotations

import atexit
import os
import signal
import subprocess
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Start backend API and scan worker together."

    def add_arguments(self, parser):
        parser.add_argument("--host", default="127.0.0.1", help="Runserver host")
        parser.add_argument("--port", default="8000", help="Runserver port")

    def handle(self, *args, **options):
        host = options["host"]
        port = options["port"]

        manage_py = os.path.join(os.getcwd(), "manage.py")
        py_exec = sys.executable

        worker_proc = subprocess.Popen([py_exec, manage_py, "run_scan_worker"])
        self.stdout.write(self.style.SUCCESS("Worker started."))

        def _cleanup():
            if worker_proc.poll() is None:
                worker_proc.terminate()
                try:
                    worker_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    worker_proc.kill()

        atexit.register(_cleanup)

        def _sig_handler(signum, frame):  # pragma: no cover
            _cleanup()
            raise SystemExit(0)

        signal.signal(signal.SIGINT, _sig_handler)
        signal.signal(signal.SIGTERM, _sig_handler)

        self.stdout.write(self.style.SUCCESS(f"Backend API starting on {host}:{port}"))
        subprocess.run([py_exec, manage_py, "runserver", f"{host}:{port}"])
