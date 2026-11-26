"""Gemeinsame, offline eingebettete Schüleroberfläche."""
from pathlib import Path


def einbetten(page):
    src = Path(__file__).resolve().parents[1] / "module" / "arbeitsplatz"
    style = (src / "platz.css").read_text()
    script = "\n".join((src / name).read_text() for name in ("gesundheit.js", "entwurf.js", "platz.js"))
    position = page.rindex("</style>") + len("</style>")
    page = page[:position] + "<style>" + style + "</style>" + page[position:]
    return page.replace("<script", "<script>" + script + "</script><script", 1)
