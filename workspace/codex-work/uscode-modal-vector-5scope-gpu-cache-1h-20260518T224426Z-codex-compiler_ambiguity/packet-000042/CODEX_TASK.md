# packet-000042

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/packet-000042/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/packet-000042/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000042-20260518_231303

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-f385ee97c05e6345` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->frame","deontic->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f385ee97c05e6345` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.999875778583, "hint_id": "modal-synthesis-21b01eae45af3259", "predicted_family": "deontic", "priority": 1.149875778583, "sample_id": "us-code-39-3641-75a3f1a463d54a12", "target_family": "frame"}`
  evidence: `{"family_margin": -0.880748106853, "hint_id": "modal-synthesis-3080758f176f197c", "predicted_family": "conditional_normative", "priority": 1.030748106853, "sample_id": "us-code-10-8089-28cfa15b72bab654", "target_family": "frame"}`
- `program-3b3f6fed98e734a3` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->frame","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f385ee97c05e6345` score `0.98791`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.69082040919, "hint_id": "modal-synthesis-5026d9100f6e8537", "predicted_family": "deontic", "priority": 0.84082040919, "sample_id": "us-code-15-78aa-01088ad520ec2450", "target_family": "frame"}`
  evidence: `{"family_margin": -0.993925355751, "hint_id": "modal-synthesis-c6fe1a98b831563b", "predicted_family": "deontic", "priority": 1.143925355751, "sample_id": "us-code-22-503-cc8b5baed9ddff5e", "target_family": "temporal"}`
- `program-ba48858401ae3bd5` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f385ee97c05e6345` score `0.974142`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.044252858749, "hint_id": "modal-synthesis-389bbc30ccea0833", "predicted_family": "frame", "priority": 0.194252858749, "sample_id": "us-code-18-5041-b043586cd971c29a", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.998958579084, "hint_id": "modal-synthesis-abc9c05fe90df81c", "predicted_family": "frame", "priority": 1.148958579084, "sample_id": "us-code-20-1098cc-ec3688903d9caaf0", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.92798749191, "hint_id": "modal-synthesis-c21fc30cf59987d3", "predicted_family": "frame", "priority": 1.07798749191, "sample_id": "us-code-7-511s-d96fcc7f71d0b18b", "target_family": "deontic"}`
- `program-876f6fd1ef417af5` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->frame","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f385ee97c05e6345` score `0.967374`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-b90f1de30ed88b97", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-16-582a-6-d1770b5449c74287", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.634411683997, "hint_id": "modal-synthesis-d6db3b2e54097023", "predicted_family": "deontic", "priority": 0.784411683997, "sample_id": "us-code-41-3903-2f89a64325114fd0", "target_family": "frame"}`
  evidence: `{"family_margin": -0.766391341338, "hint_id": "modal-synthesis-e56a5c4eb069d99d", "predicted_family": "frame", "priority": 0.916391341338, "sample_id": "us-code-20-6601-7071c5be7ec0a86e", "target_family": "temporal"}`
- `program-475c7b40dc92ff39` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f385ee97c05e6345` score `0.923744`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-2647045839fa9d48", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-2-4501-4ee4ed93367b922f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.977880930202, "hint_id": "modal-synthesis-3440939738509427", "predicted_family": "frame", "priority": 1.127880930202, "sample_id": "us-code-42-3543.-3718f5f6f3f6b9f7", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.994862393865, "hint_id": "modal-synthesis-92cf284a8fa88ffc", "predicted_family": "frame", "priority": 1.144862393865, "sample_id": "us-code-47-34.-add4da103cc4783e", "target_family": "deontic"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-fb8eb0e8313f3ec3", "predicted_family": "deontic", "priority": 1.15, "sample_id": "us-code-18-2257-d6b40c9abbafb4f2", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
