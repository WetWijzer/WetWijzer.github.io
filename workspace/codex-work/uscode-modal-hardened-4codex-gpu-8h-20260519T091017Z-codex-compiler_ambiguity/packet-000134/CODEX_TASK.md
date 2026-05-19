# packet-000134

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000134/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000134/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000134-20260519_114315

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-17bb0c4556b9133e` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-17bb0c4556b9133e` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.326471773923, "hint_id": "modal-synthesis-593a07b1933ef27a", "predicted_family": "frame", "priority": 0.476471773923, "sample_id": "us-code-15-4406-06b42cf5db1c97c9", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.283228545629, "hint_id": "modal-synthesis-b02354e4d932e493", "predicted_family": "deontic", "priority": 0.433228545629, "sample_id": "us-code-16-194-86bb9ee231685cf0", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.886363126312, "hint_id": "modal-synthesis-eb1a1a283ef58096", "predicted_family": "frame", "priority": 1.036363126312, "sample_id": "us-code-10-2733a-077475dad346b012", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.871641370684, "hint_id": "modal-synthesis-fc54c97a33141815", "predicted_family": "frame", "priority": 1.021641370684, "sample_id": "us-code-25-5352-0bba059599ed7867", "target_family": "conditional_normative"}`
- `program-d72b473bbbbc52d4` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","deontic->conditional_normative","frame->alethic","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-17bb0c4556b9133e` score `0.974002`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.986970544558, "hint_id": "modal-synthesis-0b5b0e8b550d2f4e", "predicted_family": "frame", "priority": 1.136970544558, "sample_id": "us-code-21-967-19871a230815c843", "target_family": "alethic"}`
  evidence: `{"family_margin": -0.174240329935, "hint_id": "modal-synthesis-35b17833e52ee0df", "predicted_family": "deontic", "priority": 0.324240329935, "sample_id": "us-code-30-704-7ffdf626721c3d66", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.976534442234, "hint_id": "modal-synthesis-58e50a3fe16e2846", "predicted_family": "frame", "priority": 1.126534442234, "sample_id": "us-code-16-403i-4fc971cb18a2761e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.130920775863, "hint_id": "modal-synthesis-d09fab772447e9ec", "predicted_family": "alethic", "priority": 0.280920775863, "sample_id": "us-code-22-277d-46-590d06ce439c2f8c", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
