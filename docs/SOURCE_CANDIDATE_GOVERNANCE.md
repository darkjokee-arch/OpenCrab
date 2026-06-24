# Source Candidate Governance

> 2026-06-23. owner 정정 반영. **source discovery 단계와 execution 단계를 분리**한다.
> 화이트리스트는 차단기가 아니라 trust-tier 신호다. 설계 문서 — production·network·실제
> crawl/ingest 0. fork preview-only.

## 0. 최종 정책 문구 (확정)

> **Whitelist absence must not block source discovery. It only affects trust tier and
> execution admission. BingguPack may freely generate arbitrary URL/source candidates in
> preview mode. Execution, crawling, scraping, ingestion, and production write remain
> separately gated and may be HOLD/REJECT depending on license, robots, PII, access, and
> user approval conditions.**

## 1. 핵심 원칙 — discovery freedom vs execution gate separation

- **source discovery는 자유**: 화이트리스트가 없다는 이유로 URL/사이트/검색 쿼리/민간 플랫폼/
  블로그/리뷰/커뮤니티/상업 사이트 후보를 **막지 않는다**.
- **execution은 통제**: 실제 fetch/crawl/scrape/browser/ingest/production write는 별도 게이트에서
  ADMIT/HOLD/REJECT 판정.
- 두 단계가 섞이는 것을 금지(섞이면 discovery 자유가 execution 위험으로 전이).

## 2. whitelist = trust tier 신호 (차단 아님)

| 상황 | candidate 생성 | trust_tier | execution_admission |
|---|---|---|---|
| whitelist 있음(공공API/공식문서 등) | 가능 | verified | ADMIT (단 전역 실행 HOLD 별개) |
| whitelist 없음 | **가능** | unverified | HOLD |
| robots unknown | 가능 | (그대로) | HOLD |
| robots disallow 확인됨 | 가능 | (그대로) | automated_fetch_rejected |
| PII 가능성 | 가능 | (그대로) | redaction_required + HOLD |
| prohibited source 확인됨 | 가능(기록) | untrusted | use_rejected / execution_rejected |

- **모든 행에서 candidate 생성은 허용**. 차단되는 것은 *실행*뿐.

## 3. source risk labels (정의)

source candidate에 부착하는 risk label enum:
```
official_api · official_doc · public_dataset · user_upload
commercial_site · review_site · blog · forum
unknown_url · login_required_possible · paywall_possible
license_unknown · license_prohibited · robots_unknown · robots_disallow
pii_possible · copyright_bulk_risk · rate_limit_sensitive
```
- 여러 label 동시 부착 가능. label은 **신호**이고 execution_admission 계산에 입력된다.

## 4. 단계 분리 (4-stage 책임 경계)

```
1. candidate generation   → GO (임의 URL/source 후보 산출 허용)
2. fetch execution        → 별도 gate (HOLD/REJECT, 현재 전역 HOLD = B안)
3. ingest                 → 별도 gate (HOLD, REAL_DATA_WIRING_FULL)
4. production execution    → STOP
```
- Pre-Admission = **execution admission gate** (candidate 생성 차단기가 **아님**).
  candidate는 항상 기록 가능, execution 여부만 판정.

## 5. execution_admission 판정 규칙

```
ADMIT  : verified source + license ok + robots ok + pii 없음
         (단 전역 실행 HOLD/B안이 우선 — 실제 실행은 별도 승인 필요)
HOLD   : whitelist 없음(unverified) / license_unknown / robots_unknown /
         login_required_possible / pii_possible(+redaction_required)
REJECT : robots_disallow 확인 / license_prohibited / prohibited source /
         copyright_bulk_risk(대량 원문 복제) / 로그인·paywall 우회 요구
```
- ADMIT이라도 현 단계 실제 실행은 전역 HOLD(B안). execution_admission은 "실행 단계가 열렸을 때의
  판정"을 미리 산출하는 신호.

## 6. 별도 승인 전까지 HOLD/STOP인 행위

```
실제 crawling / scraping / Playwright·browser 자동 접속 /
로그인벽 우회 / paywall 우회 / robots disallow 무시 / PII 수집 /
저작권 원문 대량 복제 / OpenCrab 실제 ingest / production write
```

## 7. candidate 불변식

모든 source candidate:
```
candidate = true
promotion_allowed = false
execution_admission ∈ {ADMIT, HOLD, REJECT}  (기본 HOLD if unverified)
```

## 8. 용어 (교사책임 회피 표현 제거)

- 사용 금지: "교사책임 회피".
- 사용: `source discovery freedom`, `candidate source governance`, `trust-tier labeling`,
  `execution gate separation`, `preview-first planning`, `source responsibility boundary`.
- 목표는 책임 회피가 아니라 **source 탐색 자유도와 실행 안전성의 분리**.

## 9. 4CLI 토론 C2 정정

- 기존: "source 화이트리스트로 교사책임 회피 / 화이트리스트 부재 → 구조적 추천 불가".
- **정정**: 화이트리스트 부재 → `unverified source candidate`로 **추천 가능**.
  실제 자동 수집 실행 → 별도 게이트에서 HOLD/REJECT 가능.
