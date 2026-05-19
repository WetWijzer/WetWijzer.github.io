# packet-000231

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000231/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000231/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000231-20260519_133440

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-6ab3c30bd34972f6` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["epistemic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-6ab3c30bd34972f6` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.889025829822, "hint_id": "modal-synthesis-15f36f0f258c8a9f", "predicted_family": "epistemic", "priority": 1.039025829822, "sample_id": "us-code-42-7511b.-1d3299a1a442c3ed", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.54822096945, "hint_id": "modal-synthesis-1bd75e66f97a30f7", "predicted_family": "frame", "priority": 0.69822096945, "sample_id": "us-code-42-1772.-026fbcdf892256fb", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999281017791, "hint_id": "modal-synthesis-fcbc8b0869f1e127", "predicted_family": "frame", "priority": 1.149281017791, "sample_id": "us-code-38-4301-f41e0787fba53b0a", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
