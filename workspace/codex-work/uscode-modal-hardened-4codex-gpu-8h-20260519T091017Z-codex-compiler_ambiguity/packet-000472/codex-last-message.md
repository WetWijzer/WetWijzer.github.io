Added packet-specific ambiguity-policy regression coverage in [tests/unit_tests/logic/modal/test_modal_codec.py:13974](/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000472-20260519_153850/tests/unit_tests/logic/modal/test_modal_codec.py:13974).

What this new test enforces:
- Exact `program-5eb8448439d4ac28` and `program-22f34cab6e6dc67f` evidence margins.
- Required explicit adaptive ambiguity types for:
  - `frame -> conditional_normative`
  - `temporal -> conditional_normative`
  - `deontic -> conditional_normative`
  - `frame -> deontic`
  - `deontic -> deontic` (zero-margin case)
- `compiler_ambiguity` bundle metadata and deterministic priority values.

Validation run:
- `pytest -q tests/unit_tests/logic/modal/test_modal_codec.py -k "packet_000472_compiler_ambiguity_policy_pairs or marks_todo_policy_pairs_as_compiler_ambiguity_bundle or emits_explicit_ambiguity_for_todo_evidence_margin_pairs"`
- Result: `3 passed`