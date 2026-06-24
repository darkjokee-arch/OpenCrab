# BingguPack Workflow Factory Extension (Commercial, Layer 2)

> 2026-06-23. OpenCrab Workflow Factory Extension = 빙구팩 **2차 commercial extension**.
> 사용자 개인 온톨로지(Layer 1 AGI Core)와 **독립 가능**. 설계 문서(C안)만 — production·
> network·실제 crawl/ingest 0. fork preview-only. 상위: `BINGGUPACK_FINAL_CONCEPT.md`.

## 1. 개념

사용자 목표를 입력하면, 그 목표를 달성하는 **유료 워크플로우 상품**을 OpenCrab 위에 만들기 위해
필요한 팩·데이터·source 후보·수집 계획을 역산해 산출하는 **commercial extension**.

- 빙구팩 본체(개인 온톨로지 AGI)가 아니다. 사용자 온톨로지 없이도 동작한다.
- OpenCrab 워크플로우 엔진을 **대체하지 않는다** — 추천/설계/계획/검수 계층.

## 2. 데이터 흐름

```
사용자 목표 입력
→ 목적 분석 (Purpose Analyzer)
→ 워크플로우 추천 (Workflow Recommender)
→ 필요한 팩 목록 역산 (Required Pack Deriver)
→ 팩별 데이터 요구사항 (Pack Data Requirement Generator)
→ source candidate 산출 (Source Candidate Generator)   ← discovery freedom (자유)
→ collection plan 생성 (Collection Planner, dry-run)    ← execution gate (통제)
→ evidence plan (Evidence Plan, 미실행)
→ candidate node/edge plan (미확정)
→ [HOLD] 실제 수집 / OpenCrab ingest / workflow product
```

- **discovery 단계(source candidate 산출)는 자유**, **execution 단계(실제 수집/ingest)는 통제**.
  두 단계가 섞이지 않는다(execution gate separation).

## 3. 산출물 단계별 게이트

| 단계 | 판정 | 비고 |
|---|---|---|
| 목적 분석 / 워크플로우 추천 / 팩·데이터 역산 | GO | preview, synthetic/실 Pack read-only |
| source candidate 산출 (임의 URL 포함) | GO | candidate=true, trust-tier·risk label 부착 |
| collection plan 생성 (dry-run) | GO | 수집 방법 후보 + execution_admission만, 실행 0 |
| evidence plan / node·edge plan | GO (계획) | 실제 생성 HOLD |
| 실제 fetch / crawl / scrape / browser | **HOLD** | 별도 승인 + license/robots/PII/access 게이트 |
| OpenCrab 실제 ingest | **HOLD** | REAL_DATA_WIRING_FULL |
| production write / workflow 판매 실행 | **STOP** | |

## 4. 상품화 (설계만)

- 상품 단위 = **워크플로우** (입력폼 + 결과물 + 과금 포인트).
- 현 단계 상품 형태 = **진단/계획 리포트**(실 Pack v1 read-only 실측 기반 — 탁상공론 아님):
  실측 evidence_coverage·license 분포·"어떤 source 후보로 어떤 워크플로우를 구축 가능한가"의
  실행 계획 + 단계 로드맵.
- 로드맵: 진단/계획 리포트(GO) → read-only 수집 PoC(B안, HOLD 해제 시) → 실 ingest
  (REAL_DATA_WIRING_FULL) → 유료 워크플로우 상품.
- 도메인 예시: 여행/입찰/특허/외벽디자인/고기집창업. **bid-engine 본업 인프라 미터치**(별도 트랙).

## 5. 모듈 (Layer 2)

```
Purpose Analyzer → Workflow Recommender → Required Pack Deriver →
Pack Data Requirement Generator → Source Candidate Generator →
Collection Planner(dry-run) → Evidence Plan → Node/Edge Plan →
[HOLD] Collector Adapter / Extractor / Evidence Builder / Pack Ingest Adapter →
Workflow Fit Checker → Productization Builder
```
- 굵게 HOLD 표시된 실행 모듈은 contract 설계 + dry-run plan까지만 GO. 실제 실행 HOLD.

## 6. 독립성 명시

- 본 extension은 사용자 개인 온톨로지(Layer 1)와 **데이터·코드·책임 분리**.
- 유료 워크플로우 생성에 사용자 온톨로지 불필요 → 별도 사업 레이어로 운영 가능.
