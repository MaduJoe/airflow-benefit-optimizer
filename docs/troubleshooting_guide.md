# 문제 해결 가이드

## 🚨 일반적인 문제 및 해결책

### 1️⃣ DAG 관련 문제

#### DAG가 UI에 나타나지 않음
**증상**: Airflow UI에서 `ajd_benefit_optimizer` DAG를 찾을 수 없음

**원인 및 해결책**:
```bash
# 1. AIRFLOW_HOME 경로 확인
echo $AIRFLOW_HOME
export AIRFLOW_HOME=/mnt/c/Users/jaeke/ajungdang/airflow-home

# 2. DAG 파일 경로 확인
ls -la $AIRFLOW_HOME/dags/ajd_benefit_optimizer.py

# 3. Python 구문 오류 체크
python $AIRFLOW_HOME/dags/ajd_benefit_optimizer.py

# 4. PYTHONPATH 설정
export PYTHONPATH=$AIRFLOW_HOME/dags:$PYTHONPATH

# 5. DAG 목록 새로고침
airflow dags list | grep ajd
```

#### ImportError: No module named 'lib'
**증상**: `ModuleNotFoundError: No module named 'lib'`

**해결책**:
```bash
# 1. Python 경로 설정
export PYTHONPATH=$AIRFLOW_HOME/dags:$PYTHONPATH

# 2. lib 디렉토리 확인
ls -la $AIRFLOW_HOME/dags/lib/

# 3. __init__.py 파일 확인
ls -la $AIRFLOW_HOME/dags/lib/__init__.py

# 4. 권한 확인 및 수정
chmod +x $AIRFLOW_HOME/dags/lib/*.py
```

#### DAG 구문 오류
**증상**: DAG가 로드되지 않거나 오류 표시

**디버깅 방법**:
```bash
# 1. 직접 Python 실행
cd $AIRFLOW_HOME
python dags/ajd_benefit_optimizer.py

# 2. 구문 검사
python -m py_compile dags/ajd_benefit_optimizer.py

# 3. import 테스트
python -c "from dags.lib import io_utils, rules, scoring"

# 4. Airflow에서 구문 체크
airflow dags show ajd_benefit_optimizer
```

### 2️⃣ 실행 관련 문제

#### 태스크 실행 실패
**증상**: 특정 태스크가 실패하고 재시도하지 않음

**로그 확인**:
```bash
# 1. 태스크 로그 확인
airflow tasks logs ajd_benefit_optimizer <task_id> $(date +%Y-%m-%d) 1

# 2. 전체 DAG 실행 상태
airflow dags state ajd_benefit_optimizer $(date +%Y-%m-%d)

# 3. 실패한 태스크 재실행
airflow tasks run ajd_benefit_optimizer <task_id> $(date +%Y-%m-%d)
```

**일반적인 해결책**:
```bash
# 1. 데이터 파일 존재 확인
ls -la data/offers/
ls -la data/contracts/

# 2. 디렉토리 권한 확인
chmod -R 755 data/

# 3. SQLite 파일 권한
chmod 666 data/ajd.db  # 파일이 있는 경우
```

#### XCom 데이터 전송 오류
**증상**: `KeyError: 'offers_raw'` 또는 XCom 키를 찾을 수 없음

**해결책**:
```bash
# 1. XCom 데이터 확인 (Airflow UI > Admin > XComs)
# 2. 이전 태스크 성공 여부 확인
airflow tasks state ajd_benefit_optimizer extract_offers $(date +%Y-%m-%d)

# 3. 태스크 의존성 재확인
airflow dags show ajd_benefit_optimizer
```

### 3️⃣ 환경 관련 문제

#### 가상환경 문제
**증상**: 패키지 import 오류 또는 Python 버전 불일치

**해결책**:
```bash
# 1. 가상환경 재활성화
source .venv/bin/activate

# 2. Python 경로 확인
which python
python --version

# 3. 패키지 재설치
uv pip install --force-reinstall apache-airflow pandas sqlalchemy

# 4. 가상환경 재생성 (필요시)
rm -rf .venv
uv venv -p 3.11 .venv
source .venv/bin/activate
```

#### 포트 충돌 문제
**증상**: `OSError: [Errno 98] Address already in use`

**해결책**:
```bash
# 1. 포트 사용 프로세스 확인
netstat -tlnp | grep :8080
lsof -i :8080

# 2. 프로세스 종료
kill -9 <PID>

# 3. Airflow 프로세스 정리
pkill -f airflow

# 4. 다른 포트 사용
airflow webserver --port 8081
```

### 4️⃣ 데이터베이스 관련 문제

#### SQLite 파일 생성 안됨
**증상**: `data/ajd.db` 파일이 생성되지 않음

**해결책**:
```bash
# 1. 디렉토리 존재 확인
mkdir -p data

# 2. 권한 확인
chmod 755 data/

# 3. 수동 테이블 생성
cd $AIRFLOW_HOME
python -c "
from dags.lib.io_utils import create_database_schema
create_database_schema('data/ajd.db')
print('테이블 생성 완료!')
"

# 4. SQLite 설치 확인
sqlite3 --version
```

#### SQLite 권한 오류
**증상**: `PermissionError: [Errno 13] Permission denied`

**해결책**:
```bash
# 1. 파일 권한 수정
chmod 666 data/ajd.db

# 2. 디렉토리 권한 수정
chmod 755 data/

# 3. 소유자 확인
ls -la data/ajd.db

# 4. 소유자 변경 (필요시)
chown $USER:$USER data/ajd.db
```

### 5️⃣ 네트워크 및 접속 문제

#### Airflow UI 접속 안됨
**증상**: http://localhost:8080 접속 실패

**해결책**:
```bash
# 1. 웹서버 실행 상태 확인
ps aux | grep airflow

# 2. 로그 확인
tail -f logs/webserver/*.log

# 3. 방화벽 확인 (WSL)
# Windows 방화벽에서 8080 포트 허용

# 4. 서비스 재시작
pkill -f "airflow webserver"
airflow webserver --port 8080 &
```

#### WSL 네트워크 문제
**증상**: WSL에서 localhost 접속 안됨

**해결책**:
```bash
# 1. WSL IP 확인
ip addr show eth0

# 2. Windows에서 WSL IP로 접속
# http://<WSL_IP>:8080

# 3. 포트 포워딩 설정 (PowerShell 관리자 권한)
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=<WSL_IP>
```

### 6️⃣ 성능 관련 문제

#### 실행 시간 초과
**증상**: 태스크가 SLA 시간(10분) 내에 완료되지 않음

**해결책**:
```bash
# 1. 데이터 크기 확인
wc -l data/offers/*.json
wc -l data/contracts/*.json

# 2. 실행 시간 제한 늘리기 (dags/ajd_benefit_optimizer.py 수정)
'execution_timeout': timedelta(minutes=15),
'sla': timedelta(minutes=20)

# 3. 리소스 모니터링
top
free -h
df -h
```

#### 메모리 부족
**증상**: `MemoryError` 또는 시스템 느려짐

**해결책**:
```bash
# 1. 메모리 사용량 확인
free -h
ps aux --sort=-%mem | head

# 2. 불필요한 프로세스 종료
pkill -f "example_"  # Airflow 예제 DAG들

# 3. 배치 크기 줄이기 (코드 수정)
# DataFrame 처리를 청크 단위로 변경
```

## 🔧 디버깅 도구 및 명령어

### 유용한 디버깅 명령어
```bash
# 1. 전체 시스템 상태
airflow version
airflow config list
airflow connections list

# 2. DAG 상태 확인
airflow dags list
airflow dags show ajd_benefit_optimizer
airflow dags state ajd_benefit_optimizer $(date +%Y-%m-%d)

# 3. 태스크 상태 확인
airflow tasks list ajd_benefit_optimizer
airflow tasks state ajd_benefit_optimizer <task_id> $(date +%Y-%m-%d)

# 4. 로그 실시간 모니터링
tail -f logs/scheduler/latest/*.log
tail -f logs/dag_id/task_id/execution_date/*.log
```

### 환경 점검 체크리스트
```bash
# 1. 기본 환경
echo "AIRFLOW_HOME: $AIRFLOW_HOME"
echo "PYTHONPATH: $PYTHONPATH"
which python
python --version

# 2. 파일 구조
ls -la $AIRFLOW_HOME/dags/
ls -la $AIRFLOW_HOME/dags/lib/
ls -la $AIRFLOW_HOME/data/

# 3. 권한 확인
ls -la $AIRFLOW_HOME/dags/ajd_benefit_optimizer.py
ls -la $AIRFLOW_HOME/data/

# 4. 프로세스 확인
ps aux | grep airflow
netstat -tlnp | grep 8080
```

## 📞 지원 및 추가 자료

### 로그 위치
- **DAG 실행 로그**: `logs/ajd_benefit_optimizer/`
- **스케줄러 로그**: `logs/scheduler/`
- **웹서버 로그**: `logs/webserver/`

### 설정 파일
- **Airflow 설정**: `airflow.cfg`
- **DAG 설정**: `dags/ajd_benefit_optimizer.py`
- **의존성**: `requirements.txt`

### 참고 문서
- [Apache Airflow 공식 문서](https://airflow.apache.org/docs/)
- [SQLite 공식 문서](https://sqlite.org/docs.html)
- [pandas 공식 문서](https://pandas.pydata.org/docs/)

---
*최종 업데이트: 2025-08-31*  
*검증 환경: WSL Ubuntu + Python 3.11 + Airflow 2.9.2*
