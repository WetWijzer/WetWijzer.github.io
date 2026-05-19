# packet-000027

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000027/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/packet-000027/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-codex-compiler_ambiguity-02/worktrees/agent-codex-compiler_ambiguity-02-packet-000027-20260519_073525

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-f4b612caec0c813a` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f4b612caec0c813a` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.998770601276, "hint_id": "modal-synthesis-08e0065711429f83", "predicted_family": "temporal", "priority": 1.148770601276, "sample_id": "us-code-22-9521-34e0d0fb34bfe30f", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.987482973805, "hint_id": "modal-synthesis-2e35a96b3a51ef91", "predicted_family": "frame", "priority": 1.137482973805, "sample_id": "us-code-34-20924-4eecfc8963e9330c", "target_family": "deontic"}`
- `program-2920b329e6bbd062` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","temporal->alethic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f4b612caec0c813a` score `0.977311`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-60d35b8a0d2c60aa", "predicted_family": "frame", "priority": 0.755183972302, "sample_id": "us-code-25-1778f-00c2a17384f95d42", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.931586336941, "hint_id": "modal-synthesis-71922e7d48a7129b", "predicted_family": "temporal", "priority": 1.081586336941, "sample_id": "us-code-29-161-7b18abb2ab2605ea", "target_family": "alethic"}`
  evidence: `{"family_margin": -0.996266083265, "hint_id": "modal-synthesis-873dc393be3ef58f", "predicted_family": "frame", "priority": 1.146266083265, "sample_id": "us-code-2-1826-eb548767c1332240", "target_family": "deontic"}`
- `program-841fbb72b265498d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["alethic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f4b612caec0c813a` score `0.969126`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.503766568024, "hint_id": "modal-synthesis-1975f87dc03e24b2", "predicted_family": "alethic", "priority": 0.653766568024, "sample_id": "us-code-16-398a-e687cd66b1dd5f3b", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-d761770220a070eb", "predicted_family": "frame", "priority": 1.077175206504, "sample_id": "us-code-20-2993-c0baac0499ad31c8", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.996527279879, "hint_id": "modal-synthesis-eb89d1bc9b06678c", "predicted_family": "frame", "priority": 1.146527279879, "sample_id": "us-code-10-12501-f5bf1e6a25f0e84d", "target_family": "deontic"}`
- `program-024c4ecbef1ef52d` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f4b612caec0c813a` score `0.942563`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.999914132733, "hint_id": "modal-synthesis-37b5e1eed8f42dc0", "predicted_family": "temporal", "priority": 1.149914132733, "sample_id": "us-code-26-1354-ad2c60771bf57beb", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.999999999823, "hint_id": "modal-synthesis-c990a14cb6377288", "predicted_family": "temporal", "priority": 1.149999999823, "sample_id": "us-code-10-153-56da0d65843f2d44", "target_family": "conditional_normative"}`
  evidence: `{"family_margin": -0.332359271705, "hint_id": "modal-synthesis-dcb44b7e8bdc489b", "predicted_family": "frame", "priority": 0.482359271705, "sample_id": "us-code-18-3634-d299400c2544c4c1", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.544325473206, "hint_id": "modal-synthesis-dd7ffb18f9aad609", "predicted_family": "frame", "priority": 0.694325473206, "sample_id": "us-code-50-47e.-ace4ebd3651ec612", "target_family": "deontic"}`
- `program-a4e52bcf4610219b` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->frame","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-f4b612caec0c813a` score `0.937669`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 4
  evidence: `{"family_margin": -0.987157460597, "hint_id": "modal-synthesis-35dfdf90fb8f9fd4", "predicted_family": "frame", "priority": 1.137157460597, "sample_id": "us-code-48-1405q.-9d6f199557d55566", "target_family": "temporal"}`
  evidence: `{"family_margin": 0.145871398637, "hint_id": "modal-synthesis-7da658ceea16c912", "predicted_family": "frame", "priority": 0.004128601363, "sample_id": "us-code-38-1918-45cba69d3d3264af", "target_family": "frame"}`
  evidence: `{"family_margin": -0.989785951931, "hint_id": "modal-synthesis-b842b2c237bb4175", "predicted_family": "frame", "priority": 1.139785951931, "sample_id": "us-code-38-7804-07ee3c2ccbd6323b", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.778697246128, "hint_id": "modal-synthesis-d2dbcf659dc6a4b1", "predicted_family": "frame", "priority": 0.928697246128, "sample_id": "us-code-10-775-4abe87c9c6ca820a", "target_family": "deontic"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
