# BingguPack README Diff Preview

> 2026-06-23. README 갱신 전 diff 미리보기. 실제 덮어쓰기는 owner 승인 후.

## 방향성 diff (개념 레벨)

```diff
- BingguPack: (기존) 도메인팩/캡처 도구 중심 설명
+ BingguPack: Personal Ontology AGI Core (본체) — 사용자 온톨로지 축적·AGI화
+   + Layer2 = OpenCrab Workflow Factory (2차 commercial extension, 독립)

  핵심 원칙 (추가/명확화):
+ - candidate 우선 / promotion_allowed=false 기본
+ - SAVE는 explicit user approval (자동 저장 없음)
+ - evidence-first (evidence_refs 없는 node/edge 금지)
+ - semantic은 helper (save/promotion/evidence authority 없음)
+ - source discovery 자유 / execution gate 분리
+ - actual SAVE / OpenCrab ingest / production write는 별도 gate (현재 STOP/HOLD)
+ - 신규 사용자 사용법 / WSL·Mac 호환 안내(BINGGUPACK_ROOT env)
```

## 실제 라인 diff
- 기존 README 실문구는 owner 환경(`C:\Users\PC\BingguPack\README.md`)에서 확인 후 라인 diff 작성.
- 본 preview는 **개념/섹션 레벨 변경 방향**. 실제 텍스트 교체는 owner 승인 + 직접 적용.

## 안전
- 본 단계 실제 README 수정 0 / upstream push 0. draft·plan·diff preview만.

## APPLIED (2026-06-23, Option 2)
- Option 2 승인으로 README.md 실제 반영 완료(115 insertions / 198 deletions).
- WSL은 PASS 아닌 SKIP_WITH_REASON 표기·insane-search 실행엔진 아님·SAVE/ingest not enabled 명시.
- OpenCrab 원본 README는 `docs/UPSTREAM_OPENCRAB_README.md`로 보존(손실 0·git history 복구 가능).
- upstream push 0(fork myfork만).
