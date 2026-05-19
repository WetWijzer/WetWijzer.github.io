# packet-000265

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000265/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000265/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000265-20260519_030730

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-59c913bcde9c693d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-59c913bcde9c693d` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.975764796208, "hint_id": "modal-synthesis-d52154f08351bd32", "predicted_family": "frame", "priority": 1.125764796208, "sample_id": "us-code-16-403c-4-96cbffd14ccb8ab5", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.265589752753, "hint_id": "modal-synthesis-db3e227539f69bd0", "predicted_family": "deontic", "priority": 0.415589752753, "sample_id": "us-code-18-119-3c8e7e7e47fc634f", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.99999999234, "hint_id": "modal-synthesis-e4640901ab9aec88", "predicted_family": "temporal", "priority": 1.14999999234, "sample_id": "us-code-2-1902-9bf1dcbf06b93760", "target_family": "deontic"}`
- `program-584127d8685b696e` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-59c913bcde9c693d` score `0.983627`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-37d665571769cd76", "predicted_family": "frame", "priority": 0.33771949257, "sample_id": "us-code-30-665-75575ae82f97b718", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.997326341989, "hint_id": "modal-synthesis-aef47417d4901348", "predicted_family": "temporal", "priority": 1.147326341989, "sample_id": "us-code-42-3016.-a01430f068ac3201", "target_family": "frame"}`
  evidence: `{"family_margin": -0.964745859147, "hint_id": "modal-synthesis-da79806a5d8d2b73", "predicted_family": "frame", "priority": 1.114745859147, "sample_id": "us-code-42-6341.-175bf33765c9042b", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
