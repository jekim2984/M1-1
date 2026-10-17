# 서울 아파트 매매가격과 금리·조세 사이클 시계열 분석 프로젝트

본 프로젝트는 **한국은행 기준금리, 주택담보대출 금리, 미국 연준 기준금리, 원/달러 환율, 그리고 정부의 조세 정책(보유세/양도세)**이 **서울 아파트 매매가격지수**에 미치는 복합적 인과관계와 시차(Time Lag)를 실증적으로 규명하고, 2027~2028년 서울 아파트 시장을 전망하는 데이터 분석 프로젝트입니다.

---

## 1. 프로젝트 구조

```text
M1-1/
├── data/                                 # 시계열 분석 원본 데이터셋 (150개월)
│   ├── seoul_apartment_price_index.csv   # 서울 아파트 매매가격지수 및 변동률
│   ├── seoul_apartment_trade_volume.csv  # 서울 아파트 월별 매매 거래량
│   ├── bok_interest_rates.csv            # 한국은행 기준금리 및 주담대 금리
│   └── us_fed_rate_and_fx.csv            # 미국 연준 기준금리 및 원/달러 환율
├── images/                               # 리포트 삽입용 고해상도 시각화 차트
│   ├── 01_macro_us_kr_rates.png          # [차트 1] 한미 기준금리 및 원/달러 환율 연동 추이
│   ├── 02_main_rate_vs_seoul_price.png   # [차트 2] 한국 금리 vs 서울 아파트 매매가격지수 (정책 밴드)
│   ├── 03_lag_cross_correlation.png      # [차트 3] 기준금리 변동 vs 서울 집값 시차 상관분석
│   └── 04_forecast_2027_2028_band.png    # [차트 4] 2027~2028 세제·통화 시나리오 예측 밴드
├── analysis.ipynb                        # 분석 및 시각화 실행 Jupyter Notebook
├── run_analysis.py                       # 파이썬 일괄 실행 스크립트
├── generate_data.py                      # 원본 데이터 수집/생성 스크립트
├── REPORT.md                             # [최종 결과물] 심층 분석 리포트
├── requirements.txt                      # 환경 의존성 목록
├── guide.md                              # 과제 가이드라인 원문
└── README.md                             # 프로젝트 개요 및 재현 안내서
```

---

## 2. 개발 환경 및 실행 방법

### 환경 요구사항
- Python 3.10 이상 (테스트 환경: Python 3.12)
- 한글 폰트 지원 (macOS: `AppleGothic`, Windows: `Malgun Gothic`, Linux: `NanumGothic`)

### 의존성 설치
```bash
pip install -r requirements.txt
```

### 실행 방법

1. **Jupyter Notebook 실행**:
   ```bash
   jupyter notebook analysis.ipynb
   ```
   노트북 상단 메뉴에서 `Kernel` > `Restart & Run All`을 실행하여 모든 셀을 순차 실행합니다.

2. **파이썬 스크립트 일괄 실행**:
   ```bash
   python3 run_analysis.py
   ```
   실행 즉시 시계열 분석 통계와 함께 `images/` 디렉토리에 4종의 고해상도 차트가 자동 생성됩니다.

---

## 3. 데이터 출처 및 라이선스 고지

* **한국부동산원**: 전국주택가격동향조사 (서울 아파트 월간 매매가격지수, 공공데이터포털)
* **한국은행 경제통계시스템 (ECOS)**: 기준금리, 예금은행 가계대출금리(신규취급액 주택담보대출)
* **미국 연방준비제도 (FRED)**: Federal Funds Effective Rate (연준 기준금리)
* **서울외국환중개 / 한국은행**: 원/달러(USD/KRW) 매매기준율
* **라이선스**: 본 데이터는 공공데이터 및 연구/학습 목적으로 수집 및 가공되었으며, 비상업적 학술 목적으로 재현 가능합니다.

