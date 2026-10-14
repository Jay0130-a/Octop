"""Tests for ``octop models`` ollama subcommands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from octop.cli.main import cli


def test_models_help_lists_ollama_subcommands() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["models", "--help"])
    assert result.exit_code == 0
    for sub in ("ollama-list", "ollama-pull", "ollama-rm"):
        assert sub in result.output


def _patch_active_model(monkeypatch: pytest.MonkeyPatch, body: dict) -> None:
    """Stub the offline settings read behind ``octop models active``."""
    from octop.cli.support import offline_ops as offline_mod

    monkeypatch.setattr(offline_mod, "get_active_model_offline", lambda **_kw: dict(body))


def test_models_active_explains_unset_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unset default must not print a bare "/" with both sides empty (#1930)."""
    _patch_active_model(monkeypatch, {"provider_name": "", "model": ""})
    result = CliRunner().invoke(cli, ["models", "active"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() != "/"
    assert "No global default model is set" in result.output
    assert "octop models active --provider" in result.output


def test_models_active_marks_a_missing_side_with_a_placeholder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_active_model(monkeypatch, {"provider_name": "openai", "model": ""})
    result = CliRunner().invoke(cli, ["models", "active"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "openai / ?"


def test_models_active_prints_both_sides(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_active_model(monkeypatch, {"provider_name": "openai", "model": "gpt-4o"})
    result = CliRunner().invoke(cli, ["models", "active"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "openai / gpt-4o"


def test_models_active_treats_none_as_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    """A repo that hands back ``None`` still reads as "not configured"."""
    _patch_active_model(monkeypatch, {"provider_name": None, "model": None})
    result = CliRunner().invoke(cli, ["models", "active"])
    assert result.exit_code == 0, result.output
    assert "No global default model is set" in result.output
