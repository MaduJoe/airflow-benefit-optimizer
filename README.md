# Airflow Toy Project — Life‑Solution Benefit Optimizer (Ajd‑style)

> 🎯 **목표**: 아정당 유사 시나리오(인터넷/TV, 가전렌탈, 휴대폰 등)의 **혜택·지원금 최적 조합**을 **Airflow DAG**로 자동화  
> 🔍 **포커스**: DAG 설계, 의존성/리트라이, 스케줄, XCom, idempotency, 간단 KPI/리포트

## 🏗️ 프로젝트 구조

```
airflow-home/
  dags/
    ajd_benefit_optimizer.py    # 메인 DAG 파일
    lib/
      __init__.py
      io_utils.py               # 데이터 로드/저장 유틸리티
      rules.py                  # 비즈니스 룰 및 조건 검증
      scoring.py                # 스코어링 및 최적화 로직
  data/
    offers/                     # 오퍼 데이터 (JSON)
      internet.json
      mobile.json
      rental.json
    contracts/                  # 기존 계약 데이터
      sample_contracts.json
    ajd.db                      # SQLite 데이터베이스 (실행 시 생성)
    export/                     # 생성된 리포트 (실행 시 생성)
  requirements.txt              # Python 패키지 목록
  setup_uv.ps1                  # Windows 설정 스크립트
  setup_uv.sh                   # Linux/Mac 설정 스크립트
  README.md                     # 이 파일
```

## 🚀 빠른 시작

### 1. uv를 사용한 환경 설정

```bash
# uv 가상환경 생성 (Python 3.11)
uv venv -p 3.11 .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 의존성 설치
export AIRFLOW_VERSION=2.9.2
export PYTHON_VERSION=3.11
export CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

uv pip install "apache-airflow==${AIRFLOW_VERSION}" -c "${CONSTRAINT_URL}"
uv pip install pandas>=1.5.0 sqlalchemy>=1.4.0
```

### 2. Airflow 초기화 및 실행

```bash
# Airflow 홈 디렉토리 설정
export AIRFLOW_HOME=$(pwd)

# 데이터베이스 초기화
airflow db migrate

# 관리자 계정 생성
airflow users create \
  --username admin --firstname Admin --lastname User \
  --role Admin --email admin@example.com --password admin

# Airflow 실행 (개발용)
airflow standalone
```

### 3. DAG 실행

1. 브라우저에서 http://localhost:8080 접속
2. admin / admin으로 로그인
3. `ajd_benefit_optimizer` DAG 찾기
4. DAG 활성화 후 수동 실행

## 📊 주요 기능

### DAG 워크플로우
1. **extract_offers** — JSON 파일에서 오퍼 데이터 로드
2. **extract_contracts** — 기존 계약 데이터 로드
3. **transform_clean** — 데이터 정제 및 중복 제거
4. **score_and_optimize** — 스코어링 및 최적 조합 계산
5. **load_to_sqlite** — SQLite DB에 결과 저장
6. **export_reports** — CSV/MD 리포트 생성
7. **print_kpi** — KPI 로그 출력

### 비즈니스 룰
- **총혜택 계산**: `benefit_cash + benefit_coupon - switching_cost - same_vendor_penalty + expiry_bonus`
- **만기 임박 보너스**: 계약 만료 60일 이내 시 총혜택의 +5%
- **번들 보너스**: (internet + mobile) 조합 선택 시 +50,000원
- **동일 벤더 재계약 페널티**: 같은 벤더 재계약 시 -20,000원
- **조기 해지 수수료**: 기존 계약 남은 기간에 따라 월요금 × 남은 개월 수 (최대 100,000원)
- **카테고리 제약**: 각 카테고리당 최대 1개 선택
- **자격 검증**: 신규 고객 전용 조건 등 확인

## 📈 결과 확인

### SQLite 데이터베이스
- `data/ajd.db` 파일에 `offers`, `contracts`, `recommendations` 테이블 생성
- 첫 실행 시 자동으로 생성됨

### 리포트 파일
- `data/export/report_YYYYMMDD.csv` — 추천 결과 상세
- `data/export/summary_YYYYMMDD.md` — KPI 요약
- `export/` 디렉토리는 첫 실행 시 자동으로 생성됨

### Airflow 로그
```
🎯 아정당 혜택 최적화 결과
==================================================
📊 전체 오퍼 수: 9개
🔍 고유 오퍼 수: 9개  
🗑️ 중복 제거율: 0.0%
💰 최고 총 혜택: 350,000원
🎁 번들 보너스: 50,000원
📦 선택된 오퍼: 3개
```

## 🔧 설정 및 커스터마이징

### 스케줄 변경
DAG 파일에서 `schedule_interval` 수정:
```python
schedule_interval='0 9 * * *',  # 매일 09:00 UTC (한국시간 18:00)
```

### 새로운 오퍼 추가
`data/offers/` 디렉토리에 JSON 파일 추가:
```json
[
  {
    "id": "new_offer_id",
    "category": "internet",
    "name": "새로운 인터넷 상품",
    "base_fee": 30000,
    "benefit_cash": 200000,
    "benefit_coupon": 0,
    "min_contract_months": 24,
    "conditions": ["new_customer_only"]
  }
]
```

### 지원되는 조건 목록
- `new_customer_only`: 신규 고객 전용
- `existing_customer_bonus`: 기존 고객 혜택
- `5g_coverage_required`: 5G 커버리지 필요
- `installation_required`: 설치 필요
- `summer_promo`: 여름 프로모션

## 🚨 문제 해결

### DAG가 UI에 보이지 않을 때
1. `dags/` 경로 확인
2. Python 문법 오류 체크
3. `start_date`를 과거로 설정
4. Airflow 재시작

### 권한 문제
```bash
chmod +x airflow-home/dags/ajd_benefit_optimizer.py
```

### 로그 확인
Airflow UI → DAGs → ajd_benefit_optimizer → Graph → 각 태스크 클릭 → Logs
