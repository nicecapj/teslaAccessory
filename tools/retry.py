# -*- coding: utf-8 -*-
"""Retry failed AliExpress items with slower pacing."""
import json
import random
import sys
import time

import scrape

OUT = scrape.OUT


def main():
    with open(OUT, encoding="utf-8") as f:
        items = json.load(f)
    fails = [i for i, it in enumerate(items)
             if it["source"] == "ali" and (not it["title"] or not it.get("photos"))]
    print("retrying", len(fails), "ali items")
    for n, idx in enumerate(fails):
        it = items[idx]
        print("[%d/%d] %s" % (n + 1, len(fails), it["name"]))
        for attempt in range(3):
            res = scrape.enrich({"name": it["name"], "url": it["url"],
                                 "category": it["category"]})
            if res["title"]:
                items[idx] = res
                break
            print("    attempt %d empty, backing off" % (attempt + 1))
            time.sleep(8 + random.random() * 6)
        time.sleep(3 + random.random() * 3)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    ok_t = sum(1 for r in items if r["title"])
    ok_i = sum(1 for r in items if r["thumb"])
    print("now titles: %d, thumbs: %d of %d" % (ok_t, ok_i, len(items)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
