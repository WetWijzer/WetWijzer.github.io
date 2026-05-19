# packet-000015

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/packet-000015/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/packet-000015/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-dedup-8codex-gpu-1h-20260518T233253Z-codex-compiler_registry-01/worktrees/agent-codex-compiler_registry-01-packet-000015-20260519_000042

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-23b06d229a5e617e` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-23b06d229a5e617e` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.817187532537, "hint_id": "modal-synthesis-0a62fd31a409e112", "predicted_family": "frame", "priority": 0.908940169575, "sample_id": "us-code-25-4305-d7950dea3143e948", "target_family": "deontic", "target_probability": 0.091059830425}`
  evidence: `{"family_margin": -0.992411701483, "hint_id": "modal-synthesis-651154d30536ceb9", "predicted_family": "frame", "priority": 0.998174277068, "sample_id": "us-code-38-1720B-c75bc7ca7346dec7", "target_family": "deontic", "target_probability": 0.001825722932}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-cae8758d089ffb0c", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-42-5197d.-e1e709b02810fccb", "target_family": "deontic", "target_probability": 0.173819074614}`
- `program-e7305721e04de5c5` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-23b06d229a5e617e` score `0.986665`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.999937868552, "hint_id": "modal-synthesis-44397589998b6a66", "predicted_family": "deontic", "priority": 0.999983299058, "sample_id": "us-code-37-302a-4e0eb4cf87987572", "target_family": "temporal", "target_probability": 1.6700942e-05}`
  evidence: `{"family_margin": -0.209117456717, "hint_id": "modal-synthesis-5b980529bab86717", "predicted_family": "frame", "priority": 0.677646677915, "sample_id": "us-code-22-262m-1-5f5f95186247fd54", "target_family": "deontic", "target_probability": 0.322353322085}`
- `program-391f3a77241be11e` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-23b06d229a5e617e` score `0.985199`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.999829776053, "hint_id": "modal-synthesis-a82d5e266624143b", "predicted_family": "deontic", "priority": 0.999938723182, "sample_id": "us-code-26-7608-17fabfe2c7a775c1", "target_family": "frame", "target_probability": 6.1276818e-05}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-ec7018843b278a52", "predicted_family": "deontic", "priority": 0.6248308299, "sample_id": "us-code-19-1367-79cb0669f05d3ba1", "target_family": "deontic", "target_probability": 0.3751691701}`
- `program-80c2d82073798a7a` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->frame","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-23b06d229a5e617e` score `0.942611`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.450804952557, "hint_id": "modal-synthesis-60c502c2a496a4ab", "predicted_family": "deontic", "priority": 0.73764201827, "sample_id": "us-code-12-3756-3abb23438f20afd4", "target_family": "conditional_normative", "target_probability": 0.26235798173}`
  evidence: `{"family_margin": 0.085077099697, "hint_id": "modal-synthesis-835e1d16d2d7bf62", "predicted_family": "temporal", "priority": 0.711907658528, "sample_id": "us-code-7-2287-e59d961ff6c1d601", "target_family": "temporal", "target_probability": 0.288092341472}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-c16deeee3d808ae8", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-16-9-3f261d6cb13af2ef", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.842895449086, "hint_id": "modal-synthesis-f5ae8fdebe57224a", "predicted_family": "frame", "priority": 0.97507208663, "sample_id": "us-code-20-7421-40193c348f272b9b", "target_family": "temporal", "target_probability": 0.02492791337}`

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
- TODO count: `4`

## TODOs
- `program-23b06d229a5e617e`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-23b06d229a5e617e` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.911098457343`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-38-1720B-c75bc7ca7346dec7, us-code-25-4305-d7950dea3143e948, us-code-42-5197d.-e1e709b02810fccb`
  evidence: `{"family_margin": -0.817187532537, "hint_id": "modal-synthesis-0a62fd31a409e112", "predicted_family": "frame", "priority": 0.908940169575, "sample_id": "us-code-25-4305-d7950dea3143e948", "target_family": "deontic", "target_probability": 0.091059830425}`
  evidence: `{"family_margin": -0.992411701483, "hint_id": "modal-synthesis-651154d30536ceb9", "predicted_family": "frame", "priority": 0.998174277068, "sample_id": "us-code-38-1720B-c75bc7ca7346dec7", "target_family": "deontic", "target_probability": 0.001825722932}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-cae8758d089ffb0c", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-42-5197d.-e1e709b02810fccb", "target_family": "deontic", "target_probability": 0.173819074614}`
- `program-e7305721e04de5c5`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-23b06d229a5e617e` score `0.986665`
  loss: `autoencoder_residual_cluster` = `0.838814988486`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-37-302a-4e0eb4cf87987572, us-code-22-262m-1-5f5f95186247fd54`
  evidence: `{"family_margin": -0.999937868552, "hint_id": "modal-synthesis-44397589998b6a66", "predicted_family": "deontic", "priority": 0.999983299058, "sample_id": "us-code-37-302a-4e0eb4cf87987572", "target_family": "temporal", "target_probability": 1.6700942e-05}`
  evidence: `{"family_margin": -0.209117456717, "hint_id": "modal-synthesis-5b980529bab86717", "predicted_family": "frame", "priority": 0.677646677915, "sample_id": "us-code-22-262m-1-5f5f95186247fd54", "target_family": "deontic", "target_probability": 0.322353322085}`
- `program-391f3a77241be11e`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-23b06d229a5e617e` score `0.985199`
  loss: `autoencoder_residual_cluster` = `0.812384776541`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-26-7608-17fabfe2c7a775c1, us-code-19-1367-79cb0669f05d3ba1`
  evidence: `{"family_margin": -0.999829776053, "hint_id": "modal-synthesis-a82d5e266624143b", "predicted_family": "deontic", "priority": 0.999938723182, "sample_id": "us-code-26-7608-17fabfe2c7a775c1", "target_family": "frame", "target_probability": 6.1276818e-05}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-ec7018843b278a52", "predicted_family": "deontic", "priority": 0.6248308299, "sample_id": "us-code-19-1367-79cb0669f05d3ba1", "target_family": "deontic", "target_probability": 0.3751691701}`
- `program-80c2d82073798a7a`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->frame","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-23b06d229a5e617e` score `0.942611`
  loss: `autoencoder_residual_cluster` = `0.73842646884`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-20-7421-40193c348f272b9b, us-code-12-3756-3abb23438f20afd4, us-code-7-2287-e59d961ff6c1d601, us-code-16-9-3f261d6cb13af2ef`
  evidence: `{"family_margin": -0.450804952557, "hint_id": "modal-synthesis-60c502c2a496a4ab", "predicted_family": "deontic", "priority": 0.73764201827, "sample_id": "us-code-12-3756-3abb23438f20afd4", "target_family": "conditional_normative", "target_probability": 0.26235798173}`
  evidence: `{"family_margin": 0.085077099697, "hint_id": "modal-synthesis-835e1d16d2d7bf62", "predicted_family": "temporal", "priority": 0.711907658528, "sample_id": "us-code-7-2287-e59d961ff6c1d601", "target_family": "temporal", "target_probability": 0.288092341472}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-c16deeee3d808ae8", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-16-9-3f261d6cb13af2ef", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.842895449086, "hint_id": "modal-synthesis-f5ae8fdebe57224a", "predicted_family": "frame", "priority": 0.97507208663, "sample_id": "us-code-20-7421-40193c348f272b9b", "target_family": "temporal", "target_probability": 0.02492791337}`
