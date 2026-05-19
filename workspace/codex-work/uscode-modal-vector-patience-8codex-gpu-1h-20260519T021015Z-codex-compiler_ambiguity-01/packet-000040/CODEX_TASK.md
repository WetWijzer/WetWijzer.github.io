# packet-000040

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000040/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/packet-000040/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-01/worktrees/agent-codex-compiler_ambiguity-01-packet-000040-20260519_022054

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e70c13db6db4223b` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e70c13db6db4223b` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.98344914023, "hint_id": "modal-synthesis-117bf73f21a6f95d", "predicted_family": "frame", "priority": 1.13344914023, "sample_id": "us-code-52-10310.-26f34fd94cb731ad", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-3108d54a22d6a397", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-16-1028-3a1bf3000702288a", "target_family": "temporal"}`
- `program-f1a845d42fcb293f` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e70c13db6db4223b` score `0.971663`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999972491655, "hint_id": "modal-synthesis-75b2d6e2fc31b651", "predicted_family": "temporal", "priority": 1.149972491655, "sample_id": "us-code-34-10153-56c96555be0f0204", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.994348324902, "hint_id": "modal-synthesis-adb81af27f81d919", "predicted_family": "frame", "priority": 1.144348324902, "sample_id": "us-code-48-1668.-9bf242213fd1b01c", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.464529535773, "hint_id": "modal-synthesis-e8a3573dd5f642c3", "predicted_family": "conditional_normative", "priority": 0.614529535773, "sample_id": "us-code-25-4228-3dea43be040239c7", "target_family": "temporal"}`
- `program-c6ae9bd6d61f82b0` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->epistemic","deontic->frame","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e70c13db6db4223b` score `0.937067`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.411885467434, "hint_id": "modal-synthesis-024999fe84b1e793", "predicted_family": "temporal", "priority": 0.561885467434, "sample_id": "us-code-25-181-b1aaf50455600eea", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.23602129703, "hint_id": "modal-synthesis-066d93ff31d5a28f", "predicted_family": "frame", "priority": 0.38602129703, "sample_id": "us-code-18-3101-b020ea24c0c5ac85", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.24602509287, "hint_id": "modal-synthesis-41174f0f9c4ff7c7", "predicted_family": "conditional_normative", "priority": 0.39602509287, "sample_id": "us-code-16-450rr-5e94cfe81f6a5af1", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.590749662423, "hint_id": "modal-synthesis-b2ae23fec30bb8f6", "predicted_family": "deontic", "priority": 0.740749662423, "sample_id": "us-code-42-300x-68c9c55c8a163c4d", "target_family": "frame"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
