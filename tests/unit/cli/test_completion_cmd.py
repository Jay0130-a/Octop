"""Tests for `octop completion`."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from octop.cli.main import cli


@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_completion_show_emits_script(shell: str) -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["completion", "show", "--shell", shell])
    assert result.exit_code == 0
    assert "_OCTOP_COMPLETE" in result.output


def test_completion_install_appends_eval_line_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rc = tmp_path / ".bashrc"
    rc.write_text("# existing\n")
    monkeypatch.setenv("HOME", str(tmp_path))

    runner = CliRunner()
    r1 = runner.invoke(cli, ["completion", "install", "--shell", "bash", "--rc-file", str(rc)])
    assert r1.exit_code == 0, r1.output
    contents = rc.read_text()
    assert "_OCTOP_COMPLETE" in contents
    line_count_first = contents.count("_OCTOP_COMPLETE")

    r2 = runner.invoke(cli, ["completion", "install", "--shell", "bash", "--rc-file", str(rc)])
    assert r2.exit_code == 0
    assert rc.read_text().count("_OCTOP_COMPLETE") == line_count_first


def test_completion_in_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert "completion" in result.output


def test_completion_install_handles_utf8_chinese_rc(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """rc 文件含 UTF-8 中文注释时不能在 cp936 Windows 上崩 (#1062)."""
    rc = tmp_path / ".bashrc"
    rc.write_text("# 中文备注：自定义补全\nalias ll='ls -al'\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))

    runner = CliRunner()
    result = runner.invoke(cli, ["completion", "install", "--shell", "bash", "--rc-file", str(rc)])
    assert result.exit_code == 0, result.output
    assert "_OCTOP_COMPLETE" in rc.read_text(encoding="utf-8")


def test_completion_install_handles_legacy_gbk_rc(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """rc 文件是历史 GBK 编码时，幂等检测也不能崩 (#1062)."""
    rc = tmp_path / ".bashrc"
    rc.write_bytes("# 中文备注（GBK）\nalias ll='ls -al'\n".encode("gbk"))
    monkeypatch.setenv("HOME", str(tmp_path))

    runner = CliRunner()
    result = runner.invoke(cli, ["completion", "install", "--shell", "bash", "--rc-file", str(rc)])
    assert result.exit_code == 0, result.output
    text = rc.read_text(encoding="utf-8", errors="replace")
    assert "_OCTOP_COMPLETE" in text
