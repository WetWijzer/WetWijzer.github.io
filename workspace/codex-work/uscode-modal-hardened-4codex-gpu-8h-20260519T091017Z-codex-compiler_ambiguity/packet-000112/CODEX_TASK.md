# packet-000112

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000112/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000112/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000112-20260519_112326

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-1937bd928d032b2c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-1937bd928d032b2c` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.376889143959, "hint_id": "modal-synthesis-6f507a1e50335586", "predicted_family": "frame", "priority": 0.526889143959, "sample_id": "us-code-22-4071k-55a17ec8c5e3db3e", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.992896805877, "hint_id": "modal-synthesis-d5361f2945534ff0", "predicted_family": "frame", "priority": 1.142896805877, "sample_id": "us-code-50-855.-6b18aaa5a6c9cf83", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.436671018642, "hint_id": "modal-synthesis-e3f2c2dfc7954fc4", "predicted_family": "temporal", "priority": 0.586671018642, "sample_id": "us-code-43-326.-5500eb218f8a7886", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.18481454784, "hint_id": "modal-synthesis-f9daf67597897bdd", "predicted_family": "frame", "priority": 0.33481454784, "sample_id": "us-code-50-3305.-3e025318340f6f2a", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
