#!/usr/bin/env python3
import json
import sys
import urllib.request
from pathlib import Path

REPO_JSON = Path(__file__).resolve().parents[2] / "repo.json"

FIELDS = ["title", "author", "version", "description", "details", "license", "changelog"]


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "ouncebrew-repo-updater"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    data = json.loads(REPO_JSON.read_text(encoding="utf-8"))
    packages = data.get("packages", [])
    changed = False

    for pkg in packages:
        direct_url = (pkg.get("direct_url") or pkg.get("url") or "").rstrip("/")
        if not pkg.get("file") or not direct_url:
            continue

        pkg_json_url = direct_url + "/package.json"
        try:
            remote = fetch_json(pkg_json_url)
        except Exception as e:
            print(f"[skip] {pkg.get('name', '?')}: {pkg_json_url} ({e})")
            continue

        if not isinstance(remote, dict):
            print(f"[skip] {pkg.get('name', '?')}: package.json is not an object")
            continue

        for field in FIELDS:
            value = remote.get(field)
            if isinstance(value, str) and value != pkg.get(field):
                print(f"[update] {pkg.get('name', '?')}.{field}")
                pkg[field] = value
                changed = True

    if changed:
        REPO_JSON.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        print("repo.json updated")
    else:
        print("no changes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
