#!/bin/bash
# Airflow uv 환경 설정 스크립트 (Linux/Mac)
# 실행: chmod +x setup_uv.sh && ./setup_uv.sh

echo "🚀 Airflow uv 환경 설정을 시작합니다..."

# 1. uv 가상환경 생성
echo "📦 Python 3.11 가상환경 생성 중..."
uv venv -p 3.11 .venv

if [ $? -ne 0 ]; then
    echo "❌ 가상환경 생성 실패. uv가 설치되어 있는지 확인하세요."
    exit 1
fi

# 2. 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source .venv/bin/activate

# 3. 환경 변수 설정
export AIRFLOW_VERSION=2.9.2
export PYTHON_VERSION=3.11
export CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
export AIRFLOW_HOME=$(pwd)

echo "📥 Airflow 패키지 설치 중..."
echo "   버전: $AIRFLOW_VERSION"
echo "   제약파일: $CONSTRAINT_URL"

# 4. Airflow 설치
uv pip install "apache-airflow==${AIRFLOW_VERSION}" -c "${CONSTRAINT_URL}"

if [ $? -ne 0 ]; then
    echo "❌ Airflow 설치 실패"
    exit 1
fi

# 5. 추가 패키지 설치
echo "📊 추가 패키지 설치 중..."
uv pip install pandas sqlalchemy

# 6. Airflow 초기화
echo "🗄️ Airflow 데이터베이스 초기화 중..."
airflow db migrate

# 7. 관리자 계정 생성
echo "👤 관리자 계정 생성 중..."
airflow users create \
  --username admin --firstname Admin --lastname User \
  --role Admin --email admin@example.com --password admin

echo "✅ 설정 완료!"
echo ""
echo "🎯 다음 단계:"
echo "   1. airflow standalone    # Airflow 실행"
echo "   2. http://localhost:8080 # 브라우저에서 접속"
echo "   3. admin / PxDdG3nGDsBnHGDH         # 로그인 정보"
echo ""
echo "💡 환경 변수가 설정되었습니다:"
echo "   AIRFLOW_HOME = $AIRFLOW_HOME"
echo ""
echo "🔄 새 터미널에서 작업할 때:"
echo "   source .venv/bin/activate"
echo "   export AIRFLOW_HOME=$(pwd)"
