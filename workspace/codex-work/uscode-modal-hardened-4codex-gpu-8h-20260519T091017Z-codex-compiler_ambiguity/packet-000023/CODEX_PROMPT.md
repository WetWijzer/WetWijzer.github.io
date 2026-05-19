# packet-000023

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000023/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000023/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000023-20260519_094546

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e964e2f9407f505d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->alethic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.739578936711, "hint_id": "modal-synthesis-12ab55758c49d8d5", "predicted_family": "frame", "priority": 0.889578936711, "sample_id": "us-code-29-3221-a5a6deb63d139047", "target_family": "alethic"}`
  evidence: `{"family_margin": -0.879491493241, "hint_id": "modal-synthesis-c3c2cc370498cf82", "predicted_family": "frame", "priority": 1.029491493241, "sample_id": "us-code-49-41310.-d010484de13ae8d0", "target_family": "deontic"}`
- `program-505482364b202f08` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.97574`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.007279991044, "hint_id": "modal-synthesis-52622728c5eb9417", "predicted_family": "deontic", "priority": 0.142720008956, "sample_id": "us-code-15-52-8e1157bd728bbdff", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.912069343873, "hint_id": "modal-synthesis-dae4d0ea3ce82799", "predicted_family": "deontic", "priority": 1.062069343873, "sample_id": "us-code-12-3041-c49da1d75259d673", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.959785107952, "hint_id": "modal-synthesis-ef493cadf633f299", "predicted_family": "frame", "priority": 1.109785107952, "sample_id": "us-code-31-6904-714f9a12df496721", "target_family": "deontic"}`
- `program-ac014c9394c2db77` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.971671`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.612873897209, "hint_id": "modal-synthesis-3d0e10914eaaf1a6", "predicted_family": "deontic", "priority": 0.762873897209, "sample_id": "us-code-42-300s-2ad85e15c53957bb", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-92df89c7cf7fe43b", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-10-8780-2539f35ce317901f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.79631899279, "hint_id": "modal-synthesis-d5cc6ea03be08e34", "predicted_family": "deontic", "priority": 0.94631899279, "sample_id": "us-code-44-703.-d84677bf1ce82052", "target_family": "temporal"}`
- `program-31686e3e64b4e572` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal","temporal->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.964363`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.240981950365, "hint_id": "modal-synthesis-01c7a1475c1960ee", "predicted_family": "frame", "priority": 0.390981950365, "sample_id": "us-code-42-3271.-bbdebdd3b4a07703", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.65257734715, "hint_id": "modal-synthesis-63f232cb51227d0e", "predicted_family": "frame", "priority": 0.80257734715, "sample_id": "us-code-10-467-2e5d5d26ed55812b", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.327726688886, "hint_id": "modal-synthesis-c563bd2caae6f973", "predicted_family": "temporal", "priority": 0.477726688886, "sample_id": "us-code-16-6551-10034197b0128141", "target_family": "epistemic"}`
- `program-2e397e730f74c890` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","temporal->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.962439`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": 0.133552825543, "hint_id": "modal-synthesis-35a107a8b0a4bc51", "predicted_family": "temporal", "priority": 0.016447174457, "sample_id": "us-code-51-50922.-770ebeebe323b49b", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.416225497581, "hint_id": "modal-synthesis-8e1e9354942947e5", "predicted_family": "conditional_normative", "priority": 0.566225497581, "sample_id": "us-code-10-3681-c44b2b729da795d9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.118344203765, "hint_id": "modal-synthesis-c17efd026c957c79", "predicted_family": "temporal", "priority": 0.268344203765, "sample_id": "us-code-7-1736-924f9153fa08ba7a", "target_family": "deontic"}`
- `program-1bd02c9411dc4e82` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.936902`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.364600427884, "hint_id": "modal-synthesis-43c88582d977c1bf", "predicted_family": "frame", "priority": 0.514600427884, "sample_id": "us-code-20-2341-bc423b78c83aa543", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.996957729615, "hint_id": "modal-synthesis-6f8625de54cfb883", "predicted_family": "frame", "priority": 1.146957729615, "sample_id": "us-code-42-16183.-128b2c1ba48b8f9d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.201482979004, "hint_id": "modal-synthesis-7a1097c911e1904c", "predicted_family": "frame", "priority": 0.351482979004, "sample_id": "us-code-33-59jj-f5897fef9d8e4971", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.953447421386, "hint_id": "modal-synthesis-d6ae54897b9496cb", "predicted_family": "frame", "priority": 1.103447421386, "sample_id": "us-code-42-9605.-e797e44e0150247e", "target_family": "temporal"}`

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
- `program-e964e2f9407f505d`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->alethic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.959535214976`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-49-41310.-d010484de13ae8d0, us-code-29-3221-a5a6deb63d139047`
  evidence: `{"family_margin": -0.739578936711, "hint_id": "modal-synthesis-12ab55758c49d8d5", "predicted_family": "frame", "priority": 0.889578936711, "sample_id": "us-code-29-3221-a5a6deb63d139047", "target_family": "alethic"}`
  evidence: `{"family_margin": -0.879491493241, "hint_id": "modal-synthesis-c3c2cc370498cf82", "predicted_family": "frame", "priority": 1.029491493241, "sample_id": "us-code-49-41310.-d010484de13ae8d0", "target_family": "deontic"}`
- `program-505482364b202f08`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.97574`
  loss: `autoencoder_residual_cluster` = `0.77152482026`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-31-6904-714f9a12df496721, us-code-12-3041-c49da1d75259d673, us-code-15-52-8e1157bd728bbdff`
  evidence: `{"family_margin": 0.007279991044, "hint_id": "modal-synthesis-52622728c5eb9417", "predicted_family": "deontic", "priority": 0.142720008956, "sample_id": "us-code-15-52-8e1157bd728bbdff", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.912069343873, "hint_id": "modal-synthesis-dae4d0ea3ce82799", "predicted_family": "deontic", "priority": 1.062069343873, "sample_id": "us-code-12-3041-c49da1d75259d673", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.959785107952, "hint_id": "modal-synthesis-ef493cadf633f299", "predicted_family": "frame", "priority": 1.109785107952, "sample_id": "us-code-31-6904-714f9a12df496721", "target_family": "deontic"}`
- `program-ac014c9394c2db77`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.971671`
  loss: `autoencoder_residual_cluster` = `0.792579524128`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-44-703.-d84677bf1ce82052, us-code-42-300s-2ad85e15c53957bb, us-code-10-8780-2539f35ce317901f`
  evidence: `{"family_margin": -0.612873897209, "hint_id": "modal-synthesis-3d0e10914eaaf1a6", "predicted_family": "deontic", "priority": 0.762873897209, "sample_id": "us-code-42-300s-2ad85e15c53957bb", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-92df89c7cf7fe43b", "predicted_family": "frame", "priority": 0.668545682385, "sample_id": "us-code-10-8780-2539f35ce317901f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.79631899279, "hint_id": "modal-synthesis-d5cc6ea03be08e34", "predicted_family": "deontic", "priority": 0.94631899279, "sample_id": "us-code-44-703.-d84677bf1ce82052", "target_family": "temporal"}`
- `program-31686e3e64b4e572`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal","temporal->epistemic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.964363`
  loss: `autoencoder_residual_cluster` = `0.5570953288`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-467-2e5d5d26ed55812b, us-code-16-6551-10034197b0128141, us-code-42-3271.-bbdebdd3b4a07703`
  evidence: `{"family_margin": -0.240981950365, "hint_id": "modal-synthesis-01c7a1475c1960ee", "predicted_family": "frame", "priority": 0.390981950365, "sample_id": "us-code-42-3271.-bbdebdd3b4a07703", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.65257734715, "hint_id": "modal-synthesis-63f232cb51227d0e", "predicted_family": "frame", "priority": 0.80257734715, "sample_id": "us-code-10-467-2e5d5d26ed55812b", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.327726688886, "hint_id": "modal-synthesis-c563bd2caae6f973", "predicted_family": "temporal", "priority": 0.477726688886, "sample_id": "us-code-16-6551-10034197b0128141", "target_family": "epistemic"}`
- `program-2e397e730f74c890`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","temporal->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.962439`
  loss: `autoencoder_residual_cluster` = `0.283672291934`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-3681-c44b2b729da795d9, us-code-7-1736-924f9153fa08ba7a, us-code-51-50922.-770ebeebe323b49b`
  evidence: `{"family_margin": 0.133552825543, "hint_id": "modal-synthesis-35a107a8b0a4bc51", "predicted_family": "temporal", "priority": 0.016447174457, "sample_id": "us-code-51-50922.-770ebeebe323b49b", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.416225497581, "hint_id": "modal-synthesis-8e1e9354942947e5", "predicted_family": "conditional_normative", "priority": 0.566225497581, "sample_id": "us-code-10-3681-c44b2b729da795d9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.118344203765, "hint_id": "modal-synthesis-c17efd026c957c79", "predicted_family": "temporal", "priority": 0.268344203765, "sample_id": "us-code-7-1736-924f9153fa08ba7a", "target_family": "deontic"}`
- `program-1bd02c9411dc4e82`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e964e2f9407f505d` score `0.936902`
  loss: `autoencoder_residual_cluster` = `0.779122139472`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-16183.-128b2c1ba48b8f9d, us-code-42-9605.-e797e44e0150247e, us-code-20-2341-bc423b78c83aa543, us-code-33-59jj-f5897fef9d8e4971`
  evidence: `{"family_margin": -0.364600427884, "hint_id": "modal-synthesis-43c88582d977c1bf", "predicted_family": "frame", "priority": 0.514600427884, "sample_id": "us-code-20-2341-bc423b78c83aa543", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.996957729615, "hint_id": "modal-synthesis-6f8625de54cfb883", "predicted_family": "frame", "priority": 1.146957729615, "sample_id": "us-code-42-16183.-128b2c1ba48b8f9d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.201482979004, "hint_id": "modal-synthesis-7a1097c911e1904c", "predicted_family": "frame", "priority": 0.351482979004, "sample_id": "us-code-33-59jj-f5897fef9d8e4971", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.953447421386, "hint_id": "modal-synthesis-d6ae54897b9496cb", "predicted_family": "frame", "priority": 1.103447421386, "sample_id": "us-code-42-9605.-e797e44e0150247e", "target_family": "temporal"}`
