"""방한 외래관광객 월별 시계열 분석.

데이터: data/kto_foreign_visitors_monthly.csv (collect_data.py로 수집)
출력: images/*.png, 그리고 REPORT.md 작성에 쓸 요약 수치를 표준출력으로 찍는다.

실행:
    python analysis.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "kto_foreign_visitors_monthly.csv"
IMG_DIR = BASE_DIR / "images"
IMG_DIR.mkdir(exist_ok=True)

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, dtype={"base_ym": str})
    df["date"] = pd.to_datetime(df["base_ym"], format="%Y%m")
    df = df.sort_values("date").reset_index(drop=True)
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    return df


def fmt_million(x, _pos):
    return f"{x / 1e6:.1f}M" if x >= 1e6 else f"{int(x):,}"


def chart_trend(df: pd.DataFrame) -> None:
    df = df.copy()
    df["ma12"] = df["foreign_visitors"].rolling(12).mean()

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(df["date"], df["foreign_visitors"], color="#8ecae6", linewidth=1.2, label="월별 방한 외래관광객수")
    ax.plot(df["date"], df["ma12"], color="#023047", linewidth=2.2, label="12개월 이동평균")
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_million))
    ax.set_title("월별 방한 외래관광객수 추이 (2015.01 ~ 2026.07, 단위: 명)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "01_monthly_trend.png", dpi=140)
    plt.close(fig)


def chart_yoy(df: pd.DataFrame) -> pd.Series:
    df = df.copy()
    df["yoy"] = df["foreign_visitors"].pct_change(12) * 100

    fig, ax = plt.subplots(figsize=(11, 5))
    colors = np.where(df["yoy"] >= 0, "#2a9d8f", "#e76f51")
    ax.bar(df["date"], df["yoy"], color=colors, width=20)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("전년동월대비 증감률(YoY, %)")
    ax.set_ylabel("%")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "02_yoy_growth.png", dpi=140)
    plt.close(fig)
    return df["yoy"]


def chart_seasonality(df: pd.DataFrame) -> pd.Series:
    # 코로나 충격 구간(2020.03~2022.12)은 계절성이 아니라 이례적 이상치이므로 제외한다.
    normal = df[~df["date"].between("2020-03-01", "2022-12-31")]
    monthly_avg = normal.groupby("month")["foreign_visitors"].mean()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(monthly_avg.index, monthly_avg.values, color="#f4a261")
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("월")
    ax.set_ylabel("평균 방문자수", rotation=0, ha="right", va="center")
    ax.set_title("월별 평균 방한 외래관광객수 (코로나 충격 구간 제외)")
    ax.yaxis.set_major_formatter(FuncFormatter(fmt_million))
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "03_seasonality.png", dpi=140)
    plt.close(fig)
    return monthly_avg


def chart_decompose(df: pd.DataFrame) -> None:
    from statsmodels.tsa.seasonal import seasonal_decompose

    s = df.set_index("date")["foreign_visitors"]
    result = seasonal_decompose(s, model="additive", period=12, extrapolate_trend="period")

    fig, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
    for ax, series, name in zip(
        axes,
        [s, result.trend, result.seasonal, result.resid],
        ["원본", "추세(Trend)", "계절성(Seasonal)", "잔차(Residual)"],
    ):
        ax.plot(series.index, series.values, linewidth=1.2)
        ax.set_ylabel(name, rotation=0, ha="right", va="center")
        ax.grid(alpha=0.3)
    axes[0].set_title("시계열 분해: 방한 외래관광객수 (추세/계절성/잔차)")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "04_decompose.png", dpi=140)
    plt.close(fig)


def main() -> None:
    df = load()

    print(f"데이터 기간: {df['base_ym'].iloc[0]} ~ {df['base_ym'].iloc[-1]} ({len(df)}개월)")
    print(f"결측치: {df['foreign_visitors'].isna().sum()}건")
    print(f"전체 평균: {df['foreign_visitors'].mean():,.0f}명, 표준편차: {df['foreign_visitors'].std():,.0f}명")

    pre_covid = df[df["date"] < "2020-01-01"]["foreign_visitors"]
    trough = df.loc[df["foreign_visitors"].idxmin()]
    print(f"\n코로나 이전(2015~2019) 월평균: {pre_covid.mean():,.0f}명")
    print(f"역대 최저월: {trough['base_ym']} ({trough['foreign_visitors']:,.0f}명)")

    recovered = df[(df["date"] >= "2022-01-01") & (df["foreign_visitors"] >= pre_covid.mean())]
    if len(recovered):
        print(f"코로나 이전 평균 수준을 처음 회복한 달: {recovered.iloc[0]['base_ym']}")

    chart_trend(df)
    yoy = chart_yoy(df)
    print(f"\nYoY 최저치: {yoy.min():.1f}% ({df.loc[yoy.idxmin(), 'base_ym']})")
    print(f"YoY 최고치: {yoy.max():.1f}% ({df.loc[yoy.idxmax(), 'base_ym']})")

    monthly_avg = chart_seasonality(df)
    peak_month = monthly_avg.idxmax()
    low_month = monthly_avg.idxmin()
    print(f"\n평균 방문자수가 가장 많은 달: {peak_month}월 ({monthly_avg[peak_month]:,.0f}명)")
    print(f"평균 방문자수가 가장 적은 달: {low_month}월 ({monthly_avg[low_month]:,.0f}명)")

    chart_decompose(df)
    print("\n차트 저장 완료: images/01_monthly_trend.png, 02_yoy_growth.png, 03_seasonality.png, 04_decompose.png")


if __name__ == "__main__":
    main()
