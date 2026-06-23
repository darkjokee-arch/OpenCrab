"""
layer1_role_boundary_helper.py — Layer1/Layer2 문장 역할 기반 분리 helper (PoC)

[지위] production implementation 아님. 기존 classify 결과를 대체하지 않고 그 위에 role_type/
boundary_reason/final_ontology_layer만 추가. keyword는 **signal**일 뿐 final이 아님.

핵심: Layer2 keyword(workflow factory/OpenCrab/commercial/source)가 있어도, 문장이 사용자
구조원칙/제품전략/권한경계/작업방식이면 Layer1 candidate. 실제 상품데이터/source후보/수집URL만 Layer2.

write/network/모델 0.
Reference: docs/BINGGUPACK_LAYER1_ADAPTER_CANDIDATE_INTEGRATION.md §6
"""

from __future__ import annotations

import re

# Layer2 keyword (signal only — final 아님)
_LAYER2_KW = ["workflow factory", "commercial extension", "source discovery", "유료 워크플로우",
              "opencrab", "commercial", "source candidate", "source 후보", "수집"]

# 사용자 원칙/전략/권한경계/작업방식 signal → Layer1 (Layer2 kw 있어도 override)
_PRINCIPLE = {
    "user_product_strategy": ["2차 확장", "본체", "확장 기능", "상품화", "제품 전략", "유료 워크플로우 상품"],
    "user_authority_boundary": ["authority", "권한", "save authority", "discovery는 자유", "execution은 통제",
                                "통제한다", "권한이 아니"],
    "user_development_policy": ["재사용", "새로 만들지", "다시 만들지", "wrapper", "기존 기능", "중복"],
    "user_workflow_rule": ["검증 과잉", "병렬", "preview-only", "과잉 금지", "가능한 작업"],
    "user_principle": ["능력", "무능", "원칙", "유연", "고집"],
}
# 실제 commercial/source data signal → Layer2 excluded
_COMMERCIAL = {
    "source_candidate_data": ["source 후보는", "url 후보", "후보는 a", "후보는 다음", "수집 대상은", "크롤링 대상"],
    "commercial_workflow_data": ["여행팩에", "입찰팩에", "특허팩에", "고기집팩", "kipris", "맛집 데이터", "팩 자료",
                                 "팩에 .* 넣", "데이터를 넣"],
    "external_collection_target": ["http://", "https://", "외부 api", "크롤링", "스크래핑"],
}


def _hit(text: str, pats: list[str]) -> bool:
    low = text.lower()
    return any(re.search(p, low) if any(c in p for c in ".*") else (p.lower() in low) for p in pats)


def classify_role(candidate_id: str, text: str) -> dict:
    layer2_kw = _hit(text, _LAYER2_KW)

    # 1) 실제 상품/source/수집 데이터 우선 판정 → Layer2
    for rtype, pats in _COMMERCIAL.items():
        if _hit(text, pats):
            return _result(candidate_id, text, layer2_kw, rtype, "workflow_factory",
                           f"commercial/source data signal ({rtype})", 0.8,
                           user_principle=False, commercial=True)
    # 2) 사용자 원칙/전략/권한/작업방식 → Layer1 (Layer2 kw 있어도 override)
    for rtype, pats in _PRINCIPLE.items():
        if _hit(text, pats):
            reason = ("Layer2 keyword 있으나 사용자 원칙/전략 → Layer1 override"
                      if layer2_kw else f"user principle signal ({rtype})")
            return _result(candidate_id, text, layer2_kw, rtype, "personal_ontology_core",
                           reason, 0.75, user_principle=True, commercial=False)
    # 3) 그 외: keyword만 있으면 Layer2, 없으면 Layer1(기본 personal)
    if layer2_kw:
        return _result(candidate_id, text, layer2_kw, "unknown", "workflow_factory",
                       "Layer2 keyword only, no principle signal", 0.5,
                       user_principle=False, commercial=False)
    return _result(candidate_id, text, layer2_kw, "unknown", "personal_ontology_core",
                   "no layer2 signal → default personal", 0.5,
                   user_principle=False, commercial=False)


def _result(cid, text, l2kw, role, layer, reason, conf, user_principle, commercial) -> dict:
    return {
        "candidate_id": cid, "text": text,
        "keyword_layer_guess": "workflow_factory" if l2kw else "personal_ontology_core",
        "role_type": role, "final_ontology_layer": layer,
        "boundary_reason": reason, "boundary_confidence": conf,
        "layer2_keyword_present": l2kw,
        "user_principle_signal": user_principle, "commercial_data_signal": commercial,
    }


if __name__ == "__main__":
    samples = [
        ("s1", "Workflow Factory는 2차 확장이다."),
        ("s2", "기존 기능은 새로 만들지 말고 재사용한다."),
        ("s3", "source discovery는 자유롭게 하되 execution은 통제한다."),
        ("s4", "제주 여행팩 source 후보는 A/B/C다."),
        ("s5", "특허팩에 KIPRIS 데이터를 넣는다."),
        ("s6", "semantic은 save authority가 아니다."),
    ]
    print("=== Layer1/Layer2 Role-based Boundary Helper ===")
    overrides = 0
    for cid, t in samples:
        r = classify_role(cid, t)
        ov = r["layer2_keyword_present"] and r["final_ontology_layer"] == "personal_ontology_core"
        overrides += ov
        print(f"  {cid}: kw_guess={r['keyword_layer_guess']:<20} final={r['final_ontology_layer']:<22} "
              f"role={r['role_type']:<26} {'[OVERRIDE]' if ov else ''}")
    print(f"\nboundary_overrides(keyword→role): {overrides}")

    # smoke
    fails = []
    cases = {classify_role(c, t)["final_ontology_layer"]: (c, t) for c, t in samples}
    assert classify_role("s1", "Workflow Factory는 2차 확장이다.")["final_ontology_layer"] == "personal_ontology_core", "s1 Layer1 실패"
    assert classify_role("s3", "source discovery는 자유롭게 하되 execution은 통제한다.")["final_ontology_layer"] == "personal_ontology_core", "s3 Layer1 실패"
    assert classify_role("s4", "제주 여행팩 source 후보는 A/B/C다.")["final_ontology_layer"] == "workflow_factory", "s4 Layer2 실패"
    assert classify_role("s5", "특허팩에 KIPRIS 데이터를 넣는다.")["final_ontology_layer"] == "workflow_factory", "s5 Layer2 실패"
    print("SMOKE OK: Layer2 keyword 있어도 사용자 원칙은 Layer1 override / 실제 상품·source 데이터는 Layer2")
