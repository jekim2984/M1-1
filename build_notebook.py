import json

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# 글로벌 통화 충격과 조세 정책의 이중주\n",
            "## 금리·양도세 사이클로 본 서울 아파트 10년 궤적과 2027~2028년 시나리오 전망\n",
            "\n",
            "**분석 대상**: 서울 아파트 매매가격지수 및 거시경제·정책 변수 (2014-01 ~ 2026-06)\n",
            "**작성 목적**: AI 데이터 분석 미션 (시계열 트렌드 및 시차·정책 상호작용 분석)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 1,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import numpy as np\n",
            "import pandas as pd\n",
            "import matplotlib.pyplot as plt\n",
            "\n",
            "# 한글 폰트 설정 (macOS AppleGothic)\n",
            "plt.rcParams['font.family'] = 'AppleGothic'\n",
            "plt.rcParams['axes.unicode_minus'] = False\n",
            "plt.rcParams['font.size'] = 11\n",
            "os.environ['MPLCONFIGDIR'] = '/tmp/mpl'\n",
            "os.makedirs('images', exist_ok=True)\n",
            "print('라이브러리 로드 및 환경 설정 완료')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 1. 데이터 로드 및 정제\n",
            "- 서울 아파트 매매가격지수 (한국부동산원)\n",
            "- 한국은행 기준금리 및 주담대 금리 (한국은행 ECOS)\n",
            "- 미국 연준 기준금리 및 원/달러 환율 (FRED / 외환중개)\n",
            "- 서울 아파트 매매 거래량"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 2,
        "metadata": {},
        "outputs": [],
        "source": [
            "df_price = pd.read_csv('data/seoul_apartment_price_index.csv')\n",
            "df_volume = pd.read_csv('data/seoul_apartment_trade_volume.csv')\n",
            "df_bok = pd.read_csv('data/bok_interest_rates.csv')\n",
            "df_fed = pd.read_csv('data/us_fed_rate_and_fx.csv')\n",
            "\n",
            "df = df_price.merge(df_volume, on='date')\n",
            "df = df.merge(df_bok, on='date')\n",
            "df = df.merge(df_fed, on='date')\n",
            "df['date_dt'] = pd.to_datetime(df['date'] + '-01')\n",
            "df = df.sort_values('date_dt').reset_index(drop=True)\n",
            "\n",
            "print(f'데이터 총 행 수: {len(df)} (기간: {df[\"date\"].iloc[0]} ~ {df[\"date\"].iloc[-1]})')\n",
            "print('결측치 점검:\\n', df.isnull().sum())\n",
            "df.head()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 2. 시계열 파생 지표 생성 (이동평균 & 변화율)\n",
            "- 이동평균(3개월, 12개월 MA)을 통한 단기 노이즈 제거\n",
            "- 한미 기준금리 역전차 산출"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 3,
        "metadata": {},
        "outputs": [],
        "source": [
            "df['price_ma03'] = df['price_index'].rolling(window=3).mean()\n",
            "df['price_ma12'] = df['price_index'].rolling(window=12).mean()\n",
            "df['rate_diff'] = df['bok_base_rate'] - df['fed_funds_rate']  # 한국 - 미국 금리차\n",
            "df['bok_rate_diff_1m'] = df['bok_base_rate'].diff()\n",
            "df[['date', 'price_index', 'price_ma12', 'mom_change_rate', 'bok_base_rate', 'rate_diff']].tail()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 3. [시각화 1] 글로벌 통화 긴축과 국내 외생 압력\n",
            "- 미국 연준 기준금리 vs 한국은행 기준금리 vs 원/달러 환율"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 4,
        "metadata": {},
        "outputs": [],
        "source": [
            "fig, ax1 = plt.subplots(figsize=(12, 6))\n",
            "color_fed = '#D9534F'\n",
            "color_bok = '#0275D8'\n",
            "color_fx = '#5CB85C'\n",
            "\n",
            "ax1.plot(df['date_dt'], df['fed_funds_rate'], label='미국 연준 기준금리 (Fed Funds Rate)', color=color_fed, linewidth=2.5, linestyle='--')\n",
            "ax1.plot(df['date_dt'], df['bok_base_rate'], label='한국은행 기준금리 (BOK Base Rate)', color=color_bok, linewidth=2.5)\n",
            "ax1.set_xlabel('연도', fontweight='bold', fontsize=12)\n",
            "ax1.set_ylabel('기준금리 (%)', fontweight='bold', fontsize=12)\n",
            "ax1.set_ylim(-0.5, 6.5)\n",
            "ax1.grid(True, linestyle=':', alpha=0.6)\n",
            "\n",
            "ax2 = ax1.twinx()\n",
            "ax2.plot(df['date_dt'], df['krw_usd_rate'], label='원/달러 환율 (KRW/USD)', color=color_fx, linewidth=1.8, alpha=0.85)\n",
            "ax2.set_ylabel('원/달러 환율 (KRW)', color=color_fx, fontweight='bold', fontsize=12)\n",
            "ax2.set_ylim(950, 1600)\n",
            "\n",
            "inversion_mask = df['fed_funds_rate'] > df['bok_base_rate']\n",
            "ax1.fill_between(df['date_dt'], -0.5, 6.5, where=inversion_mask, color='salmon', alpha=0.15, label='한미 금리 역전 구간')\n",
            "\n",
            "lines_1, labels_1 = ax1.get_legend_handles_labels()\n",
            "lines_2, labels_2 = ax2.get_legend_handles_labels()\n",
            "ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', frameon=True, facecolor='white', framealpha=0.9)\n",
            "plt.title('[시각화 1] 글로벌 통화 긴축과 국내 외생 압력: 한·미 기준금리 및 원/달러 환율 추이', fontsize=14, fontweight='bold', pad=15)\n",
            "plt.tight_layout()\n",
            "plt.savefig('images/01_macro_us_kr_rates.png', dpi=300)\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 4. [시각화 2] 통화정책과 주택가격의 10년 궤적\n",
            "- 한국 기준금리·대출금리 vs 서울 아파트 매매가격지수 (정책 국면 밴드 포함)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 5,
        "metadata": {},
        "outputs": [],
        "source": [
            "fig, ax1 = plt.subplots(figsize=(13, 6.5))\n",
            "line1 = ax1.plot(df['date_dt'], df['bok_base_rate'], label='한국은행 기준금리 (%)', color='#0275D8', linewidth=2.2, linestyle='--')\n",
            "line2 = ax1.plot(df['date_dt'], df['mortgage_loan_rate'], label='주택담보대출 금리 (%)', color='#025AA5', linewidth=1.5, alpha=0.7)\n",
            "ax1.set_xlabel('연도', fontweight='bold', fontsize=12)\n",
            "ax1.set_ylabel('금리 (%)', color='#0275D8', fontweight='bold', fontsize=12)\n",
            "ax1.set_ylim(0, 7.0)\n",
            "ax1.grid(True, linestyle=':', alpha=0.6)\n",
            "\n",
            "ax2 = ax1.twinx()\n",
            "line3 = ax2.plot(df['date_dt'], df['price_index'], label='서울 아파트 매매가격지수 (월별)', color='#D9534F', linewidth=2.8)\n",
            "line4 = ax2.plot(df['date_dt'], df['price_ma12'], label='12개월 이동평균선 (추세선)', color='#8E2800', linewidth=1.8, linestyle=':')\n",
            "ax2.set_ylabel('매매가격지수 (2021.06=100)', color='#D9534F', fontweight='bold', fontsize=12)\n",
            "ax2.set_ylim(60, 115)\n",
            "\n",
            "ax1.axvspan(pd.to_datetime('2020-05-01'), pd.to_datetime('2021-08-01'), color='#FFEDA0', alpha=0.35, label='[국면1] 초저금리 & 패닉바잉')\n",
            "ax1.axvspan(pd.to_datetime('2021-08-01'), pd.to_datetime('2022-12-01'), color='#FEB24C', alpha=0.3, label='[국면2] 금리 급인상 충격기')\n",
            "ax1.axvspan(pd.to_datetime('2023-01-01'), pd.to_datetime('2024-08-01'), color='#E0F3F8', alpha=0.4, label='[국면3] 고금리 속 정책금융 반등기')\n",
            "ax1.axvspan(pd.to_datetime('2024-09-01'), pd.to_datetime('2026-06-01'), color='#CCCCCC', alpha=0.3, label='[국면4] 대출 규제 & 금리 재상승기')\n",
            "\n",
            "lines = line1 + line2 + line3 + line4\n",
            "labels = [l.get_label() for l in lines]\n",
            "ax1.legend(lines, labels, loc='upper left', frameon=True, facecolor='white', framealpha=0.9, fontsize=9.5)\n",
            "plt.title('[시각화 2] 한국 금리 vs 서울 아파트 매매가격지수 (2014~2026)', fontsize=14, fontweight='bold', pad=15)\n",
            "plt.tight_layout()\n",
            "plt.savefig('images/02_main_rate_vs_seoul_price.png', dpi=300)\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 5. [시각화 3] 시차 상관분석 (Cross-Correlation with Lag 0~12개월)\n",
            "- 기준금리 변동폭($\\Delta Rate_t$)과 $k$개월 뒤 서울 아파트 월간 변동률($MoM_{t+k}$) 간의 상관계수"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 6,
        "metadata": {},
        "outputs": [],
        "source": [
            "lags = list(range(0, 13))\n",
            "corrs = []\n",
            "s_rate_diff = df['bok_base_rate'].diff()\n",
            "\n",
            "for k in lags:\n",
            "    s_price_mom = df['mom_change_rate'].shift(-k)\n",
            "    valid = ~(s_rate_diff.isna() | s_price_mom.isna())\n",
            "    corr = np.corrcoef(s_rate_diff[valid], s_price_mom[valid])[0, 1]\n",
            "    corrs.append(corr)\n",
            "\n",
            "min_idx = int(np.argmin(corrs))\n",
            "print(f'최대 음(-)의 상관계수 시차: {min_idx}개월 (r = {corrs[min_idx]:.3f})')\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(10, 5.5))\n",
            "bars = ax.bar(lags, corrs, color='#2B5B84', width=0.6, edgecolor='black', alpha=0.85)\n",
            "bars[min_idx].set_color('#D9534F')\n",
            "ax.set_xlabel('시차 (개월, Lag $k$)', fontweight='bold', fontsize=12)\n",
            "ax.set_ylabel('상관계수 (Pearson Correlation $r$)', fontweight='bold', fontsize=12)\n",
            "ax.set_xticks(lags)\n",
            "ax.set_xticklabels([f'{k}개월' if k > 0 else '동일월(0)' for k in lags])\n",
            "ax.grid(axis='y', linestyle=':', alpha=0.7)\n",
            "for bar, val in zip(bars, corrs):\n",
            "    yval = bar.get_height()\n",
            "    offset = -0.035 if yval < 0 else 0.02\n",
            "    ax.text(bar.get_x() + bar.get_width()/2.0, yval + offset, f'{val:.3f}', ha='center', va='center', fontsize=9.5, fontweight='bold')\n",
            "plt.title('[시각화 3] 기준금리 변동과 서울 아파트 가격 변동률(MoM) 간 시차 상관분석', fontsize=14, fontweight='bold', pad=15)\n",
            "plt.tight_layout()\n",
            "plt.savefig('images/03_lag_cross_correlation.png', dpi=300)\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### 6. [시각화 4 / 보너스 과제] 2027~2028년 서울 아파트 3대 시나리오 예측\n",
            "- 2027년 양도세 일몰 전 절세 급매 출회 효과\n",
            "- 2028년 양도세 본격 시행 후 매물 잠김(Lock-in) 효과"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": 7,
        "metadata": {},
        "outputs": [],
        "source": [
            "forecast_dates = pd.date_range(start='2026-07-01', end='2028-12-01', freq='MS')\n",
            "last_date = df['date_dt'].iloc[-1]\n",
            "last_price = df['price_index'].iloc[-1]\n",
            "\n",
            "# 시나리오 A (기준): 2027 절세 급매 하락 조정 -> 2028 매물잠김 완만한 반등\n",
            "scen_a = [last_price]\n",
            "for d in forecast_dates:\n",
            "    p = scen_a[-1] * (1 - 0.0015) if d.strftime('%Y-%m') < '2028-01' else scen_a[-1] * (1 + 0.0012)\n",
            "    scen_a.append(p)\n",
            "scen_a = scen_a[1:]\n",
            "\n",
            "# 시나리오 B (비관): 고금리 장기화 지속 침체\n",
            "scen_b = [last_price * ((1 - 0.0030) ** i) for i in range(1, len(forecast_dates) + 1)]\n",
            "\n",
            "# 시나리오 C (낙관): 금리 조기 피벗 반등\n",
            "scen_c = [last_price * ((1 + 0.0025) ** i) for i in range(1, len(forecast_dates) + 1)]\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(13, 6.5))\n",
            "hist_mask = df['date_dt'] >= '2020-01-01'\n",
            "ax.plot(df.loc[hist_mask, 'date_dt'], df.loc[hist_mask, 'price_index'], label='서울 아파트 실적치 (2020~2026.06)', color='#333333', linewidth=2.5)\n",
            "\n",
            "all_fc_dates = [last_date] + list(forecast_dates)\n",
            "ax.plot(all_fc_dates, [last_price] + scen_a, label='시나리오 A (기준): 2027 절세 급매 조정 후 2028 매물잠김 반등', color='#0275D8', linewidth=2.5)\n",
            "ax.plot(all_fc_dates, [last_price] + scen_b, label='시나리오 B (비관): 고금리 장기화 침체', color='#D9534F', linewidth=2.2, linestyle='--')\n",
            "ax.plot(all_fc_dates, [last_price] + scen_c, label='시나리오 C (낙관): 금리 피벗 반등', color='#5CB85C', linewidth=2.2, linestyle='-.')\n",
            "ax.fill_between(all_fc_dates, [last_price] + scen_b, [last_price] + scen_c, color='#0275D8', alpha=0.1, label='예측 신뢰 밴드')\n",
            "\n",
            "ax.axvspan(pd.to_datetime('2026-07-01'), pd.to_datetime('2027-12-31'), color='#FFF3CD', alpha=0.3, label='2027년: 절세 급매 출회기')\n",
            "ax.axvspan(pd.to_datetime('2028-01-01'), pd.to_datetime('2028-12-31'), color='#F8D7DA', alpha=0.3, label='2028년: 양도세 중과 & 매물 잠김기')\n",
            "ax.axvline(x=pd.to_datetime('2026-06-01'), color='gray', linestyle=':')\n",
            "\n",
            "ax.set_xlabel('연도', fontweight='bold', fontsize=12)\n",
            "ax.set_ylabel('서울 아파트 매매가격지수 (2021.06=100)', fontweight='bold', fontsize=12)\n",
            "ax.set_ylim(82, 110)\n",
            "ax.grid(True, linestyle=':', alpha=0.6)\n",
            "ax.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.92, fontsize=9.5)\n",
            "plt.title('[시각화 4] 세제 개편 및 통화 경로에 따른 서울 아파트 가격 3대 시나리오 예측 (2026~2028)', fontsize=14, fontweight='bold', pad=15)\n",
            "plt.tight_layout()\n",
            "plt.savefig('images/04_forecast_2027_2028_band.png', dpi=300)\n",
            "plt.show()"
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.12"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open("analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=2)

print("analysis.ipynb generated successfully!")

