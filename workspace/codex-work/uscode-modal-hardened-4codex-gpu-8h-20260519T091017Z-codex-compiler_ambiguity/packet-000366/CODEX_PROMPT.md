# packet-000366

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000366/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000366/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000366-20260519_142642

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-68ceb887138a3d2b` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal","hybrid->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-68ceb887138a3d2b` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.885319001402, "hint_id": "modal-synthesis-330ce76303b01dcf", "predicted_family": "frame", "priority": 1.035319001402, "sample_id": "us-code-42-10154.-3990045c9fffc0c5", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.951659333425, "hint_id": "modal-synthesis-594309b87c296426", "predicted_family": "frame", "priority": 1.101659333425, "sample_id": "us-code-7-6807-8b07fd1cc236bb34", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.991577311702, "hint_id": "modal-synthesis-961019eb17010ef6", "predicted_family": "frame", "priority": 1.141577311702, "sample_id": "us-code-10-8679-527c7516d5479316", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.18032295659, "hint_id": "modal-synthesis-ca3a203db10ae7a7", "predicted_family": "hybrid", "priority": 0.33032295659, "sample_id": "us-code-43-2901.-7aac673167dc177c", "target_family": "frame"}`
- `program-1a69b023fd2c8ee9` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-68ceb887138a3d2b` score `0.98422`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.125384604062, "hint_id": "modal-synthesis-526a6352faf28648", "predicted_family": "deontic", "priority": 0.275384604062, "sample_id": "us-code-42-17242.-18143a7842efc3da", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.814383146408, "hint_id": "modal-synthesis-7a6ef024903f329b", "predicted_family": "frame", "priority": 0.964383146408, "sample_id": "us-code-26-6151-8cf146ef1cb76a82", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.99753314728, "hint_id": "modal-synthesis-e62cbd0f1241e794", "predicted_family": "frame", "priority": 1.14753314728, "sample_id": "us-code-42-1862s-59a34514597fe4f9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.998618289075, "hint_id": "modal-synthesis-f816ed8366bc810c", "predicted_family": "frame", "priority": 1.148618289075, "sample_id": "us-code-6-314a-3a3b3dc754213770", "target_family": "conditional_normative"}`

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
- `program-68ceb887138a3d2b`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal","hybrid->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-68ceb887138a3d2b` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.90221965078`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-10-8679-527c7516d5479316, us-code-7-6807-8b07fd1cc236bb34, us-code-42-10154.-3990045c9fffc0c5, us-code-43-2901.-7aac673167dc177c`
  evidence: `{"family_margin": -0.885319001402, "hint_id": "modal-synthesis-330ce76303b01dcf", "predicted_family": "frame", "priority": 1.035319001402, "sample_id": "us-code-42-10154.-3990045c9fffc0c5", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.951659333425, "hint_id": "modal-synthesis-594309b87c296426", "predicted_family": "frame", "priority": 1.101659333425, "sample_id": "us-code-7-6807-8b07fd1cc236bb34", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.991577311702, "hint_id": "modal-synthesis-961019eb17010ef6", "predicted_family": "frame", "priority": 1.141577311702, "sample_id": "us-code-10-8679-527c7516d5479316", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.18032295659, "hint_id": "modal-synthesis-ca3a203db10ae7a7", "predicted_family": "hybrid", "priority": 0.33032295659, "sample_id": "us-code-43-2901.-7aac673167dc177c", "target_family": "frame"}`
- `program-1a69b023fd2c8ee9`
  action: `add_or_review_modal_ambiguity_policy`
  role: `program_synthesis`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-68ceb887138a3d2b` score `0.98422`
  loss: `autoencoder_residual_cluster` = `0.883979796706`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  samples: `us-code-6-314a-3a3b3dc754213770, us-code-42-1862s-59a34514597fe4f9, us-code-26-6151-8cf146ef1cb76a82, us-code-42-17242.-18143a7842efc3da`
  evidence: `{"family_margin": -0.125384604062, "hint_id": "modal-synthesis-526a6352faf28648", "predicted_family": "deontic", "priority": 0.275384604062, "sample_id": "us-code-42-17242.-18143a7842efc3da", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.814383146408, "hint_id": "modal-synthesis-7a6ef024903f329b", "predicted_family": "frame", "priority": 0.964383146408, "sample_id": "us-code-26-6151-8cf146ef1cb76a82", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.99753314728, "hint_id": "modal-synthesis-e62cbd0f1241e794", "predicted_family": "frame", "priority": 1.14753314728, "sample_id": "us-code-42-1862s-59a34514597fe4f9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.998618289075, "hint_id": "modal-synthesis-f816ed8366bc810c", "predicted_family": "frame", "priority": 1.148618289075, "sample_id": "us-code-6-314a-3a3b3dc754213770", "target_family": "conditional_normative"}`
