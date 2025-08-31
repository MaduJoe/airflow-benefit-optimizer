"""
Scoring and optimization logic for Ajd Benefit Optimizer
스코어링 및 최적화 로직
"""
from typing import Dict, List, Any, Tuple
from itertools import combinations
from .rules import (
    check_eligibility, calculate_switching_cost, calculate_same_vendor_penalty,
    calculate_expiry_bonus, calculate_bundle_bonus
)


def calculate_offer_score(offer: Dict[str, Any], contracts: List[Dict[str, Any]], user_id: str = "u001") -> Tuple[int, Dict[str, Any]]:
    """
    개별 오퍼의 스코어 계산
    총혜택 = benefit_cash + benefit_coupon - switching_cost - penalty + bonus
    """
    # 기본 혜택
    base_benefit = offer['benefit_cash'] + offer.get('benefit_coupon', 0)
    
    # 비용 계산
    switching_cost = calculate_switching_cost(offer, contracts, user_id)
    same_vendor_penalty = calculate_same_vendor_penalty(offer, contracts, user_id)
    
    # 보너스 계산
    expiry_bonus_rate = calculate_expiry_bonus(contracts, user_id)
    expiry_bonus = int(base_benefit * expiry_bonus_rate)
    
    # 총 혜택 계산
    total_benefit = base_benefit - switching_cost - same_vendor_penalty + expiry_bonus
    
    # 스코어 세부사항
    score_details = {
        'base_benefit': base_benefit,
        'switching_cost': switching_cost,
        'same_vendor_penalty': same_vendor_penalty,
        'expiry_bonus': expiry_bonus,
        'total_benefit': total_benefit
    }
    
    return total_benefit, score_details


def find_optimal_combination(offers: List[Dict[str, Any]], contracts: List[Dict[str, Any]], user_id: str = "u001") -> Dict[str, Any]:
    """
    카테고리별 최대 1개 선택 제약 하에서 최적 조합 찾기
    """
    # 카테고리별로 오퍼 그룹화
    offers_by_category = {}
    for offer in offers:
        category = offer['category']
        if category not in offers_by_category:
            offers_by_category[category] = []
        offers_by_category[category].append(offer)
    
    # 카테고리별 최고 스코어 오퍼 선택
    selected_offers = []
    total_score = 0
    category_scores = {}
    
    for category, category_offers in offers_by_category.items():
        best_offer = None
        best_score = -float('inf')
        best_details = None
        
        for offer in category_offers:
            # 자격 확인
            if not check_eligibility(offer, contracts, user_id):
                continue
            
            score, details = calculate_offer_score(offer, contracts, user_id)
            
            if score > best_score:
                best_score = score
                best_offer = offer
                best_details = details
        
        if best_offer:
            selected_offers.append(best_offer)
            total_score += best_score
            category_scores[category] = {
                'offer': best_offer,
                'score': best_score,
                'details': best_details
            }
    
    # 번들 보너스 적용
    bundle_bonus = calculate_bundle_bonus(selected_offers)
    total_score += bundle_bonus
    
    return {
        'selected_offers': selected_offers,
        'total_score': total_score,
        'bundle_bonus': bundle_bonus,
        'category_scores': category_scores,
        'selected_count': len(selected_offers)
    }


def calculate_kpi_metrics(offers: List[Dict[str, Any]], optimization_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    KPI 메트릭 계산
    """
    # 카테고리별 분석
    category_breakdown = {}
    for category, score_info in optimization_result['category_scores'].items():
        category_breakdown[category] = {
            'selected_offer': score_info['offer']['name'],
            'benefit': score_info['details']['total_benefit'],
            'base_benefit': score_info['details']['base_benefit'],
            'costs': score_info['details']['switching_cost'] + score_info['details']['same_vendor_penalty']
        }
    
    # 전체 통계
    total_offers = len(offers)
    unique_ids = set(offer['id'] for offer in offers)
    unique_offers = len(unique_ids)
    dup_rate = ((total_offers - unique_offers) / total_offers * 100) if total_offers > 0 else 0
    
    kpi_data = {
        'total_offers': total_offers,
        'unique_offers': unique_offers,
        'dup_rate': dup_rate,
        'best_total_benefit': optimization_result['total_score'],
        'selected_offers_count': optimization_result['selected_count'],
        'bundle_bonus': optimization_result['bundle_bonus'],
        'category_breakdown': category_breakdown
    }
    
    return kpi_data


def prepare_recommendations_data(optimization_result: Dict[str, Any], user_id: str = "u001") -> List[Dict[str, Any]]:
    """
    추천 결과를 저장용 형태로 변환
    """
    from datetime import datetime
    
    recommendations = []
    
    for offer in optimization_result['selected_offers']:
        rec = {
            'recommendation_id': f"{user_id}_{offer['category']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'user_id': user_id,
            'offer_id': offer['id'],
            'offer_name': offer['name'],
            'category': offer['category'],
            'total_benefit': optimization_result['category_scores'][offer['category']]['details']['total_benefit'],
            'created_at': datetime.now().isoformat()
        }
        recommendations.append(rec)
    
    return recommendations
