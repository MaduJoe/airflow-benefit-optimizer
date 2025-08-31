# 아정당 혜택 최적화 프로젝트 - 전체 개요

## 📋 프로젝트 소개

### 🎯 목표
- **목적**: 아정당 유사 시나리오의 혜택·지원금 최적 조합을 Airflow DAG로 자동화
- **포커스**: DAG 설계, 의존성/리트라이, 스케줄링, XCom, idempotency, KPI 리포팅
- **기술스택**: Apache Airflow 2.9.2, Python 3.11, SQLite, pandas, uv

### 🏗️ 아키텍처 개요
```
WSL Environment
├── Airflow Scheduler (매일 09:00 UTC)
├── DAG Pipeline (7단계)
├── SQLite Database (data/ajd.db)
├── JSON Input Files (9개 오퍼, 3개 계약)
└── Export Reports (CSV/MD)
```

## 📊 비즈니스 모델

### 카테고리
- **인터넷/TV**: SKT, KT, LG U+
- **모바일**: 5G/LTE 요금제
- **가전렌탈**: 정수기, 에어컨, 세탁기

### 최적화 알고리즘
```
총혜택 = benefit_cash + benefit_coupon - switching_cost - same_vendor_penalty + expiry_bonus + bundle_bonus
```

### 제약 조건
- 카테고리별 최대 1개 선택
- 신규 고객 전용 조건 확인
- 계약 만료 60일 이내 전환 가능
- 번들 보너스: internet + mobile = +50,000원

## 🎯 면접 어필 포인트

### ✅ 기술적 역량
- **DAG 설계**: 7개 태스크의 명확한 의존성 체인
- **XCom 활용**: 태스크 간 데이터 전송 최적화
- **리트라이/SLA**: 실패 복구 및 성능 모니터링
- **데이터 파이프라인**: Extract → Transform → Load → Report

### ✅ 비즈니스 역량  
- **복잡한 스코어링**: 다중 조건 최적화 알고리즘
- **실시간 KPI**: 자동화된 성과 지표 계산
- **확장성**: 새로운 카테고리/룰 추가 용이
- **모니터링**: 실시간 로그 및 리포트 생성

## 📈 실행 결과 예시 (2025-08-31)

### 처리 현황
- **전체 오퍼**: 9개
- **기존 계약**: 3개  
- **선택된 오퍼**: 2개
- **총 혜택**: 484,000원

### 최적 조합
- **KT 1G 36개월** (인터넷): 295,000원
- **LG 에어컨 렌탈**: 189,000원
- **모바일**: 자격 조건 미충족으로 미선택

## 📁 관련 문서

1. **[서비스 실행 가이드](./service_execution_guide.md)** - 전체 실행 방법
2. **[기술 명세서](./technical_specification.md)** - 코드 구조 및 API
3. **[플로우 다이어그램](./service_flow_diagram.md)** - 실행 흐름 시각화
4. **[문제 해결 가이드](./troubleshooting_guide.md)** - 트러블슈팅

---
*최종 업데이트: 2025-08-31*  
*프로젝트 상태: 완료 및 검증됨*
