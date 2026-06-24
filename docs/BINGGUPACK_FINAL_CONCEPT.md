# BingguPack — Final Concept (정정 확정)

> 2026-06-23. owner 최종 정정. 빙구팩의 본질을 재정의하고 2개 레이어로 분리한다.
> 본 문서는 개념 정의(설계)만. production 실행·writeback·promotion·실제 crawl/ingest·
> network 0. fork(ci/preview-gate-activation) preview-only.

## 0. 한 줄 정의

**BingguPack = Personal Ontology AGI Core (1차 본질)**.
OpenCrab Pack/Workflow Builder = **2차 commercial extension** (별도 사업 레이어, 개인 온톨로지와 독립 가능).

## 1. Layer 1 — Personal Ontology AGI Core (본질)

빙구팩의 1차 목표는 OpenCrab 팩 제작이 **아니다**.

- **목적**: 사용자의 대화·판단·취향·원칙·작업방식·의사결정 기준·반복 업무 패턴을
  `evidence — node — edge` 구조로 축적 → **사용자 온톨로지 기반 AGI화**.
- **산출 가치**: 사용자 맞춤 추론, 사용자형 판단 보조, 사용자 온톨로지 기반 의사결정 지원.
- **안전 불변식**: 자동 확정 금지, `candidate` 우선, evidence 기반, `promotion_allowed=false` 유지.
- 이 레이어가 빙구팩의 **본체**다.

## 2. Layer 2 — OpenCrab Pack / Workflow Builder Extension (commercial)

- **역할**: OpenCrab용 도메인팩 생성 / 팩 조합 추천 / 워크플로우 구성 / 수집 계획 생성 /
  상품화 설계 / 유료 워크플로우 패키징.
- **독립성**: 이 레이어는 **사용자 개인 온톨로지와 직접 관련 없는 별도 사업 레이어**.
  사용자 온톨로지 없이도 유료 워크플로우를 생성할 수 있다(독립 가능).
- **명칭**: `BingguPack Commercial Extension` / `OpenCrab Workflow Factory Extension`.

## 3. 레이어 경계 (명확화)

| 구분 | Layer 1 (Core) | Layer 2 (Extension) |
|---|---|---|
| 본질/부차 | 본체(1차) | 확장(2차) |
| 데이터 | 사용자 개인 대화/판단/원칙 | 도메인 자료(여행/입찰/창업 등) |
| 목적 | 사용자 온톨로지 AGI화 | 유료 워크플로우 상품 |
| 온톨로지 의존 | 본질적으로 사용자 온톨로지 그 자체 | **독립 가능**(사용자 온톨로지 불필요) |
| 안전 불변식 | candidate·evidence·promotion_allowed=false | candidate·preview-only·execution gate 분리 |

- 두 레이어는 **데이터·목적·책임이 분리**된다. Layer 2 작업이 Layer 1(개인 온톨로지)을
  오염시키지 않는다. 유료 워크플로우 생성은 사용자 온톨로지와 무관하게 가능.

## 4. 이번 작업의 위치

이번 "토탈 워크플로우 공장팩" 작업 = **Layer 2 (Commercial Extension)**.
- 빙구팩 본체(Layer 1 AGI Core)가 아니다. 본체인 것처럼 문서화하지 않는다.
- 별도 문서로 분리 기술: `BINGGUPACK_WORKFLOW_FACTORY_EXTENSION.md`.

## 5. 운영 경계 (전 레이어 공통)

```
FORK_DEVELOPMENT_MODE: GO (ci/preview-gate-activation)
UPSTREAM push / PR: STOP
REAL_DATA_WIRING_FULL: HOLD
PRODUCTION_EXECUTION: STOP
실제 crawl / scrape / browser / ingest / network: HOLD (별도 게이트)
candidate=true / promotion_allowed=false: 강제
```

## 6. 관련 문서

- Layer 2 상세: `docs/BINGGUPACK_WORKFLOW_FACTORY_EXTENSION.md`
- source 거버넌스: `docs/SOURCE_CANDIDATE_GOVERNANCE.md`
- source 스키마: `schemas/source_candidate.schema.json`
- PoC: `docs/poc/workflow_factory/`
