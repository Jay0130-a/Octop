"""A SKILL.md saved with a UTF-8 BOM keeps its frontmatter."""

from __future__ import annotations

from octop.api.routers.skills import _parse_frontmatter


def test_bom_prefixed_skill_md_keeps_its_frontmatter() -> None:
    """The skills router reads user-authored SKILL.md files.

    Windows editors (Notepad, and the Windows PowerShell 5.1
    ``Set-Content -Encoding UTF8`` switch) prepend a BOM. A plain
    ``startswith("---\\n")`` check then reports "no frontmatter" and loses the
    name/description the skill editor and listing depend on.
    """
    text = "\ufeff---\nname: demo\ndescription: Demo skill\n---\n# Body\n"

    meta, body = _parse_frontmatter(text)

    assert meta == {"name": "demo", "description": "Demo skill"}
    assert body.startswith("# Body")
    assert "\ufeff" not in body


def test_plain_skill_md_is_unaffected() -> None:
    meta, body = _parse_frontmatter("---\nname: demo\n---\n# Body\n")
    assert meta == {"name": "demo"}
    assert body.startswith("# Body")
