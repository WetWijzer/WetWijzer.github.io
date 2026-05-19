# packet-000188

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000188/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000188/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000188-20260519_024350

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-e9a3b5fc3e748a37` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->frame","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e9a3b5fc3e748a37` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.992349673205, "hint_id": "modal-synthesis-a918564e571d6554", "predicted_family": "frame", "priority": 1.142349673205, "sample_id": "us-code-7-8321-65577258c00d4c8d", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.948762054016, "hint_id": "modal-synthesis-b7c768185a202b50", "predicted_family": "conditional_normative", "priority": 1.098762054016, "sample_id": "us-code-38-7361-a13d78c7455475ca", "target_family": "frame"}`
- `program-c58ff0826f0cbfba` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e9a3b5fc3e748a37` score `0.975672`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999752902114, "hint_id": "modal-synthesis-0f8cc537a0e036ee", "predicted_family": "conditional_normative", "priority": 1.149752902114, "sample_id": "us-code-12-2001-2c579d9b8e36ca92", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.37467147672, "hint_id": "modal-synthesis-864008c559251caa", "predicted_family": "deontic", "priority": 0.52467147672, "sample_id": "us-code-12-4405-1c8e651c6443dede", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-cc184ac447b55049", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-38-4111-6a6fb3e21bf602aa", "target_family": "temporal"}`
- `program-149c0bdf34c66e93` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-e9a3b5fc3e748a37` score `0.92551`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.608343394737, "hint_id": "modal-synthesis-4658f6a19da4ff72", "predicted_family": "temporal", "priority": 0.758343394737, "sample_id": "us-code-42-1862i.-143aec5d69724dc4", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.98523581034, "hint_id": "modal-synthesis-c94fe7b514525f3a", "predicted_family": "frame", "priority": 1.13523581034, "sample_id": "us-code-46-60104.-2c0508c6a33c27c3", "target_family": "temporal"}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-e492621f05111503", "predicted_family": "temporal", "priority": 1.15, "sample_id": "us-code-28-172-9175d654e2f6f6e6", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-fe628cb39d5ead2f", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-28-2345-b875b92e6b07960b", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
