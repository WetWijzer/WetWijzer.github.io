# packet-000109

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000109/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000109/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000109-20260519_111904

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-2fb35f97044a33c7` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->dynamic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2fb35f97044a33c7` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.986993978813, "hint_id": "modal-synthesis-29e62c2a2f843120", "predicted_family": "frame", "priority": 1.136993978813, "sample_id": "us-code-5-556-333c12c1b5eab192", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999091091691, "hint_id": "modal-synthesis-2c61528fe24eae81", "predicted_family": "frame", "priority": 1.149091091691, "sample_id": "us-code-42-1437u.-0904464f49467b7f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.431079117926, "hint_id": "modal-synthesis-e93601256162f4c3", "predicted_family": "deontic", "priority": 0.581079117926, "sample_id": "us-code-12-2403-0e192b428d978f5b", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.231207676845, "hint_id": "modal-synthesis-f7f9529819567f1a", "predicted_family": "deontic", "priority": 0.381207676845, "sample_id": "us-code-42-9858h.-c26cffb188ec1c8c", "target_family": "conditional_normative"}`

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
- TODO count: `1`

## TODOs
- `program-2fb35f97044a33c7`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->dynamic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-2fb35f97044a33c7` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.812092966319`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-42-1437u.-0904464f49467b7f, us-code-5-556-333c12c1b5eab192, us-code-12-2403-0e192b428d978f5b, us-code-42-9858h.-c26cffb188ec1c8c`
  evidence: `{"family_margin": -0.986993978813, "hint_id": "modal-synthesis-29e62c2a2f843120", "predicted_family": "frame", "priority": 1.136993978813, "sample_id": "us-code-5-556-333c12c1b5eab192", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999091091691, "hint_id": "modal-synthesis-2c61528fe24eae81", "predicted_family": "frame", "priority": 1.149091091691, "sample_id": "us-code-42-1437u.-0904464f49467b7f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.431079117926, "hint_id": "modal-synthesis-e93601256162f4c3", "predicted_family": "deontic", "priority": 0.581079117926, "sample_id": "us-code-12-2403-0e192b428d978f5b", "target_family": "dynamic"}`
  evidence: `{"family_margin": -0.231207676845, "hint_id": "modal-synthesis-f7f9529819567f1a", "predicted_family": "deontic", "priority": 0.381207676845, "sample_id": "us-code-42-9858h.-c26cffb188ec1c8c", "target_family": "conditional_normative"}`
