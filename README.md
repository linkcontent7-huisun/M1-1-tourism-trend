# M1-1 · AI 데이터 분석: 데이터 기반 트렌드 분석

**미션: AI 데이터 분석: 데이터 기반 트렌드 분석 (M1-1)** — 시계열 데이터에서 패턴을 찾고 인사이트를 도출하는 개인 미션.

2015.01~2026.07 월별 **방한 외국인 관광객수**(한국관광공사, 139개월)를 분석해 코로나 충격·회복·계절성을 확인했다. [가톨릭 성지순례 앱](https://github.com/linkcontent7-huisun)의 해외 이용자 저변을 가늠하는 참고 자료로 삼기 위해 이 주제를 골랐다.

**결과 리포트: [REPORT.md](REPORT.md)**

## 폴더 구조

```
M1-1-tourism-trend/
|-- data/
|   |-- kto_foreign_visitors_monthly.csv   # 수집된 원본 데이터
|-- images/
|   |-- 01_monthly_trend.png
|   |-- 02_yoy_growth.png
|   |-- 03_seasonality.png
|   |-- 04_decompose.png                  # 보너스: 시계열 분해
|-- collect_data.py                        # 데이터 수집 스크립트
|-- analysis.py                            # 정제·분석·시각화
|-- REPORT.md                              # 분석 리포트 (필수 결과물)
|-- requirements.txt
```

## 실행 방법

```bash
python -m venv .venv
```

Windows:
```bash
.venv/Scripts/activate
```

```bash
pip install -r requirements.txt
python collect_data.py
python analysis.py
```

`collect_data.py`는 로그인·API 키 없이 [한국관광 데이터랩](https://datalab.visitkorea.or.kr) 공개 대시보드가 쓰는 API를 직접 호출해 CSV를 만든다. `analysis.py`는 그 CSV를 읽어 `images/`에 차트 4장을 만들고, 요약 통계를 표준출력에 찍는다(REPORT.md의 수치 출처).

## 개발 환경

- Python 3.10 이상 (개발은 3.13에서 확인)
- 이 컴퓨터의 기본 `python`(3.14)은 `_ctypes` DLL 손상으로 pandas 계열 패키지가 아예 안 열려서, `py -3.13`으로 새 가상환경을 만들어 썼다.
