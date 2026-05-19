# packet-000177

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000177/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000177/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000177-20260519_141804

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-aad18a6d45cfcc7c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-8007e785d30e54e3", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-36-125-1122a4ae451de969", "target_family": "temporal", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.919945361726, "hint_id": "modal-synthesis-8c85a233726843fb", "predicted_family": "frame", "priority": 0.999378121134, "sample_id": "us-code-26-755-459e8bff6592359e", "target_family": "dynamic", "target_probability": 0.000621878866}`
  evidence: `{"family_margin": -0.882186283574, "hint_id": "modal-synthesis-f3443f278b1b7cfd", "predicted_family": "frame", "priority": 0.98139797818, "sample_id": "us-code-16-1404-2a34b181256a4c20", "target_family": "deontic", "target_probability": 0.01860202182}`
- `program-8fb4bcbb83bb36e6` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->alethic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `0.991423`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.492615934833, "hint_id": "modal-synthesis-2cd97710f91a0229", "predicted_family": "frame", "priority": 0.858512370036, "sample_id": "us-code-36-152302-3067b411c0c3067d", "target_family": "alethic", "target_probability": 0.141487629964}`
  evidence: `{"family_margin": -0.351867372331, "hint_id": "modal-synthesis-5fb71fcfb66583dc", "predicted_family": "frame", "priority": 0.702940573341, "sample_id": "us-code-20-9165-bf87f59846f54c29", "target_family": "temporal", "target_probability": 0.297059426659}`
  evidence: `{"family_margin": -0.902318654676, "hint_id": "modal-synthesis-c62502390ad3740a", "predicted_family": "frame", "priority": 0.976190859478, "sample_id": "us-code-38-4103-444a14e5c270c515", "target_family": "deontic", "target_probability": 0.023809140522}`
- `program-695897cd0958bc3f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `0.985605`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-13e84ab414bc196b", "predicted_family": "temporal", "priority": 0.633596363007, "sample_id": "us-code-25-640-83a907ff97a1dbfe", "target_family": "temporal", "target_probability": 0.366403636993}`
  evidence: `{"family_margin": -0.999658532901, "hint_id": "modal-synthesis-7cac2346251166f8", "predicted_family": "frame", "priority": 0.999966377259, "sample_id": "us-code-22-1475e-bec3039174fdd403", "target_family": "conditional_normative", "target_probability": 3.3622741e-05}`
  evidence: `{"family_margin": -0.909146257792, "hint_id": "modal-synthesis-bbcbd084685c5f5c", "predicted_family": "frame", "priority": 0.993272708102, "sample_id": "us-code-10-20252-b0cdb1bc77136b17", "target_family": "temporal", "target_probability": 0.006727291898}`
- `program-8789b1e47142f4f6` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `0.974681`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.023404022064, "hint_id": "modal-synthesis-366bd8452d312db6", "predicted_family": "deontic", "priority": 0.633079645058, "sample_id": "us-code-10-9419-9ac943033310c3a2", "target_family": "deontic", "target_probability": 0.366920354942}`
  evidence: `{"family_margin": -0.672201401144, "hint_id": "modal-synthesis-b53378808b6191a2", "predicted_family": "frame", "priority": 0.921286492015, "sample_id": "us-code-42-16373.-1f21fbe53e1c938d", "target_family": "conditional_normative", "target_probability": 0.078713507985}`
  evidence: `{"family_margin": -0.966264760437, "hint_id": "modal-synthesis-d706dd33a17b652e", "predicted_family": "frame", "priority": 0.983941883696, "sample_id": "us-code-7-7643-b2e24d4bd533c9c9", "target_family": "deontic", "target_probability": 0.016058116304}`
- `program-e1fa2d905ab75591` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `0.973781`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.999000718287, "hint_id": "modal-synthesis-15543f6a812aeb35", "predicted_family": "frame", "priority": 0.999715626189, "sample_id": "us-code-16-824b-ddf0987a8feb3cf5", "target_family": "deontic", "target_probability": 0.000284373811}`
  evidence: `{"family_margin": -0.491677371288, "hint_id": "modal-synthesis-61ba9648b8c79942", "predicted_family": "conditional_normative", "priority": 0.998718744886, "sample_id": "us-code-42-300gg-cbf171777bfb8c11", "target_family": "frame", "target_probability": 0.001281255114}`
  evidence: `{"family_margin": -0.127854029255, "hint_id": "modal-synthesis-e10a63d28c1013d4", "predicted_family": "temporal", "priority": 0.712328434176, "sample_id": "us-code-42-17937.-f79f9efdaaa4d382", "target_family": "conditional_normative", "target_probability": 0.287671565824}`

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
- TODO count: `5`

## TODOs
- `program-aad18a6d45cfcc7c`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.935652341567`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-26-755-459e8bff6592359e, us-code-16-1404-2a34b181256a4c20, us-code-36-125-1122a4ae451de969`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-8007e785d30e54e3", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-36-125-1122a4ae451de969", "target_family": "temporal", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.919945361726, "hint_id": "modal-synthesis-8c85a233726843fb", "predicted_family": "frame", "priority": 0.999378121134, "sample_id": "us-code-26-755-459e8bff6592359e", "target_family": "dynamic", "target_probability": 0.000621878866}`
  evidence: `{"family_margin": -0.882186283574, "hint_id": "modal-synthesis-f3443f278b1b7cfd", "predicted_family": "frame", "priority": 0.98139797818, "sample_id": "us-code-16-1404-2a34b181256a4c20", "target_family": "deontic", "target_probability": 0.01860202182}`
- `program-8fb4bcbb83bb36e6`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->alethic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `0.991423`
  loss: `autoencoder_residual_cluster` = `0.845881267618`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-38-4103-444a14e5c270c515, us-code-36-152302-3067b411c0c3067d, us-code-20-9165-bf87f59846f54c29`
  evidence: `{"family_margin": -0.492615934833, "hint_id": "modal-synthesis-2cd97710f91a0229", "predicted_family": "frame", "priority": 0.858512370036, "sample_id": "us-code-36-152302-3067b411c0c3067d", "target_family": "alethic", "target_probability": 0.141487629964}`
  evidence: `{"family_margin": -0.351867372331, "hint_id": "modal-synthesis-5fb71fcfb66583dc", "predicted_family": "frame", "priority": 0.702940573341, "sample_id": "us-code-20-9165-bf87f59846f54c29", "target_family": "temporal", "target_probability": 0.297059426659}`
  evidence: `{"family_margin": -0.902318654676, "hint_id": "modal-synthesis-c62502390ad3740a", "predicted_family": "frame", "priority": 0.976190859478, "sample_id": "us-code-38-4103-444a14e5c270c515", "target_family": "deontic", "target_probability": 0.023809140522}`
- `program-695897cd0958bc3f`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `0.985605`
  loss: `autoencoder_residual_cluster` = `0.875611816123`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-1475e-bec3039174fdd403, us-code-10-20252-b0cdb1bc77136b17, us-code-25-640-83a907ff97a1dbfe`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-13e84ab414bc196b", "predicted_family": "temporal", "priority": 0.633596363007, "sample_id": "us-code-25-640-83a907ff97a1dbfe", "target_family": "temporal", "target_probability": 0.366403636993}`
  evidence: `{"family_margin": -0.999658532901, "hint_id": "modal-synthesis-7cac2346251166f8", "predicted_family": "frame", "priority": 0.999966377259, "sample_id": "us-code-22-1475e-bec3039174fdd403", "target_family": "conditional_normative", "target_probability": 3.3622741e-05}`
  evidence: `{"family_margin": -0.909146257792, "hint_id": "modal-synthesis-bbcbd084685c5f5c", "predicted_family": "frame", "priority": 0.993272708102, "sample_id": "us-code-10-20252-b0cdb1bc77136b17", "target_family": "temporal", "target_probability": 0.006727291898}`
- `program-8789b1e47142f4f6`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `0.974681`
  loss: `autoencoder_residual_cluster` = `0.84610267359`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-7-7643-b2e24d4bd533c9c9, us-code-42-16373.-1f21fbe53e1c938d, us-code-10-9419-9ac943033310c3a2`
  evidence: `{"family_margin": 0.023404022064, "hint_id": "modal-synthesis-366bd8452d312db6", "predicted_family": "deontic", "priority": 0.633079645058, "sample_id": "us-code-10-9419-9ac943033310c3a2", "target_family": "deontic", "target_probability": 0.366920354942}`
  evidence: `{"family_margin": -0.672201401144, "hint_id": "modal-synthesis-b53378808b6191a2", "predicted_family": "frame", "priority": 0.921286492015, "sample_id": "us-code-42-16373.-1f21fbe53e1c938d", "target_family": "conditional_normative", "target_probability": 0.078713507985}`
  evidence: `{"family_margin": -0.966264760437, "hint_id": "modal-synthesis-d706dd33a17b652e", "predicted_family": "frame", "priority": 0.983941883696, "sample_id": "us-code-7-7643-b2e24d4bd533c9c9", "target_family": "deontic", "target_probability": 0.016058116304}`
- `program-e1fa2d905ab75591`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->frame","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-aad18a6d45cfcc7c` score `0.973781`
  loss: `autoencoder_residual_cluster` = `0.90358760175`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-824b-ddf0987a8feb3cf5, us-code-42-300gg-cbf171777bfb8c11, us-code-42-17937.-f79f9efdaaa4d382`
  evidence: `{"family_margin": -0.999000718287, "hint_id": "modal-synthesis-15543f6a812aeb35", "predicted_family": "frame", "priority": 0.999715626189, "sample_id": "us-code-16-824b-ddf0987a8feb3cf5", "target_family": "deontic", "target_probability": 0.000284373811}`
  evidence: `{"family_margin": -0.491677371288, "hint_id": "modal-synthesis-61ba9648b8c79942", "predicted_family": "conditional_normative", "priority": 0.998718744886, "sample_id": "us-code-42-300gg-cbf171777bfb8c11", "target_family": "frame", "target_probability": 0.001281255114}`
  evidence: `{"family_margin": -0.127854029255, "hint_id": "modal-synthesis-e10a63d28c1013d4", "predicted_family": "temporal", "priority": 0.712328434176, "sample_id": "us-code-42-17937.-f79f9efdaaa4d382", "target_family": "conditional_normative", "target_probability": 0.287671565824}`
