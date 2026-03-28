# AigesX

AigesX is a web-based Fuzzing-as-a-Service platform.

Its purpose is to help developers and security teams find vulnerabilities in software by uploading a target binary or providing a public GitHub repository link for analysis.

## What The Project Does

AigesX runs automated security analysis pipelines and combines multiple techniques to surface real vulnerability signals.

Core analysis capabilities include:

- AFL++-driven fuzzing workflows
- Symbolic execution modules
- CVE pattern matching and correlation
- Crash and vulnerability reporting with metadata

The platform focuses on turning raw security analysis output into actionable findings that users can inspect from a web dashboard.

## Product Flow

High-level product flow:

1. User submits a target (binary upload or public repository link).
2. Backend orchestrates scanning and analysis jobs.
3. AigesX engine components run fuzzing, symbolic analysis, and CVE correlation.
4. Results are collected and exposed in dashboard-friendly report format.
5. Binary and User submited data except the report are removed from storage.

## Architecture At A Glance

The application is organized into two product surfaces:

- Backend: job orchestration, scanning integration, report generation, and artifact management.
- Frontend: user dashboard for submitting targets, tracking jobs, and reviewing findings.

## MVP Runtime Stack (Confirmed)

The MVP runtime stack is locked to the following baseline:

- PostgreSQL for primary relational persistence.
- Redis for queueing and worker coordination layer.
- Docker for environment consistency and service packaging.

This lock is used as the target deployment baseline for the MVP gate.

## Project Goal

Build a practical and extensible Fuzzing-as-a-Service web product that makes advanced vulnerability discovery accessible through a simple user workflow.
