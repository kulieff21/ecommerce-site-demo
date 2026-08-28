#!/usr/bin/env python3
"""Proves audit.py actually catches things.

A checklist that only ever prints ticks is indistinguishable from a checklist that
does not run. This copies the site to a temporary directory, breaks one thing at a
time in a way we have really found on client sites, and asserts the audit fails and
says why.

    python3 tools/audit_selftest.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sub(path: str, old: str, new: str, count: int = 1):
    """Replace literal text in one file of the copied site."""
    def apply(root: Path) -> None:
        f = root / path
        text = f.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"self-test is stale: {old[:60]!r} not in {path}")
        f.write_text(text.replace(old, new, count), encoding="utf-8")
    return apply


def regex_sub(path: str, pattern: str, new: str):
    def apply(root: Path) -> None:
        f = root / path
        text = f.read_text(encoding="utf-8")
        text2, n = re.subn(pattern, new, text, count=1)
        if not n:
            raise AssertionError(f"self-test is stale: /{pattern}/ not in {path}")
        f.write_text(text2, encoding="utf-8")
    return apply


# (name, mutation, the words the audit must say about it)
FAULTS = [
    ("no lang attribute",
     sub("magaza.html", '<html lang="az"', "<html"), "lang"),
    ("empty alt on a product image",
     regex_sub("magaza.html", r'alt="Zərrə [^"]+"', 'alt=""'), "empty alt"),
    ("no h1",
     regex_sub("terkib.html", r"<h1>.*?</h1>", ""), "<h1>"),
    ("h1 is just the brand name",
     regex_sub("terkib.html", r"<h1>.*?</h1>", "<h1>Zərrə</h1>"), "brand name"),
    ("two pages sharing one title",
     regex_sub("qaytarma.html", r"<title>.*?</title>",
               "<title>Çatdırılma və ödəniş | Zərrə</title>"), "copy of"),
    ("og:image pointing at a missing file",
     sub("index.html", "assets/img/og-cover.png", "assets/img/kohne-banner.png"),
     "does not exist"),
    ("mail: instead of mailto:",
     sub("elaqe.html", 'href="mailto:', 'href="mail:'), "nothing will open"),
    ("a link to a page that was deleted",
     sub("index.html", 'href="magaza.html"', 'href="mehsullar.html"'),
     "does not exist"),
    ("lorem ipsum left in the copy",
     sub("haqqimizda.html", "<h2>Necə başladı</h2>", "<h2>Lorem ipsum dolor</h2>"),
     "placeholder"),
    ("a CDN stylesheet",
     sub("index.html", '<link rel="stylesheet" href="assets/css/style.css" />',
         '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/x/y.css" />'),
     "external stylesheet"),
    ("the shown price disagreeing with the schema offer",
     sub("mehsul-gulab-toniki.html", '"price": "19.90"', '"price": "17.90"'),
     "schema offer says"),
    ("a sitemap listing a page that 404s",
     sub("sitemap.xml", "<loc>https://kulieff21.github.io/ecommerce-site-demo/terkib.html</loc>",
         "<loc>https://kulieff21.github.io/ecommerce-site-demo/blog.html</loc>"),
     "does not exist"),
    ("body text dropped below AA contrast",
     sub("assets/css/style.css", "--ink-3:    #5c6558;", "--ink-3:    #9aa394;"),
     "below 4.5"),
    ("a catalogue built by script rather than shipped as markup",
     regex_sub("magaza.html", r'<ul class="grid">.*?</ul>', '<ul class="grid"></ul>'),
     "must not be built by script"),
    ("aggregateRating with no review count",
     sub("mehsul-nar-c-serumu.html", '"reviewCount": "63",', ""), "reviewCount"),
]


def run_audit(root: Path) -> str:
    proc = subprocess.run([sys.executable, str(root / "tools" / "audit.py")],
                          capture_output=True, text=True)
    return proc.stdout + proc.stderr, proc.returncode


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        clean = Path(tmp) / "clean"
        shutil.copytree(ROOT, clean, ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "*.pyc"))

        out, code = run_audit(clean)
        if code != 0:
            print("the untouched site does not pass its own audit:")
            print(out)
            return 1
        print("  \033[32m✓\033[0m untouched site passes")

        missed = 0
        for name, mutate, expect in FAULTS:
            work = Path(tmp) / "work"
            shutil.rmtree(work, ignore_errors=True)
            shutil.copytree(clean, work)
            mutate(work)
            out, code = run_audit(work)
            caught = code != 0 and expect in out
            mark = "\033[32m✓\033[0m" if caught else "\033[31m✗\033[0m"
            print(f"  {mark} caught: {name}")
            if not caught:
                missed += 1
                print(f"      expected the report to mention {expect!r}; it did not")

    print()
    if missed:
        print(f"{missed} of {len(FAULTS)} injected faults slipped through")
        return 1
    print(f"all {len(FAULTS)} injected faults were caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
