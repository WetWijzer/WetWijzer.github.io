Implemented `compiler_ambiguity` policy cleanup by fixing deterministic priority-pair ordering in [modal_registry.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000057-20260519_080717/ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py#L156).

Changes made:
- Removed duplicate `temporal -> conditional_normative` from `PRIORITY_SIGNAL_FREE_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS`.
- Removed duplicate `deontic -> deontic` from `PRIORITY_SIGNAL_FREE_ADAPTIVE_AMBIGUITY_FAMILY_PAIRS`.
- Kept all required ambiguity directions for this packet (`deontic->temporal`, `frame->deontic`, `frame->temporal`, `temporal->deontic`, `deontic->conditional_normative`, `deontic->frame`, and `deontic->deontic` still present once where intended).

Validation run:
- `pytest -q tests/unit/optimizers/logic_theorem_optimizer/test_modal_registry.py`
- `pytest -q` on targeted modal-compiler ambiguity tests (temporal/deontic/frame/compiled-primary/self-pair cases)

Result: 19 passed, 0 failed.