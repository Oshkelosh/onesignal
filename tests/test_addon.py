"""Minimal unit tests for the onesignal addon."""

from app.addons.notifications.onesignal.addon import OnesignalAddon


def test_addon_identity():
    assert OnesignalAddon.addon_id == "onesignal"
    assert OnesignalAddon.addon_category == "notification"
