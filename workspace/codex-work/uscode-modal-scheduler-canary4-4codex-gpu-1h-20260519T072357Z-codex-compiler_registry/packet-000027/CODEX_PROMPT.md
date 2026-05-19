# packet-000027

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/packet-000027/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/packet-000027/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000027-20260519_074123

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-de09e0b44ac7ca53` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.867664184115, "hint_id": "modal-synthesis-15728233863adbe7", "predicted_family": "frame", "priority": 0.98170419515, "sample_id": "us-code-43-957.-45fa418d1d5e2b87", "target_family": "deontic", "target_probability": 0.01829580485}`
  evidence: `{"family_margin": -0.989259898926, "hint_id": "modal-synthesis-58a17cd619eda17c", "predicted_family": "frame", "priority": 0.995037244255, "sample_id": "us-code-20-5604-e496c6af4f6ffb97", "target_family": "temporal", "target_probability": 0.004962755745}`
  evidence: `{"family_margin": -0.952290911916, "hint_id": "modal-synthesis-6543331b414a564c", "predicted_family": "frame", "priority": 0.999356255689, "sample_id": "us-code-10-7542-3e20c9ff17b7c98f", "target_family": "dynamic", "target_probability": 0.000643744311}`
- `program-8fdfc7f4cf3397c9` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.990402`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.575984669239, "hint_id": "modal-synthesis-aa1247db577984b6", "predicted_family": "temporal", "priority": 0.837743751184, "sample_id": "us-code-29-154-7dde92e6219a1637", "target_family": "deontic", "target_probability": 0.162256248816}`
  evidence: `{"family_margin": -0.319474751465, "hint_id": "modal-synthesis-b427b66f1010ca83", "predicted_family": "temporal", "priority": 0.969159340844, "sample_id": "us-code-18-2515-b7fe0ab6c51e49e0", "target_family": "frame", "target_probability": 0.030840659156}`
  evidence: `{"family_margin": -0.928741747566, "hint_id": "modal-synthesis-e5d8df42cac00716", "predicted_family": "frame", "priority": 0.987224974098, "sample_id": "us-code-40-15301-89c9da52313b9d58", "target_family": "temporal", "target_probability": 0.012775025902}`
- `program-4ba4703598d81855` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.986559`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.503766568024, "hint_id": "modal-synthesis-9ef8bd44178f5f00", "predicted_family": "alethic", "priority": 0.826279474642, "sample_id": "us-code-16-398a-e687cd66b1dd5f3b", "target_family": "deontic", "target_probability": 0.173720525358}`
  evidence: `{"family_margin": -0.996527279879, "hint_id": "modal-synthesis-b20f5c8c065bda75", "predicted_family": "frame", "priority": 0.999326352107, "sample_id": "us-code-10-12501-f5bf1e6a25f0e84d", "target_family": "deontic", "target_probability": 0.000673647893}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-cde0daa8cd2630a9", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-20-2993-c0baac0499ad31c8", "target_family": "temporal", "target_probability": 0.008091643722}`
- `program-f35a46304ceecfe1` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.983161`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.089006714447, "hint_id": "modal-synthesis-3dfaac9e3836c008", "predicted_family": "deontic", "priority": 0.507738604186, "sample_id": "us-code-51-60147.-5d171f00b3f04d8f", "target_family": "deontic", "target_probability": 0.492261395814}`
  evidence: `{"family_margin": -0.936653792488, "hint_id": "modal-synthesis-685d6a49de613390", "predicted_family": "frame", "priority": 0.998589677644, "sample_id": "us-code-21-2001-23dd91fc9477a14b", "target_family": "temporal", "target_probability": 0.001410322356}`
  evidence: `{"family_margin": -0.999658532901, "hint_id": "modal-synthesis-7cac2346251166f8", "predicted_family": "frame", "priority": 0.999966377259, "sample_id": "us-code-22-1475e-bec3039174fdd403", "target_family": "conditional_normative", "target_probability": 3.3622741e-05}`
- `program-8438bf2c8a1c3ad2` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.983064`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-32ed7df1c1ec3691", "predicted_family": "temporal", "priority": 0.585977688839, "sample_id": "us-code-18-3528-de588bcb29c3c29c", "target_family": "conditional_normative", "target_probability": 0.414022311161}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-5d5d38ecb9c91917", "predicted_family": "alethic", "priority": 1.0, "sample_id": "us-code-21-301-5c6041ea0606b416", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.996246890038, "hint_id": "modal-synthesis-ad9221aa4352bd3f", "predicted_family": "frame", "priority": 0.999326541649, "sample_id": "us-code-16-1011-3904d048740cdb51", "target_family": "temporal", "target_probability": 0.000673458351}`
- `program-e492f87243c980b9` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.9821`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-3002d08e74d2d97e", "predicted_family": "deontic", "priority": 0.551919856002, "sample_id": "us-code-19-81h-0a0f7a05da441d89", "target_family": "deontic", "target_probability": 0.448080143998}`
  evidence: `{"family_margin": -0.917577654701, "hint_id": "modal-synthesis-368bd9cf1f24bcdf", "predicted_family": "frame", "priority": 0.964860784179, "sample_id": "us-code-16-459a-5a-a4059543f2650ab3", "target_family": "deontic", "target_probability": 0.035139215821}`
  evidence: `{"family_margin": -0.999055720716, "hint_id": "modal-synthesis-3d3972f0216c12db", "predicted_family": "frame", "priority": 0.999690873361, "sample_id": "us-code-12-5226-76bc695a57d44291", "target_family": "deontic", "target_probability": 0.000309126639}`

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

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-de09e0b44ac7ca53`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.992032565031`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-7542-3e20c9ff17b7c98f, us-code-20-5604-e496c6af4f6ffb97, us-code-43-957.-45fa418d1d5e2b87`
  evidence: `{"family_margin": -0.867664184115, "hint_id": "modal-synthesis-15728233863adbe7", "predicted_family": "frame", "priority": 0.98170419515, "sample_id": "us-code-43-957.-45fa418d1d5e2b87", "target_family": "deontic", "target_probability": 0.01829580485}`
  evidence: `{"family_margin": -0.989259898926, "hint_id": "modal-synthesis-58a17cd619eda17c", "predicted_family": "frame", "priority": 0.995037244255, "sample_id": "us-code-20-5604-e496c6af4f6ffb97", "target_family": "temporal", "target_probability": 0.004962755745}`
  evidence: `{"family_margin": -0.952290911916, "hint_id": "modal-synthesis-6543331b414a564c", "predicted_family": "frame", "priority": 0.999356255689, "sample_id": "us-code-10-7542-3e20c9ff17b7c98f", "target_family": "dynamic", "target_probability": 0.000643744311}`
- `program-8fdfc7f4cf3397c9`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.990402`
  loss: `autoencoder_residual_cluster` = `0.931376022042`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-40-15301-89c9da52313b9d58, us-code-18-2515-b7fe0ab6c51e49e0, us-code-29-154-7dde92e6219a1637`
  evidence: `{"family_margin": -0.575984669239, "hint_id": "modal-synthesis-aa1247db577984b6", "predicted_family": "temporal", "priority": 0.837743751184, "sample_id": "us-code-29-154-7dde92e6219a1637", "target_family": "deontic", "target_probability": 0.162256248816}`
  evidence: `{"family_margin": -0.319474751465, "hint_id": "modal-synthesis-b427b66f1010ca83", "predicted_family": "temporal", "priority": 0.969159340844, "sample_id": "us-code-18-2515-b7fe0ab6c51e49e0", "target_family": "frame", "target_probability": 0.030840659156}`
  evidence: `{"family_margin": -0.928741747566, "hint_id": "modal-synthesis-e5d8df42cac00716", "predicted_family": "frame", "priority": 0.987224974098, "sample_id": "us-code-40-15301-89c9da52313b9d58", "target_family": "temporal", "target_probability": 0.012775025902}`
- `program-4ba4703598d81855`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.986559`
  loss: `autoencoder_residual_cluster` = `0.939171394342`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-12501-f5bf1e6a25f0e84d, us-code-20-2993-c0baac0499ad31c8, us-code-16-398a-e687cd66b1dd5f3b`
  evidence: `{"family_margin": -0.503766568024, "hint_id": "modal-synthesis-9ef8bd44178f5f00", "predicted_family": "alethic", "priority": 0.826279474642, "sample_id": "us-code-16-398a-e687cd66b1dd5f3b", "target_family": "deontic", "target_probability": 0.173720525358}`
  evidence: `{"family_margin": -0.996527279879, "hint_id": "modal-synthesis-b20f5c8c065bda75", "predicted_family": "frame", "priority": 0.999326352107, "sample_id": "us-code-10-12501-f5bf1e6a25f0e84d", "target_family": "deontic", "target_probability": 0.000673647893}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-cde0daa8cd2630a9", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-20-2993-c0baac0499ad31c8", "target_family": "temporal", "target_probability": 0.008091643722}`
- `program-f35a46304ceecfe1`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.983161`
  loss: `autoencoder_residual_cluster` = `0.83543155303`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-1475e-bec3039174fdd403, us-code-21-2001-23dd91fc9477a14b, us-code-51-60147.-5d171f00b3f04d8f`
  evidence: `{"family_margin": 0.089006714447, "hint_id": "modal-synthesis-3dfaac9e3836c008", "predicted_family": "deontic", "priority": 0.507738604186, "sample_id": "us-code-51-60147.-5d171f00b3f04d8f", "target_family": "deontic", "target_probability": 0.492261395814}`
  evidence: `{"family_margin": -0.936653792488, "hint_id": "modal-synthesis-685d6a49de613390", "predicted_family": "frame", "priority": 0.998589677644, "sample_id": "us-code-21-2001-23dd91fc9477a14b", "target_family": "temporal", "target_probability": 0.001410322356}`
  evidence: `{"family_margin": -0.999658532901, "hint_id": "modal-synthesis-7cac2346251166f8", "predicted_family": "frame", "priority": 0.999966377259, "sample_id": "us-code-22-1475e-bec3039174fdd403", "target_family": "conditional_normative", "target_probability": 3.3622741e-05}`
- `program-8438bf2c8a1c3ad2`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.983064`
  loss: `autoencoder_residual_cluster` = `0.861768076829`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-21-301-5c6041ea0606b416, us-code-16-1011-3904d048740cdb51, us-code-18-3528-de588bcb29c3c29c`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-32ed7df1c1ec3691", "predicted_family": "temporal", "priority": 0.585977688839, "sample_id": "us-code-18-3528-de588bcb29c3c29c", "target_family": "conditional_normative", "target_probability": 0.414022311161}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-5d5d38ecb9c91917", "predicted_family": "alethic", "priority": 1.0, "sample_id": "us-code-21-301-5c6041ea0606b416", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.996246890038, "hint_id": "modal-synthesis-ad9221aa4352bd3f", "predicted_family": "frame", "priority": 0.999326541649, "sample_id": "us-code-16-1011-3904d048740cdb51", "target_family": "temporal", "target_probability": 0.000673458351}`
- `program-e492f87243c980b9`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-de09e0b44ac7ca53` score `0.9821`
  loss: `autoencoder_residual_cluster` = `0.838823837847`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-5226-76bc695a57d44291, us-code-16-459a-5a-a4059543f2650ab3, us-code-19-81h-0a0f7a05da441d89`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-3002d08e74d2d97e", "predicted_family": "deontic", "priority": 0.551919856002, "sample_id": "us-code-19-81h-0a0f7a05da441d89", "target_family": "deontic", "target_probability": 0.448080143998}`
  evidence: `{"family_margin": -0.917577654701, "hint_id": "modal-synthesis-368bd9cf1f24bcdf", "predicted_family": "frame", "priority": 0.964860784179, "sample_id": "us-code-16-459a-5a-a4059543f2650ab3", "target_family": "deontic", "target_probability": 0.035139215821}`
  evidence: `{"family_margin": -0.999055720716, "hint_id": "modal-synthesis-3d3972f0216c12db", "predicted_family": "frame", "priority": 0.999690873361, "sample_id": "us-code-12-5226-76bc695a57d44291", "target_family": "deontic", "target_probability": 0.000309126639}`
