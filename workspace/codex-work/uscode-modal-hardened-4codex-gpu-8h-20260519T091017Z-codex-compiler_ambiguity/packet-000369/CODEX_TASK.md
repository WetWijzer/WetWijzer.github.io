# packet-000369

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000369/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/packet-000369/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000369-20260519_144224

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-286339d1f28e6083` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-286339d1f28e6083` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.819948970608, "hint_id": "modal-synthesis-3e459236fb1bd2f4", "predicted_family": "frame", "priority": 0.969948970608, "sample_id": "us-code-26-45L-42236fa7dda0591e", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.738638395995, "hint_id": "modal-synthesis-b9fc8f9a1ff5b6c9", "predicted_family": "deontic", "priority": 0.888638395995, "sample_id": "us-code-16-410n-d27716bf4667f350", "target_family": "conditional_normative"}`
- `program-425c9be56603b9ac` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->deontic","deontic->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-286339d1f28e6083` score `0.977172`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.830738257014, "hint_id": "modal-synthesis-df24e043c959628f", "predicted_family": "deontic", "priority": 0.980738257014, "sample_id": "us-code-33-1276-78104eb1d3b59bd3", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.224697529935, "hint_id": "modal-synthesis-e6fd5dfc78612f72", "predicted_family": "frame", "priority": 0.374697529935, "sample_id": "us-code-22-7402-f13b16a29fa68295", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.012389592663, "hint_id": "modal-synthesis-f4894eefcc3a5d48", "predicted_family": "conditional_normative", "priority": 0.162389592663, "sample_id": "us-code-20-1078-10-192bae91a06078eb", "target_family": "deontic"}`
- `program-c15bcba3a19952a5` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-286339d1f28e6083` score `0.971003`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": 0.144667398472, "hint_id": "modal-synthesis-8371bbfd53d636b0", "predicted_family": "temporal", "priority": 0.005332601528, "sample_id": "us-code-22-866-be9f23427595bfe1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.991845939729, "hint_id": "modal-synthesis-d9cd093617e0be30", "predicted_family": "frame", "priority": 1.141845939729, "sample_id": "us-code-46-30105.-024fee1fbe6f67ee", "target_family": "temporal"}`
- `program-cfcbff554f78be50` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->temporal","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-286339d1f28e6083` score `0.943209`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.125156415541, "hint_id": "modal-synthesis-0f152963ce5f41b6", "predicted_family": "temporal", "priority": 0.275156415541, "sample_id": "us-code-50-3040.-9d91aee75289e33b", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.53369122802, "hint_id": "modal-synthesis-88c057196c11c3b7", "predicted_family": "temporal", "priority": 0.68369122802, "sample_id": "us-code-15-7407-a39ea8637eeb8bc6", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.941814049738, "hint_id": "modal-synthesis-af2abd8ba60b5e76", "predicted_family": "frame", "priority": 1.091814049738, "sample_id": "us-code-42-1320a-19cde0462c72cc39", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.840692295338, "hint_id": "modal-synthesis-bfdcb032c76f254c", "predicted_family": "frame", "priority": 0.990692295338, "sample_id": "us-code-26-6050J-5b6ef7c634b15989", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
