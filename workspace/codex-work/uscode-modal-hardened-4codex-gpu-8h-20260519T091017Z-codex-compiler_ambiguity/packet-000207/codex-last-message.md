Implemented a narrow `modal.compiler.ambiguity` hardening plus targeted regressions.

- Hardened explicit adaptive-ambiguity backfill to safely handle missing/non-dict base metadata, so explicit ambiguity records are still emitted instead of failing on `.get(...)` access: [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000207-20260519_125503/ipfs_datasets_py/logic/modal/compiler.py#L592).
- Added regression test for that metadata-missing backfill path: [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000207-20260519_125503/tests/unit_tests/logic/modal/test_modal_codec.py#L1890).
- Added a TODO-evidence regression that validates explicit ambiguity emission and exact `family_margin_raw`/`adaptive_priority` for the requested pairs (`alethic->temporal`, `frame->deontic`, `frame->temporal`, `conditional_normative->temporal`, `temporal->deontic`): [test_modal_codec.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000207-20260519_125503/tests/unit_tests/logic/modal/test_modal_codec.py#L12980).

Tests run:

- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "metadata_is_missing or todo_evidence_margin_pairs or required_margin_bundle_pairs"`  
  Passed (`3 passed`).
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`  
  Fails with 2 assertions in existing registry-order expectations (outside edited files).