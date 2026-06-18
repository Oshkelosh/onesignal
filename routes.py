"""OneSignal addon routes."""

from __future__ import annotations

from typing import Any

from app.addons.notifications.shared_routes import build_notification_routers


def _parse_onesignal_config_form(form: Any) -> tuple[dict[str, Any], bool]:
    return (
        {
            "app_id": form.get("app_id", ""),
            "rest_api_key": form.get("rest_api_key", ""),
        },
        form.get("is_enabled") == "on",
    )


admin_router, jinja_env = build_notification_routers(
    "onesignal",
    template_name="onesignal_config.html",
    page_title="OneSignal Settings",
    secret_keys=("rest_api_key",),
    parse_config_form=_parse_onesignal_config_form,
)
