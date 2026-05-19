# packet-000046

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000046/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000046/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000046-20260519_080347

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-023c99d557ac80c7` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->epistemic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-023c99d557ac80c7` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-45ff59380241c15f", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-7-428-0eedbd792171d56c", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999627887078, "hint_id": "modal-synthesis-a23482480339b49f", "predicted_family": "frame", "priority": 1.149627887078, "sample_id": "us-code-46-14306.-ca967fe82ca4b42b", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.999999978986, "hint_id": "modal-synthesis-a2423eb9469e3744", "predicted_family": "temporal", "priority": 1.149999978986, "sample_id": "us-code-46-55601.-050cf2f773a2a467", "target_family": "deontic"}`
- `program-8c47a1e614a1d22c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->conditional_normative","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-023c99d557ac80c7` score `0.97711`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.42318286485, "hint_id": "modal-synthesis-3e37283620a938af", "predicted_family": "deontic", "priority": 0.57318286485, "sample_id": "us-code-43-390c.-c8a96ce5a854ea46", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-581e5290c951fc60", "predicted_family": "deontic", "priority": 0.15, "sample_id": "us-code-42-7176.-001d470af47d3304", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.998914959864, "hint_id": "modal-synthesis-a73b66292b466b23", "predicted_family": "alethic", "priority": 1.148914959864, "sample_id": "us-code-42-3056.-ca748d473f4cae16", "target_family": "deontic"}`
- `program-366e1942853cf94a` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-023c99d557ac80c7` score `0.96791`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.998961585451, "hint_id": "modal-synthesis-182871496f1fe3fa", "predicted_family": "frame", "priority": 1.148961585451, "sample_id": "us-code-33-2330b-9aa26e5961270d1d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.599864963847, "hint_id": "modal-synthesis-aa58094360529331", "predicted_family": "deontic", "priority": 0.749864963847, "sample_id": "us-code-16-460aaa-7-9c44309c9a316ae6", "target_family": "conditional_normative"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
