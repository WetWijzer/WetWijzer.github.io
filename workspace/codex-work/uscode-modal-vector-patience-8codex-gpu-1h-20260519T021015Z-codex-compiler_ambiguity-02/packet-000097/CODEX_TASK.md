# packet-000097

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000097/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/packet-000097/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-patience-8codex-gpu-1h-20260519T021015Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000097-20260519_022309

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-c152840e2028a6c8` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->epistemic","conditional_normative->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c152840e2028a6c8` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.526872655614, "hint_id": "modal-synthesis-8dfb23a2f4b5dc21", "predicted_family": "frame", "priority": 0.676872655614, "sample_id": "us-code-20-3261-ea1591f1a07c9688", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.959954072958, "hint_id": "modal-synthesis-b52c952405055305", "predicted_family": "conditional_normative", "priority": 1.109954072958, "sample_id": "us-code-20-1228c-c9995833bca47965", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.926239302123, "hint_id": "modal-synthesis-e59501dff1215481", "predicted_family": "conditional_normative", "priority": 1.076239302123, "sample_id": "us-code-5-6120-d6895339c5166af1", "target_family": "epistemic"}`
- `program-91597b195c6c393d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c152840e2028a6c8` score `0.987232`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.761278285879, "hint_id": "modal-synthesis-28b39cc864cb6bd9", "predicted_family": "temporal", "priority": 0.911278285879, "sample_id": "us-code-12-4801-6a44921af4549801", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.662709793818, "hint_id": "modal-synthesis-b9fd093c0cd037f2", "predicted_family": "conditional_normative", "priority": 0.812709793818, "sample_id": "us-code-13-24-c62ea50845a9a459", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.454264517727, "hint_id": "modal-synthesis-ebb303c849ea94b0", "predicted_family": "deontic", "priority": 0.604264517727, "sample_id": "us-code-50-212.-52c61a0954a48012", "target_family": "temporal"}`
- `program-23511494970734d7` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-c152840e2028a6c8` score `0.973176`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.999999999924, "hint_id": "modal-synthesis-017154b616ac99e8", "predicted_family": "temporal", "priority": 1.149999999924, "sample_id": "us-code-18-3621-709da9f6e1948604", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.285555820105, "hint_id": "modal-synthesis-29f1bd6104434890", "predicted_family": "temporal", "priority": 0.435555820105, "sample_id": "us-code-10-9772-34f2c9038d0713a9", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.139016052347, "hint_id": "modal-synthesis-6116da582d49120d", "predicted_family": "frame", "priority": 0.289016052347, "sample_id": "us-code-16-612-ff406c8a8a0e2154", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
