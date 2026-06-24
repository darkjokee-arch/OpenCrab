# BingguPack README Apply Checklist

> 2026-06-23. README 실제 반영 전 체크리스트. **이번 단계 실제 overwrite 0** (owner 승인 후).

## owner approval token
```
OWNER_APPROVES_BINGGUPACK_README_APPLY:<YYYY-MM-DD>:<operator>
```

## 체크리스트 (전부 ✅ + token 후 반영)
```
[ ] owner approval token 유효
[ ] BINGGUPACK_README_FINAL_CANDIDATE.md 검토 완료
[ ] BINGGUPACK_README_DIFF_PREVIEW.md 확인
[ ] 대상 README 확정 (BingguPack 기존 repo / OpenCrab fork — upstream push 금지)
[ ] GitHub description = BINGGUPACK_GITHUB_DESCRIPTION_FINAL_CANDIDATE.md
[ ] badge(run 후) 삽입 여부
```

## 반영 절차 (owner 승인 후)
1. token 확인 → 2. final candidate로 README overwrite(owner 직접 또는 승인) →
3. GitHub description 적용 → 4. badge 삽입(CI run 후).

## 금지
- owner token 없이 README overwrite 0 / upstream push·PR 0 / 기존 BingguPack 파일 임의 수정 0.
