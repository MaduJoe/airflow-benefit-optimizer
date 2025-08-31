# Airflow uv 환경 설정 스크립트 (Windows PowerShell)
# 실행: .\setup_uv.ps1

Write-Host "🚀 Airflow uv 환경 설정을 시작합니다..." -ForegroundColor Green

# 1. uv 가상환경 생성
Write-Host "📦 Python 3.11 가상환경 생성 중..." -ForegroundColor Yellow
uv venv -p 3.11 .venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 가상환경 생성 실패. uv가 설치되어 있는지 확인하세요." -ForegroundColor Red
    exit 1
}
# 2. 가상환경 활성화
Write-Host "🔧 가상환경 활성화 중..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# 3. 환경 변수 설정
$env:AIRFLOW_VERSION = "2.9.2"
$env:PYTHON_VERSION = "3.11"
$env:CONSTRAINT_URL = "https://raw.githubusercontent.com/apache/airflow/constraints-$env:AIRFLOW_VERSION/constraints-$env:PYTHON_VERSION.txt"
$env:AIRFLOW_HOME = $PWD.Path

Write-Host "📥 Airflow 패키지 설치 중..." -ForegroundColor Yellow
Write-Host "   버전: $env:AIRFLOW_VERSION" -ForegroundColor Cyan
Write-Host "   제약파일: $env:CONSTRAINT_URL" -ForegroundColor Cyan

# 4. Airflow 설치
uv pip install "apache-airflow==$env:AIRFLOW_VERSION" -c $env:CONSTRAINT_URL

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Airflow 설치 실패" -ForegroundColor Red
    exit 1
}

# 5. 추가 패키지 설치
Write-Host "📊 추가 패키지 설치 중..." -ForegroundColor Yellow
uv pip install pandas sqlalchemy

# 6. Airflow 초기화
Write-Host "🗄️ Airflow 데이터베이스 초기화 중..." -ForegroundColor Yellow
airflow db migrate

# 7. 관리자 계정 생성
Write-Host "👤 관리자 계정 생성 중..." -ForegroundColor Yellow
airflow users create `
  --username admin `
  --firstname Admin `
  --lastname User `
  --role Admin `
  --email admin@example.com `
  --password admin

Write-Host "✅ 설정 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 다음 단계:" -ForegroundColor Cyan
Write-Host "   1. airflow standalone    # Airflow 실행"
Write-Host "   2. http://localhost:8080 # 브라우저에서 접속"
Write-Host "   3. admin / admin         # 로그인 정보"
Write-Host ""
Write-Host "💡 환경 변수가 설정되었습니다:" -ForegroundColor Cyan
Write-Host "   AIRFLOW_HOME = $env:AIRFLOW_HOME"
Write-Host ""
