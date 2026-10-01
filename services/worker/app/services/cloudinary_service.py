"""Cloudinary media ingestion and signature service."""

from __future__ import annotations

import hashlib
import time
import os
from typing import Any
from uuid import UUID

from contracts import CloudinaryAssetRef


class CloudinaryService:
    def __init__(self) -> None:
        self.cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "demo")
        self.api_key = os.getenv("CLOUDINARY_API_KEY", "123456789")
        self.api_secret = os.getenv("CLOUDINARY_API_SECRET", "secret")
        self.upload_preset = os.getenv("CLOUDINARY_UPLOAD_PRESET", "impacttrace_preset")

    def generate_signed_upload_params(
        self,
        project_id: UUID,
        site_id: UUID | None = None,
        folder_prefix: str = "impacttrace",
    ) -> dict[str, Any]:
        timestamp = int(time.time())
        public_id_prefix = f"{folder_prefix}/projects/{project_id}"
        if site_id:
            public_id_prefix += f"/sites/{site_id}"

        params_to_sign = {
            "timestamp": timestamp,
            "upload_preset": self.upload_preset,
            "folder": public_id_prefix,
        }

        # Sign params: alphabetically sorted key=value pairs joined with & plus secret
        sorted_params = "&".join(f"{k}={v}" for k, v in sorted(params_to_sign.items()))
        string_to_sign = f"{sorted_params}{self.api_secret}"
        signature = hashlib.sha1(string_to_sign.encode("utf-8")).hexdigest()

        return {
            "cloud_name": self.cloud_name,
            "api_key": self.api_key,
            "timestamp": timestamp,
            "upload_preset": self.upload_preset,
            "folder": public_id_prefix,
            "signature": signature,
            "upload_url": f"https://api.cloudinary.com/v1_1/{self.cloud_name}/auto/upload",
        }

    def verify_webhook_signature(self, body_bytes: bytes, timestamp: str, signature: str) -> bool:
        if not signature or not timestamp:
            return False
        expected = hashlib.sha1(f"{body_bytes.decode('utf-8')}{timestamp}{self.api_secret}".encode("utf-8")).hexdigest()
        return signature == expected

    def build_thumbnail_url(self, public_id: str, width: int = 400, height: int = 300, crop: str = "fill") -> str:
        return f"https://res.cloudinary.com/{self.cloud_name}/image/upload/c_{crop},w_{width},h_{height}/{public_id}"
