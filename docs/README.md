# 📚 아정당 혜택 최적화 프로젝트 문서

## 📖 문서 목록

### 🎯 개요 및 시작하기
- **[프로젝트 개요](./project_overview.md)** - 전체 프로젝트 소개 및 비즈니스 모델
- **[서비스 실행 가이드](./service_execution_guide.md)** - WSL 환경에서 처음부터 끝까지 실행 방법

### 🔧 기술 문서
- **[기술 명세서](./technical_specification.md)** - 시스템 아키텍처, DAG 구조, 데이터 스키마
- **[플로우 다이어그램](./service_flow_diagram.md)** - 실행 흐름 Mermaid 다이어그램

### 🚨 문제 해결
- **[문제 해결 가이드](./troubleshooting_guide.md)** - 일반적인 문제 및 해결책

### 📊 실행 결과
- **[플로우 다이어그램 파일](./flow_diagram.mmd)** - 순수 Mermaid 파일

## 🚀 빠른 시작

### 1️⃣ 처음 사용하는 경우
1. **[프로젝트 개요](./project_overview.md)** 읽기 - 전체 프로젝트 이해
2. **[서비스 실행 가이드](./service_execution_guide.md)** 따라하기 - 환경 설정부터 실행까지
3. 문제 발생 시 **[문제 해결 가이드](./troubleshooting_guide.md)** 참조

### 2️⃣ 기술적 세부사항이 필요한 경우
1. **[기술 명세서](./technical_specification.md)** - 코드 구조 및 API 이해
2. **[플로우 다이어그램](./service_flow_diagram.md)** - 실행 흐름 시각적 이해

### 3️⃣ 프로젝트 이어서 진행하는 경우
```bash
# 1. 환경 설정 확인
cd /mnt/c/Users/jaeke/ajungdang/airflow-home
source .venv/bin/activate
export AIRFLOW_HOME=$(pwd)
export PYTHONPATH=$AIRFLOW_HOME/dags:$PYTHONPATH

# 2. Airflow 시작
airflow standalone &

# 3. DAG 실행
airflow dags trigger ajd_benefit_optimizer

# 4. 결과 확인
ls -la data/export/
sqlite3 data/ajd.db "SELECT * FROM recommendations;"
```

## 📋 프로젝트 현황 (2025-08-31 기준)

### ✅ 완료된 기능
- **DAG 설계**: 7단계 태스크 파이프라인 구현
- **비즈니스 로직**: 스코어링 및 최적화 알고리즘 완료
- **데이터 파이프라인**: JSON → SQLite → 리포트 생성 완료
- **모니터링**: KPI 로그 및 리포트 자동 생성
- **문서화**: 완전한 기술 문서 및 실행 가이드

### 📊 실행 결과 예시
- **처리 오퍼**: 9개 (인터넷 3, 모바일 3, 렌탈 3)
- **기존 계약**: 3개
- **최적 조합**: 2개 선택 (KT 인터넷 + LG 에어컨)
- **총 혜택**: 484,000원

### 🎯 면접 어피용 포인트
- **기술적 역량**: Airflow DAG, XCom, 리트라이/SLA, 데이터 파이프라인
- **비즈니스 역량**: 복잡한 최적화 알고리즘, 실시간 KPI, 확장 가능한 구조
- **운영 역량**: 완전 자동화, 모니터링, 문제 해결 가이드

## 🔄 지속적인 개선 방향

### 단기 개선 사항
- [ ] Airflow 3.0 호환성 (`schedule_interval` → `schedule`)
- [ ] 더 많은 테스트 케이스 추가
- [ ] 성능 최적화 (대용량 데이터 처리)

### 중기 확장 계획
- [ ] 다중 사용자 지원
- [ ] 외부 API 연동 (실시간 요금 정보)
- [ ] 웹 대시보드 추가
- [ ] 알림 시스템 (Slack, 이메일)

### 장기 발전 방향
- [ ] 기계학습 기반 예측 모델
- [ ] 클라우드 배포 (AWS, GCP)
- [ ] 마이크로서비스 아키텍처
- [ ] A/B 테스트 프레임워크

## 📞 문의 및 지원

### 문제 해결 순서
1. **[문제 해결 가이드](./troubleshooting_guide.md)** 확인
2. 로그 파일 확인 (`logs/` 디렉토리)
3. 환경 설정 재점검
4. 가상환경 재설정

### 개발 환경
- **OS**: WSL (Ubuntu)
- **Python**: 3.11
- **Airflow**: 2.9.2
- **Database**: SQLite 3
- **Package Manager**: uv

---
*최종 업데이트: 2025-08-31*  
*문서 버전: 1.0.0*  
*프로젝트 상태: 완료 및 실행 검증됨*
