# packet-000020

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000020/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000020/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000020-20260519_092231

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-b7de2a42bf2380ba` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b7de2a42bf2380ba` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.995479656744, "hint_id": "modal-synthesis-46acde3498a92f98", "predicted_family": "frame", "priority": 1.145479656744, "sample_id": "us-code-22-2370c-ecf99a4ce73acee6", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.999856812397, "hint_id": "modal-synthesis-79727d5267530233", "predicted_family": "frame", "priority": 1.149856812397, "sample_id": "us-code-19-4584-b1c82116f196949b", "target_family": "temporal"}`
- `program-be1ea360261ba19c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b7de2a42bf2380ba` score `0.989702`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.475806685034, "hint_id": "modal-synthesis-2b98a5aa74c37770", "predicted_family": "frame", "priority": 0.625806685034, "sample_id": "us-code-22-2701-9339678f754757c1", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.890473622324, "hint_id": "modal-synthesis-34547dfc817028b9", "predicted_family": "frame", "priority": 1.040473622324, "sample_id": "us-code-43-942-923f98d291d0a371", "target_family": "temporal"}`
- `program-d07f7ccb41bf7b9c` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b7de2a42bf2380ba` score `0.969025`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.73880192382, "hint_id": "modal-synthesis-17a65f233a8e7a10", "predicted_family": "frame", "priority": 0.88880192382, "sample_id": "us-code-42-9125.-66edf52c2c4a26ae", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.24602509287, "hint_id": "modal-synthesis-1c6a39f456fa1c69", "predicted_family": "deontic", "priority": 0.39602509287, "sample_id": "us-code-7-1912-fc36229e34b4e587", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.815144126803, "hint_id": "modal-synthesis-720f6fc8ddeb9b17", "predicted_family": "frame", "priority": 0.965144126803, "sample_id": "us-code-21-387f-4b0c7d5eb20848f5", "target_family": "temporal"}`
- `program-722735126dbde00b` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->deontic","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b7de2a42bf2380ba` score `0.968474`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.973329297143, "hint_id": "modal-synthesis-1332616e56fffa0e", "predicted_family": "frame", "priority": 1.123329297143, "sample_id": "us-code-46-41309.-c3abb50984c239b8", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": 0.065445330881, "hint_id": "modal-synthesis-c880f96144cfefea", "predicted_family": "deontic", "priority": 0.084554669119, "sample_id": "us-code-7-3804-064a6153dad82f40", "target_family": "deontic"}`
- `program-35956d8fa9079224` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b7de2a42bf2380ba` score `0.96718`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.116641973985, "hint_id": "modal-synthesis-247df5e027efcaa2", "predicted_family": "frame", "priority": 0.266641973985, "sample_id": "us-code-12-1715q-ebcaf4fb3e07f927", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.895164401832, "hint_id": "modal-synthesis-44a1286799fdfff9", "predicted_family": "frame", "priority": 1.045164401832, "sample_id": "us-code-41-3306-7d2ec975af5db2d0", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999387520342, "hint_id": "modal-synthesis-f5946bb7a1ae1e34", "predicted_family": "frame", "priority": 1.149387520342, "sample_id": "us-code-16-460bb-3-df133d34a259e547", "target_family": "deontic"}`
- `program-33cfd2fd852bae48` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-b7de2a42bf2380ba` score `0.965942`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.13020617018, "hint_id": "modal-synthesis-0e20e66e55ba62ca", "predicted_family": "temporal", "priority": 0.28020617018, "sample_id": "us-code-38-2301-967c0000415decec", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.783951103158, "hint_id": "modal-synthesis-782b56750899f8d5", "predicted_family": "frame", "priority": 0.933951103158, "sample_id": "us-code-2-1814-390f121b05230b7e", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-d48e74b2d450a24e", "predicted_family": "frame", "priority": 0.33771949257, "sample_id": "us-code-36-154108-10b5a65ddc888004", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
