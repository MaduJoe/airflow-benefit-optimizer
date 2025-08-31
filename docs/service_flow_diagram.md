# 아정당 혜택 최적화 서비스 전체 실행 흐름

## 📊 실행 결과 기반 플로우 다이어그램

**실행일시**: 2025-08-31 17:30:35  
**처리 결과**: 총 9개 오퍼 중 2개 선택, 484,000원 혜택

```mermaid
graph TD
    subgraph "🚀 서비스 시작"
        A1["WSL 환경<br/>+ 가상환경 활성화"]
        A2["Airflow 설치<br/>+ 환경설정"]
        A3["airflow standalone<br/>웹서버 + 스케줄러"]
        A1 --> A2 --> A3
    end
    
    subgraph "📥 입력 데이터"
        B1["data/offers/<br/>• internet.json (3개)<br/>• mobile.json (3개)<br/>• rental.json (3개)"]
        B2["data/contracts/<br/>• sample_contracts.json<br/>• u001: 인터넷(KT), 모바일(SKT)<br/>• u002: 렌탈(Coway)"]
    end
    
    subgraph "🔄 DAG 실행 (ajd_benefit_optimizer)"
        C1["⏰ 스케줄러 트리거<br/>매일 09:00 UTC"]
        C2["📥 extract_offers<br/>JSON 파일 로드 (9개)"]
        C3["📥 extract_contracts<br/>기존 계약 로드 (3개)"]
        C4["🔄 transform_clean<br/>데이터 정제 & 중복제거"]
        C5["🎯 score_and_optimize<br/>스코어링 & 최적화<br/>• KT 인터넷: 295,000원<br/>• LG 에어컨: 189,000원<br/>• 총혜택: 484,000원"]
        C6["💾 load_to_sqlite<br/>DB 저장"]
        C7["📊 export_reports<br/>리포트 생성"]
        C8["📋 print_kpi<br/>KPI 로그 출력"]
        
        C1 --> C2
        C1 --> C3
        C2 --> C4
        C3 --> C4
        C4 --> C5
        C5 --> C6
        C5 --> C7
        C6 --> C8
        C7 --> C8
    end
    
    subgraph "🎯 비즈니스 로직"
        D1["자격 검증<br/>• new_customer_only<br/>• 계약 만료 60일 이내"]
        D2["스코어 계산<br/>benefit_cash + benefit_coupon<br/>- switching_cost - penalty<br/>+ expiry_bonus"]
        D3["카테고리별 최적화<br/>• internet: 최고 스코어<br/>• mobile: 자격 없음<br/>• rental: 최고 스코어"]
        D4["번들 보너스<br/>internet + mobile = +50,000원<br/>(미적용: mobile 선택 안됨)"]
        
        C5 --> D1 --> D2 --> D3 --> D4
    end
    
    subgraph "📤 출력 결과"
        E1["💽 data/ajd.db<br/>• offers (9개)<br/>• contracts (3개)<br/>• recommendations (2개)"]
        E2["📄 data/export/<br/>• report_20250831.csv<br/>• summary_20250831.md"]
        E3["🖥️ Airflow 로그<br/>🎯 아정당 혜택 최적화 결과<br/>📊 전체 오퍼 수: 9개<br/>💰 최고 총 혜택: 484,000원<br/>📦 선택된 오퍼: 2개"]
    end
    
    subgraph "🌐 모니터링"
        F1["Airflow UI<br/>http://localhost:8080<br/>admin/admin"]
        F2["CLI 명령어<br/>airflow dags trigger<br/>airflow tasks logs"]
        F3["SQLite 조회<br/>sqlite3 data/ajd.db<br/>.tables, SELECT *"]
    end
    
    B1 -.->|데이터 입력| C2
    B2 -.->|데이터 입력| C3
    A3 -->|DAG 실행| C1
    
    C6 -.->|데이터 저장| E1
    C7 -.->|파일 생성| E2
    C8 -.->|로그 출력| E3
    
    A3 -.->|웹 접속| F1
    C1 -.->|CLI 제어| F2
    E1 -.->|DB 조회| F3
    
    style A3 fill:#e1f5fe
    style C5 fill:#f3e5f5
    style E1 fill:#e8f5e8
    style E2 fill:#fff3e0
    style E3 fill:#fce4ec
```

## 📋 실행 흐름 상세 설명

### 1️⃣ 서비스 시작 단계
- **WSL 환경**: Linux 환경에서 실행
- **가상환경**: uv로 Python 3.11 환경 구성
- **Airflow 설치**: apache-airflow 2.9.2 + 의존성

### 2️⃣ 입력 데이터 구조
- **오퍼 데이터**: 9개 상품 (인터넷 3개, 모바일 3개, 렌탈 3개)
- **계약 데이터**: 3개 기존 계약 (u001: 2개, u002: 1개)

### 3️⃣ DAG 실행 프로세스
1. **extract_offers**: JSON 파일에서 9개 오퍼 로드
2. **extract_contracts**: 3개 기존 계약 로드
3. **transform_clean**: 데이터 검증 및 정제
4. **score_and_optimize**: 비즈니스 룰 적용 최적화
5. **load_to_sqlite**: 결과를 SQLite DB에 저장
6. **export_reports**: CSV/MD 리포트 생성
7. **print_kpi**: KPI 로그 출력

### 4️⃣ 비즈니스 로직 핵심
- **자격 검증**: 신규 고객 조건, 계약 만료 임박 확인
- **스코어 계산**: 혜택 - 비용 + 보너스
- **카테고리별 제약**: 각 카테고리 최대 1개 선택
- **번들 보너스**: 인터넷+모바일 조합 시 추가 혜택

### 5️⃣ 실제 실행 결과 (2025-08-31)
- **선택된 오퍼**: 
  - KT 1G 36개월 (인터넷): 295,000원
  - LG 에어컨 렌탈: 189,000원
- **총 혜택**: 484,000원
- **모바일**: 자격 조건 미충족으로 미선택

### 6️⃣ 출력 및 모니터링
- **데이터베이스**: `data/ajd.db` SQLite 파일
- **리포트**: CSV (상세), MD (요약)
- **로그**: Airflow UI 및 CLI로 실시간 모니터링

## 🔧 실행 명령어 요약

```bash
# 환경 설정
cd /mnt/c/Users/jaeke/ajungdang/airflow-home
source .venv/bin/activate
export AIRFLOW_HOME=$(pwd)

# 서비스 시작
airflow standalone &

# DAG 실행
airflow dags trigger ajd_benefit_optimizer

# 결과 확인
sqlite3 data/ajd.db "SELECT * FROM recommendations;"
cat data/export/summary_$(date +%Y%m%d).md
```

---
*생성일시: 2025-08-31*  
*기반 데이터: 실제 DAG 실행 결과*
