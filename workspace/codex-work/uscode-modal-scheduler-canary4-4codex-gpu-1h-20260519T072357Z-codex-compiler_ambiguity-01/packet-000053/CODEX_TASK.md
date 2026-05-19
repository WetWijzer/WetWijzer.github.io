# packet-000053

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/packet-000053/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/packet-000053/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000053-20260519_072832

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-b5ee8dc80e1707d2` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b5ee8dc80e1707d2` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999055720716, "hint_id": "modal-synthesis-8ee07cda3e9d6c95", "predicted_family": "frame", "priority": 1.149055720716, "sample_id": "us-code-12-5226-76bc695a57d44291", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-9da791dd2c06c1b6", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-19-81h-0a0f7a05da441d89", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.917577654701, "hint_id": "modal-synthesis-d40e2d524cf979c3", "predicted_family": "frame", "priority": 1.067577654701, "sample_id": "us-code-16-459a-5a-a4059543f2650ab3", "target_family": "deontic"}`
- `program-34e9f180c2082b3a` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b5ee8dc80e1707d2` score `0.983719`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999658532901, "hint_id": "modal-synthesis-39170cc488ad7698", "predicted_family": "frame", "priority": 1.149658532901, "sample_id": "us-code-22-1475e-bec3039174fdd403", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.936653792488, "hint_id": "modal-synthesis-6b57c5764e97510c", "predicted_family": "frame", "priority": 1.086653792488, "sample_id": "us-code-21-2001-23dd91fc9477a14b", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.089006714447, "hint_id": "modal-synthesis-9c8f37b1efcc89e2", "predicted_family": "deontic", "priority": 0.060993285553, "sample_id": "us-code-51-60147.-5d171f00b3f04d8f", "target_family": "deontic"}`
- `program-c11b7a331be60bd1` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->epistemic","conditional_normative->temporal","deontic->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b5ee8dc80e1707d2` score `0.93572`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.849125533952, "hint_id": "modal-synthesis-0b2958916efb4cd2", "predicted_family": "alethic", "priority": 0.999125533952, "sample_id": "us-code-12-2601-0af01eb6373587c4", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.353247727878, "hint_id": "modal-synthesis-653e9e15b9e1f31a", "predicted_family": "conditional_normative", "priority": 0.503247727878, "sample_id": "us-code-22-6902-0455e288c9f045ab", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-ea1cbc123e4c4560", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-27-101-844dd81c93261fc8", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.983251755846, "hint_id": "modal-synthesis-f7c9b6dbe79bdeef", "predicted_family": "temporal", "priority": 1.133251755846, "sample_id": "us-code-11-1116-0ab0cdf0164f0a74", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
