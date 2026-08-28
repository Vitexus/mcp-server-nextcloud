"""Read-only mode guard for BaseNextcloudClient._make_request.

Defaults to enabled (fail-closed): set NEXTCLOUD_READONLY=false to allow
write methods (POST/PUT/DELETE/PATCH/MKCOL/COPY/MOVE/PROPPATCH/...) against
the Nextcloud REST/WebDAV/CalDAV/CardDAV APIs.

Note: CalendarClient talks CalDAV via its own ``caldav`` library session, not
the shared httpx client, so it does not go through ``_make_request`` and is
NOT covered by this guard -- see ``client/calendar.py``.
"""

from __future__ import annotations

from nextcloud_mcp_server.config import cfg_bool

#: WebDAV/CalDAV/CardDAV/HTTP methods that only read state.
_READ_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PROPFIND", "REPORT"})


def is_read_only() -> bool:
    return cfg_bool("NEXTCLOUD_READONLY", True)


def require_writable(method: str) -> None:
    if method.upper() in _READ_METHODS:
        return
    if is_read_only():
        raise RuntimeError(
            f"This server is running in read-only mode (NEXTCLOUD_READONLY=true); "
            f"refusing {method.upper()} request. Set NEXTCLOUD_READONLY=false to "
            f"allow writes."
        )
