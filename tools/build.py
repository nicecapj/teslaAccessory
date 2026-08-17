# -*- coding: utf-8 -*-
"""Compose final index.html: template + scraped items + zones + vehicles + photos."""
import base64
import json
import os
import re
import sys
import urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "..", "index.html")

ZONES = [
    ("ext-front",  "ext", "프론트 · 프렁크", "앞 범퍼 하단 송풍구(벌레막이)와 프렁크 안쪽 송풍구"),
    ("ext-wiper",  "ext", "와이퍼 · 윈드실드", "앞유리 하단 와이퍼"),
    ("ext-camera", "ext", "사이드 카메라", "앞 펜더의 방향지시 카메라 렌즈"),
    ("ext-door",   "ext", "도어 (외부)", "도어 핸들 · 엣지 · 실링 부위"),
    ("ext-wheel",  "ext", "휠 · 타이어 · 하부", "머드플랩, 공기압, 잭 포인트"),
    ("ext-roof",   "ext", "루프 글라스", "파노라마 글라스 루프(선쉐이드) · 차박 텐트"),
    ("ext-charge", "ext", "충전 포트", "뒤 왼쪽 테일램프 옆 충전구"),
    ("ext-rear",   "ext", "테일게이트", "트렁크 입구 · 리어 범퍼 상단"),
    ("int-pedal",  "int", "페달", "가속 · 브레이크 페달 커버"),
    ("int-wheel",  "int", "스티어링 · 계기판", "핸들(요크) 교체와 핸들 뒤 계기판"),
    ("int-mirror", "int", "룸미러 주변", "실내 카메라 · 하이패스 부착 위치"),
    ("int-screen", "int", "센터 디스플레이", "15.4인치 중앙 화면과 그 주변"),
    ("int-dash",   "int", "대시보드 · 글로브박스", "조수석 쪽 수납함과 대시보드 위"),
    ("int-console","int", "센터콘솔", "무선충전 패드 · 컵홀더 · 콘솔 수납"),
    ("int-seat",   "int", "시트", "1·2열 시트, 시트 아래 공간, 안전벨트"),
    ("int-door",   "int", "도어 트림 (실내)", "도어 안쪽 킥 부위 · 문턱(실) · 열림 버튼"),
    ("int-floor",  "int", "플로어", "실내 바닥 + 프렁크/트렁크 매트"),
    ("int-rear",   "int", "2열", "뒷좌석 송풍구 · 8인치 스크린 · 팔걸이"),
    ("int-trunk",  "int", "트렁크", "트렁크 바닥 · 양옆 수납 공간"),
    ("int-misc",   "int", "차량 공용", "특정 부위 없이 차에서 쓰는 용품"),
]

MAP = {
    "프론트범퍼,프렁크 송풍구 보호커버": "ext-front",
    "티슬릭스 최신형 오토프렁크": "ext-front",
    "드드득 소리없애는 와이퍼": "ext-wiper",
    "카메라 렌즈 보호커버": "ext-camera",
    "문콕방지 데프콕": "ext-door",
    "도어 실링 스트립 가드": "ext-door",
    "티슬릭스 최신형 오토도어핸들": "ext-door",
    "티슬릭스 최신형 소프트클로징": "ext-door",
    "머드플랩": "ext-wheel",
    "테슬라 공기압 주입기": "ext-wheel",
    "테슬라 리프팅 잭패드": "ext-wheel",
    "티슬릭스 듀얼쉐이드 전동 선쉐이드(양문형)": "ext-roof",
    "티슬리그 싱글쉐이드 전동 선쉐이드(단문형)": "ext-roof",
    "티슬릭스 슬림핏쉐이드 전동 선쉐이드 (스타라이트)": "ext-roof",
    "티슬릭스 모델3&하이랜드 트윈쉐이드 전동선쉐이드": "ext-roof",
    "테슬라 에어 도킹텐트": "ext-roof",
    "테슬라 가정용 220v 충전기": "ext-charge",
    "테일게이트 보호커버": "ext-rear",
    "엑셀,브레이크 페달": "int-pedal",
    "티슬릭스 요크핸들 350mm V2 / V2 플로팅": "int-wheel",
    "티슬릭스 요크핸들 359mm 화이트&블랙&젠그레이": "int-wheel",
    "티슬릭스 요크핸들 350mm 구형": "int-wheel",
    "티슬릭스 사이버트럭 핸들 350mm": "int-wheel",
    "티슬릭스 10.88 터치 디스플레이 계기판": "int-wheel",
    "테슬라 9.6인치 2세대 계기판": "int-wheel",
    "내부카메라 보호커버": "int-mirror",
    "모니터 테두리 보호커버": "int-screen",
    "모니터 강화유리 필름": "int-screen",
    "티슬릭스 스위블 마운트": "int-screen",
    "테슬라 게임기": "int-screen",
    "중앙모니터수납함": "int-screen",
    "거치대 흡착식 볼마운트": "int-screen",
    "C타입 글로브 박스": "int-dash",
    "테슬라 주차번호판": "int-dash",
    "센터콘솔수납함": "int-console",
    "콘솔 충전 도킹스테이션": "int-console",
    "Qi2.2 초고속 맥세이프 충전기": "int-console",
    "중앙제어측면 보호커버": "int-console",
    "8방오 시트커버": "int-seat",
    "폼포나치 가죽시트 코팅": "int-seat",
    "1열 시트아래 수납함": "int-seat",
    "도어 실 가드 카본 8EA": "int-door",
    "킥 도어 커버": "int-door",
    "도어 오픈 레드 스티커": "int-door",
    "2열 도어 비상해제": "int-door",
    "티슬릭스 BSD V2 엠비언트": "int-door",
    "플로어매트 바닥,프렁크.트렁크 11EA": "int-floor",
    "2열 에어벤트커버2EA": "int-rear",
    "2열 송풍구 보호커버": "int-rear",
    "2열 모니터 에어밴트 충전 도킹스테이션": "int-rear",
    "2열 팔걸이 커버": "int-rear",
    "트렁크 로프": "int-trunk",
    "트렁크 사이드 수납함": "int-trunk",
    "트렁크 사이드 보호커버": "int-trunk",
    "테슬라 차량용 청소기 아임반 루미락": "int-misc",
    "테슬라 노래방 마이크": "int-misc",
}

# ---- essentials (user-curated must-buy list) ----
ESSENTIAL = {
    "도어 실 가드 카본 8EA": "도어실가드",
    "엑셀,브레이크 페달": "안전패달",
    "모니터 강화유리 필름": "액정보호필름",
    "모니터 테두리 보호커버": "액정보호가드",
    "2열 에어벤트커버2EA": "시트하단 송풍구 커버",
    "콘솔 충전 도킹스테이션": "콘솔박스 일체형 충전기",
    "센터콘솔수납함": "수납함",
    "프론트범퍼,프렁크 송풍구 보호커버": "앞범퍼 벌레막이 · 프렁크 안쪽 송풍구",
}

# ---- items the user asked for that are not in the Excel ----
NEW_ITEMS = [
    {"name": "RF 하이패스 단말기", "zone": "int-mirror", "essential": "필수",
     "kw": "RF 하이패스 단말기", "cars": ["juniper", "m3", "yl"]},
    {"name": "선쉐이드 (자석식)", "zone": "ext-roof", "essential": "필수",
     "kw": "Tesla Model Y magnetic roof sunshade", "cars": ["juniper", "m3", "yl"]},
    {"name": "안전벨트 연장 클립", "zone": "int-seat", "essential": "필수",
     "kw": "seat belt extender clip", "cars": ["juniper", "m3", "yl"]},
]

# ---- AliExpress equivalent-search keywords for Korean-shop items ----
ALI_EQUIV = {
    "티슬릭스 요크핸들 350mm V2 / V2 플로팅": "Tesla Model Y yoke steering wheel 350mm",
    "티슬릭스 요크핸들 359mm 화이트&블랙&젠그레이": "Tesla Model Y custom steering wheel white grey",
    "티슬릭스 요크핸들 350mm 구형": "Tesla Model Y yoke steering wheel",
    "티슬릭스 사이버트럭 핸들 350mm": "Tesla Model Y Cybertruck style steering wheel",
    "티슬릭스 듀얼쉐이드 전동 선쉐이드(양문형)": "Tesla Model Y Juniper electric roof sunshade automatic",
    "티슬리그 싱글쉐이드 전동 선쉐이드(단문형)": "Tesla Model Y Juniper electric roof sunshade",
    "티슬릭스 슬림핏쉐이드 전동 선쉐이드 (스타라이트)": "Tesla Model Y electric sunshade starlight",
    "티슬릭스 모델3&하이랜드 트윈쉐이드 전동선쉐이드": "Tesla Model 3 Highland electric roof sunshade",
    "티슬릭스 10.88 터치 디스플레이 계기판": "Tesla Model Y Juniper instrument cluster dashboard touch screen",
    "티슬릭스 BSD V2 엠비언트": "Tesla Model Y blind spot BSD display ambient",
    "티슬릭스 스위블 마운트": "Tesla Model Y screen swivel rotating mount",
    "티슬릭스 최신형 오토도어핸들": "Tesla Model Y Juniper electric auto door handle",
    "티슬릭스 최신형 소프트클로징": "Tesla Model Y soft close door kit",
    "티슬릭스 최신형 오토프렁크": "Tesla Model Y Juniper electric auto frunk",
    "테슬라 차량용 청소기 아임반 루미락": "wireless handheld car vacuum cleaner",
    "테슬라 주차번호판": "car parking phone number plate luminous",
    "폼포나치 가죽시트 코팅": "car leather seat care coating kit",
    "Qi2.2 초고속 맥세이프 충전기": "Tesla Model Y Qi2 magsafe wireless car charger",
    "거치대 흡착식 볼마운트": "suction cup ball mount phone holder car screen",
    "문콕방지 데프콕": "car door edge protector guard",
    "드드득 소리없애는 와이퍼": "Tesla Model Y silent wiper blades",
}

GENERIC_ALL_CARS = {
    "테슬라 차량용 청소기 아임반 루미락", "테슬라 주차번호판", "폼포나치 가죽시트 코팅",
    "Qi2.2 초고속 맥세이프 충전기", "거치대 흡착식 볼마운트", "문콕방지 데프콕",
    "테슬라 노래방 마이크", "테슬라 가정용 220v 충전기", "테슬라 에어 도킹텐트",
    "테슬라 공기압 주입기", "테슬라 리프팅 잭패드", "테슬라 게임기",
}
M3_ALSO_NAMES = {
    "티슬릭스 요크핸들 350mm V2 / V2 플로팅", "티슬릭스 요크핸들 359mm 화이트&블랙&젠그레이",
    "티슬릭스 요크핸들 350mm 구형", "티슬릭스 사이버트럭 핸들 350mm",
    "티슬릭스 스위블 마운트", "티슬릭스 BSD V2 엠비언트", "티슬릭스 최신형 소프트클로징",
}


def cars_for(name, title):
    # Excel items target Juniper+YL by default (the sheet is a Juniper & YL list);
    # add Model 3 Highland when the product or Teslix lineup covers it.
    if name == "티슬릭스 모델3&하이랜드 트윈쉐이드 전동선쉐이드":
        return ["m3"]
    if name in GENERIC_ALL_CARS:
        return ["juniper", "m3", "yl"]
    cars = {"juniper", "yl"}
    t = (title or "").lower()
    if "model 3" in t or "highland" in t or "모델3" in name or name in M3_ALSO_NAMES:
        cars.add("m3")
    return sorted(cars)


def search_url(q, korean=False):
    host = "ko.aliexpress.com" if korean else "www.aliexpress.com"
    return ("https://%s/wholesale?SearchText=" % host
            + urllib.parse.quote(q) + "&SortType=price_asc")


def title_query(title):
    q = re.sub(r"[^A-Za-z0-9 ]", " ", title)
    q = re.sub(r"\s+", " ", q).strip()
    return " ".join(q.split(" ")[:10])


def b64file(path, mime="image/jpeg"):
    with open(path, "rb") as f:
        return "data:%s;base64," % mime + base64.b64encode(f.read()).decode()


def load_vehicle_photos():
    """vehicles.json: {vehicleId: {ext: {file, markers:{zone:[x,y]}, credit}, int: {...}}}"""
    vp_path = os.path.join(BASE, "vehicles.json")
    if not os.path.exists(vp_path):
        return {}
    with open(vp_path, encoding="utf-8") as f:
        conf = json.load(f)
    out = {}
    for vid, views in conf.items():
        out[vid] = {}
        for view, v in views.items():
            img = os.path.join(BASE, "commons", v["file"])
            out[vid][view] = {
                "img": b64file(img),
                "markers": v["markers"],
                "credit": v.get("credit", ""),
            }
    return out


def main():
    with open(os.path.join(BASE, "items.json"), encoding="utf-8") as f:
        raw = json.load(f)

    unmapped = [r["name"] for r in raw if r["name"] not in MAP]
    if unmapped:
        print("UNMAPPED:", unmapped)
        sys.exit(1)

    items = []
    for r in raw:
        name = r["name"]
        group = "tune" if r["category"].startswith("튜닝") else "acc"
        it = {
            "id": len(items),
            "name": name,
            "zone": MAP[name],
            "source": r["source"],
            "group": group,
            "url": r["url"],
            "title": r.get("title", ""),
            "thumb": r.get("thumb", ""),
            "photos": r.get("photos", []),
            "cars": cars_for(name, r.get("title", "")),
        }
        if name in ESSENTIAL:
            it["essential"] = ESSENTIAL[name]
        if r["source"] == "ali":
            if r.get("title"):
                it["search"] = search_url(title_query(r["title"]))
            else:
                q = name if "테슬라" in name else "테슬라 모델Y " + name
                it["search"] = search_url(q, korean=True)
        elif name in ALI_EQUIV:
            it["search"] = search_url(ALI_EQUIV[name])
        items.append(it)

    for n in NEW_ITEMS:
        items.append({
            "id": len(items),
            "name": n["name"],
            "zone": n["zone"],
            "source": "ali",
            "group": "acc",
            "url": search_url(n["kw"], korean=("하이패스" in n["kw"])),
            "noProduct": True,
            "title": "",
            "thumb": "",
            "photos": [],
            "cars": n["cars"],
            "essential": n["essential"],
        })

    zones = []
    for num, (zid, view, name, desc) in enumerate(ZONES, 1):
        zones.append({"id": zid, "view": view, "num": num, "name": name, "desc": desc})

    vehicles_photos = load_vehicle_photos()
    vehicles = []
    for vid, label in [("juniper", "모델 Y 주니퍼"), ("m3", "모델 3 하이랜드"), ("yl", "모델 Y L")]:
        vehicles.append({"id": vid, "label": label,
                         "views": vehicles_photos.get(vid, {})})

    data = {"zones": zones, "items": items, "vehicles": vehicles}
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    with open(os.path.join(BASE, "template.html"), encoding="utf-8") as f:
        tpl = f.read()
    html = tpl.replace("/*__DATA__*/", payload, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    ess = sum(1 for i in items if i.get("essential"))
    ph = sum(1 for i in items if i.get("photos"))
    print("wrote %s: %d bytes, %d items (%d essential, %d with gallery), %d zones, vehicles with photos: %s"
          % (OUT, len(html), len(items), ess, ph, len(zones),
             [v["id"] for v in vehicles if v["views"]]))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
