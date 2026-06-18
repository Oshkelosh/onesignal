"""OneSignal push notification integration."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field, SecretStr

from app.addons.notifications.base import NotificationAddon
from app.addons.notifications.helpers import post_json_webhook
from app.addons.log import info, warning
from app.addons.config_serialization import dump_addon_config


class OnesignalConfig(BaseModel):
    app_id: str = Field(default=..., description="OneSignal App ID")
    rest_api_key: SecretStr = Field(default=..., description="OneSignal REST API key")

    @classmethod
    def config_model(cls):
        return cls


class OnesignalAddon(NotificationAddon):
    addon_id: str = "onesignal"
    addon_name: str = "OneSignal"
    addon_description: str = "Send push notifications via OneSignal."
    addon_category: str = "notification"
    version: str = "1.0.0"
    is_enabled: bool = False
    supported_channels: ClassVar[list[str]] = ["push"]

    _config: Dict[str, Any] | None = None
    _app_id: str | None = None
    _rest_api_key: str | None = None

    @classmethod
    def config_schema(cls):
        return OnesignalConfig

    async def initialize(self, config: dict) -> None:
        validated = self.config_schema()(**config)
        self._config = dump_addon_config(validated)
        self._app_id = validated.app_id
        self._rest_api_key = validated.rest_api_key.get_secret_value()
        self.is_enabled = True
        info("OneSignal", "Initialized (app_id={})", self._app_id)

    async def validate_config(self, config: dict) -> None:
        from app.core.exceptions import ValidationError

        validated = self.config_schema()(**config)
        rest_api_key = validated.rest_api_key.get_secret_value()
        if not rest_api_key:
            return
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"https://onesignal.com/api/v1/apps/{validated.app_id}",
                headers={"Authorization": f"Basic {rest_api_key}"},
            )
        if resp.status_code == 401:
            raise ValidationError(message="Invalid REST API key — check your credentials")
        if resp.status_code == 403:
            raise ValidationError(
                message="REST API key is valid but missing required permissions: apps:read"
            )
        if resp.status_code >= 400:
            raise ValidationError(message="OneSignal rejected the REST API key")

    async def shutdown(self) -> None:
        self._app_id = None
        self._rest_api_key = None
        self.is_enabled = False

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> Dict[str, Any]:
        return self.channel_not_supported("email", to)

    async def send_sms(self, to: str, body: str) -> Dict[str, Any]:
        return self.channel_not_supported("sms", to)

    async def send_push(
        self,
        to: str,
        title: str,
        body: str,
        data: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if not self._app_id or not self._rest_api_key:
            return {"success": False, "message_id": "", "error": "Not configured", "to": to}

        payload: dict[str, Any] = {
            "app_id": self._app_id,
            "headings": {"en": title},
            "contents": {"en": body},
            "include_player_ids": [to],
        }
        if data:
            payload["data"] = data

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://onesignal.com/api/v1/notifications",
                    headers={
                        "Authorization": f"Basic {self._rest_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                result = resp.json()
                return {
                    "success": True,
                    "message_id": result.get("id", ""),
                    "to": to,
                }
        except Exception as exc:
            warning("OneSignal", "send_push to={} error: {}", to, exc)
            return {"success": False, "message_id": "", "error": str(exc), "to": to}

    async def send_webhook(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = await post_json_webhook(url, payload)
        if not result.get("success"):
            warning("OneSignal", "send_webhook to={} error: {}", url, result.get("error"))
        return result

    def list_public_push_config(self) -> dict[str, Any] | None:
        if not self._app_id:
            return None
        return {"provider": self.addon_id, "config": {"appId": self._app_id}}

    def get_routers(self) -> List[APIRouter]:
        return []

    def get_admin_routes(self) -> List[APIRouter]:
        from app.addons.notifications.onesignal.routes import admin_router

        return [admin_router]

    def get_admin_templates(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "templates")

    def get_admin_static(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "static")
