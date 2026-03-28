# MVP Runtime Stack Lock

This document records the confirmed runtime stack for AigesX MVP.

## Confirmed Components

- Database: PostgreSQL
- Queue/Broker: Redis
- Packaging/Runtime: Docker

## Scope of This Decision

- This is a platform baseline decision.
- It does not imply that all components are fully implemented today.
- Queue + worker implementation remains tracked under the MVP job-management tasks.

## Why This Baseline

- PostgreSQL supports reliable relational storage for users, jobs, and reports.
- Redis is a standard low-latency broker for queue and worker signaling.
- Docker gives reproducible local/dev/prod service behavior.

## Follow-up Implementation Tasks

- Add queue system (Redis + worker model).
- Add worker execution isolation and resource controls.
- Add deployment profile and environment templates for MVP.
