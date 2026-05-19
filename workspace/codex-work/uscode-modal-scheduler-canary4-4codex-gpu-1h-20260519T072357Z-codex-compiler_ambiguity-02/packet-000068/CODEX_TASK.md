# packet-000068

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000068/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000068/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000068-20260519_081029

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-ceb151182912d6ed` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ceb151182912d6ed` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.968591331278, "hint_id": "modal-synthesis-a44c9c9b041dbc46", "predicted_family": "frame", "priority": 1.118591331278, "sample_id": "us-code-42-300e-538148287b29314d", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.995156173451, "hint_id": "modal-synthesis-c087a14c544456ba", "predicted_family": "frame", "priority": 1.145156173451, "sample_id": "us-code-33-405-f31c9ec3aa899498", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.308462327773, "hint_id": "modal-synthesis-eeca8e3cbe7a6560", "predicted_family": "frame", "priority": 0.458462327773, "sample_id": "us-code-46-13106.-1fd00cdf20630972", "target_family": "temporal"}`
- `program-f37808775ab6396c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","deontic->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ceb151182912d6ed` score `0.94764`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.403405277522, "hint_id": "modal-synthesis-49fd59a2225fb374", "predicted_family": "deontic", "priority": 0.553405277522, "sample_id": "us-code-7-211-54586d3d201577c2", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.48083331552, "hint_id": "modal-synthesis-c32aa6702ff9e97b", "predicted_family": "temporal", "priority": 0.63083331552, "sample_id": "us-code-15-2215-f0d33acfaeb3b3c4", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.440769754603, "hint_id": "modal-synthesis-f1a01bcc65a7b2de", "predicted_family": "deontic", "priority": 0.590769754603, "sample_id": "us-code-42-287d.-ab84902992754ac0", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.401111762185, "hint_id": "modal-synthesis-fc553f9978c4a9b3", "predicted_family": "deontic", "priority": 0.551111762185, "sample_id": "us-code-30-205-3dae58a00287cef3", "target_family": "conditional_normative"}`
- `program-7b4e3a6864632154` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-ceb151182912d6ed` score `0.944333`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.849347066385, "hint_id": "modal-synthesis-22a1865759f91182", "predicted_family": "frame", "priority": 0.999347066385, "sample_id": "us-code-6-238-5ea2504de5e7b983", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.969786681592, "hint_id": "modal-synthesis-461c8d2a0e08ca8d", "predicted_family": "frame", "priority": 1.119786681592, "sample_id": "us-code-12-57-34419cf11091e65d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.996172137662, "hint_id": "modal-synthesis-c1e7c4aa5028c6ee", "predicted_family": "frame", "priority": 1.146172137662, "sample_id": "us-code-15-6307b-80d228e7d0b2dc48", "target_family": "deontic"}`
  evidence: `{"family_margin": 0.030026284792, "hint_id": "modal-synthesis-c61d6af5e836dc43", "predicted_family": "deontic", "priority": 0.119973715208, "sample_id": "us-code-20-9562-b0d93b3fff15dd56", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
