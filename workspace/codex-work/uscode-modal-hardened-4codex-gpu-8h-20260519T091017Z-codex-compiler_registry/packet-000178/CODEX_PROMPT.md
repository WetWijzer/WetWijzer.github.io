# packet-000178

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000178/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000178/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000178-20260519_142816

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-1c14a442cec324b3` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal","hybrid->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.991577311702, "hint_id": "modal-synthesis-1eed44bc531e2e5a", "predicted_family": "frame", "priority": 0.999329698263, "sample_id": "us-code-10-8679-527c7516d5479316", "target_family": "conditional_normative", "target_probability": 0.000670301737}`
  evidence: `{"family_margin": -0.951659333425, "hint_id": "modal-synthesis-4ee0192e3f35d7ed", "predicted_family": "frame", "priority": 0.984007873007, "sample_id": "us-code-7-6807-8b07fd1cc236bb34", "target_family": "conditional_normative", "target_probability": 0.015992126993}`
  evidence: `{"family_margin": -0.18032295659, "hint_id": "modal-synthesis-a0ef7f99388cb884", "predicted_family": "hybrid", "priority": 0.927591115091, "sample_id": "us-code-43-2901.-7aac673167dc177c", "target_family": "frame", "target_probability": 0.072408884909}`
  evidence: `{"family_margin": -0.885319001402, "hint_id": "modal-synthesis-d583b9bad8bedbdb", "predicted_family": "frame", "priority": 0.99555867779, "sample_id": "us-code-42-10154.-3990045c9fffc0c5", "target_family": "temporal", "target_probability": 0.00444132221}`
- `program-5c949f249f773bdc` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `0.980654`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.125384604062, "hint_id": "modal-synthesis-52b8abb29a925acb", "predicted_family": "deontic", "priority": 0.623846187813, "sample_id": "us-code-42-17242.-18143a7842efc3da", "target_family": "temporal", "target_probability": 0.376153812187}`
  evidence: `{"family_margin": -0.99753314728, "hint_id": "modal-synthesis-9237af80cb5acde0", "predicted_family": "frame", "priority": 0.999325672145, "sample_id": "us-code-42-1862s-59a34514597fe4f9", "target_family": "deontic", "target_probability": 0.000674327855}`
  evidence: `{"family_margin": -0.814383146408, "hint_id": "modal-synthesis-bc2f61bfbe558853", "predicted_family": "frame", "priority": 0.952686355011, "sample_id": "us-code-26-6151-8cf146ef1cb76a82", "target_family": "conditional_normative", "target_probability": 0.047313644989}`
  evidence: `{"family_margin": -0.998618289075, "hint_id": "modal-synthesis-ee3fbb4347d3db71", "predicted_family": "frame", "priority": 0.999751764861, "sample_id": "us-code-6-314a-3a3b3dc754213770", "target_family": "conditional_normative", "target_probability": 0.000248235139}`
- `program-3cd1fc77e0de199b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->frame","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `0.946373`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-8bc04c2127938595", "predicted_family": "deontic", "priority": 0.664086982317, "sample_id": "us-code-12-337-b2cb2b5a46e4a975", "target_family": "deontic", "target_probability": 0.335913017683}`
  evidence: `{"family_margin": -0.986259707155, "hint_id": "modal-synthesis-a2174336571815d7", "predicted_family": "frame", "priority": 0.998185594787, "sample_id": "us-code-15-1070-3a95d3516d947988", "target_family": "deontic", "target_probability": 0.001814405213}`
  evidence: `{"family_margin": -0.329001948153, "hint_id": "modal-synthesis-c668b1cab585513f", "predicted_family": "alethic", "priority": 0.675461337141, "sample_id": "us-code-16-1413-6b0a661df8209521", "target_family": "frame", "target_probability": 0.324538662859}`
- `program-2774ae8a5bda0538` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `0.945163`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.813922215476, "hint_id": "modal-synthesis-162a283580e32526", "predicted_family": "frame", "priority": 0.996823563928, "sample_id": "us-code-33-59ee-1-a6cd77c9bf3393ce", "target_family": "temporal", "target_probability": 0.003176436072}`
  evidence: `{"family_margin": -0.448314320645, "hint_id": "modal-synthesis-5920cd4911706e82", "predicted_family": "frame", "priority": 0.897306477431, "sample_id": "us-code-45-501 to 502.-8e8f2d25c9ff5006", "target_family": "temporal", "target_probability": 0.102693522569}`
  evidence: `{"family_margin": -0.432296025335, "hint_id": "modal-synthesis-7da4700413736ac7", "predicted_family": "frame", "priority": 0.838048715012, "sample_id": "us-code-22-9688-5f6bbc5155d748f5", "target_family": "dynamic", "target_probability": 0.161951284988}`
- `program-81908cbb75040c80` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `0.944812`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.026084716803, "hint_id": "modal-synthesis-5101e03c09e82ca5", "predicted_family": "alethic", "priority": 0.530676891783, "sample_id": "us-code-12-2289-1e358d5edf0d64b7", "target_family": "deontic", "target_probability": 0.469323108217}`
  evidence: `{"family_margin": 0.068966987935, "hint_id": "modal-synthesis-5d76d81600616575", "predicted_family": "deontic", "priority": 0.689648554292, "sample_id": "us-code-49-44806.-394c29631583f2d2", "target_family": "deontic", "target_probability": 0.310351445708}`
  evidence: `{"family_margin": -0.279404198743, "hint_id": "modal-synthesis-c19ba458142e5e6a", "predicted_family": "frame", "priority": 0.764116659823, "sample_id": "us-code-41-3901-a0e6f0f39e8159f5", "target_family": "deontic", "target_probability": 0.235883340177}`
  evidence: `{"family_margin": -0.274690539061, "hint_id": "modal-synthesis-c65fe77f3a4e66e4", "predicted_family": "deontic", "priority": 0.725309460939, "sample_id": "us-code-23-178-7ece24719db412c2", "target_family": "temporal", "target_probability": 0.274690539061}`

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
- `program-1c14a442cec324b3`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal","hybrid->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.976621841038`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-8679-527c7516d5479316, us-code-42-10154.-3990045c9fffc0c5, us-code-7-6807-8b07fd1cc236bb34, us-code-43-2901.-7aac673167dc177c`
  evidence: `{"family_margin": -0.991577311702, "hint_id": "modal-synthesis-1eed44bc531e2e5a", "predicted_family": "frame", "priority": 0.999329698263, "sample_id": "us-code-10-8679-527c7516d5479316", "target_family": "conditional_normative", "target_probability": 0.000670301737}`
  evidence: `{"family_margin": -0.951659333425, "hint_id": "modal-synthesis-4ee0192e3f35d7ed", "predicted_family": "frame", "priority": 0.984007873007, "sample_id": "us-code-7-6807-8b07fd1cc236bb34", "target_family": "conditional_normative", "target_probability": 0.015992126993}`
  evidence: `{"family_margin": -0.18032295659, "hint_id": "modal-synthesis-a0ef7f99388cb884", "predicted_family": "hybrid", "priority": 0.927591115091, "sample_id": "us-code-43-2901.-7aac673167dc177c", "target_family": "frame", "target_probability": 0.072408884909}`
  evidence: `{"family_margin": -0.885319001402, "hint_id": "modal-synthesis-d583b9bad8bedbdb", "predicted_family": "frame", "priority": 0.99555867779, "sample_id": "us-code-42-10154.-3990045c9fffc0c5", "target_family": "temporal", "target_probability": 0.00444132221}`
- `program-5c949f249f773bdc`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `0.980654`
  loss: `autoencoder_residual_cluster` = `0.893902494958`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-6-314a-3a3b3dc754213770, us-code-42-1862s-59a34514597fe4f9, us-code-26-6151-8cf146ef1cb76a82, us-code-42-17242.-18143a7842efc3da`
  evidence: `{"family_margin": -0.125384604062, "hint_id": "modal-synthesis-52b8abb29a925acb", "predicted_family": "deontic", "priority": 0.623846187813, "sample_id": "us-code-42-17242.-18143a7842efc3da", "target_family": "temporal", "target_probability": 0.376153812187}`
  evidence: `{"family_margin": -0.99753314728, "hint_id": "modal-synthesis-9237af80cb5acde0", "predicted_family": "frame", "priority": 0.999325672145, "sample_id": "us-code-42-1862s-59a34514597fe4f9", "target_family": "deontic", "target_probability": 0.000674327855}`
  evidence: `{"family_margin": -0.814383146408, "hint_id": "modal-synthesis-bc2f61bfbe558853", "predicted_family": "frame", "priority": 0.952686355011, "sample_id": "us-code-26-6151-8cf146ef1cb76a82", "target_family": "conditional_normative", "target_probability": 0.047313644989}`
  evidence: `{"family_margin": -0.998618289075, "hint_id": "modal-synthesis-ee3fbb4347d3db71", "predicted_family": "frame", "priority": 0.999751764861, "sample_id": "us-code-6-314a-3a3b3dc754213770", "target_family": "conditional_normative", "target_probability": 0.000248235139}`
- `program-3cd1fc77e0de199b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->frame","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `0.946373`
  loss: `autoencoder_residual_cluster` = `0.779244638082`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-1070-3a95d3516d947988, us-code-16-1413-6b0a661df8209521, us-code-12-337-b2cb2b5a46e4a975`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-8bc04c2127938595", "predicted_family": "deontic", "priority": 0.664086982317, "sample_id": "us-code-12-337-b2cb2b5a46e4a975", "target_family": "deontic", "target_probability": 0.335913017683}`
  evidence: `{"family_margin": -0.986259707155, "hint_id": "modal-synthesis-a2174336571815d7", "predicted_family": "frame", "priority": 0.998185594787, "sample_id": "us-code-15-1070-3a95d3516d947988", "target_family": "deontic", "target_probability": 0.001814405213}`
  evidence: `{"family_margin": -0.329001948153, "hint_id": "modal-synthesis-c668b1cab585513f", "predicted_family": "alethic", "priority": 0.675461337141, "sample_id": "us-code-16-1413-6b0a661df8209521", "target_family": "frame", "target_probability": 0.324538662859}`
- `program-2774ae8a5bda0538`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->dynamic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `0.945163`
  loss: `autoencoder_residual_cluster` = `0.910726252124`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-33-59ee-1-a6cd77c9bf3393ce, us-code-45-501 to 502.-8e8f2d25c9ff5006, us-code-22-9688-5f6bbc5155d748f5`
  evidence: `{"family_margin": -0.813922215476, "hint_id": "modal-synthesis-162a283580e32526", "predicted_family": "frame", "priority": 0.996823563928, "sample_id": "us-code-33-59ee-1-a6cd77c9bf3393ce", "target_family": "temporal", "target_probability": 0.003176436072}`
  evidence: `{"family_margin": -0.448314320645, "hint_id": "modal-synthesis-5920cd4911706e82", "predicted_family": "frame", "priority": 0.897306477431, "sample_id": "us-code-45-501 to 502.-8e8f2d25c9ff5006", "target_family": "temporal", "target_probability": 0.102693522569}`
  evidence: `{"family_margin": -0.432296025335, "hint_id": "modal-synthesis-7da4700413736ac7", "predicted_family": "frame", "priority": 0.838048715012, "sample_id": "us-code-22-9688-5f6bbc5155d748f5", "target_family": "dynamic", "target_probability": 0.161951284988}`
- `program-81908cbb75040c80`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-1c14a442cec324b3` score `0.944812`
  loss: `autoencoder_residual_cluster` = `0.677437891709`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-41-3901-a0e6f0f39e8159f5, us-code-23-178-7ece24719db412c2, us-code-49-44806.-394c29631583f2d2, us-code-12-2289-1e358d5edf0d64b7`
  evidence: `{"family_margin": -0.026084716803, "hint_id": "modal-synthesis-5101e03c09e82ca5", "predicted_family": "alethic", "priority": 0.530676891783, "sample_id": "us-code-12-2289-1e358d5edf0d64b7", "target_family": "deontic", "target_probability": 0.469323108217}`
  evidence: `{"family_margin": 0.068966987935, "hint_id": "modal-synthesis-5d76d81600616575", "predicted_family": "deontic", "priority": 0.689648554292, "sample_id": "us-code-49-44806.-394c29631583f2d2", "target_family": "deontic", "target_probability": 0.310351445708}`
  evidence: `{"family_margin": -0.279404198743, "hint_id": "modal-synthesis-c19ba458142e5e6a", "predicted_family": "frame", "priority": 0.764116659823, "sample_id": "us-code-41-3901-a0e6f0f39e8159f5", "target_family": "deontic", "target_probability": 0.235883340177}`
  evidence: `{"family_margin": -0.274690539061, "hint_id": "modal-synthesis-c65fe77f3a4e66e4", "predicted_family": "deontic", "priority": 0.725309460939, "sample_id": "us-code-23-178-7ece24719db412c2", "target_family": "temporal", "target_probability": 0.274690539061}`
