"""한국관광 데이터랩(한국관광공사)에서 월별 방한 외래관광객 수를 수집한다.

출처: 한국관광 데이터랩 (datalab.visitkorea.or.kr) > 국가별 분석 > 방한여행 현황
API: POST https://datalab.visitkorea.or.kr/visualize/getTempleteData.do (qid=NAT_07_01_001)
     로그인·인증키 불필요 (공개 대시보드가 내부적으로 호출하는 엔드포인트).

실행:
    python collect_data.py
"""
from __future__ import annotations

import csv
import json
import urllib.request
from pathlib import Path

URL = "https://datalab.visitkorea.or.kr/visualize/getTempleteData.do"
QID = "NAT_07_01_001"
START_YM = "201501"
END_YM = "202607"
OUT_PATH = Path(__file__).parent / "data" / "kto_foreign_visitors_monthly.csv"


def fetch() -> list[dict]:
    body = (
        f"natCd=&tarCd=&BASE_YM1={START_YM}&BASE_YM2={END_YM}"
        f"&srchAreaDate=1&qid={QID}"
    ).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["list"]


def main() -> None:
    rows = fetch()
    # 당월(마지막 달)은 집계가 끝나지 않아 0으로 잡히므로 제외한다.
    rows = [r for r in rows if r["BASE_DATE"] <= END_YM and r["PSON_NUM"] > 0]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["base_ym", "foreign_visitors"])
        for r in rows:
            writer.writerow([r["BASE_DATE"], int(r["PSON_NUM"])])

    print(f"저장 완료: {OUT_PATH} ({len(rows)}개월, {rows[0]['BASE_DATE']}~{rows[-1]['BASE_DATE']})")


if __name__ == "__main__":
    main()
