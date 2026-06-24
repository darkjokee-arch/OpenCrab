# BingguPack Layer Boundary — FINAL

> 2026-06-23. Layer1/Layer2 분리 최종 기준. **키워드 아닌 문장 역할 기반.**

## 1. 레이어 정의
- **Layer1 = Personal Ontology AGI Core** (본체). 사용자 개인 사고/원칙/판단/작업방식/권한경계.
- **Layer2 = OpenCrab Workflow Factory commercial extension** (2차). 도메인 상품 데이터·source·워크플로우.

## 2. 분리 기준 = 문장 역할 (keyword 아님)

| 문장 역할 | 처리 |
|---|---|
| 사용자 구조 원칙 ("Workflow Factory는 2차 확장") | **Layer1** |
| 사용자 작업방식/개발 원칙 ("기존 재사용", "검증 과잉 금지") | **Layer1** |
| 사용자 권한 경계 ("semantic은 save authority 아님") | **Layer1** |
| 사용자 의사결정 원칙 ("source discovery 자유, execution 통제") | **Layer1** |
| 외부 상품/팩/워크플로우 데이터 (여행팩 맛집 데이터 등) | **Layer2** |
| source 후보 자체 (URL/사이트) | **Layer2** |
| 수집 대상/크롤링 target | **Layer2** |

## 3. 핵심 규칙
- **Layer2 keyword(workflow factory/OpenCrab/commercial/source) present만으로 excluded 금지.**
- Layer2를 언급해도 그것이 사용자 원칙/제품전략/경계판단이면 **Layer1 candidate**.
- 실제 Layer2 데이터/source 후보/수집 URL만 Layer2 excluded.
- 구현: `layer1_role_boundary_helper.py` (keyword=signal·role=final·boundary_override 추적).

## 4. 경계 안전
- boundary는 **approved_preview를 늘릴 권한 없음**, **evidence_status를 resolved로 바꿀 권한 없음**.
- Layer1/Layer2는 같은 그래프/스코프 혼입 금지.
