# OpenCrab Visual Plan / Visual Recap 설계

> 모드: design-only / preview-only. agent-native `skills/visual-plans`·`skills/visual-recap` 패턴을 OpenCrab evidence-first 모델에 결합.

---

## 1. Visual Plan 목적

사용자가 **실행을 누르기 전에** "무슨 일이 일어날지"를 한 화면에서 보고 승인 여부를 결정하게 한다. agent-native 원칙("NEVER hand the plan as inline chat — always a structured artifact") 차용.

Visual Plan은 7가지를 반드시 보여준다:
1. 어떤 **팩**을 쓰는가 (`pack_id`)
2. 어떤 **action**이 실행되는가 (순서 포함)
3. 어떤 **evidence/자료**를 참조하는가
4. 어떤 **결과물**이 나오는가
5. **위험도**는 무엇인가 (`risk_flags`)
6. **human review**가 필요한가
7. 실제 **write가 발생하는가** (`writeback_mode`)

→ OpenCrab에서 7번은 **항상 `none`(preview_only)**. "write 없음"을 사용자가 명시적으로 확인.

---

## 2. Visual Plan JSON 구조

```json
{
  "plan_id": "plan:bid_review:20260622:001",
  "pack_id": "bid_review_pack",
  "workflow_id": "wf:run:abc123",
  "actions": [
    {
      "action_id": "analyze_bid_notice",
      "order": 1,
      "inputs_preview": { "notice_id": "R26BK01234567" },
      "risk_level": "low",
      "requires_human_review": true
    },
    {
      "action_id": "check_qualification",
      "order": 2,
      "inputs_preview": { "notice_id": "R26BK01234567", "license_profile_id": "lic:self:001" },
      "risk_level": "medium",
      "requires_human_review": true
    }
  ],
  "evidence_refs": [
    "evidence:bid:R26BK01234567:notice",
    "evidence:bid:R26BK01234567:qual",
    "evidence:license:self:001"
  ],
  "expected_outputs": [
    { "action_id": "analyze_bid_notice", "kind": "candidate_claims", "estimate": "조건 4~6개" },
    { "action_id": "check_qualification", "kind": "eligibility_report", "estimate": "충족/미충족 + 누락 목록" }
  ],
  "risk_flags": ["qualification_judgment_affects_bid"],
  "requires_approval": true,
  "writeback_mode": "none",
  "execution_mode": "preview_only"
}
```

### 검증 규칙
- `writeback_mode != "none"` 이면 → 가드가 plan을 STOP(본 설계 범위에서 write 불가).
- `evidence_refs`에 pack에 없는 ref가 있으면 → `risk_flags`에 `evidence_missing` 자동 추가 + `requires_approval=true` 강제.
- plan은 read-only 아티팩트(파일/로컬). 호스팅 DB 자동저장 안 함(빙구팩 KV 정책 정합).

---

## 3. Visual Recap 목적

실행(preview) **후** 결과를 사용자가 이해하기 쉽게 보여주고, "다음에 무엇을 승인할지"를 제시한다. Visual Plan의 역방향.

포함 7항목:
1. 실행된 action 목록
2. 사용된 evidence 목록
3. 생성된 결과물 (candidate)
4. 판단 근거 (evidence_ref → claim 매핑)
5. 실패/보류된 항목
6. 사용자가 다음에 승인해야 할 항목
7. 실제 반영 여부 (`writeback_result`)

---

## 4. Visual Recap JSON 구조

```json
{
  "recap_id": "recap:bid_review:20260622:001",
  "plan_id": "plan:bid_review:20260622:001",
  "executed_actions": [
    { "action_id": "analyze_bid_notice", "status": "completed", "claims_created": 5 },
    { "action_id": "check_qualification", "status": "completed", "claims_created": 1 }
  ],
  "used_evidence_refs": [
    "evidence:bid:R26BK01234567:notice",
    "evidence:bid:R26BK01234567:qual"
  ],
  "outputs": [
    {
      "claim_id": "claim:bid:cond:001",
      "label": "기초금액 1.2억",
      "promotion_status": "candidate",
      "evidence_refs": ["evidence:bid:R26BK01234567:notice#L42"]
    }
  ],
  "blocked_items": [
    { "action_id": "check_qualification", "reason": "evidence:license:self:001 누락 → 부분판정만" }
  ],
  "review_required_items": [
    { "claim_id": "claim:bid:eligibility:001", "decision": "candidate→validated 승인 필요" }
  ],
  "writeback_result": "not_executed",
  "next_user_decision": [
    "자격충족 판정을 validated로 승인하시겠습니까?",
    "누락된 license evidence를 보강하시겠습니까?"
  ]
}
```

`writeback_result`는 항상 `not_executed`(preview_only). 실제 반영은 별도 승인 흐름.

---

## 5. 사용자 승인 흐름

```
[1] action 호출 (UI/AI/MCP/API)
      ↓
[2] Visual Plan 생성  ──→  사용자에게 표시 (write 0)
      ↓  사용자 "실행" 클릭
[3] preview 실행 → candidate Claim 생성 (production write 0)
      ↓
[4] Visual Recap 생성  ──→  사용자에게 표시
      ↓  next_user_decision 제시
[5] approvals 큐 (pending)
      ├ 사람 approved → PromotionEngine candidate→validated
      └ 사람 rejected → candidate 유지, action_log 기록
```

핵심: [2]와 [4] 사이에서 **production write·promotion·외부반영 0**. AI는 [1][3]까지만, [5]는 사람만.

---

## 6. preview_only 흐름

- 모든 action의 기본 `execution_mode=preview_only`.
- preview 실행 결과 = **candidate Claim + evidence_ref 링크**만. 기존 confirmed/promoted 그래프 미변경.
- preview는 OpenCrab `workflow_runs.status=pending`으로 기록, `completed`는 "preview 완료"를 의미(반영 아님).

---

## 7. writeback 차단 흐름

```
action → writeback_mode 검사
   ├ "none"  → 통과 (preview만)
   └ 그 외   → guard_no_unapproved_writeback STOP → 실행 거부 + 사유 로그
```
- 본 설계에서 `writeback_mode`는 `none`만 허용. `apply`/`sync`는 미구현(향후 별도 승인 설계).
- AI actor가 writeback을 시도하면 무조건 차단(사람 reviewer_id 없이는 불가).

---

## 8. 예시 화면 구성 (텍스트 와이어프레임)

### Visual Plan 화면
```
┌─ 실행 전 검토: 입찰 검토팩 ──────────────────┐
│ 팩: bid_review_pack          위험도: ● medium │
│                                               │
│ 실행될 작업 (2)                                │
│  1. 공고문 분석        [low]   사람검토 필요   │
│  2. 자격충족 판정      [medium] 사람검토 필요  │
│                                               │
│ 참조 자료 (evidence 3)                         │
│  • 공고 원문  • 자격 요건  • 보유 면허          │
│                                               │
│ 나올 결과                                      │
│  • candidate 조건 4~6개                        │
│  • 충족/미충족 + 누락 목록                      │
│                                               │
│ ⚠ 실제 저장: 없음 (preview_only)              │
│ ⚠ 자격판정이 투찰 결정에 영향                  │
│                                               │
│        [ 취소 ]        [ 미리보기 실행 ]        │
└───────────────────────────────────────────────┘
```

### Visual Recap 화면
```
┌─ 실행 결과: 입찰 검토팩 ─────────────────────┐
│ 실행 완료 (2)    생성 candidate: 6           │
│                                              │
│ 결과                                          │
│  ✓ 기초금액 1.2억      근거: 공고원문 L42     │
│  ✓ 마감 6/30 18:00     근거: 공고원문 L08     │
│  △ 자격충족: 부분판정   (면허 evidence 누락)   │
│                                              │
│ 실제 반영: 안 됨 (승인 대기)                   │
│                                              │
│ 다음 결정이 필요합니다                         │
│  1. 자격판정 validated 승인?                  │
│  2. 누락 면허 자료 보강?                       │
│                                              │
│   [ 승인 ]   [ 보류 ]   [ 자료 보강 ]          │
└──────────────────────────────────────────────┘
```
