# 주니퍼 악세사리 맵 (Tesla Accessory Map)

테슬라 **모델 Y 주니퍼 / 모델 3 하이랜드 / 모델 Y L** 악세사리 73종을
실제 차량 사진 위의 부위별 마커로 확인하고, 알리익스프레스 최저가를 찾아 기록하는
단일 파일 정적 웹앱입니다.

- 차량 사진 위 번호 마커 클릭 → 해당 부위 악세사리만 필터
- 차종 탭(주니퍼/모델3/YL)별 호환 아이템 필터
- ★ 필수 장착 목록 뱃지·필터
- 아이템별: 상품 링크, 알리 최저가 검색(낮은 가격순), 가격 입력(localStorage 저장), 예산 합계
- 티슬릭스(네이버) 튜닝 제품 → 알리 동일 제품 검색 링크

## 구조

```
index.html                  # 완성된 웹앱 (이것만 배포하면 됨)
deploy/                     # Cloud Run 배포용 (Dockerfile + nginx)
tools/                      # 재생성 파이프라인
  scrape.py                 #   엑셀의 링크에서 상품명/썸네일/갤러리 수집 → items.json
  retry.py                  #   수집 실패분 재시도
  build.py                  #   items.json + template.html + vehicles.json → ../index.html
  template.html             #   앱 본체 템플릿 (/*__DATA__*/ 자리에 데이터 주입)
  vehicles.json             #   차종별 사진 파일과 마커 좌표(%)
  items.json                #   수집된 아이템 데이터
  commons/                  #   차량 사진 (Wikimedia Commons, CC BY-SA 4.0 / CC0)
```

## 다시 빌드하기

```bash
pip install openpyxl requests pillow
python tools/scrape.py   # (선택) 상품 데이터 재수집 — 원본 엑셀 필요(저장소 미포함), AliExpress 봇 차단 주의
python tools/build.py    # index.html 재생성
```

## 배포

### Cloud Run (권장)
```bash
python tools/build.py --adsense --out deploy/index.html
cd deploy
gcloud run deploy tesla-accessory-map --source . --region asia-northeast3 --allow-unauthenticated
```

### jedragon.kr (VM nginx)
`https://jedragon.kr` 은 이 프로젝트의 Compute Engine VM(us-east1, 기존 nginx에 서버 블록 추가)에서
서빙합니다. 페이지 갱신:
```bash
python tools/build.py --adsense --out deploy/index.html
gcloud compute scp deploy/index.html instance-20251228-162235:/tmp/jedragon-index.html --zone us-east1-c
gcloud compute ssh instance-20251228-162235 --zone us-east1-c --command "sudo mv /tmp/jedragon-index.html /var/www/jedragon/index.html"
```
HTTPS는 Let's Encrypt(certbot 자동 갱신), ads.txt 포함.

### GitHub Pages
저장소 Settings → Pages → Deploy from branch → `main` / root 를 선택하면
`https://nicecapj.github.io/teslaAccessory/` 로 서빙됩니다 (index.html이 루트에 있음).

## 사진 출처

차량 사진은 Wikimedia Commons (주니퍼: Damian B Oh·Ethan Llamas CC BY-SA 4.0,
YL: JustAnotherCarDesigner CC0·Ethan Llamas CC BY-SA 4.0,
모델3: Mliu92 CC BY-SA 4.0·Mpelas199 CC0). 상품 썸네일은 각 판매 페이지에서 가져왔습니다.
