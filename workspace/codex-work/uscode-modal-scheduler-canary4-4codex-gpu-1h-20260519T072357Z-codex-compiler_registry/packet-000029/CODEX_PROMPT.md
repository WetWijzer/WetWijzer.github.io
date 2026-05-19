# packet-000029

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/packet-000029/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/packet-000029/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000029-20260519_080348

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-2f7cb1ab8986387c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.987482973805, "hint_id": "modal-synthesis-e53e3c8e77deff78", "predicted_family": "frame", "priority": 0.995947822463, "sample_id": "us-code-34-20924-4eecfc8963e9330c", "target_family": "deontic", "target_probability": 0.004052177537}`
  evidence: `{"family_margin": -0.998770601276, "hint_id": "modal-synthesis-f845c1dd6355d7d2", "predicted_family": "temporal", "priority": 1.0, "sample_id": "us-code-22-9521-34e0d0fb34bfe30f", "target_family": "conditional_normative", "target_probability": 0.0}`
- `program-a612988da61dd24b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.996411`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.927756191866, "hint_id": "modal-synthesis-afb7699cf4f977b0", "predicted_family": "frame", "priority": 0.964470990669, "sample_id": "us-code-18-2232-d79e57e648a5300a", "target_family": "temporal", "target_probability": 0.035529009331}`
  evidence: `{"family_margin": -0.682861911733, "hint_id": "modal-synthesis-b3bcda08b808c36b", "predicted_family": "conditional_normative", "priority": 0.904559516606, "sample_id": "us-code-19-1319-4a008bf97b1ec553", "target_family": "deontic", "target_probability": 0.095440483394}`
- `program-11b789d59260cd44` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.987762`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.998961585451, "hint_id": "modal-synthesis-995f1c9e131b5052", "predicted_family": "frame", "priority": 0.999908662354, "sample_id": "us-code-33-2330b-9aa26e5961270d1d", "target_family": "conditional_normative", "target_probability": 9.1337646e-05}`
  evidence: `{"family_margin": -0.599864963847, "hint_id": "modal-synthesis-cf37e14eefd9b949", "predicted_family": "deontic", "priority": 0.820040510846, "sample_id": "us-code-16-460aaa-7-9c44309c9a316ae6", "target_family": "conditional_normative", "target_probability": 0.179959489154}`
- `program-c4c313060ef58a46` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.987484`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.560778212654, "hint_id": "modal-synthesis-abdd4e2997247d4e", "predicted_family": "temporal", "priority": 0.970617634971, "sample_id": "us-code-19-273-7820f6e8db339143", "target_family": "deontic", "target_probability": 0.029382365029}`
  evidence: `{"family_margin": -0.998647484376, "hint_id": "modal-synthesis-ad4cd180d710cb76", "predicted_family": "alethic", "priority": 0.999999991921, "sample_id": "us-code-5-5702-300a57e6beeea23d", "target_family": "conditional_normative", "target_probability": 8.079e-09}`
- `program-c81c9039f28ccbbc` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.987352`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.837873320286, "hint_id": "modal-synthesis-944b14b414e25ee6", "predicted_family": "frame", "priority": 0.924298069574, "sample_id": "us-code-16-833e-30cd9a25a3398f01", "target_family": "deontic", "target_probability": 0.075701930426}`
  evidence: `{"family_margin": -0.83015760469, "hint_id": "modal-synthesis-c7bb470f50c51e26", "predicted_family": "temporal", "priority": 0.968433961873, "sample_id": "us-code-16-3931-c4cea8b87c9b66c5", "target_family": "deontic", "target_probability": 0.031566038127}`
- `program-9bcf0541671f3989` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.982289`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.319507045233, "hint_id": "modal-synthesis-ac8ab9289778b987", "predicted_family": "deontic", "priority": 0.861740025355, "sample_id": "us-code-2-1385-ebbcc5d70fc5a836", "target_family": "temporal", "target_probability": 0.138259974645}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-c46f506c829d7b63", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-6-321h-83093fb8aa566f6e", "target_family": "deontic", "target_probability": 0.173819074614}`

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
- `program-2f7cb1ab8986387c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.997973911232`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-9521-34e0d0fb34bfe30f, us-code-34-20924-4eecfc8963e9330c`
  evidence: `{"family_margin": -0.987482973805, "hint_id": "modal-synthesis-e53e3c8e77deff78", "predicted_family": "frame", "priority": 0.995947822463, "sample_id": "us-code-34-20924-4eecfc8963e9330c", "target_family": "deontic", "target_probability": 0.004052177537}`
  evidence: `{"family_margin": -0.998770601276, "hint_id": "modal-synthesis-f845c1dd6355d7d2", "predicted_family": "temporal", "priority": 1.0, "sample_id": "us-code-22-9521-34e0d0fb34bfe30f", "target_family": "conditional_normative", "target_probability": 0.0}`
- `program-a612988da61dd24b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.996411`
  loss: `autoencoder_residual_cluster` = `0.934515253637`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-18-2232-d79e57e648a5300a, us-code-19-1319-4a008bf97b1ec553`
  evidence: `{"family_margin": -0.927756191866, "hint_id": "modal-synthesis-afb7699cf4f977b0", "predicted_family": "frame", "priority": 0.964470990669, "sample_id": "us-code-18-2232-d79e57e648a5300a", "target_family": "temporal", "target_probability": 0.035529009331}`
  evidence: `{"family_margin": -0.682861911733, "hint_id": "modal-synthesis-b3bcda08b808c36b", "predicted_family": "conditional_normative", "priority": 0.904559516606, "sample_id": "us-code-19-1319-4a008bf97b1ec553", "target_family": "deontic", "target_probability": 0.095440483394}`
- `program-11b789d59260cd44`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.987762`
  loss: `autoencoder_residual_cluster` = `0.9099745866`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-33-2330b-9aa26e5961270d1d, us-code-16-460aaa-7-9c44309c9a316ae6`
  evidence: `{"family_margin": -0.998961585451, "hint_id": "modal-synthesis-995f1c9e131b5052", "predicted_family": "frame", "priority": 0.999908662354, "sample_id": "us-code-33-2330b-9aa26e5961270d1d", "target_family": "conditional_normative", "target_probability": 9.1337646e-05}`
  evidence: `{"family_margin": -0.599864963847, "hint_id": "modal-synthesis-cf37e14eefd9b949", "predicted_family": "deontic", "priority": 0.820040510846, "sample_id": "us-code-16-460aaa-7-9c44309c9a316ae6", "target_family": "conditional_normative", "target_probability": 0.179959489154}`
- `program-c4c313060ef58a46`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.987484`
  loss: `autoencoder_residual_cluster` = `0.985308813446`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-5-5702-300a57e6beeea23d, us-code-19-273-7820f6e8db339143`
  evidence: `{"family_margin": -0.560778212654, "hint_id": "modal-synthesis-abdd4e2997247d4e", "predicted_family": "temporal", "priority": 0.970617634971, "sample_id": "us-code-19-273-7820f6e8db339143", "target_family": "deontic", "target_probability": 0.029382365029}`
  evidence: `{"family_margin": -0.998647484376, "hint_id": "modal-synthesis-ad4cd180d710cb76", "predicted_family": "alethic", "priority": 0.999999991921, "sample_id": "us-code-5-5702-300a57e6beeea23d", "target_family": "conditional_normative", "target_probability": 8.079e-09}`
- `program-c81c9039f28ccbbc`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.987352`
  loss: `autoencoder_residual_cluster` = `0.946366015723`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-3931-c4cea8b87c9b66c5, us-code-16-833e-30cd9a25a3398f01`
  evidence: `{"family_margin": -0.837873320286, "hint_id": "modal-synthesis-944b14b414e25ee6", "predicted_family": "frame", "priority": 0.924298069574, "sample_id": "us-code-16-833e-30cd9a25a3398f01", "target_family": "deontic", "target_probability": 0.075701930426}`
  evidence: `{"family_margin": -0.83015760469, "hint_id": "modal-synthesis-c7bb470f50c51e26", "predicted_family": "temporal", "priority": 0.968433961873, "sample_id": "us-code-16-3931-c4cea8b87c9b66c5", "target_family": "deontic", "target_probability": 0.031566038127}`
- `program-9bcf0541671f3989`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2f7cb1ab8986387c` score `0.982289`
  loss: `autoencoder_residual_cluster` = `0.843960475371`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-2-1385-ebbcc5d70fc5a836, us-code-6-321h-83093fb8aa566f6e`
  evidence: `{"family_margin": -0.319507045233, "hint_id": "modal-synthesis-ac8ab9289778b987", "predicted_family": "deontic", "priority": 0.861740025355, "sample_id": "us-code-2-1385-ebbcc5d70fc5a836", "target_family": "temporal", "target_probability": 0.138259974645}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-c46f506c829d7b63", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-6-321h-83093fb8aa566f6e", "target_family": "deontic", "target_probability": 0.173819074614}`
