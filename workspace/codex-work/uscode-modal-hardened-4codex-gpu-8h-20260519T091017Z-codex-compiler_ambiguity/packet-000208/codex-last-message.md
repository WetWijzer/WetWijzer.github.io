Implemented the `compiler_ambiguity` packet update with a policy hardening + targeted regressions.

### What changed
- Normalized adaptive `family_margin` metadata display to always round the raw computed margin (instead of recomputing from rounded shares), keeping ambiguity metadata deterministic and consistent across adaptive paths.
- Added packet-specific regression coverage for all requested compiler-required family pairs:
  - `conditional_normative->temporal`
  - `frame->temporal`
  - `frame->conditional_normative`
  - `temporal->temporal`
  - `temporal->deontic`
  - `alethic->deontic`
  - `deontic->conditional_normative`
  - `frame->deontic`

### Files updated
- [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000208-20260519_130322/ipfs_datasets_py/logic/modal/compiler.py#L870)
- [compiler.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000208-20260519_130322/ipfs_datasets_py/logic/modal/compiler.py#L1580)
- [test_legal_modal_parser_deterministic_rules.py](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000208-20260519_130322/ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py#L66)

### Validation run
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py -k packet_000208` → `8 passed`
- `pytest -q ipfs_datasets_py/optimizers/logic_theorem_optimizer/test_legal_modal_parser_deterministic_rules.py` → `35 passed`