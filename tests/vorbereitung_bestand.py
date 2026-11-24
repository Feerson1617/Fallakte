"""Prüft die beiden ausgelieferten UB-Module beim Bau der separaten Vorbereitung."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile

from lxml.html import fromstring


ROOT = Path(__file__).resolve().parents[1]
JOINT = "d24308f4a0eca8ed39f0f75b04b890b78bcc8332"
FIRST = "8b50305b6d98a19e1771a842ea9917c67282ecb9"
# Gemeinsame Auslieferung aus Actions-Lauf 45345951346. Der 02.12. ist
# zusätzlich am eigenständigen HTML der Referenz 8b50305 abgeglichen.
MODULES = {
    "02": "6f969460d00005fefd27fed985b6c95b7f1203bee0a9e4d72fcaaf9aea605cb2",
    "08": "0606de0b43bcbe4ef28b9fb0b036ee6ae1a8179d855b6af47baa5246438f1d2f",
}
DELIVERY = {
    "Fallakte.html": "254e5d06cb9190250bacc63fa9eea6c118846b45ce2b305ffa640d766f44a820",
    "Fallakte-SCORM12.zip": "fce49c6079d4fa791640c5480f9b28aefdccaa582a6d20922601389a12610424",
}


def verify(directory):
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", "-z", JOINT, "--",
         "02-12.html", "index.html", "app", "assets", "data", "material",
         "module", "scorm", "scripts", "tagesauswahl"], cwd=ROOT,
    ).decode().rstrip("\0").split("\0")
    # Nur die damaligen Produktionsdateien vergleichen. Die neue Anwendung hat eigene Pfade.
    subprocess.run(["git", "diff", "--exit-code", JOINT, "--", *paths],
                   cwd=ROOT, check=True)
    for name, expected in DELIVERY.items():
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        assert actual == expected, f"{name}: erwartet {expected}, erhalten {actual}"
    html = (directory / "Fallakte.html").read_bytes()
    with ZipFile(directory / "Fallakte-SCORM12.zip") as package:
        assert package.testzip() is None
        assert package.read("index.html") == html, "SCORM und Offline-HTML weichen voneinander ab"
    document = fromstring(html)
    for day, expected in MODULES.items():
        script = document.get_element_by_id("modul-" + day)
        module = base64.b64decode(script.text, validate=True)
        assert hashlib.sha256(module).hexdigest() == expected, f"Unterrichtstag {day}.12. verändert"
    return {"gemeinsame_referenz": JOINT, "referenz_02": FIRST, "dateien_sha256": DELIVERY,
            "module_sha256": MODULES, "verglichene_quellpfade": len(paths)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("auslieferung", type=Path, help="Verzeichnis mit Fallakte.html und Fallakte-SCORM12.zip")
    print(json.dumps(verify(parser.parse_args().auslieferung), ensure_ascii=False, indent=2))
