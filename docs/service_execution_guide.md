# 서비스 실행 가이드

## 🚀 완전 실행 가이드 (WSL 환경)

### 1️⃣ 환경 설정

#### WSL 진입 및 디렉토리 이동
```bash
# PowerShell에서 WSL 진입
wsl

# 프로젝트 디렉토리로 이동
cd /mnt/c/Users/jaeke/ajungdang/airflow-home

# 현재 위치 확인
pwd
ls -la
```

#### Python 가상환경 설정
```bash
# uv로 가상환경 생성 (Python 3.11)
uv venv -p 3.11 .venv

# 가상환경 활성화
source .venv/bin/activate

# 가상환경 확인 (프롬프트에 (.venv) 표시)
which python
python --version
```

### 2️⃣ Airflow 설치 및 설정

#### 의존성 설치
```bash
# Airflow 버전 설정
export AIRFLOW_VERSION=2.9.2
export PYTHON_VERSION=3.11
export CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Airflow 설치
uv pip install "apache-airflow==${AIRFLOW_VERSION}" -c "${CONSTRAINT_URL}"

# 추가 의존성 설치
uv pip install pandas>=1.5.0 sqlalchemy>=1.4.0

# 설치 확인
airflow version
```

#### Airflow 초기화
```bash
# Airflow 홈 디렉토리 설정
export AIRFLOW_HOME=/mnt/c/Users/jaeke/ajungdang/airflow-home

# 환경변수 확인
echo "AIRFLOW_HOME: $AIRFLOW_HOME"

# 데이터베이스 초기화
airflow db migrate

# 관리자 계정 생성
airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin
```

### 3️⃣ DAG 검증

#### DAG 파일 확인
```bash
# Python 경로 설정 (lib 모듈 인식용)
export PYTHONPATH=$AIRFLOW_HOME/dags:$PYTHONPATH

# DAG 파일 구문 검사
python dags/ajd_benefit_optimizer.py

# DAG 목록 확인
airflow dags list | grep ajd

# DAG 상세 구조 확인
airflow dags show ajd_benefit_optimizer
```

### 4️⃣ 서비스 시작

#### 방법 1: 스탠드얼론 모드 (권장)
```bash
# 백그라운드 실행
airflow standalone &

# 포그라운드 실행 (로그 확인용)
airflow standalone
```

#### 방법 2: 개별 서비스 실행
```bash
# 터미널 1: 웹서버
airflow webserver --port 8080 &

# 터미널 2: 스케줄러  
airflow scheduler &
```

### 5️⃣ DAG 실행

#### CLI 실행
```bash
# 수동 트리거
airflow dags trigger ajd_benefit_optimizer

# 실행 상태 확인
airflow dags state ajd_benefit_optimizer $(date +%Y-%m-%d)

# 실행 이력 확인
airflow dags list-runs -d ajd_benefit_optimizer
```

#### 웹 UI 실행
1. 브라우저에서 **http://localhost:8080** 접속
2. `admin` / `admin`으로 로그인
3. `ajd_benefit_optimizer` DAG 찾기
4. 토글 스위치로 활성화
5. "Trigger DAG" 버튼 클릭

### 6️⃣ 실행 결과 확인

#### 생성된 파일 확인
```bash
# 전체 파일 구조
ls -la data/
ls -la data/export/

# SQLite 데이터베이스 확인
file data/ajd.db
sqlite3 data/ajd.db ".tables"
sqlite3 data/ajd.db "SELECT COUNT(*) FROM offers;"
sqlite3 data/ajd.db "SELECT * FROM recommendations;"
```

#### 리포트 파일 확인
```bash
# CSV 리포트
cat data/export/report_$(date +%Y%m%d).csv

# 마크다운 요약
cat data/export/summary_$(date +%Y%m%d).md
```

#### 태스크별 로그 확인
```bash
# 개별 태스크 로그
airflow tasks logs ajd_benefit_optimizer extract_offers $(date +%Y-%m-%d) 1
airflow tasks logs ajd_benefit_optimizer print_kpi $(date +%Y-%m-%d) 1
```

## 🎯 예상 실행 결과

### 파일 생성 순서
1. **`data/ajd.db`** - SQLite 데이터베이스 생성
2. **`data/export/`** 디렉토리 자동 생성  
3. **`data/export/report_YYYYMMDD.csv`** - 추천 결과 상세
4. **`data/export/summary_YYYYMMDD.md`** - KPI 요약

### SQLite 테이블 구조
- **`offers`**: 9개 오퍼 데이터
- **`contracts`**: 3개 기존 계약  
- **`recommendations`**: 최적화된 추천 결과

### 로그 출력 예시
```
==================================================
🎯 아정당 혜택 최적화 결과
==================================================
📊 전체 오퍼 수: 9개
🔍 고유 오퍼 수: 9개  
🗑️ 중복 제거율: 0.0%
💰 최고 총 혜택: 484,000원
🎁 번들 보너스: 0원 (mobile 미선택)
📦 선택된 오퍼: 2개

📋 카테고리별 세부사항:
  • internet: KT 1G 36개월 (295,000원)
  • rental: LG 에어컨 렌탈 (189,000원)
==================================================
```

## 🔧 문제 해결

### 일반적인 문제들
```bash
# DAG 구문 오류 체크
python -m py_compile dags/ajd_benefit_optimizer.py

# 포트 충돌 해결
netstat -tlnp | grep :8080
kill -9 <PID>

# Airflow 프로세스 정리
pkill -f airflow

# 로그 파일 확인
tail -f logs/scheduler/latest/*.log
```

### 환경 문제 해결
```bash
# 환경변수 재설정
export AIRFLOW_HOME=/mnt/c/Users/jaeke/ajungdang/airflow-home
export PYTHONPATH=$AIRFLOW_HOME/dags:$PYTHONPATH

# 가상환경 재활성화
source .venv/bin/activate

# 권한 문제 해결
chmod +x dags/ajd_benefit_optimizer.py
```

## 📅 자동 스케줄링

### 스케줄 설정
- **실행 시간**: 매일 09:00 UTC (한국시간 18:00)
- **Catchup**: False (과거 실행 건너뛰기)
- **리트라이**: 2회, 1분 간격
- **SLA**: 10분 이내 완료

### 스케줄 수정 방법
```python
# dags/ajd_benefit_optimizer.py에서 수정
schedule_interval='0 9 * * *',  # 매일 09:00 UTC
```

---
*최종 검증: 2025-08-31*  
*실행 환경: WSL + Python 3.11 + Airflow 2.9.2*
