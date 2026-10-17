import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 한글 폰트 설정 (macOS AppleGothic)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 11

os.environ['MPLCONFIGDIR'] = '/tmp/mpl'
os.makedirs('images', exist_ok=True)

# 1. 데이터 로드 및 병합
df_price = pd.read_csv('data/seoul_apartment_price_index.csv')
df_volume = pd.read_csv('data/seoul_apartment_trade_volume.csv')
df_bok = pd.read_csv('data/bok_interest_rates.csv')
df_fed = pd.read_csv('data/us_fed_rate_and_fx.csv')

df = df_price.merge(df_volume, on='date')
df = df.merge(df_bok, on='date')
df = df.merge(df_fed, on='date')
df['date_dt'] = pd.to_datetime(df['date'] + '-01')
df = df.sort_values('date_dt').reset_index(drop=True)

print("=== 데이터 병합 완료 ===")
print(f"총 행 수: {len(df)}, 기간: {df['date'].iloc[0]} ~ {df['date'].iloc[-1]}")
print("결측치 여부:\n", df.isnull().sum())

# 2. 시계열 전처리 및 파생 지표 생성
# 이동평균 (MA 3개월, 12개월)
df['price_ma03'] = df['price_index'].rolling(window=3).mean()
df['price_ma12'] = df['price_index'].rolling(window=12).mean()
df['rate_diff'] = df['bok_base_rate'] - df['fed_funds_rate'] # 한미 금리차 (한국 - 미국)
df['bok_rate_diff_1m'] = df['bok_base_rate'].diff() # 금리 월별 변동폭

# ==========================================
# 차트 1: 글로벌-국내 금리 연동 및 환율 추이
# ==========================================
fig, ax1 = plt.subplots(figsize=(12, 6))

color_fed = '#D9534F' # 미국 연준 (빨강 계열)
color_bok = '#0275D8' # 한국은행 (파랑 계열)
color_fx = '#5CB85C'  # 원/달러 환율 (초록 계열)

# 좌측 축: 금리 (%)
ax1.plot(df['date_dt'], df['fed_funds_rate'], label='미국 연준 기준금리 (Fed Funds Rate)', color=color_fed, linewidth=2.5, linestyle='--')
ax1.plot(df['date_dt'], df['bok_base_rate'], label='한국은행 기준금리 (BOK Base Rate)', color=color_bok, linewidth=2.5)
ax1.set_xlabel('연도', fontweight='bold', fontsize=12)
ax1.set_ylabel('기준금리 (%)', fontweight='bold', fontsize=12)
ax1.set_ylim(-0.5, 6.5)
ax1.grid(True, linestyle=':', alpha=0.6)

# 우측 축: 환율 (원)
ax2 = ax1.twinx()
ax2.plot(df['date_dt'], df['krw_usd_rate'], label='원/달러 환율 (KRW/USD)', color=color_fx, linewidth=1.8, alpha=0.85)
ax2.set_ylabel('원/달러 환율 (KRW)', color=color_fx, fontweight='bold', fontsize=12)
ax2.set_ylim(950, 1600)
ax2.tick_params(axis='y', labelcolor=color_fx)

# 한미 금리 역전 구간 하이라이트 (미국 > 한국)
inversion_mask = df['fed_funds_rate'] > df['bok_base_rate']
ax1.fill_between(df['date_dt'], -0.5, 6.5, where=inversion_mask, color='salmon', alpha=0.15, label='한미 금리 역전 구간 (외환 유출 압력)')

# 주석 추가
ax1.annotate('2022년 미 연준 자이언트스텝\n& 한은 빅스텝', xy=(pd.to_datetime('2022-07-01'), 2.25), 
             xytext=(pd.to_datetime('2019-01-01'), 4.8),
             arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
             fontsize=10, fontweight='bold', bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.3))

# 범례 통합
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', frameon=True, facecolor='white', framealpha=0.9)

plt.title('[시각화 1] 글로벌 통화 긴축과 국내 외생 압력: 한·미 기준금리 및 원/달러 환율 추이 (2014~2026)', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('images/01_macro_us_kr_rates.png', dpi=300)
plt.close()
print("Saved images/01_macro_us_kr_rates.png")

# ==========================================
# 차트 2: 한국 금리 vs 서울 아파트 매매가격지수 (정책 밴드)
# ==========================================
fig, ax1 = plt.subplots(figsize=(13, 6.5))

color_rate = '#0275D8'
color_price = '#D9534F'

# 좌측 축: 금리 (%)
line1 = ax1.plot(df['date_dt'], df['bok_base_rate'], label='한국은행 기준금리 (%)', color=color_rate, linewidth=2.2, linestyle='--')
line2 = ax1.plot(df['date_dt'], df['mortgage_loan_rate'], label='주택담보대출 금리 (%)', color='#025AA5', linewidth=1.5, alpha=0.7)
ax1.set_xlabel('연도', fontweight='bold', fontsize=12)
ax1.set_ylabel('금리 (%)', color=color_rate, fontweight='bold', fontsize=12)
ax1.tick_params(axis='y', labelcolor=color_rate)
ax1.set_ylim(0, 7.0)
ax1.grid(True, linestyle=':', alpha=0.6)

# 우측 축: 서울 아파트 가격지수
ax2 = ax1.twinx()
line3 = ax2.plot(df['date_dt'], df['price_index'], label='서울 아파트 매매가격지수 (월별)', color=color_price, linewidth=2.8)
line4 = ax2.plot(df['date_dt'], df['price_ma12'], label='12개월 이동평균선 (추세선)', color='#8E2800', linewidth=1.8, linestyle=':')
ax2.set_ylabel('매매가격지수 (2021.06=100)', color=color_price, fontweight='bold', fontsize=12)
ax2.tick_params(axis='y', labelcolor=color_price)
ax2.set_ylim(60, 115)

# 정책 국면 밴드 표시
# 국면 1: 2020.06 ~ 2021.07 (초저금리 유동성 파티 & 세제 중과)
ax1.axvspan(pd.to_datetime('2020-05-01'), pd.to_datetime('2021-08-01'), color='#FFEDA0', alpha=0.35, label='[국면1] 초저금리(0.5%) & 패닉바잉')
# 국면 2: 2021.08 ~ 2022.12 (금리 급인상 및 레고랜드 사태)
ax1.axvspan(pd.to_datetime('2021-08-01'), pd.to_datetime('2022-12-01'), color='#FEB24C', alpha=0.3, label='[국면2] 금리 급인상 충격기(급락)')
# 국면 3: 2023.01 ~ 2024.08 (특례보금자리론 및 반등)
ax1.axvspan(pd.to_datetime('2023-01-01'), pd.to_datetime('2024-08-01'), color='#E0F3F8', alpha=0.4, label='[국면3] 고금리 속 정책금융 반등기')
# 국면 4: 2024.09 ~ 현재 (스트레스 DSR & 금리 재상승)
ax1.axvspan(pd.to_datetime('2024-09-01'), pd.to_datetime('2026-06-01'), color='#CCCCCC', alpha=0.3, label='[국면4] 대출 규제 & 금리 재상승기')

# 주요 변곡점 주석
ax2.annotate('2021.11 최고점 (104.3)\n금리인상 4개월 후 피크아웃', xy=(pd.to_datetime('2021-11-01'), 104.3),
             xytext=(pd.to_datetime('2018-06-01'), 108),
             arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
             fontsize=9.5, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='red', alpha=0.8))

ax2.annotate('2022.12 저점 (92.5)\n빅스텝 충격 & 거래절벽', xy=(pd.to_datetime('2022-12-01'), 92.5),
             xytext=(pd.to_datetime('2022-01-01'), 75),
             arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
             fontsize=9.5, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='blue', alpha=0.8))

lines = line1 + line2 + line3 + line4
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', framealpha=0.9, fontsize=9.5)

plt.title('[시각화 2] 통화정책과 주택가격의 10년 궤적: 한국 금리 vs 서울 아파트 매매가격지수 (2014~2026)', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('images/02_main_rate_vs_seoul_price.png', dpi=300)
plt.close()
print("Saved images/02_main_rate_vs_seoul_price.png")

# ==========================================
# 차트 3: 금리 변동 vs 서울 집값 변동률 시차 상관분석 (Cross-Correlation)
# ==========================================
lags = list(range(0, 13))
corrs = []
# 기준금리 변동폭(t)과 k개월 뒤 서울 아파트 MoM 변동률(t+k) 간의 피어슨 상관계수
s_rate_diff = df['bok_base_rate'].diff()

for k in lags:
    s_price_mom = df['mom_change_rate'].shift(-k)
    valid = ~(s_rate_diff.isna() | s_price_mom.isna())
    corr = np.corrcoef(s_rate_diff[valid], s_price_mom[valid])[0, 1]
    corrs.append(corr)

fig, ax = plt.subplots(figsize=(10, 5.5))
bars = ax.bar(lags, corrs, color='#2B5B84', width=0.6, edgecolor='black', alpha=0.85)

# 최대 음의 상관계수 지점 강조 (시차 4개월)
min_idx = int(np.argmin(corrs))
bars[min_idx].set_color('#D9534F')
bars[min_idx].set_edgecolor('black')
bars[min_idx].set_linewidth(1.5)

ax.set_xlabel('시차 (개월, Lag $k$)', fontweight='bold', fontsize=12)
ax.set_ylabel('상관계수 (Pearson Correlation $r$)', fontweight='bold', fontsize=12)
ax.set_xticks(lags)
ax.set_xticklabels([f'{k}개월' if k > 0 else '동일월(0)' for k in lags])
ax.grid(axis='y', linestyle=':', alpha=0.7)
ax.set_ylim(min(corrs) - 0.15, max(corrs) + 0.1)

# 바 위에 수치 표시
for bar, val in zip(bars, corrs):
    yval = bar.get_height()
    va = 'bottom' if yval < 0 else 'top'
    offset = -0.035 if yval < 0 else 0.02
    ax.text(bar.get_x() + bar.get_width()/2.0, yval + offset, f'{val:.3f}', ha='center', va='center', fontsize=9.5, fontweight='bold')

ax.annotate(f'최대 음(-)의 상관관계 (시차 {min_idx}개월)\n$r = {corrs[min_idx]:.3f}$ (가격 파급 정점)', 
            xy=(min_idx, corrs[min_idx]), 
            xytext=(min_idx + 1.0, corrs[min_idx] - 0.09),
            arrowprops=dict(facecolor='red', arrowstyle='->', lw=1.5),
            fontsize=10.5, fontweight='bold', color='red',
            bbox=dict(boxstyle='round,pad=0.3', fc='#FFF0F0', ec='red', alpha=0.9))

plt.title('[시각화 3] 기준금리 변동과 서울 아파트 가격 변동률(MoM) 간 시차(Lag 0~12개월) 상관분석', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('images/03_lag_cross_correlation.png', dpi=300)
plt.close()
print(f"Saved images/03_lag_cross_correlation.png (Peak at lag {min_idx}: {corrs[min_idx]:.3f})")

# ==========================================
# 차트 4: [보너스 과제] 2027~2028년 서울 아파트 3대 시나리오 예측 밴드
# ==========================================
# 예측 기간: 2026-07 ~ 2028-12 (30개월)
forecast_dates = pd.date_range(start="2026-07-01", end="2028-12-01", freq="MS")
n_fc = len(forecast_dates)

last_date = df['date_dt'].iloc[-1]
last_price = df['price_index'].iloc[-1]

# 3대 시나리오 정의
# 시나리오 A (기준 경로: 조세 역설형)
# 2026하반기~2027년: 고금리 지속 + 2028 양도세 중과 대비 절세 급매물 출회로 완만한 가격 조정 (월 -0.15% 하락)
# 2028년: 양도세 본격 시행으로 매물 잠김(Lock-in) 발생, 거래 절벽 속 호가 유지 및 완만한 반등 (월 +0.12%)
scen_a = [last_price]
for d in forecast_dates:
    ym = d.strftime('%Y-%m')
    if ym < '2028-01':
        p = scen_a[-1] * (1 - 0.0015)
    else:
        p = scen_a[-1] * (1 + 0.0012)
    scen_a.append(p)
scen_a = scen_a[1:]

# 시나리오 B (비관 경로: 고금리 장기 침체형)
# 금리 추가 인상 및 DSR 규제 강화로 2028년까지 지속 하향 (월 -0.30%)
scen_b = [last_price]
for d in forecast_dates:
    p = scen_b[-1] * (1 - 0.0030)
    scen_b.append(p)
scen_b = scen_b[1:]

# 시나리오 C (낙관 경로: 통화 피벗 & 정책 방어형)
# 2027년 초 금리 조기 인하 및 공급 부족 부각으로 반등 (월 +0.25%)
scen_c = [last_price]
for d in forecast_dates:
    p = scen_c[-1] * (1 + 0.0025)
    scen_c.append(p)
scen_c = scen_c[1:]

fig, ax = plt.subplots(figsize=(13, 6.5))

# 과거 2020~2026년 데이터 연결
hist_mask = df['date_dt'] >= '2020-01-01'
ax.plot(df.loc[hist_mask, 'date_dt'], df.loc[hist_mask, 'price_index'], label='서울 아파트 실적치 (2020~2026.06)', color='#333333', linewidth=2.5)

# 예측 구간 플롯 (실적치 마지막 점과 연결)
all_fc_dates = [last_date] + list(forecast_dates)
fc_a = [last_price] + scen_a
fc_b = [last_price] + scen_b
fc_c = [last_price] + scen_c

ax.plot(all_fc_dates, fc_a, label='시나리오 A (기준): 2027 절세 급매 조정 후 2028 매물잠김 반등', color='#0275D8', linewidth=2.5, linestyle='-')
ax.plot(all_fc_dates, fc_b, label='시나리오 B (비관): 고금리 장기화 및 대출규제 지속 침체', color='#D9534F', linewidth=2.2, linestyle='--')
ax.plot(all_fc_dates, fc_c, label='시나리오 C (낙관): 금리 조기 피벗(인하) 및 공급부족 반등', color='#5CB85C', linewidth=2.2, linestyle='-.')

# 신뢰 밴드 (시나리오 B ~ C 구간 채우기)
ax.fill_between(all_fc_dates, fc_b, fc_c, color='#0275D8', alpha=0.1, label='예측 신뢰 밴드 (Scenarios Range)')

# 2027년 및 2028년 정책 구간 수직선 및 배경
ax.axvspan(pd.to_datetime('2026-07-01'), pd.to_datetime('2027-12-31'), color='#FFF3CD', alpha=0.3, label='2027년: 양도세 일몰 전 절세 급매 출회기')
ax.axvspan(pd.to_datetime('2028-01-01'), pd.to_datetime('2028-12-31'), color='#F8D7DA', alpha=0.3, label='2028년: 양도세 중과 본격화 & 매물 잠김기')
ax.axvline(x=pd.to_datetime('2026-06-01'), color='gray', linestyle=':', linewidth=1.5)

# 주석
ax.annotate('현재 시점 (2026.06)\n실적치 종료', xy=(pd.to_datetime('2026-06-01'), last_price),
            xytext=(pd.to_datetime('2025-01-01'), 88),
            arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
            fontsize=9.5, fontweight='bold', bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.9))

ax.set_xlabel('연도', fontweight='bold', fontsize=12)
ax.set_ylabel('서울 아파트 매매가격지수 (2021.06=100)', fontweight='bold', fontsize=12)
ax.set_ylim(82, 110)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.92, fontsize=9.5)

plt.title('[시각화 4] 세제 개편 및 통화 경로에 따른 서울 아파트 가격 3대 시나리오 예측 (2026~2028)', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('images/04_forecast_2027_2028_band.png', dpi=300)
plt.close()
print("Saved images/04_forecast_2027_2028_band.png")

print("=== 모든 차트 생성 완료 ===")
