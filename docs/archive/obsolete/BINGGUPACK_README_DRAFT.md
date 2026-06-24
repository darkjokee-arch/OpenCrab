# BingguPack — README (DRAFT, 새 기준 갱신안)

> 2026-06-23. **README 갱신안 draft.** 실제 README(BingguPack 기존 / OpenCrab upstream) 직접 수정은
> owner 승인 후. 본 draft는 새 2-layer 기준을 반영한 내용 제안.

## BingguPack이란

BingguPack은 **사용자 온톨로지 기반 AGI 코어**다. 사용자의 대화·판단·취향·원칙·작업방식·의사결정
기준·권한 경계를 evidence-node-edge로 축적해 사용자형 추론/판단 보조로 간다.

## 2-layer 구조

- **Layer1 = Personal Ontology AGI Core (본체/1차 목표)** — 사용자 개인 온톨로지 축적·AGI화.
- **Layer2 = OpenCrab Workflow Factory (2차 commercial extension)** — 유료 워크플로우 상품. 개인 온톨로지와 독립.

## 핵심 원칙 (필수 반영)

- BingguPack 주목표 = **Personal Ontology AGI Core**. Workflow Factory = 2차 commercial extension.
- 기존 BingguPack 기능 **재사용**(classify/SAVE n/evidence/leak_guard) — 병렬 재구현 안 함.
- **source discovery 자유 / execution gate 분리** — 임의 URL 후보 산출은 자유, 실제 수집은 별도 gate.
- **SAVE는 explicit user approval** — 자동 저장 없음. SAVE 명령 있어도 자격(evidence/PII/layer) 미달이면 blocked.
- **candidate 우선 / promotion_allowed=false 기본** — confirmed 승격은 별도 미래 단계.
- **semantic은 helper** — node_type/confidence/duplicate 보조. save/promotion/evidence authority 없음.
- **evidence-first** — evidence_refs 없는 node/edge 금지.
- **OpenCrab ingest / production write는 별도 gate** — 현재 STOP/HOLD.

## 신규 사용자 사용법

1. 대화를 입력 → 2. candidate preview 생성 → 3. Layer1/Layer2 자동 분리 →
4. evidence/semantic 상태 부착 → 5. review CLI에서 확인 → 6. SAVE/REJECT/HOLD 판단 →
7. dry-run handoff로 저장 계획 확인 → 8. 실제 저장은 owner 승인 후에만.

## preview/dry-run 사용법

- Layer1: `docs/poc/personal_ontology/layer1_real_conversation_preview_runner.py`, `..._batch_preview.py`.
- Layer2: `docs/poc/workflow_factory/workflow_factory_goal_preview_runner.py`.
- review: `..._review_cli_preview.py` (display only).

## WSL/Mac 호환 안내

- pathlib·utf-8 준수. 단 기존 BingguPack 경로(`C:\Users\PC\BingguPack`) 의존부는 WSL/Mac 이식 시
  env var/config로 외부화 필요(`BINGGUPACK_WSL_MAC_COMPATIBILITY.md` 참조·현재 static check WARN).

## 자세히

- 전체: `BINGGUPACK_DOC_INDEX.md` / 사용설명서: `BINGGUPACK_USER_GUIDE_FINAL.md` /
  status: `BINGGUPACK_FINAL_GOAL_MODE_STATUS.md`.
