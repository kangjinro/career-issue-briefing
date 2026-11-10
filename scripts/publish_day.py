# -*- coding: utf-8 -*-
"""브리핑 JSON 파일을 data/ 에 넣고 data/index.json 을 갱신한 뒤 깃허브에 올린다.

사용법:
  python scripts/publish_day.py 새브리핑.json [--no-push]
JSON 형식은 data/2026-11-09.json 과 같다 (date, dow, range, anniv, bk_note, news[5], yt[]).
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
GIT = r"C:\Program Files\Git\cmd\git.exe"


def check(d):
    for k in ("date", "dow", "anniv", "news"):
        if k not in d:
            raise SystemExit(f"필수 항목 없음: {k}")
    for it in d["news"] + d.get("yt", []):
        for k in ("t", "url", "sum", "q", "d", "sub", "cat"):
            if not it.get(k):
                raise SystemExit(f"항목 '{it.get('t')}' 에 {k} 없음")


def rebuild_index():
    dates = sorted(f[:-5] for f in os.listdir(DATA) if f[:4].isdigit() and f.endswith(".json"))
    with open(os.path.join(DATA, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"dates": dates}, f, ensure_ascii=False, indent=1)
    return dates


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        with open(args[0], encoding="utf-8") as f:
            d = json.load(f)
        check(d)
        with open(os.path.join(DATA, d["date"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        msg = f"브리핑 {d['date']} 추가"
    else:
        msg = "브리핑 목록 갱신"
    dates = rebuild_index()
    print("dates:", dates[-3:], "총", len(dates))
    if "--no-push" in sys.argv:
        return
    run = lambda *a: subprocess.run([GIT, "-C", ROOT, *a], check=True)
    run("add", "-A")
    if subprocess.run([GIT, "-C", ROOT, "diff", "--cached", "--quiet"]).returncode == 0:
        print("변경 없음")
        return
    run("commit", "-m", msg)
    run("push")
    print("게시 완료")


if __name__ == "__main__":
    main()
