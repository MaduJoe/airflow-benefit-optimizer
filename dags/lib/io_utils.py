"""
IO utilities for Ajd Benefit Optimizer
데이터 로드/저장/변환 관련 유틸리티
"""
import json
import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def load_json_files(directory: str, pattern: str = "*.json") -> List[Dict[str, Any]]:
    """
    지정된 디렉토리에서 JSON 파일들을 로드하여 통합 리스트로 반환
    """
    data = []
    path = Path(directory)
    
    for json_file in path.glob(pattern):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    data.extend(file_data)
                else:
                    data.append(file_data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return data


def save_to_sqlite(df: pd.DataFrame, table_name: str, db_path: str) -> None:
    """
    DataFrame을 SQLite 테이블에 upsert (if_exists='replace')
    """
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Saved {len(df)} records to {table_name} table")


def create_database_schema(db_path: str) -> None:
    """
    SQLite 데이터베이스 스키마 생성
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # offers 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id TEXT PRIMARY KEY,
            category TEXT,
            name TEXT,
            base_fee INTEGER,
            benefit_cash INTEGER,
            benefit_coupon INTEGER,
            min_contract_months INTEGER,
            conditions TEXT
        )
        """)
        
        # contracts 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            user_id TEXT,
            category TEXT,
            vendor TEXT,
            end_date TEXT,
            monthly_fee INTEGER,
            PRIMARY KEY (user_id, category)
        )
        """)
        
        # recommendations 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            recommendation_id TEXT PRIMARY KEY,
            user_id TEXT,
            offer_ids TEXT,
            total_benefit INTEGER,
            total_score REAL,
            created_at TEXT
        )
        """)
        
        conn.commit()
        print("Database schema created successfully")


def export_to_csv(data: Dict[str, Any], output_dir: str) -> str:
    """
    결과 데이터를 CSV로 내보내기
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    csv_path = Path(output_dir) / f"report_{timestamp}.csv"
    
    # 추천 결과를 DataFrame으로 변환
    if 'recommendations' in data:
        df = pd.DataFrame(data['recommendations'])
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"Report exported to {csv_path}")
        return str(csv_path)
    
    return ""


def export_summary_md(kpi_data: Dict[str, Any], output_dir: str) -> str:
    """
    KPI 요약을 마크다운으로 내보내기
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    md_path = Path(output_dir) / f"summary_{timestamp}.md"
    
    summary = f"""# 아정당 혜택 최적화 리포트 ({timestamp})

## 처리 결과
- 전체 오퍼 수: {kpi_data.get('total_offers', 0)}개
- 고유 오퍼 수: {kpi_data.get('unique_offers', 0)}개
- 중복 제거율: {kpi_data.get('dup_rate', 0):.1f}%

## 최적 조합
- 최고 총 혜택: {kpi_data.get('best_total_benefit', 0):,}원
- 선택된 오퍼 수: {kpi_data.get('selected_offers_count', 0)}개

## 카테고리별 분석
{kpi_data.get('category_breakdown', '데이터 없음')}

---
*생성일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"Summary exported to {md_path}")
    return str(md_path)
