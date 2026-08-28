"""Tests for the NEXTCLOUD_READONLY fail-closed guard (nextcloud_mcp_server.readonly)."""

import pytest

from nextcloud_mcp_server import config as _config
from nextcloud_mcp_server.readonly import is_read_only, require_writable


def _set_readonly(monkeypatch: pytest.MonkeyPatch, value: str | None) -> None:
    if value is None:
        monkeypatch.delenv("NEXTCLOUD_READONLY", raising=False)
    else:
        monkeypatch.setenv("NEXTCLOUD_READONLY", value)
    _config._dynaconf.reload()
    _config._clear_settings_caches()


def test_defaults_to_read_only_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_readonly(monkeypatch, None)
    assert is_read_only() is True


def test_explicit_false_disables_read_only(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_readonly(monkeypatch, "false")
    assert is_read_only() is False


def test_explicit_true_keeps_read_only(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_readonly(monkeypatch, "true")
    assert is_read_only() is True


def test_require_writable_allows_read_methods_even_when_read_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_readonly(monkeypatch, None)
    for method in ("GET", "HEAD", "OPTIONS", "PROPFIND", "REPORT", "get", "head"):
        require_writable(method)  # must not raise


def test_require_writable_blocks_write_methods_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_readonly(monkeypatch, None)
    for method in (
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "MKCOL",
        "COPY",
        "MOVE",
        "PROPPATCH",
    ):
        with pytest.raises(RuntimeError, match="read-only mode"):
            require_writable(method)


def test_require_writable_allows_writes_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_readonly(monkeypatch, "false")
    for method in ("POST", "PUT", "DELETE", "PATCH"):
        require_writable(method)  # must not raise
