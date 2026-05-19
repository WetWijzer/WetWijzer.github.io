# packet-000107

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000107/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000107/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000107-20260519_131306

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-8d2487709fc6e372` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8d2487709fc6e372` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.997947612652, "hint_id": "modal-synthesis-45de6c32828b6d9b", "predicted_family": "alethic", "priority": 0.999835307431, "sample_id": "us-code-17-803-4925869c1c3dd85c", "target_family": "temporal", "target_probability": 0.000164692569}`
  evidence: `{"family_margin": -0.991738583671, "hint_id": "modal-synthesis-6dd970f72738e694", "predicted_family": "frame", "priority": 0.99663885775, "sample_id": "us-code-7-1471-04ee1ac7fb635c23", "target_family": "temporal", "target_probability": 0.00336114225}`
- `program-6f8ea168c503219d` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8d2487709fc6e372` score `0.972471`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.47329391192, "hint_id": "modal-synthesis-544bb9478d32aea0", "predicted_family": "frame", "priority": 0.756621129861, "sample_id": "us-code-36-127-067f228d78e1bf9e", "target_family": "temporal", "target_probability": 0.243378870139}`
  evidence: `{"family_margin": 0.181415197012, "hint_id": "modal-synthesis-e4aead8ff867b7d1", "predicted_family": "frame", "priority": 0.571173346654, "sample_id": "us-code-27-202a-4586fd950c465123", "target_family": "frame", "target_probability": 0.428826653346}`
  evidence: `{"family_margin": -0.894267809045, "hint_id": "modal-synthesis-fd725378bf01baf4", "predicted_family": "frame", "priority": 0.965491663512, "sample_id": "us-code-28-753-b3528ea3cc826027", "target_family": "deontic", "target_probability": 0.034508336488}`
- `program-778042d28431b566` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8d2487709fc6e372` score `0.953387`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.165277862425, "hint_id": "modal-synthesis-4f5100ef71067282", "predicted_family": "deontic", "priority": 0.803732538371, "sample_id": "us-code-5-7702-1825e5b9086791ee", "target_family": "conditional_normative", "target_probability": 0.196267461629}`
  evidence: `{"family_margin": -0.997156465148, "hint_id": "modal-synthesis-746ccf4be40ad8a2", "predicted_family": "frame", "priority": 0.998813454347, "sample_id": "us-code-33-2281b-8546f4642621a7d1", "target_family": "deontic", "target_probability": 0.001186545653}`
  evidence: `{"family_margin": -0.799996361094, "hint_id": "modal-synthesis-ea660ae9ed8176f8", "predicted_family": "frame", "priority": 0.952421591314, "sample_id": "us-code-16-708-32bb9e2fe6d4dd26", "target_family": "deontic", "target_probability": 0.047578408686}`
- `program-ad040dd75c6dadd3` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8d2487709fc6e372` score `0.909186`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.481314124117, "hint_id": "modal-synthesis-1198d841a6149c2b", "predicted_family": "temporal", "priority": 0.967129261466, "sample_id": "us-code-45-54a.-588104832696356e", "target_family": "frame", "target_probability": 0.032870738534}`
  evidence: `{"family_margin": -0.527232618908, "hint_id": "modal-synthesis-5e15275f9c4e3c88", "predicted_family": "deontic", "priority": 0.977530661222, "sample_id": "us-code-16-460dddd-2-99d88e35ebefd229", "target_family": "temporal", "target_probability": 0.022469338778}`
  evidence: `{"family_margin": -0.847748132148, "hint_id": "modal-synthesis-e3d3118ea31d44f2", "predicted_family": "frame", "priority": 0.941772330783, "sample_id": "us-code-16-429b-3c1f35181bc74549", "target_family": "deontic", "target_probability": 0.058227669217}`
  evidence: `{"family_margin": -0.127336912018, "hint_id": "modal-synthesis-f69a93abc62a5fd1", "predicted_family": "frame", "priority": 0.636033424741, "sample_id": "us-code-46-53108.-34737068fa6ea77e", "target_family": "deontic", "target_probability": 0.363966575259}`

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
- TODO count: `4`

## TODOs
- `program-8d2487709fc6e372`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8d2487709fc6e372` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.998237082591`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-17-803-4925869c1c3dd85c, us-code-7-1471-04ee1ac7fb635c23`
  evidence: `{"family_margin": -0.997947612652, "hint_id": "modal-synthesis-45de6c32828b6d9b", "predicted_family": "alethic", "priority": 0.999835307431, "sample_id": "us-code-17-803-4925869c1c3dd85c", "target_family": "temporal", "target_probability": 0.000164692569}`
  evidence: `{"family_margin": -0.991738583671, "hint_id": "modal-synthesis-6dd970f72738e694", "predicted_family": "frame", "priority": 0.99663885775, "sample_id": "us-code-7-1471-04ee1ac7fb635c23", "target_family": "temporal", "target_probability": 0.00336114225}`
- `program-6f8ea168c503219d`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8d2487709fc6e372` score `0.972471`
  loss: `autoencoder_residual_cluster` = `0.764428713342`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-28-753-b3528ea3cc826027, us-code-36-127-067f228d78e1bf9e, us-code-27-202a-4586fd950c465123`
  evidence: `{"family_margin": -0.47329391192, "hint_id": "modal-synthesis-544bb9478d32aea0", "predicted_family": "frame", "priority": 0.756621129861, "sample_id": "us-code-36-127-067f228d78e1bf9e", "target_family": "temporal", "target_probability": 0.243378870139}`
  evidence: `{"family_margin": 0.181415197012, "hint_id": "modal-synthesis-e4aead8ff867b7d1", "predicted_family": "frame", "priority": 0.571173346654, "sample_id": "us-code-27-202a-4586fd950c465123", "target_family": "frame", "target_probability": 0.428826653346}`
  evidence: `{"family_margin": -0.894267809045, "hint_id": "modal-synthesis-fd725378bf01baf4", "predicted_family": "frame", "priority": 0.965491663512, "sample_id": "us-code-28-753-b3528ea3cc826027", "target_family": "deontic", "target_probability": 0.034508336488}`
- `program-778042d28431b566`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8d2487709fc6e372` score `0.953387`
  loss: `autoencoder_residual_cluster` = `0.918322528011`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-33-2281b-8546f4642621a7d1, us-code-16-708-32bb9e2fe6d4dd26, us-code-5-7702-1825e5b9086791ee`
  evidence: `{"family_margin": -0.165277862425, "hint_id": "modal-synthesis-4f5100ef71067282", "predicted_family": "deontic", "priority": 0.803732538371, "sample_id": "us-code-5-7702-1825e5b9086791ee", "target_family": "conditional_normative", "target_probability": 0.196267461629}`
  evidence: `{"family_margin": -0.997156465148, "hint_id": "modal-synthesis-746ccf4be40ad8a2", "predicted_family": "frame", "priority": 0.998813454347, "sample_id": "us-code-33-2281b-8546f4642621a7d1", "target_family": "deontic", "target_probability": 0.001186545653}`
  evidence: `{"family_margin": -0.799996361094, "hint_id": "modal-synthesis-ea660ae9ed8176f8", "predicted_family": "frame", "priority": 0.952421591314, "sample_id": "us-code-16-708-32bb9e2fe6d4dd26", "target_family": "deontic", "target_probability": 0.047578408686}`
- `program-ad040dd75c6dadd3`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-8d2487709fc6e372` score `0.909186`
  loss: `autoencoder_residual_cluster` = `0.880616419553`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-460dddd-2-99d88e35ebefd229, us-code-45-54a.-588104832696356e, us-code-16-429b-3c1f35181bc74549, us-code-46-53108.-34737068fa6ea77e`
  evidence: `{"family_margin": -0.481314124117, "hint_id": "modal-synthesis-1198d841a6149c2b", "predicted_family": "temporal", "priority": 0.967129261466, "sample_id": "us-code-45-54a.-588104832696356e", "target_family": "frame", "target_probability": 0.032870738534}`
  evidence: `{"family_margin": -0.527232618908, "hint_id": "modal-synthesis-5e15275f9c4e3c88", "predicted_family": "deontic", "priority": 0.977530661222, "sample_id": "us-code-16-460dddd-2-99d88e35ebefd229", "target_family": "temporal", "target_probability": 0.022469338778}`
  evidence: `{"family_margin": -0.847748132148, "hint_id": "modal-synthesis-e3d3118ea31d44f2", "predicted_family": "frame", "priority": 0.941772330783, "sample_id": "us-code-16-429b-3c1f35181bc74549", "target_family": "deontic", "target_probability": 0.058227669217}`
  evidence: `{"family_margin": -0.127336912018, "hint_id": "modal-synthesis-f69a93abc62a5fd1", "predicted_family": "frame", "priority": 0.636033424741, "sample_id": "us-code-46-53108.-34737068fa6ea77e", "target_family": "deontic", "target_probability": 0.363966575259}`
