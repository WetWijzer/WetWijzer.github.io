# packet-000471

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000471/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000471/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000471-20260519_152946

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-f4371d99f823cfde` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f4371d99f823cfde` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.58228743692, "hint_id": "modal-synthesis-59017a72720b86bf", "predicted_family": "deontic", "priority": 0.73228743692, "sample_id": "us-code-6-591h-bb53b6b6583b4a41", "target_family": "frame"}`
  evidence: `{"family_margin": -0.99126278774, "hint_id": "modal-synthesis-91111aad22f3ad6a", "predicted_family": "frame", "priority": 1.14126278774, "sample_id": "us-code-12-4517-b1c5aba229b723b7", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.356459015591, "hint_id": "modal-synthesis-9bf910be7840e079", "predicted_family": "frame", "priority": 0.506459015591, "sample_id": "us-code-10-8724-f0e36a7d35395997", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.459134623027, "hint_id": "modal-synthesis-9c20296bc7cb346e", "predicted_family": "frame", "priority": 0.609134623027, "sample_id": "us-code-7-1379c-0abb909cfabdc378", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
