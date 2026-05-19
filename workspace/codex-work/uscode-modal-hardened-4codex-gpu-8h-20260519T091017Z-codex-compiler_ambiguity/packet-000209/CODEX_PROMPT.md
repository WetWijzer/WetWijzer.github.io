# packet-000209

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000209/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000209/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000209-20260519_131150

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-b94c0f2c82f1bf44` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b94c0f2c82f1bf44` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.991738583671, "hint_id": "modal-synthesis-35951312b0bfa375", "predicted_family": "frame", "priority": 1.141738583671, "sample_id": "us-code-7-1471-04ee1ac7fb635c23", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.997947612652, "hint_id": "modal-synthesis-b6cd8d7cee69ee6f", "predicted_family": "alethic", "priority": 1.147947612652, "sample_id": "us-code-17-803-4925869c1c3dd85c", "target_family": "temporal"}`
- `program-eadb469ff67222ec` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b94c0f2c82f1bf44` score `0.959998`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.165277862425, "hint_id": "modal-synthesis-1216ca83f0847128", "predicted_family": "deontic", "priority": 0.315277862425, "sample_id": "us-code-5-7702-1825e5b9086791ee", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.997156465148, "hint_id": "modal-synthesis-5c6455d006967851", "predicted_family": "frame", "priority": 1.147156465148, "sample_id": "us-code-33-2281b-8546f4642621a7d1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.799996361094, "hint_id": "modal-synthesis-e543eba84f61f530", "predicted_family": "frame", "priority": 0.949996361094, "sample_id": "us-code-16-708-32bb9e2fe6d4dd26", "target_family": "deontic"}`
- `program-5f02aa7ae7af6918` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b94c0f2c82f1bf44` score `0.922981`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.127336912018, "hint_id": "modal-synthesis-195cd5b62dbfcee9", "predicted_family": "frame", "priority": 0.277336912018, "sample_id": "us-code-46-53108.-34737068fa6ea77e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.481314124117, "hint_id": "modal-synthesis-bf89b344418e77f7", "predicted_family": "temporal", "priority": 0.631314124117, "sample_id": "us-code-45-54a.-588104832696356e", "target_family": "frame"}`
  evidence: `{"family_margin": -0.527232618908, "hint_id": "modal-synthesis-d1f5717b59a8e561", "predicted_family": "deontic", "priority": 0.677232618908, "sample_id": "us-code-16-460dddd-2-99d88e35ebefd229", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.847748132148, "hint_id": "modal-synthesis-ee93fb307d4a483d", "predicted_family": "frame", "priority": 0.997748132148, "sample_id": "us-code-16-429b-3c1f35181bc74549", "target_family": "deontic"}`

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
- TODO count: `3`

## TODOs
- `program-b94c0f2c82f1bf44`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b94c0f2c82f1bf44` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.144843098162`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-17-803-4925869c1c3dd85c, us-code-7-1471-04ee1ac7fb635c23`
  evidence: `{"family_margin": -0.991738583671, "hint_id": "modal-synthesis-35951312b0bfa375", "predicted_family": "frame", "priority": 1.141738583671, "sample_id": "us-code-7-1471-04ee1ac7fb635c23", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.997947612652, "hint_id": "modal-synthesis-b6cd8d7cee69ee6f", "predicted_family": "alethic", "priority": 1.147947612652, "sample_id": "us-code-17-803-4925869c1c3dd85c", "target_family": "temporal"}`
- `program-eadb469ff67222ec`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b94c0f2c82f1bf44` score `0.959998`
  loss: `autoencoder_residual_cluster` = `0.804143562889`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-33-2281b-8546f4642621a7d1, us-code-16-708-32bb9e2fe6d4dd26, us-code-5-7702-1825e5b9086791ee`
  evidence: `{"family_margin": -0.165277862425, "hint_id": "modal-synthesis-1216ca83f0847128", "predicted_family": "deontic", "priority": 0.315277862425, "sample_id": "us-code-5-7702-1825e5b9086791ee", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.997156465148, "hint_id": "modal-synthesis-5c6455d006967851", "predicted_family": "frame", "priority": 1.147156465148, "sample_id": "us-code-33-2281b-8546f4642621a7d1", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.799996361094, "hint_id": "modal-synthesis-e543eba84f61f530", "predicted_family": "frame", "priority": 0.949996361094, "sample_id": "us-code-16-708-32bb9e2fe6d4dd26", "target_family": "deontic"}`
- `program-5f02aa7ae7af6918`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b94c0f2c82f1bf44` score `0.922981`
  loss: `autoencoder_residual_cluster` = `0.645907946798`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-16-429b-3c1f35181bc74549, us-code-16-460dddd-2-99d88e35ebefd229, us-code-45-54a.-588104832696356e, us-code-46-53108.-34737068fa6ea77e`
  evidence: `{"family_margin": -0.127336912018, "hint_id": "modal-synthesis-195cd5b62dbfcee9", "predicted_family": "frame", "priority": 0.277336912018, "sample_id": "us-code-46-53108.-34737068fa6ea77e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.481314124117, "hint_id": "modal-synthesis-bf89b344418e77f7", "predicted_family": "temporal", "priority": 0.631314124117, "sample_id": "us-code-45-54a.-588104832696356e", "target_family": "frame"}`
  evidence: `{"family_margin": -0.527232618908, "hint_id": "modal-synthesis-d1f5717b59a8e561", "predicted_family": "deontic", "priority": 0.677232618908, "sample_id": "us-code-16-460dddd-2-99d88e35ebefd229", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.847748132148, "hint_id": "modal-synthesis-ee93fb307d4a483d", "predicted_family": "frame", "priority": 0.997748132148, "sample_id": "us-code-16-429b-3c1f35181bc74549", "target_family": "deontic"}`
