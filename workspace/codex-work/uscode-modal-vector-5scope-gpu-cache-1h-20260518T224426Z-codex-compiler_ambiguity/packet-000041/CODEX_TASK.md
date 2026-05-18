# packet-000041

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/packet-000041/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/packet-000041/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-vector-5scope-gpu-cache-1h-20260518T224426Z-codex-compiler_ambiguity/worktrees/agent-codex-compiler_ambiguity-packet-000041-20260518_230952

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-476ade1cfd27ba84` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->frame","deontic->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-476ade1cfd27ba84` score `1.0`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.999999958321, "hint_id": "modal-synthesis-2f6285f991d03876", "predicted_family": "conditional_normative", "priority": 1.149999958321, "sample_id": "us-code-21-812-2eb1864ec2e64b00", "target_family": "frame"}`
  evidence: `{"family_margin": -0.999999694098, "hint_id": "modal-synthesis-94347bdbc57cdc62", "predicted_family": "deontic", "priority": 1.149999694098, "sample_id": "us-code-26-4943-da67256c0ed21118", "target_family": "temporal"}`
- `program-6f99799c0aa22849` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-476ade1cfd27ba84` score `0.987869`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.58149724676, "hint_id": "modal-synthesis-393de5be6dc2597e", "predicted_family": "frame", "priority": 0.73149724676, "sample_id": "us-code-16-695-492b4df7c31e8f3d", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.997819511486, "hint_id": "modal-synthesis-4113a5da9645d978", "predicted_family": "frame", "priority": 1.147819511486, "sample_id": "us-code-42-217a-6ec68696965efbfe", "target_family": "deontic"}`
- `program-70f6dabd5d08e379` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-476ade1cfd27ba84` score `0.986531`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.999999990827, "hint_id": "modal-synthesis-7bacf00d2adf4e32", "predicted_family": "deontic", "priority": 1.149999990827, "sample_id": "us-code-15-694-1-19bbe1ebb1be0815", "target_family": "epistemic"}`
  evidence: `{"family_margin": -0.72116659717, "hint_id": "modal-synthesis-93fb1d43551ee942", "predicted_family": "frame", "priority": 0.87116659717, "sample_id": "us-code-17-410-0758ab00b97b8f33", "target_family": "temporal"}`
- `program-f8e0f2835830c528` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-476ade1cfd27ba84` score `0.985681`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 2
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-7e857da4a0bd72a0", "predicted_family": "frame", "priority": 0.33771949257, "sample_id": "us-code-46-53513.-4951b7ed362e76de", "target_family": "deontic"}`
  evidence: `{"family_margin": -0.936603825667, "hint_id": "modal-synthesis-fe0940cc77839ab1", "predicted_family": "deontic", "priority": 1.086603825667, "sample_id": "us-code-46-53723.-c79c0fa010e0afe2", "target_family": "temporal"}`
- `program-8ebf7794d70c1727` `add_or_review_modal_ambiguity_policy`
  target: `modal.compiler.ambiguity`
  scope: `compiler_ambiguity`
  bundle: `{"action":"add_or_review_modal_ambiguity_policy","family_pairs":["conditional_normative->temporal","deontic->temporal","frame->temporal"],"program_synthesis_scope":"compiler_ambiguity","target_component":"modal.compiler.ambiguity"}`
  vector_bundle: `program-476ade1cfd27ba84` score `0.978297`
  objective: The adaptive family margin is small, so the compiler should expose an explicit ambiguity.
  support: 3
  evidence: `{"family_margin": -0.495914480481, "hint_id": "modal-synthesis-5a843800ae15e6b6", "predicted_family": "conditional_normative", "priority": 0.645914480481, "sample_id": "us-code-46-7113.-352a3c716bd8efb0", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.56927588958, "hint_id": "modal-synthesis-bfcce8334149f067", "predicted_family": "frame", "priority": 0.71927588958, "sample_id": "us-code-50-2656.-10e19e6cd88e6b96", "target_family": "temporal"}`
  evidence: `{"family_margin": -0.757541915301, "hint_id": "modal-synthesis-d40ccd3072a96e76", "predicted_family": "deontic", "priority": 0.907541915301, "sample_id": "us-code-2-1511-313ca032e8ac0971", "target_family": "temporal"}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
