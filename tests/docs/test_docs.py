"""Docs stay in lockstep with the gallery catalogue.

Every gallery page (except Typography, which is covered by the architecture
doc) must have a component doc at ``docs/components/<slug>.md``, and every
component doc must be linked from ``docs/README.md``. Adding a widget
therefore fails this test until its doc exists — see the "Adding a widget"
recipe in the top-level README.
"""

from __future__ import annotations

from pathlib import Path

from material_qt.gallery.gallery import COMPONENT_META

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / "docs"
COMPONENTS_DIR = DOCS / "components"

# The type scale has no widget; it is documented in docs/architecture.md.
NON_COMPONENT_PAGES = {"Typography"}


def _slug(page: str) -> str:
    return page.lower().replace(" ", "-")


def _expected_docs() -> dict[str, str]:
    return {
        page: f"{_slug(page)}.md"
        for page in COMPONENT_META
        if page not in NON_COMPONENT_PAGES
    }


def test_every_gallery_page_has_a_component_doc():
    missing = {
        page: name
        for page, name in _expected_docs().items()
        if not (COMPONENTS_DIR / name).is_file()
    }
    assert not missing, f"gallery pages without a doc: {missing}"


def test_no_orphan_component_docs():
    expected = set(_expected_docs().values())
    actual = {p.name for p in COMPONENTS_DIR.glob("*.md")}
    assert actual - expected == set(), f"docs without a gallery page: {actual - expected}"


def test_index_links_every_component_doc():
    index = (DOCS / "README.md").read_text(encoding="utf-8")
    unlinked = [
        name
        for name in _expected_docs().values()
        if f"(./components/{name})" not in index
    ]
    assert not unlinked, f"docs/README.md does not link: {unlinked}"
