# packet-000022

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000022/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/packet-000022/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-02/worktrees/agent-codex-compiler_registry-02-packet-000022-20260518_235953

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-abf324e649c4f4e7` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999794724519, "hint_id": "modal-synthesis-5ee2b49471bc0738", "predicted_family": "deontic", "priority": 0.999954607329, "sample_id": "us-code-42-254c-cff7c0b338926702", "target_family": "temporal", "target_probability": 4.5392671e-05}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-b0253dd9ac3224aa", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-19-4204-56dfc3aa09064923", "target_family": "conditional_normative", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.999974756549, "hint_id": "modal-synthesis-e97e2e5f17ef22e6", "predicted_family": "deontic", "priority": 0.999999352421, "sample_id": "us-code-42-2000a-a72598b7e52c6ff1", "target_family": "temporal", "target_probability": 6.47579e-07}`
- `program-ba6e7d86de2654de` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.987355`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.522862570721, "hint_id": "modal-synthesis-123f50636b4b25a5", "predicted_family": "conditional_normative", "priority": 0.918162782949, "sample_id": "us-code-42-15002.-1b888a13a1154232", "target_family": "temporal", "target_probability": 0.081837217051}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-b35af6faa7962e00", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-15-2063-a311159029e92eb8", "target_family": "conditional_normative", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-da51c53425b9355a", "predicted_family": "frame", "priority": 0.833356638801, "sample_id": "us-code-16-1444-b4ceb64e9f14f67c", "target_family": "deontic", "target_probability": 0.166643361199}`
- `program-83893175931d5de5` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.984103`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.184209960794, "hint_id": "modal-synthesis-0832ea0e05ab2e3e", "predicted_family": "deontic", "priority": 0.531831474697, "sample_id": "us-code-30-27-80697a344cb94927", "target_family": "deontic", "target_probability": 0.468168525303}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-0d54ca3c1dbcbc5f", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-22-266a-6fea26e1a0b4c9d8", "target_family": "temporal", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.999999686486, "hint_id": "modal-synthesis-8ccd88d425ed2778", "predicted_family": "deontic", "priority": 0.999999999995, "sample_id": "us-code-42-1962d-68a2d7727b46b5ff", "target_family": "epistemic", "target_probability": 5e-12}`
- `program-9304d50d872dbcaa` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.979207`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999663046469, "hint_id": "modal-synthesis-0683ced7b4f57ed8", "predicted_family": "deontic", "priority": 0.999954613307, "sample_id": "us-code-7-203-e7b6091da8305ac1", "target_family": "temporal", "target_probability": 4.5386693e-05}`
  evidence: `{"family_margin": -0.982007836763, "hint_id": "modal-synthesis-83c728df9ce5f1b8", "predicted_family": "conditional_normative", "priority": 0.999997003762, "sample_id": "us-code-42-4016.-01f4e3fc11a0dfef", "target_family": "frame", "target_probability": 2.996238e-06}`
  evidence: `{"family_margin": -0.994157979433, "hint_id": "modal-synthesis-9cea358b71b626f5", "predicted_family": "deontic", "priority": 0.999092617842, "sample_id": "us-code-14-3739-9876992d772d0081", "target_family": "conditional_normative", "target_probability": 0.000907382158}`
- `program-aa385d55a4bfe125` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.978155`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.460871051442, "hint_id": "modal-synthesis-2e6336957493f306", "predicted_family": "conditional_normative", "priority": 0.731783783191, "sample_id": "us-code-15-2068-96f550da92fa0031", "target_family": "deontic", "target_probability": 0.268216216809}`
  evidence: `{"family_margin": -0.148879075705, "hint_id": "modal-synthesis-6bb8622c407ca825", "predicted_family": "frame", "priority": 0.574459546304, "sample_id": "us-code-12-635j-d4055fd8d6fa8eb8", "target_family": "deontic", "target_probability": 0.425540453696}`
- `program-9bce289c7cd05f30` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.97776`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.244804791593, "hint_id": "modal-synthesis-1393be09d57c5981", "predicted_family": "frame", "priority": 0.622634862383, "sample_id": "us-code-49-60127.-8664408f5c716452", "target_family": "deontic", "target_probability": 0.377365137617}`
  evidence: `{"family_margin": -0.71376499545, "hint_id": "modal-synthesis-696c7af2fd9184c5", "predicted_family": "frame", "priority": 0.920464621814, "sample_id": "us-code-34-21301-1e886420be029827", "target_family": "deontic", "target_probability": 0.079535378186}`
  evidence: `{"family_margin": -0.999091663546, "hint_id": "modal-synthesis-f570ccf3db6c9f25", "predicted_family": "deontic", "priority": 0.999547379178, "sample_id": "us-code-42-5422.-5b961f79f3664b3e", "target_family": "frame", "target_probability": 0.000452620822}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.


## Execution Instructions
Work only inside the packet worktree.
Your worktree edits may be applied back to the source checkout and validated automatically when this packet finishes.
Do not create changes.patch or other patch artifact files; leave source and test edits directly in the worktree.
Treat the packet's program_synthesis_scope metadata as the AST/write-scope boundary; keep edits inside that lane unless a test requires a small adjacent change.
When multiple TODOs are present, treat their semantic_bundle_key or vector_bundle metadata as evidence for one generalized compiler/decompiler/frame improvement over one-off sample fixes.
Implement a narrow deterministic parser, IR, decoder, or frame-logic improvement for the claimed TODOs.
Prefer explainable compiler/decompiler code over learned weights when the TODO concerns modal or frame semantics.
Use local repository files and tests only; do not use web search for this packet.
Run the smallest relevant tests you can before finishing.
Leave unrelated files alone.

## Claimed Autoencoder TODO List
# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-abf324e649c4f4e7`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.99998465325`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-19-4204-56dfc3aa09064923, us-code-42-2000a-a72598b7e52c6ff1, us-code-42-254c-cff7c0b338926702`
  evidence: `{"family_margin": -0.999794724519, "hint_id": "modal-synthesis-5ee2b49471bc0738", "predicted_family": "deontic", "priority": 0.999954607329, "sample_id": "us-code-42-254c-cff7c0b338926702", "target_family": "temporal", "target_probability": 4.5392671e-05}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-b0253dd9ac3224aa", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-19-4204-56dfc3aa09064923", "target_family": "conditional_normative", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.999974756549, "hint_id": "modal-synthesis-e97e2e5f17ef22e6", "predicted_family": "deontic", "priority": 0.999999352421, "sample_id": "us-code-42-2000a-a72598b7e52c6ff1", "target_family": "temporal", "target_probability": 6.47579e-07}`
- `program-ba6e7d86de2654de`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.987355`
  loss: `autoencoder_residual_cluster` = `0.917173140583`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-2063-a311159029e92eb8, us-code-42-15002.-1b888a13a1154232, us-code-16-1444-b4ceb64e9f14f67c`
  evidence: `{"family_margin": -0.522862570721, "hint_id": "modal-synthesis-123f50636b4b25a5", "predicted_family": "conditional_normative", "priority": 0.918162782949, "sample_id": "us-code-42-15002.-1b888a13a1154232", "target_family": "temporal", "target_probability": 0.081837217051}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-b35af6faa7962e00", "predicted_family": "deontic", "priority": 1.0, "sample_id": "us-code-15-2063-a311159029e92eb8", "target_family": "conditional_normative", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-da51c53425b9355a", "predicted_family": "frame", "priority": 0.833356638801, "sample_id": "us-code-16-1444-b4ceb64e9f14f67c", "target_family": "deontic", "target_probability": 0.166643361199}`
- `program-83893175931d5de5`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.984103`
  loss: `autoencoder_residual_cluster` = `0.786004133359`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-1962d-68a2d7727b46b5ff, us-code-22-266a-6fea26e1a0b4c9d8, us-code-30-27-80697a344cb94927`
  evidence: `{"family_margin": 0.184209960794, "hint_id": "modal-synthesis-0832ea0e05ab2e3e", "predicted_family": "deontic", "priority": 0.531831474697, "sample_id": "us-code-30-27-80697a344cb94927", "target_family": "deontic", "target_probability": 0.468168525303}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-0d54ca3c1dbcbc5f", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-22-266a-6fea26e1a0b4c9d8", "target_family": "temporal", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.999999686486, "hint_id": "modal-synthesis-8ccd88d425ed2778", "predicted_family": "deontic", "priority": 0.999999999995, "sample_id": "us-code-42-1962d-68a2d7727b46b5ff", "target_family": "epistemic", "target_probability": 5e-12}`
- `program-9304d50d872dbcaa`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.979207`
  loss: `autoencoder_residual_cluster` = `0.999681411637`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-4016.-01f4e3fc11a0dfef, us-code-7-203-e7b6091da8305ac1, us-code-14-3739-9876992d772d0081`
  evidence: `{"family_margin": -0.999663046469, "hint_id": "modal-synthesis-0683ced7b4f57ed8", "predicted_family": "deontic", "priority": 0.999954613307, "sample_id": "us-code-7-203-e7b6091da8305ac1", "target_family": "temporal", "target_probability": 4.5386693e-05}`
  evidence: `{"family_margin": -0.982007836763, "hint_id": "modal-synthesis-83c728df9ce5f1b8", "predicted_family": "conditional_normative", "priority": 0.999997003762, "sample_id": "us-code-42-4016.-01f4e3fc11a0dfef", "target_family": "frame", "target_probability": 2.996238e-06}`
  evidence: `{"family_margin": -0.994157979433, "hint_id": "modal-synthesis-9cea358b71b626f5", "predicted_family": "deontic", "priority": 0.999092617842, "sample_id": "us-code-14-3739-9876992d772d0081", "target_family": "conditional_normative", "target_probability": 0.000907382158}`
- `program-aa385d55a4bfe125`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.978155`
  loss: `autoencoder_residual_cluster` = `0.653121664747`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-2068-96f550da92fa0031, us-code-12-635j-d4055fd8d6fa8eb8`
  evidence: `{"family_margin": -0.460871051442, "hint_id": "modal-synthesis-2e6336957493f306", "predicted_family": "conditional_normative", "priority": 0.731783783191, "sample_id": "us-code-15-2068-96f550da92fa0031", "target_family": "deontic", "target_probability": 0.268216216809}`
  evidence: `{"family_margin": -0.148879075705, "hint_id": "modal-synthesis-6bb8622c407ca825", "predicted_family": "frame", "priority": 0.574459546304, "sample_id": "us-code-12-635j-d4055fd8d6fa8eb8", "target_family": "deontic", "target_probability": 0.425540453696}`
- `program-9bce289c7cd05f30`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-abf324e649c4f4e7` score `0.97776`
  loss: `autoencoder_residual_cluster` = `0.847548954458`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-5422.-5b961f79f3664b3e, us-code-34-21301-1e886420be029827, us-code-49-60127.-8664408f5c716452`
  evidence: `{"family_margin": -0.244804791593, "hint_id": "modal-synthesis-1393be09d57c5981", "predicted_family": "frame", "priority": 0.622634862383, "sample_id": "us-code-49-60127.-8664408f5c716452", "target_family": "deontic", "target_probability": 0.377365137617}`
  evidence: `{"family_margin": -0.71376499545, "hint_id": "modal-synthesis-696c7af2fd9184c5", "predicted_family": "frame", "priority": 0.920464621814, "sample_id": "us-code-34-21301-1e886420be029827", "target_family": "deontic", "target_probability": 0.079535378186}`
  evidence: `{"family_margin": -0.999091663546, "hint_id": "modal-synthesis-f570ccf3db6c9f25", "predicted_family": "deontic", "priority": 0.999547379178, "sample_id": "us-code-42-5422.-5b961f79f3664b3e", "target_family": "frame", "target_probability": 0.000452620822}`
