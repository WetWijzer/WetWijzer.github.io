# packet-000136

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000136/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000136/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000136-20260519_115726

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-cc8df2b8766d67e4` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-cc8df2b8766d67e4` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.804489585093, "hint_id": "modal-synthesis-94bd02d294b8450a", "predicted_family": "frame", "priority": 0.954489585093, "sample_id": "us-code-5-8102a-c38142dd6938d00d", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-bd58ada0c22fd52b", "predicted_family": "temporal", "priority": 0.15, "sample_id": "us-code-22-1571-8ee22a2210e4b14d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.94331159456, "hint_id": "modal-synthesis-d5913f901dc64416", "predicted_family": "frame", "priority": 1.09331159456, "sample_id": "us-code-20-1161b-1fb334a71e66301b", "target_family": "deontic"}`
- `program-dbd08ba8fede4ed1` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-cc8df2b8766d67e4` score `0.962681`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.268764268861, "hint_id": "modal-synthesis-80cb1eaa95317d25", "predicted_family": "frame", "priority": 0.418764268861, "sample_id": "us-code-30-937-f058702f2785ed46", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.427971886065, "hint_id": "modal-synthesis-ae6e565ff1719bb1", "predicted_family": "temporal", "priority": 0.577971886065, "sample_id": "us-code-29-1085b-cffafd0b7cf5d453", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-e4493bb832a01cce", "predicted_family": "frame", "priority": 0.982441698483, "sample_id": "us-code-33-466-9e6d8c7abbc26172", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.289155588506, "hint_id": "modal-synthesis-f38fc3c7976bb82b", "predicted_family": "deontic", "priority": 0.439155588506, "sample_id": "us-code-20-9706-db957ea3fc5fbd91", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
