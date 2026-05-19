# packet-000363

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000363/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000363/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000363-20260519_140613

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-7f70bfb5166e49a6` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->dynamic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-7f70bfb5166e49a6` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.219959544438, "hint_id": "modal-synthesis-501f233dd5074d22", "predicted_family": "frame", "priority": 0.369959544438, "sample_id": "us-code-16-410ss-1-196de05d18239619", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.085397246028, "hint_id": "modal-synthesis-5fb180aae902d4e7", "predicted_family": "deontic", "priority": 0.235397246028, "sample_id": "us-code-38-3221-d0911ad7952419ce", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.795861109774, "hint_id": "modal-synthesis-8016c5ac1d647643", "predicted_family": "deontic", "priority": 0.945861109774, "sample_id": "us-code-12-2405-c618ad908c655a89", "target_family": "dynamic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
