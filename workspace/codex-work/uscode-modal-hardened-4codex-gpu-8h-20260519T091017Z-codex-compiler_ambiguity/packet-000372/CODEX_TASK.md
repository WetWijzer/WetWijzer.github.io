# packet-000372

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000372/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000372/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000372-20260519_145812

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-f6c8228ddadc1de8` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->conditional_normative","deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f6c8228ddadc1de8` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.914900774437, "hint_id": "modal-synthesis-01fa4343debf31d6", "predicted_family": "deontic", "priority": 1.064900774437, "sample_id": "us-code-43-883.-4cf3c55207a7042d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.988780738882, "hint_id": "modal-synthesis-7d44737360a31641", "predicted_family": "frame", "priority": 1.138780738882, "sample_id": "us-code-46-3303.-262060b4e52c28d7", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.75246836579, "hint_id": "modal-synthesis-8973b7e60133c099", "predicted_family": "deontic", "priority": 0.90246836579, "sample_id": "us-code-2-2182-5a4da71f9b7ed715", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.360131386457, "hint_id": "modal-synthesis-93d5d678bc638306", "predicted_family": "alethic", "priority": 0.510131386457, "sample_id": "us-code-50-3533.-fbe9761d5d5aa91b", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
