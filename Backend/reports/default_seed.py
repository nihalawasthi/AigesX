from __future__ import annotations

import hashlib
import uuid

from django.core.files.base import ContentFile

from .models import UploadedArtifact


def _device_mac_hex() -> str:
    return f"{uuid.getnode():012x}"


def _default_seed_name_for_user(user_id: int) -> str:
    return f"default_seed_u{user_id}_{_device_mac_hex()}.bin"


def _build_seed_bytes(user_id: int) -> bytes:
    base = f"aigesx:{user_id}:{_device_mac_hex()}".encode("utf-8")
    digest = hashlib.sha256(base).digest()
    # Deterministic corpus-like byte stream for the same user on the same device.
    return (digest + b"\x00\x01\xff\nAIGESX-SEED\n") * 32


def ensure_default_seed_artifact(user):
    expected = _default_seed_name_for_user(user.id)
    existing = (
        UploadedArtifact.objects.filter(user=user, kind=UploadedArtifact.KIND_CORPUS)
        .order_by("-created_at")
    )

    for artifact in existing:
        if artifact.file and artifact.file.name.endswith(expected):
            return artifact

    payload = _build_seed_bytes(user.id)
    artifact = UploadedArtifact.objects.create(
        user=user,
        kind=UploadedArtifact.KIND_CORPUS,
        file=ContentFile(payload, name=expected),
    )
    return artifact
