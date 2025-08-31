# 기술 명세서

## 🏗️ 시스템 아키텍처

### 전체 구조
```
airflow-home/
├── dags/
│   ├── ajd_benefit_optimizer.py     # 메인 DAG
│   └── lib/
│       ├── __init__.py
│       ├── io_utils.py              # 데이터 I/O
│       ├── rules.py                 # 비즈니스 룰
│       └── scoring.py               # 스코어링 로직
├── data/
│   ├── offers/                      # 입력: 오퍼 데이터
│   ├── contracts/                   # 입력: 기존 계약
│   ├── ajd.db                       # 출력: SQLite DB
│   └── export/                      # 출력: 리포트
├── docs/                            # 문서
└── requirements.txt                 # 의존성
```

### 기술 스택
- **Orchestration**: Apache Airflow 2.9.2
- **Language**: Python 3.11
- **Database**: SQLite 3
- **Data Processing**: pandas 1.5.0+, sqlalchemy 1.4.0+
- **Package Manager**: uv
- **Environment**: WSL (Ubuntu)

## 📊 DAG 구조 상세

### DAG 설정
```python
dag = DAG(
    'ajd_benefit_optimizer',
    default_args={
        'owner': 'ajungdang',
        'retries': 2,
        'retry_delay': timedelta(minutes=1),
        'execution_timeout': timedelta(minutes=5),
        'sla': timedelta(minutes=10)
    },
    schedule_interval='0 9 * * *',  # 매일 09:00 UTC
    catchup=False,
    tags=['benefit', 'optimization', 'ajungdang']
)
```

### 태스크 의존성
```
extract_offers ────┐
                   ├──> transform_clean ──> score_and_optimize ┌──> load_to_sqlite ────┐
extract_contracts ─┘                                          └──> export_reports ──┴──> print_kpi
```

### 태스크별 상세 기능

#### 1. extract_offers
- **목적**: JSON 파일에서 오퍼 데이터 로드
- **입력**: `data/offers/*.json`
- **출력**: XCom `offers_raw`
- **처리량**: 9개 오퍼 (internet: 3, mobile: 3, rental: 3)

#### 2. extract_contracts  
- **목적**: 기존 계약 데이터 로드
- **입력**: `data/contracts/*.json`
- **출력**: XCom `contracts_raw`
- **처리량**: 3개 계약

#### 3. transform_clean
- **목적**: 데이터 정제 및 중복 제거
- **입력**: XCom `offers_raw`, `contracts_raw`
- **처리**: 
  - 유효성 검증 (`validate_offer_data`)
  - 중복 제거 (`deduplicate_offers`)
  - DataFrame 변환
- **출력**: XCom `offers_df`, `contracts_df`, `offers_clean`

#### 4. score_and_optimize
- **목적**: 스코어링 및 최적 조합 계산
- **입력**: XCom `offers_clean`, `contracts_df`
- **처리**:
  - 자격 검증 (`check_eligibility`)
  - 스코어 계산 (`calculate_offer_score`)
  - 카테고리별 최적화 (`find_optimal_combination`)
  - KPI 계산 (`calculate_kpi_metrics`)
- **출력**: XCom `best_bundle`, `kpi`, `recommendations`

#### 5. load_to_sqlite
- **목적**: SQLite 데이터베이스에 저장
- **입력**: XCom `offers_df`, `contracts_df`, `recommendations`
- **처리**:
  - 스키마 생성 (`create_database_schema`)
  - 데이터 저장 (`save_to_sqlite`)
- **출력**: `data/ajd.db`

#### 6. export_reports
- **목적**: CSV/MD 리포트 생성
- **입력**: XCom `recommendations`, `kpi`
- **처리**:
  - CSV 내보내기 (`export_to_csv`)
  - 마크다운 요약 (`export_summary_md`)
- **출력**: `data/export/report_YYYYMMDD.csv`, `summary_YYYYMMDD.md`

#### 7. print_kpi
- **목적**: KPI 로그 출력
- **입력**: XCom `kpi`
- **출력**: Airflow 로그

## 🎯 비즈니스 로직 상세

### 스코어링 공식
```python
def calculate_offer_score(offer, contracts, user_id="u001"):
    base_benefit = offer['benefit_cash'] + offer.get('benefit_coupon', 0)
    switching_cost = calculate_switching_cost(offer, contracts, user_id)
    same_vendor_penalty = calculate_same_vendor_penalty(offer, contracts, user_id)
    expiry_bonus_rate = calculate_expiry_bonus(contracts, user_id)
    expiry_bonus = int(base_benefit * expiry_bonus_rate)
    
    total_benefit = base_benefit - switching_cost - same_vendor_penalty + expiry_bonus
    return total_benefit
```

### 자격 검증 로직
```python
def check_eligibility(offer, contracts, user_id="u001"):
    # 신규 고객 전용 조건
    if "new_customer_only" in offer.get('conditions', []):
        existing_contracts = [c for c in contracts 
                            if c['user_id'] == user_id 
                            and c['category'] == offer['category']]
        if existing_contracts:
            return False
    
    # 만료 임박 확인 (60일 이내)
    for contract in existing_contracts:
        end_date = datetime.strptime(contract['end_date'], "%Y-%m-%d")
        if (end_date - datetime.now()).days > 60:
            return False
    
    return True
```

### 최적화 알고리즘
```python
def find_optimal_combination(offers, contracts, user_id="u001"):
    # 카테고리별 그룹화
    offers_by_category = {}
    for offer in offers:
        category = offer['category']
        if category not in offers_by_category:
            offers_by_category[category] = []
        offers_by_category[category].append(offer)
    
    # 카테고리별 최고 스코어 선택
    selected_offers = []
    total_score = 0
    
    for category, category_offers in offers_by_category.items():
        best_offer = None
        best_score = -float('inf')
        
        for offer in category_offers:
            if not check_eligibility(offer, contracts, user_id):
                continue
            
            score, details = calculate_offer_score(offer, contracts, user_id)
            if score > best_score:
                best_score = score
                best_offer = offer
        
        if best_offer:
            selected_offers.append(best_offer)
            total_score += best_score
    
    # 번들 보너스 적용
    bundle_bonus = calculate_bundle_bonus(selected_offers)
    total_score += bundle_bonus
    
    return {
        'selected_offers': selected_offers,
        'total_score': total_score,
        'bundle_bonus': bundle_bonus,
        'selected_count': len(selected_offers)
    }
```

## 🗄️ 데이터 구조

### 입력 데이터 스키마

#### 오퍼 데이터 (offers/*.json)
```json
{
  "id": "string",                    // 고유 식별자
  "category": "internet|mobile|rental", // 카테고리
  "name": "string",                  // 상품명
  "base_fee": "integer",             // 월요금 (원)
  "benefit_cash": "integer",         // 현금혜택 (원)
  "benefit_coupon": "integer",       // 쿠폰혜택 (원)
  "min_contract_months": "integer",  // 최소계약기간 (개월)
  "conditions": ["string"]           // 조건 배열
}
```

#### 계약 데이터 (contracts/*.json)
```json
{
  "user_id": "string",               // 사용자 ID
  "category": "string",              // 카테고리
  "vendor": "string",                // 벤더명
  "end_date": "YYYY-MM-DD",          // 계약 만료일
  "monthly_fee": "integer"           // 월요금 (원)
}
```

### 출력 데이터 스키마

#### SQLite 테이블 구조
```sql
-- offers 테이블
CREATE TABLE offers (
    id TEXT PRIMARY KEY,
    category TEXT,
    name TEXT,
    base_fee INTEGER,
    benefit_cash INTEGER,
    benefit_coupon INTEGER,
    min_contract_months INTEGER,
    conditions TEXT
);

-- contracts 테이블
CREATE TABLE contracts (
    user_id TEXT,
    category TEXT,
    vendor TEXT,
    end_date TEXT,
    monthly_fee INTEGER,
    PRIMARY KEY (user_id, category)
);

-- recommendations 테이블
CREATE TABLE recommendations (
    recommendation_id TEXT PRIMARY KEY,
    user_id TEXT,
    offer_id TEXT,
    offer_name TEXT,
    category TEXT,
    total_benefit INTEGER,
    created_at TEXT
);
```

## 🔧 설정 및 환경변수

### 필수 환경변수
```bash
export AIRFLOW_HOME=/mnt/c/Users/jaeke/ajungdang/airflow-home
export PYTHONPATH=$AIRFLOW_HOME/dags:$PYTHONPATH
export AIRFLOW_VERSION=2.9.2
export PYTHON_VERSION=3.11
```

### 주요 설정 파일
- **airflow.cfg**: Airflow 전역 설정
- **requirements.txt**: Python 의존성
- **dags/ajd_benefit_optimizer.py**: DAG 설정

### 성능 및 제한사항
- **실행 시간**: 평균 30초 이내
- **메모리 사용량**: 약 100MB
- **동시 실행**: 단일 DAG 인스턴스
- **데이터 크기**: 수백 개 오퍼까지 확장 가능

## 🔍 모니터링 및 로깅

### 로그 위치
- **Airflow 로그**: `logs/dag_id/task_id/execution_date/`
- **웹서버 로그**: `logs/webserver/`
- **스케줄러 로그**: `logs/scheduler/`

### KPI 메트릭
- 전체 오퍼 수
- 고유 오퍼 수  
- 중복 제거율
- 최고 총 혜택
- 선택된 오퍼 수
- 번들 보너스
- 카테고리별 분석

### 모니터링 도구
- **Airflow UI**: http://localhost:8080
- **CLI**: `airflow dags`, `airflow tasks`
- **SQLite**: 직접 쿼리를 통한 데이터 확인

---
*최종 업데이트: 2025-08-31*  
*버전: 1.0.0*
