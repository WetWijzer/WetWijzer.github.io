# Guarded Agent Release Reviewer Checklist v1

Manual signoff: {{manual_signoff_reviewer}}

Unresolved blocker handling: if any blocker remains unresolved, the release stays blocked and the reviewer records the blocker evidence before stopping. source: ppd/tests/fixtures/release_reviewer_checklist_v1/valid_checklist.md

Validation replay commands:

```bash
python3 ppd/daemon/ppd_daemon.py --self-test
pytest ppd/tests/test_release_reviewer_checklist_v1.py
```

Rollback checkpoint: reviewer records the last accepted fixture-backed checkpoint before release handoff. source: ppd/tests/fixtures/release_reviewer_checklist_v1/valid_checklist.md

- [ ] Checklist rows are source-backed and cite deterministic fixtures. source: ppd/tests/fixtures/release_reviewer_checklist_v1/valid_checklist.md
- [ ] Manual reviewer signoff placeholder is present before handoff. source: ppd/tests/fixtures/release_reviewer_checklist_v1/valid_checklist.md
- [ ] Unresolved blockers keep release blocked. source: ppd/tests/fixtures/release_reviewer_checklist_v1/valid_checklist.md
- [ ] Validation replay commands are listed for deterministic rerun. source: ppd/tests/fixtures/release_reviewer_checklist_v1/valid_checklist.md
- [ ] Rollback checkpoint is captured before release handoff. source: ppd/tests/fixtures/release_reviewer_checklist_v1/valid_checklist.md
