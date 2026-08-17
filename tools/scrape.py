# -*- coding: utf-8 -*-
"""Collect og:title / og:image / price(if any) for every link in the Excel file."""
import base64
import io
import os
import json
import re
import sys
import time

import openpyxl
import requests
from PIL import Image

XLSX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "테슬라 주니퍼 & YL 악세사리 정리 엑셀.xlsx")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "items.json")

BOT_UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

sess = requests.Session()


def parse_excel():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    ws = wb.worksheets[0]
    items, category = [], None
    for row in ws.iter_rows(values_only=True):
        name, link = row[1], row[2]
        if name and not link:
            category = str(name).strip()
            continue
        if name and link and str(name).strip() != "품목":
            items.append({"name": str(name).strip(), "url": str(link).strip(),
                          "category": category or ""})
    return items


def og(html, prop):
    m = re.search(r'<meta[^>]+property=["\']og:%s["\'][^>]+content=["\']([^"\']*)' % prop, html)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:%s' % prop, html)
    return m.group(1).strip() if m else ""


def find_price(html):
    # JSON-LD offers
    for m in re.finditer(r'"lowPrice"\s*:\s*"?([0-9][0-9,.]*)', html):
        return m.group(1)
    for m in re.finditer(r'"price"\s*:\s*"?([0-9][0-9,.]*)', html):
        return m.group(1)
    # naver smartstore embedded state
    m = re.search(r'"discountedSalePrice"\s*:\s*([0-9]+)', html)
    if m:
        return m.group(1)
    m = re.search(r'"salePrice"\s*:\s*([0-9]+)', html)
    if m:
        return m.group(1)
    return ""


def fetch(url, ua, timeout=30):
    return sess.get(url, headers={"User-Agent": ua, "Accept-Language": "ko-KR,ko;q=0.9"},
                    timeout=timeout, allow_redirects=True)


def img_b64(img_url, ref, size, quality):
    try:
        r = sess.get(img_url, headers={"User-Agent": BROWSER_UA, "Referer": ref}, timeout=30)
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert("RGB")
        im.thumbnail((size, size))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print("    img fail:", e)
        return ""


def gallery_urls(html, og_img):
    urls = []
    m = re.search(r'"imagePathList"\s*:\s*\[([^\]]*)\]', html)
    if m:
        urls = re.findall(r'"(https?:[^"]+)"', m.group(1))
    if not urls:
        urls = re.findall(r'"(https://ae-pic[^"]+?\.(?:jpg|jpeg|png|webp))"', html)
    if og_img:
        og = og_img if not og_img.startswith("//") else "https:" + og_img
        if og not in urls:
            urls.insert(0, og)
    seen, out = set(), []
    for u in urls:
        base = u.split("?")[0]
        if base in seen:
            continue
        seen.add(base)
        out.append(u)
    return out[:5]


def enrich(item):
    url = item["url"]
    out = dict(item, title="", image="", price="", finalUrl=url, source="", photos=[])
    html = ""
    try:
        if "aliexpress" in url:
            out["source"] = "ali"
            r = fetch(url, BROWSER_UA)
            m = re.search(r"/item/(\d+)\.html", r.url)
            if not m:
                m = re.search(r"/item/(\d+)\.html", url)
            if m:
                pid = m.group(1)
                out["productId"] = pid
                r2 = fetch("https://www.aliexpress.com/item/%s.html" % pid, BOT_UA)
                html = r2.text
                title = og(html, "title")
                out["title"] = re.sub(r"\s*-\s*AliExpress.*$", "", title)
                out["image"] = og(html, "image")
                out["price"] = find_price(html)
        else:
            out["source"] = "naver"
            r = fetch(url, BROWSER_UA)
            html = r.text
            out["finalUrl"] = r.url
            out["title"] = og(html, "title")
            out["image"] = og(html, "image")
            out["price"] = find_price(html)
            desc = og(html, "description")
            if not out["price"]:
                m = re.search(r"([0-9][0-9,]{3,})\s*원", desc)
                if m:
                    out["price"] = m.group(1).replace(",", "")
    except Exception as e:
        print("    FAIL:", e)
    if out["image"]:
        img = out["image"]
        if img.startswith("//"):
            img = "https:" + img
        out["thumb"] = img_b64(img, out["finalUrl"], 176, 68)
    else:
        out["thumb"] = ""
    if html and out["source"] == "ali":
        for u in gallery_urls(html, out.get("image", "")):
            if u.startswith("//"):
                u = "https:" + u
            b = img_b64(u, out["finalUrl"], 340, 70)
            if b:
                out["photos"].append(b)
            time.sleep(0.3)
    out.pop("image", None)
    return out


def main():
    items = parse_excel()
    print("total items:", len(items))
    results = []
    for i, it in enumerate(items):
        print("[%d/%d] %s" % (i + 1, len(items), it["name"]))
        results.append(enrich(it))
        time.sleep(0.8)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    ok_t = sum(1 for r in results if r["title"])
    ok_i = sum(1 for r in results if r["thumb"])
    ok_p = sum(1 for r in results if r["price"])
    print("titles: %d, thumbs: %d, prices: %d" % (ok_t, ok_i, ok_p))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
