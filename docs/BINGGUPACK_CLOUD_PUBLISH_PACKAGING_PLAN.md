# BingguPack — Cloud / Publish Packaging Plan

> 2026-06-23. Cloud/Publish packaging 설계. **실제 publish 0.** owner approval token 필요.

## 1. 원칙
- Cloud/Publish는 **아직 실행하지 않음**.
- Cloud를 **source-of-truth로 쓰지 않음**(로컬/fork가 진실).
- synthetic/review-only pack release **금지**.
- private data 제외. README/CI/approval status 포함.

## 2. publish 전 조건 (release_ready)
- Option 1 CI: PASS (충족: 3-OS 11/11).
- Option 2 README: 반영 완료 (충족).
- Option 3 SAVE: real run 완료 또는 명시적 제외(현재 BLOCKED).
- Option 4 ingest: real run 완료 또는 명시적 제외(현재 BLOCKED).
- private/evidence 원본 미포함 확인.
- risk register 검토 완료.

## 3. release_ready 판정
- 현재: **NOT release_ready** (Option 3·4 BLOCKED·실저장/ingest 미완).
- packaging은 설계만. 실제 패키징/업로드 0.

## 4. Cloud/Publish token 형식
```
OWNER_APPROVES_BINGGUPACK_CLOUD_PUBLISH_PACKAGE:<YYYY-MM-DD>:<package_id>:<operator>
```
- token 있어도 release_ready 조건 미충족 시 publish 금지.

## 5. 금지
- 실제 publish / Cloud 업로드 / 패키지 생성 0. owner approval + release_ready 전까지 HOLD.
