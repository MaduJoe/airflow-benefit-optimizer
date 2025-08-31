"""
Business rules for Ajd Benefit Optimizer
비즈니스 룰 및 조건 검증 로직
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd


def check_eligibility(offer: Dict[str, Any], contracts: List[Dict[str, Any]], user_id: str = "u001") -> bool:
    """
    사용자가 특정 오퍼에 대해 자격이 있는지 확인
    """
    # 동일 카테고리 기존 계약 확인
    existing_contracts = [c for c in contracts if c['user_id'] == user_id and c['category'] == offer['category']]
    
    # new_customer_only 조건 확인
    if "new_customer_only" in offer.get('conditions', []):
        if existing_contracts:
            return False
    
    # 만료 임박 확인 (60일 이내)
    for contract in existing_contracts:
        end_date = datetime.strptime(contract['end_date'], "%Y-%m-%d")
        if (end_date - datetime.now()).days > 60:
            return False  # 아직 만료가 멀음
    
    return True


def calculate_switching_cost(offer: Dict[str, Any], contracts: List[Dict[str, Any]], user_id: str = "u001") -> int:
    """
    기존 계약에서 전환 시 발생하는 비용 계산
    """
    switching_cost = 0
    
    # 동일 카테고리 기존 계약 찾기
    existing_contracts = [c for c in contracts if c['user_id'] == user_id and c['category'] == offer['category']]
    
    for contract in existing_contracts:
        end_date = datetime.strptime(contract['end_date'], "%Y-%m-%d")
        days_remaining = (end_date - datetime.now()).days
        
        # 조기 해지 수수료 (남은 기간에 비례)
        if days_remaining > 0:
            early_termination_fee = min(100000, contract['monthly_fee'] * (days_remaining // 30))
            switching_cost += early_termination_fee
    
    return switching_cost


def calculate_same_vendor_penalty(offer: Dict[str, Any], contracts: List[Dict[str, Any]], user_id: str = "u001") -> int:
    """
    동일 벤더 재계약 시 페널티 계산
    """
    # 오퍼에서 벤더 추출 (name에서 첫 번째 단어)
    offer_vendor = offer['name'].split()[0]
    
    # 동일 카테고리, 동일 벤더 기존 계약 확인
    same_vendor_contracts = [
        c for c in contracts 
        if c['user_id'] == user_id 
        and c['category'] == offer['category'] 
        and c['vendor'].upper() == offer_vendor.upper()
    ]
    
    if same_vendor_contracts:
        return 20000  # 고정 페널티
    
    return 0


def calculate_expiry_bonus(contracts: List[Dict[str, Any]], user_id: str = "u001") -> float:
    """
    만기 임박 보너스 계산 (총혜택에 5% 가산)
    """
    for contract in contracts:
        if contract['user_id'] == user_id:
            end_date = datetime.strptime(contract['end_date'], "%Y-%m-%d")
            days_remaining = (end_date - datetime.now()).days
            
            if 0 <= days_remaining <= 60:
                return 0.05  # 5% 보너스
    
    return 0.0


def calculate_bundle_bonus(selected_offers: List[Dict[str, Any]]) -> int:
    """
    번들 보너스 계산 (internet + mobile 조합 시 +50,000원)
    """
    categories = {offer['category'] for offer in selected_offers}
    
    if 'internet' in categories and 'mobile' in categories:
        return 50000
    
    return 0


def deduplicate_offers(offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    중복 오퍼 제거 (같은 ID 기준)
    """
    seen_ids = set()
    unique_offers = []
    
    for offer in offers:
        if offer['id'] not in seen_ids:
            unique_offers.append(offer)
            seen_ids.add(offer['id'])
    
    return unique_offers


def validate_offer_data(offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    오퍼 데이터 유효성 검증 및 정제
    """
    valid_offers = []
    
    for offer in offers:
        # 필수 필드 확인
        required_fields = ['id', 'category', 'name', 'base_fee', 'benefit_cash']
        if all(field in offer for field in required_fields):
            # 기본값 설정
            offer.setdefault('benefit_coupon', 0)
            offer.setdefault('min_contract_months', 12)
            offer.setdefault('conditions', [])
            
            valid_offers.append(offer)
        else:
            print(f"Invalid offer data: {offer}")
    
    return valid_offers
