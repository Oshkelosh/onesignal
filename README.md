# OneSignal (`onesignal`)

Send push notifications via the OneSignal REST API.

## Overview

| | |
|---|---|
| Addon ID | `onesignal` |
| Category | notification |
| Channels | push |
| Version | 1.0.0 |
| Category guide | [../README.md](../README.md) |

Only **one** notification provider per channel can be active at a time.

## Enable and configure

1. Install this package under `app/addons/notifications/onesignal/`
2. Open **Admin → Notifications → OneSignal** at `/admin/notifications/onesignal`
3. Enter App ID and REST API key
4. Enable the provider checkbox and save

## Configuration schema

| Field | Type | Description |
|-------|------|-------------|
| `app_id` | string | OneSignal application UUID |
| `rest_api_key` | secret | OneSignal REST API key |

Secrets are stored in `addon_configs`, not in `.env`.

## Routes

### Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/notifications/onesignal` | Config form |
| POST | `/admin/notifications/onesignal/save` | Save config |

### Public API

None — core calls `send_push()` with a OneSignal **player ID** as `to`.

## Provider setup

1. Create an app at [OneSignal](https://onesignal.com/).
2. Configure iOS/Android/Web platforms and integrate the OneSignal SDK in your client app.
3. Copy **App ID** and **REST API Key** from **Settings → Keys & IDs**.
4. Store each subscriber's **player ID** and pass it as the `to` argument when dispatching push.

Uses `POST https://onesignal.com/api/v1/notifications` with Basic auth.

Email and SMS are not supported.

## Package layout

```
onesignal/
├── README.md
├── addon.py
├── routes.py
└── templates/
    └── onesignal_config.html
```

## See also

- [Notification addon development](../README.md)
- [Oshkelosh addon guide](../../README.md)
