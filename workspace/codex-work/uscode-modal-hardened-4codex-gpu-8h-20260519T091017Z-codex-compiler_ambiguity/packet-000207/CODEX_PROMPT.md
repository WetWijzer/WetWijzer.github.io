# packet-000207

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000207/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000207/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000207-20260519_125503

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-958beaa0547eb8a5` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-958beaa0547eb8a5` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999907091831, "hint_id": "modal-synthesis-3d3e2ff33e7fabf0", "predicted_family": "frame", "priority": 1.149907091831, "sample_id": "us-code-18-956-b86919ed0b6b3fa9", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.795219252903, "hint_id": "modal-synthesis-762bc8433e666467", "predicted_family": "alethic", "priority": 0.945219252903, "sample_id": "us-code-49-20101.-2ac3d3010e2c3de8", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.99240219376, "hint_id": "modal-synthesis-a8538c8c8daf0f2c", "predicted_family": "frame", "priority": 1.14240219376, "sample_id": "us-code-28-1738-a2fdec05f100f657", "target_family": "deontic"}`
- `program-98e38db99ce3d71a` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-958beaa0547eb8a5` score `0.982892`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.137812866903, "hint_id": "modal-synthesis-423e31d0ead53b5a", "predicted_family": "temporal", "priority": 0.287812866903, "sample_id": "us-code-26-2010-1d49b3824d22c29f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.228446639842, "hint_id": "modal-synthesis-5b35b44ee0afc6ad", "predicted_family": "frame", "priority": 0.378446639842, "sample_id": "us-code-36-230310-1fc4e0a5e5a733b8", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.284224385856, "hint_id": "modal-synthesis-842e953d37a46873", "predicted_family": "conditional_normative", "priority": 0.434224385856, "sample_id": "us-code-19-2372-7a8bb398787d1d34", "target_family": "temporal"}`

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
- TODO count: `2`

## TODOs
- `program-958beaa0547eb8a5`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-958beaa0547eb8a5` score `1.0`
  loss: `autoencoder_residual_cluster` = `1.079176179498`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-18-956-b86919ed0b6b3fa9, us-code-28-1738-a2fdec05f100f657, us-code-49-20101.-2ac3d3010e2c3de8`
  evidence: `{"family_margin": -0.999907091831, "hint_id": "modal-synthesis-3d3e2ff33e7fabf0", "predicted_family": "frame", "priority": 1.149907091831, "sample_id": "us-code-18-956-b86919ed0b6b3fa9", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.795219252903, "hint_id": "modal-synthesis-762bc8433e666467", "predicted_family": "alethic", "priority": 0.945219252903, "sample_id": "us-code-49-20101.-2ac3d3010e2c3de8", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.99240219376, "hint_id": "modal-synthesis-a8538c8c8daf0f2c", "predicted_family": "frame", "priority": 1.14240219376, "sample_id": "us-code-28-1738-a2fdec05f100f657", "target_family": "deontic"}`
- `program-98e38db99ce3d71a`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-958beaa0547eb8a5` score `0.982892`
  loss: `autoencoder_residual_cluster` = `0.3668279642`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-19-2372-7a8bb398787d1d34, us-code-36-230310-1fc4e0a5e5a733b8, us-code-26-2010-1d49b3824d22c29f`
  evidence: `{"family_margin": -0.137812866903, "hint_id": "modal-synthesis-423e31d0ead53b5a", "predicted_family": "temporal", "priority": 0.287812866903, "sample_id": "us-code-26-2010-1d49b3824d22c29f", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.228446639842, "hint_id": "modal-synthesis-5b35b44ee0afc6ad", "predicted_family": "frame", "priority": 0.378446639842, "sample_id": "us-code-36-230310-1fc4e0a5e5a733b8", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.284224385856, "hint_id": "modal-synthesis-842e953d37a46873", "predicted_family": "conditional_normative", "priority": 0.434224385856, "sample_id": "us-code-19-2372-7a8bb398787d1d34", "target_family": "temporal"}`
