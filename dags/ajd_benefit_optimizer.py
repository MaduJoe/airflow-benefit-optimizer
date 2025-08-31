"""
Ajd Benefit Optimizer DAG
아정당 혜택 최적화 자동화 워크플로우

매일 09:00에 실행되어 다음 작업을 수행:
1. offers, contracts 데이터 로드
2. 데이터 정제 및 중복 제거
3. 스코어링 및 최적 조합 계산
4. SQLite DB 저장
5. 리포트 생성
6. KPI 출력
"""

from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# lib 모듈 import
from lib.io_utils import (
    load_json_files, save_to_sqlite, create_database_schema,
    export_to_csv, export_summary_md
)
from lib.rules import deduplicate_offers, validate_offer_data
from lib.scoring import find_optimal_combination, calculate_kpi_metrics, prepare_recommendations_data

# 기본 설정
BASE_DIR = Path(__file__).parent.parent  # airflow-home 디렉토리
DATA_DIR = BASE_DIR / "data"
OFFERS_DIR = DATA_DIR / "offers"
CONTRACTS_DIR = DATA_DIR / "contracts"
EXPORT_DIR = DATA_DIR / "export"
DB_PATH = DATA_DIR / "ajd.db"

# DAG 기본 인수
default_args = {
    'owner': 'ajungdang',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
    'execution_timeout': timedelta(minutes=5),
    'sla': timedelta(minutes=10)
}

# DAG 정의
dag = DAG(
    'ajd_benefit_optimizer',
    default_args=default_args,
    description='아정당 혜택 최적화 자동화',
    schedule_interval='0 9 * * *',  # 매일 09:00 (UTC)
    catchup=False,
    tags=['benefit', 'optimization', 'ajungdang']
)


def extract_offers(**context):
    """Task 1: offers 데이터 로드"""
    offers_data = load_json_files(str(OFFERS_DIR))
    print(f"Loaded {len(offers_data)} offers from JSON files")
    
    # XCom에 저장
    context['task_instance'].xcom_push(key='offers_raw', value=offers_data)
    return f"Extracted {len(offers_data)} offers"


def extract_contracts(**context):
    """Task 2: contracts 데이터 로드"""
    contracts_data = load_json_files(str(CONTRACTS_DIR))
    print(f"Loaded {len(contracts_data)} contracts from JSON files")
    
    # XCom에 저장
    context['task_instance'].xcom_push(key='contracts_raw', value=contracts_data)
    return f"Extracted {len(contracts_data)} contracts"


def transform_clean(**context):
    """Task 3: 데이터 정제 및 중복 제거"""
    # XCom에서 데이터 가져오기
    offers_raw = context['task_instance'].xcom_pull(key='offers_raw', task_ids='extract_offers')
    contracts_raw = context['task_instance'].xcom_pull(key='contracts_raw', task_ids='extract_contracts')
    
    # offers 정제
    offers_valid = validate_offer_data(offers_raw)
    offers_clean = deduplicate_offers(offers_valid)
    offers_df = pd.DataFrame(offers_clean)
    
    # conditions 리스트를 문자열로 변환 (SQLite 저장용)
    if 'conditions' in offers_df.columns:
        offers_df['conditions'] = offers_df['conditions'].apply(lambda x: ','.join(x) if x else '')
    
    # contracts 정제
    contracts_df = pd.DataFrame(contracts_raw)
    
    print(f"Cleaned data: {len(offers_clean)} offers, {len(contracts_raw)} contracts")
    
    # XCom에 저장
    context['task_instance'].xcom_push(key='offers_df', value=offers_df.to_dict('records'))
    context['task_instance'].xcom_push(key='contracts_df', value=contracts_df.to_dict('records'))
    context['task_instance'].xcom_push(key='offers_clean', value=offers_clean)
    
    return f"Transformed {len(offers_clean)} unique offers, {len(contracts_raw)} contracts"


def score_and_optimize(**context):
    """Task 4: 스코어링 및 최적 조합 계산"""
    # XCom에서 데이터 가져오기
    offers_clean = context['task_instance'].xcom_pull(key='offers_clean', task_ids='transform_clean')
    contracts_df = context['task_instance'].xcom_pull(key='contracts_df', task_ids='transform_clean')
    
    # 최적화 실행
    optimization_result = find_optimal_combination(offers_clean, contracts_df)
    
    # KPI 계산
    kpi_data = calculate_kpi_metrics(offers_clean, optimization_result)
    
    # 추천 데이터 준비
    recommendations = prepare_recommendations_data(optimization_result)
    
    print(f"Optimization complete: {optimization_result['selected_count']} offers selected")
    print(f"Total benefit: {optimization_result['total_score']:,} won")
    
    # XCom에 저장
    context['task_instance'].xcom_push(key='best_bundle', value=optimization_result)
    context['task_instance'].xcom_push(key='kpi', value=kpi_data)
    context['task_instance'].xcom_push(key='recommendations', value=recommendations)
    
    return f"Optimized to {optimization_result['total_score']:,} won total benefit"


def load_to_sqlite(**context):
    """Task 5: SQLite DB에 데이터 저장"""
    # XCom에서 데이터 가져오기
    offers_df_data = context['task_instance'].xcom_pull(key='offers_df', task_ids='transform_clean')
    contracts_df_data = context['task_instance'].xcom_pull(key='contracts_df', task_ids='transform_clean')
    recommendations = context['task_instance'].xcom_pull(key='recommendations', task_ids='score_and_optimize')
    
    # DataFrame 생성
    offers_df = pd.DataFrame(offers_df_data)
    contracts_df = pd.DataFrame(contracts_df_data)
    recommendations_df = pd.DataFrame(recommendations)
    
    # 데이터베이스 스키마 생성
    create_database_schema(str(DB_PATH))
    
    # 데이터 저장
    save_to_sqlite(offers_df, 'offers', str(DB_PATH))
    save_to_sqlite(contracts_df, 'contracts', str(DB_PATH))
    save_to_sqlite(recommendations_df, 'recommendations', str(DB_PATH))
    
    return f"Saved to database: {len(offers_df)} offers, {len(contracts_df)} contracts, {len(recommendations_df)} recommendations"


def export_reports(**context):
    """Task 6: CSV/MD 리포트 생성"""
    # XCom에서 데이터 가져오기
    recommendations = context['task_instance'].xcom_pull(key='recommendations', task_ids='score_and_optimize')
    kpi_data = context['task_instance'].xcom_pull(key='kpi', task_ids='score_and_optimize')
    
    # 리포트 생성
    EXPORT_DIR.mkdir(exist_ok=True)
    
    csv_path = export_to_csv({'recommendations': recommendations}, str(EXPORT_DIR))
    md_path = export_summary_md(kpi_data, str(EXPORT_DIR))
    
    return f"Reports exported: {csv_path}, {md_path}"


def print_kpi(**context):
    """Task 7: KPI 로그 출력"""
    kpi_data = context['task_instance'].xcom_pull(key='kpi', task_ids='score_and_optimize')
    
    print("=" * 50)
    print("🎯 아정당 혜택 최적화 결과")
    print("=" * 50)
    print(f"📊 전체 오퍼 수: {kpi_data['total_offers']}개")
    print(f"🔍 고유 오퍼 수: {kpi_data['unique_offers']}개")
    print(f"🗑️  중복 제거율: {kpi_data['dup_rate']:.1f}%")
    print(f"💰 최고 총 혜택: {kpi_data['best_total_benefit']:,}원")
    print(f"🎁 번들 보너스: {kpi_data['bundle_bonus']:,}원")
    print(f"📦 선택된 오퍼: {kpi_data['selected_offers_count']}개")
    
    if kpi_data['category_breakdown']:
        print("\n📋 카테고리별 세부사항:")
        for category, details in kpi_data['category_breakdown'].items():
            print(f"  • {category}: {details['selected_offer']} ({details['benefit']:,}원)")
    
    print("=" * 50)
    
    return "KPI logging completed"


# Task 정의
extract_offers_task = PythonOperator(
    task_id='extract_offers',
    python_callable=extract_offers,
    dag=dag
)

extract_contracts_task = PythonOperator(
    task_id='extract_contracts',
    python_callable=extract_contracts,
    dag=dag
)

transform_clean_task = PythonOperator(
    task_id='transform_clean',
    python_callable=transform_clean,
    dag=dag
)

score_and_optimize_task = PythonOperator(
    task_id='score_and_optimize',
    python_callable=score_and_optimize,
    dag=dag
)

load_to_sqlite_task = PythonOperator(
    task_id='load_to_sqlite',
    python_callable=load_to_sqlite,
    dag=dag
)

export_reports_task = PythonOperator(
    task_id='export_reports',
    python_callable=export_reports,
    dag=dag
)

print_kpi_task = PythonOperator(
    task_id='print_kpi',
    python_callable=print_kpi,
    dag=dag
)

# Task 의존성 설정
[extract_offers_task, extract_contracts_task] >> transform_clean_task
transform_clean_task >> score_and_optimize_task
score_and_optimize_task >> [load_to_sqlite_task, export_reports_task]
[load_to_sqlite_task, export_reports_task] >> print_kpi_task
