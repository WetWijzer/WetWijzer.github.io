# packet-000022

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000022/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000022/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000022-20260519_093624

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-c7b29d1a7c5cd3ea` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c7b29d1a7c5cd3ea` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.68151169487, "hint_id": "modal-synthesis-2b5fdb1f300e2ab0", "predicted_family": "frame", "priority": 0.83151169487, "sample_id": "us-code-16-459e-9-08e7333353524538", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.484415617754, "hint_id": "modal-synthesis-7a42c8c45c9da7f5", "predicted_family": "deontic", "priority": 0.634415617754, "sample_id": "us-code-35-382-0dd76b4fbbd826e0", "target_family": "frame"}`
- `program-367d3c7e4b77a233` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c7b29d1a7c5cd3ea` score `0.976259`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.538411662487, "hint_id": "modal-synthesis-331fa12374544518", "predicted_family": "conditional_normative", "priority": 0.688411662487, "sample_id": "us-code-21-1602-97330a80c926f542", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.039721031037, "hint_id": "modal-synthesis-9d6c272347817e3c", "predicted_family": "frame", "priority": 0.189721031037, "sample_id": "us-code-42-17825.-eabe147e0629bb60", "target_family": "temporal"}`
- `program-85978974596236a0` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->conditional_normative","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c7b29d1a7c5cd3ea` score `0.95742`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-5ffc3815f07a2f10", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-44-1335.-edbedca6b9a81220", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-7840388e41614f52", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-16-460ww-3-b0ba72d66eca5ae0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.844760733598, "hint_id": "modal-synthesis-b39c0a1c668943bb", "predicted_family": "alethic", "priority": 0.994760733598, "sample_id": "us-code-42-1382c.-317fd26d2273011a", "target_family": "conditional_normative"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
