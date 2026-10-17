import numpy as np
import pandas as pd

# 2014-01부터 2026-06까지 150개월 시계열 생성
dates = pd.date_range(start="2014-01-01", end="2026-06-01", freq="MS")
n_months = len(dates)  # 150개

# 1. 한국은행 기준금리 (BOK Base Rate, %)
# 2014.01: 2.50% -> 2014.08: 2.25% -> 2014.10: 2.00% -> 2015.03: 1.75% -> 2015.06: 1.50%
# 2016.06: 1.25% -> 2017.11: 1.50% -> 2018.11: 1.75% -> 2019.07: 1.50% -> 2019.10: 1.25%
# 2020.03: 0.75% -> 2020.05: 0.50% (초저금리) -> 2021.08: 0.75% -> 2021.11: 1.00%
# 2022.01: 1.25% -> 2022.04: 1.50% -> 2022.05: 1.75% -> 2022.07: 2.25% (빅스텝) -> 2022.08: 2.50% -> 2022.10: 3.00% (빅스텝) -> 2022.11: 3.25%
# 2023.01: 3.50% (동결 지속)
# 2024.10: 3.25% -> 2024.11: 3.00%
# 2025~2026년 (사용자 제시 배경: 2025년부터 거시/환율 압력으로 금리 재상승 국면)
# 2025.04: 3.25% -> 2025.08: 3.50% -> 2025.11: 3.75% -> 2026: 3.75% ~ 4.00%

bok_base_rate = []
for d in dates:
    ym = d.strftime("%Y-%m")
    if ym < "2014-08":
        r = 2.50
    elif ym < "2014-10":
        r = 2.25
    elif ym < "2015-03":
        r = 2.00
    elif ym < "2015-06":
        r = 1.75
    elif ym < "2016-06":
        r = 1.50
    elif ym < "2017-11":
        r = 1.25
    elif ym < "2018-11":
        r = 1.50
    elif ym < "2019-07":
        r = 1.75
    elif ym < "2019-10":
        r = 1.50
    elif ym < "2020-03":
        r = 1.25
    elif ym < "2020-05":
        r = 0.75
    elif ym < "2021-08":
        r = 0.50
    elif ym < "2021-11":
        r = 0.75
    elif ym < "2022-01":
        r = 1.00
    elif ym < "2022-04":
        r = 1.25
    elif ym < "2022-05":
        r = 1.50
    elif ym < "2022-07":
        r = 1.75
    elif ym < "2022-08":
        r = 2.25
    elif ym < "2022-10":
        r = 2.50
    elif ym < "2022-11":
        r = 3.00
    elif ym < "2023-01":
        r = 3.25
    elif ym < "2024-10":
        r = 3.50
    elif ym < "2024-11":
        r = 3.25
    elif ym < "2025-04":
        r = 3.00
    elif ym < "2025-08":
        r = 3.25
    elif ym < "2025-11":
        r = 3.50
    elif ym < "2026-03":
        r = 3.75
    else:
        r = 4.00
    bok_base_rate.append(r)

# 주택담보대출금리: 기준금리 + 가산금리(스프레드 약 1.2% ~ 1.7%)
np.random.seed(42)
mortgage_rates = []
for i, r in enumerate(bok_base_rate):
    # 가산금리와 시장금리 스프레드 반영
    spread = 1.25 + 0.3 * np.sin(i / 10.0) + np.random.normal(0, 0.04)
    if dates[i].strftime("%Y-%m") >= "2022-07" and dates[i].strftime("%Y-%m") <= "2022-12":
        spread += 0.5  # 레고랜드 사태 등 채권시장 신용경색 스프레드 급등
    elif dates[i].strftime("%Y-%m") >= "2024-08":
        spread += 0.4  # 스트레스 DSR 및 은행권 자율 대출규제 가산금리 인상
    mortgage_rates.append(round(r + spread, 2))

df_bok = pd.DataFrame({
    "date": dates.strftime("%Y-%m"),
    "bok_base_rate": bok_base_rate,
    "mortgage_loan_rate": mortgage_rates
})
df_bok.to_csv("data/bok_interest_rates.csv", index=False)

# 2. 미국 연준 기준금리 및 원/달러 환율
# Fed Funds Rate:
# 2014~2015: 0.12% -> 2015.12: 0.37% -> 2016~2018 점진적 인상(2.38%) -> 2019 인하(1.6%)
# 2020.03: 0.12% (제로금리) -> 2022.03 인상 시작 -> 2022 자이언트스텝(4.5%) -> 2023: 5.33%
# 2024 말 소폭 인하 -> 2025 재반등 및 고금리 장기화(Higher for longer)
fed_rates = []
fx_rates = []
for i, d in enumerate(dates):
    ym = d.strftime("%Y-%m")
    if ym < "2015-12":
        f = 0.12
        fx = 1050 + i * 2.0 + np.random.normal(0, 8)
    elif ym < "2016-12":
        f = 0.38
        fx = 1150 + np.random.normal(0, 10)
    elif ym < "2017-12":
        f = 1.15
        fx = 1130 + np.random.normal(0, 10)
    elif ym < "2018-12":
        f = 2.18
        fx = 1115 + np.random.normal(0, 10)
    elif ym < "2019-07":
        f = 2.40
        fx = 1160 + np.random.normal(0, 10)
    elif ym < "2020-03":
        f = 1.60
        fx = 1190 + np.random.normal(0, 12)
    elif ym < "2022-03":
        f = 0.12
        fx = 1150 + (i - 74) * 2.5 + np.random.normal(0, 10)
    elif ym < "2022-06":
        f = 0.88
        fx = 1250 + np.random.normal(0, 15)
    elif ym < "2022-09":
        f = 2.56
        fx = 1350 + np.random.normal(0, 18)
    elif ym < "2022-12":
        f = 3.88
        fx = 1420 + np.random.normal(0, 15)
    elif ym < "2023-08":
        f = 5.08
        fx = 1310 + np.random.normal(0, 15)
    elif ym < "2024-09":
        f = 5.33
        fx = 1350 + np.random.normal(0, 15)
    elif ym < "2025-03":
        f = 4.88
        fx = 1380 + np.random.normal(0, 15)
    elif ym < "2025-10":
        f = 5.12
        fx = 1420 + np.random.normal(0, 15)
    else:
        f = 5.38
        fx = 1450 + (i - 140) * 5 + np.random.normal(0, 12)
    fed_rates.append(round(f, 2))
    fx_rates.append(round(fx, 1))

df_fed_fx = pd.DataFrame({
    "date": dates.strftime("%Y-%m"),
    "fed_funds_rate": fed_rates,
    "krw_usd_rate": fx_rates
})
df_fed_fx.to_csv("data/us_fed_rate_and_fx.csv", index=False)

# 3. 서울 아파트 매매가격지수 및 거래량
# 한국부동산원 서울 아파트 매매가격지수 (2021.06 = 100 기준)
# 2014년 초: 약 68 ~ 70
# 2017년 말: 약 80
# 2019년 말: 약 88
# 2021년 06월: 100
# 2021년 11월: 정점 104.3
# 2022년 금리 인상기 급락 -> 2023년 초 저점 약 92.5
# 2023년 특례보금자리론으로 반등 -> 2024년 중반 약 96.0
# 2025~2026년 금리 재상승 및 대출규제로 완만한 횡보/조정 95.5 ~ 94.8
price_indices = []
cur_p = 68.5
for i, d in enumerate(dates):
    ym = d.strftime("%Y-%m")
    if ym < "2017-01":
        delta = 0.25 + np.random.normal(0, 0.05)
    elif ym < "2018-09":
        delta = 0.45 + np.random.normal(0, 0.08)
    elif ym < "2019-06":
        delta = -0.05 + np.random.normal(0, 0.06)  # 9.13 대책 후 일시 조정
    elif ym < "2020-03":
        delta = 0.35 + np.random.normal(0, 0.06)
    elif ym < "2020-06":
        delta = 0.10 + np.random.normal(0, 0.05)  # 코로나 초기 일시 멈춤
    elif ym < "2021-08":
        delta = 0.65 + np.random.normal(0, 0.08)  # 초저금리 유동성 폭등기
    elif ym < "2021-12":
        delta = 0.30 - (i - 91) * 0.08 + np.random.normal(0, 0.04)  # 2021.08 금리인상 후 둔화
    elif ym < "2022-04":
        delta = -0.10 + np.random.normal(0, 0.04)  # 하락 전환
    elif ym < "2023-01":
        delta = -0.75 + np.random.normal(0, 0.08)  # 금리 급인상 및 레고랜드 사태 급락기
    elif ym < "2023-04":
        delta = -0.20 + np.random.normal(0, 0.05)  # 하락폭 축소
    elif ym < "2024-01":
        delta = 0.28 + np.random.normal(0, 0.05)  # 특례보금자리론 반등기
    elif ym < "2024-08":
        delta = 0.22 + np.random.normal(0, 0.04)
    elif ym < "2025-06":
        delta = 0.08 + np.random.normal(0, 0.03)  # 스트레스 DSR 및 금리 상승기 둔화
    elif ym < "2026-01":
        delta = -0.08 + np.random.normal(0, 0.03)  # 금리 재상승 하방 압력
    else:
        delta = -0.12 + np.random.normal(0, 0.03)  # 2026년 금리 고점 및 하향 조정

    cur_p += delta
    price_indices.append(round(cur_p, 2))

# 거래량 (건수)
# 2014~2019: 평시 월 5,000 ~ 9,000건
# 2020년 6~7월: 영끌 패닉바잉 월 11,000 ~ 15,000건
# 2021년 하반기: 세제 중과 및 금리 인상으로 거래 절벽 2,000 ~ 4,000건
# 2022년 하반기: 극심한 거래 빙하기 월 600 ~ 1,200건
# 2023년~2024년: 회복세 월 3,500 ~ 5,000건
# 2025~2026년: 금리 재인상 및 대출 규제로 월 2,500 ~ 3,200건 수준
trade_volumes = []
for i, d in enumerate(dates):
    ym = d.strftime("%Y-%m")
    if ym < "2017-01":
        vol = 7000 + np.random.normal(0, 800)
    elif ym < "2020-03":
        vol = 6500 + np.random.normal(0, 1000)
    elif ym in ["2020-06", "2020-07"]:
        vol = 13500 + np.random.normal(0, 1200)  # 영끌 폭발
    elif ym < "2021-08":
        vol = 4500 + np.random.normal(0, 600)
    elif ym < "2022-01":
        vol = 2200 + np.random.normal(0, 400)   # 2021 세제 중과 매물잠김
    elif ym < "2023-01":
        vol = 950 + np.random.normal(0, 200)    # 2022 금리 급등 거래 빙하기
    elif ym < "2024-01":
        vol = 3600 + np.random.normal(0, 400)   # 2023 특례보금자리론 회복
    elif ym < "2024-09":
        vol = 4300 + np.random.normal(0, 500)
    else:
        vol = 2800 + np.random.normal(0, 350)   # 2025~2026 고금리 규제 둔화
    trade_volumes.append(int(max(500, vol)))

# MoM & YoY 계산
df_price = pd.DataFrame({
    "date": dates.strftime("%Y-%m"),
    "price_index": price_indices,
    "trade_volume": trade_volumes
})
df_price["mom_change_rate"] = df_price["price_index"].pct_change() * 100
df_price["yoy_change_rate"] = df_price["price_index"].pct_change(12) * 100
df_price["mom_change_rate"] = df_price["mom_change_rate"].fillna(0).round(2)
df_price["yoy_change_rate"] = df_price["yoy_change_rate"].fillna(0).round(2)

df_price[["date", "price_index", "mom_change_rate", "yoy_change_rate"]].to_csv("data/seoul_apartment_price_index.csv", index=False)
df_price[["date", "trade_volume"]].to_csv("data/seoul_apartment_trade_volume.csv", index=False)

print("All 4 data files created successfully!")
print(f"Total rows per file: {len(df_price)}")

