# packet-000109

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000109/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000109/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000109-20260519_111904

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-2fb35f97044a33c7` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->dynamic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2fb35f97044a33c7` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.986993978813, "hint_id": "modal-synthesis-29e62c2a2f843120", "predicted_family": "frame", "priority": 1.136993978813, "sample_id": "us-code-5-556-333c12c1b5eab192", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999091091691, "hint_id": "modal-synthesis-2c61528fe24eae81", "predicted_family": "frame", "priority": 1.149091091691, "sample_id": "us-code-42-1437u.-0904464f49467b7f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.431079117926, "hint_id": "modal-synthesis-e93601256162f4c3", "predicted_family": "deontic", "priority": 0.581079117926, "sample_id": "us-code-12-2403-0e192b428d978f5b", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.231207676845, "hint_id": "modal-synthesis-f7f9529819567f1a", "predicted_family": "deontic", "priority": 0.381207676845, "sample_id": "us-code-42-9858h.-c26cffb188ec1c8c", "target_family": "conditional_normative"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
