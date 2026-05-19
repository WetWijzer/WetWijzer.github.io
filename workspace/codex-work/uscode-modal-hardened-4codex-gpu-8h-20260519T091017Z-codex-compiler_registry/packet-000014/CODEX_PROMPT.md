# packet-000014

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000014/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000014/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000014-20260519_095214

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-f3fed084e53b5400` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.951864089479, "hint_id": "modal-synthesis-7976e702285339ce", "predicted_family": "frame", "priority": 0.98939568806, "sample_id": "us-code-10-668-be76cc69905bc870", "target_family": "temporal", "target_probability": 0.01060431194}`
  evidence: `{"family_margin": -0.760921047218, "hint_id": "modal-synthesis-ffaa3c44dd3cb20a", "predicted_family": "deontic", "priority": 0.991439966724, "sample_id": "us-code-30-1751-429bbb3228cd7eb2", "target_family": "frame", "target_probability": 0.008560033276}`
- `program-588256e44c83b23b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.989043`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.68151169487, "hint_id": "modal-synthesis-4c60813ff4119bee", "predicted_family": "frame", "priority": 0.924058631714, "sample_id": "us-code-16-459e-9-08e7333353524538", "target_family": "deontic", "target_probability": 0.075941368286}`
  evidence: `{"family_margin": -0.484415617754, "hint_id": "modal-synthesis-d2f9c3bb0026fbe4", "predicted_family": "deontic", "priority": 0.99803092884, "sample_id": "us-code-35-382-0dd76b4fbbd826e0", "target_family": "frame", "target_probability": 0.00196907116}`
- `program-e0192d2decc67560` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.982021`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.978102474692, "hint_id": "modal-synthesis-0da71c827dc288b7", "predicted_family": "frame", "priority": 0.999756864653, "sample_id": "us-code-26-7409-2a69930501e77785", "target_family": "temporal", "target_probability": 0.000243135347}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-1b2ac57b3a3a5fd0", "predicted_family": "deontic", "priority": 0.619763832652, "sample_id": "us-code-20-3608-fb6f1608d67075db", "target_family": "deontic", "target_probability": 0.380236167348}`
  evidence: `{"family_margin": -0.976122308832, "hint_id": "modal-synthesis-66231b97c443c29a", "predicted_family": "frame", "priority": 0.998204244387, "sample_id": "us-code-10-2650-fc88eeb2517632d4", "target_family": "temporal", "target_probability": 0.001795755613}`
- `program-85e5e9133dff773c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.979939`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.945327455354, "hint_id": "modal-synthesis-4e980319d07d6126", "predicted_family": "frame", "priority": 0.984069381973, "sample_id": "us-code-42-3789a to 3789c.-a0e95998afc35ad9", "target_family": "deontic", "target_probability": 0.015930618027}`
  evidence: `{"family_margin": 0.228522909742, "hint_id": "modal-synthesis-5f595ccbdc1c4954", "predicted_family": "deontic", "priority": 0.542954180517, "sample_id": "us-code-16-539j-ae73a6de5a483172", "target_family": "deontic", "target_probability": 0.457045819483}`
- `program-cde23d0b00803624` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.971591`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.457881989941, "hint_id": "modal-synthesis-0e0f3a83525f95ca", "predicted_family": "deontic", "priority": 0.854043860074, "sample_id": "us-code-16-430f-1-a0a5ab553335000c", "target_family": "temporal", "target_probability": 0.145956139926}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-e6ceb51a2685ae3d", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-48-1393.-d4c39a83be6fedcd", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.804231432521, "hint_id": "modal-synthesis-f89bba23296c3067", "predicted_family": "frame", "priority": 0.98304175554, "sample_id": "us-code-42-12333.-d32797690eb1f7a0", "target_family": "deontic", "target_probability": 0.01695824446}`
- `program-4e67ca97ad4eccb5` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.97088`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.612873897209, "hint_id": "modal-synthesis-1441587b87fef9f9", "predicted_family": "deontic", "priority": 0.846781525698, "sample_id": "us-code-42-300s-2ad85e15c53957bb", "target_family": "conditional_normative", "target_probability": 0.153218474302}`
  evidence: `{"family_margin": -0.79631899279, "hint_id": "modal-synthesis-5722331cc2e5ea9d", "predicted_family": "deontic", "priority": 0.97550328209, "sample_id": "us-code-44-703.-d84677bf1ce82052", "target_family": "temporal", "target_probability": 0.02449671791}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-9afab96163b9109a", "predicted_family": "frame", "priority": 0.851064907891, "sample_id": "us-code-10-8780-2539f35ce317901f", "target_family": "deontic", "target_probability": 0.148935092109}`

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

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-f3fed084e53b5400`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.990417827392`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-30-1751-429bbb3228cd7eb2, us-code-10-668-be76cc69905bc870`
  evidence: `{"family_margin": -0.951864089479, "hint_id": "modal-synthesis-7976e702285339ce", "predicted_family": "frame", "priority": 0.98939568806, "sample_id": "us-code-10-668-be76cc69905bc870", "target_family": "temporal", "target_probability": 0.01060431194}`
  evidence: `{"family_margin": -0.760921047218, "hint_id": "modal-synthesis-ffaa3c44dd3cb20a", "predicted_family": "deontic", "priority": 0.991439966724, "sample_id": "us-code-30-1751-429bbb3228cd7eb2", "target_family": "frame", "target_probability": 0.008560033276}`
- `program-588256e44c83b23b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.989043`
  loss: `autoencoder_residual_cluster` = `0.961044780277`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-35-382-0dd76b4fbbd826e0, us-code-16-459e-9-08e7333353524538`
  evidence: `{"family_margin": -0.68151169487, "hint_id": "modal-synthesis-4c60813ff4119bee", "predicted_family": "frame", "priority": 0.924058631714, "sample_id": "us-code-16-459e-9-08e7333353524538", "target_family": "deontic", "target_probability": 0.075941368286}`
  evidence: `{"family_margin": -0.484415617754, "hint_id": "modal-synthesis-d2f9c3bb0026fbe4", "predicted_family": "deontic", "priority": 0.99803092884, "sample_id": "us-code-35-382-0dd76b4fbbd826e0", "target_family": "frame", "target_probability": 0.00196907116}`
- `program-e0192d2decc67560`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.982021`
  loss: `autoencoder_residual_cluster` = `0.872574980564`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-26-7409-2a69930501e77785, us-code-10-2650-fc88eeb2517632d4, us-code-20-3608-fb6f1608d67075db`
  evidence: `{"family_margin": -0.978102474692, "hint_id": "modal-synthesis-0da71c827dc288b7", "predicted_family": "frame", "priority": 0.999756864653, "sample_id": "us-code-26-7409-2a69930501e77785", "target_family": "temporal", "target_probability": 0.000243135347}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-1b2ac57b3a3a5fd0", "predicted_family": "deontic", "priority": 0.619763832652, "sample_id": "us-code-20-3608-fb6f1608d67075db", "target_family": "deontic", "target_probability": 0.380236167348}`
  evidence: `{"family_margin": -0.976122308832, "hint_id": "modal-synthesis-66231b97c443c29a", "predicted_family": "frame", "priority": 0.998204244387, "sample_id": "us-code-10-2650-fc88eeb2517632d4", "target_family": "temporal", "target_probability": 0.001795755613}`
- `program-85e5e9133dff773c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.979939`
  loss: `autoencoder_residual_cluster` = `0.763511781245`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-3789a to 3789c.-a0e95998afc35ad9, us-code-16-539j-ae73a6de5a483172`
  evidence: `{"family_margin": -0.945327455354, "hint_id": "modal-synthesis-4e980319d07d6126", "predicted_family": "frame", "priority": 0.984069381973, "sample_id": "us-code-42-3789a to 3789c.-a0e95998afc35ad9", "target_family": "deontic", "target_probability": 0.015930618027}`
  evidence: `{"family_margin": 0.228522909742, "hint_id": "modal-synthesis-5f595ccbdc1c4954", "predicted_family": "deontic", "priority": 0.542954180517, "sample_id": "us-code-16-539j-ae73a6de5a483172", "target_family": "deontic", "target_probability": 0.457045819483}`
- `program-cde23d0b00803624`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.971591`
  loss: `autoencoder_residual_cluster` = `0.788723242516`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-12333.-d32797690eb1f7a0, us-code-16-430f-1-a0a5ab553335000c, us-code-48-1393.-d4c39a83be6fedcd`
  evidence: `{"family_margin": -0.457881989941, "hint_id": "modal-synthesis-0e0f3a83525f95ca", "predicted_family": "deontic", "priority": 0.854043860074, "sample_id": "us-code-16-430f-1-a0a5ab553335000c", "target_family": "temporal", "target_probability": 0.145956139926}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-e6ceb51a2685ae3d", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-48-1393.-d4c39a83be6fedcd", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.804231432521, "hint_id": "modal-synthesis-f89bba23296c3067", "predicted_family": "frame", "priority": 0.98304175554, "sample_id": "us-code-42-12333.-d32797690eb1f7a0", "target_family": "deontic", "target_probability": 0.01695824446}`
- `program-4e67ca97ad4eccb5`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-f3fed084e53b5400` score `0.97088`
  loss: `autoencoder_residual_cluster` = `0.891116571893`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-44-703.-d84677bf1ce82052, us-code-10-8780-2539f35ce317901f, us-code-42-300s-2ad85e15c53957bb`
  evidence: `{"family_margin": -0.612873897209, "hint_id": "modal-synthesis-1441587b87fef9f9", "predicted_family": "deontic", "priority": 0.846781525698, "sample_id": "us-code-42-300s-2ad85e15c53957bb", "target_family": "conditional_normative", "target_probability": 0.153218474302}`
  evidence: `{"family_margin": -0.79631899279, "hint_id": "modal-synthesis-5722331cc2e5ea9d", "predicted_family": "deontic", "priority": 0.97550328209, "sample_id": "us-code-44-703.-d84677bf1ce82052", "target_family": "temporal", "target_probability": 0.02449671791}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-9afab96163b9109a", "predicted_family": "frame", "priority": 0.851064907891, "sample_id": "us-code-10-8780-2539f35ce317901f", "target_family": "deontic", "target_probability": 0.148935092109}`
