# packet-000180

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000180/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000180/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000180-20260519_144722

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-32c367aabba7d254` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-32c367aabba7d254` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.72561328302, "hint_id": "modal-synthesis-06e88979dd4bbdd5", "predicted_family": "frame", "priority": 0.984699519393, "sample_id": "us-code-10-8761a-f20006898ff8c3e4", "target_family": "conditional_normative", "target_probability": 0.015300480607}`
  evidence: `{"family_margin": -0.667479661137, "hint_id": "modal-synthesis-6a4aa103b898758d", "predicted_family": "alethic", "priority": 0.999867205882, "sample_id": "us-code-15-4652-c7d562053cccf08d", "target_family": "deontic", "target_probability": 0.000132794118}`
  evidence: `{"family_margin": -0.889153440775, "hint_id": "modal-synthesis-a8e45d56c0830a4e", "predicted_family": "frame", "priority": 0.981251066793, "sample_id": "us-code-44-726.-9ba99f9695a05c64", "target_family": "deontic", "target_probability": 0.018748933207}`
- `program-b5af1f78f954e2e4` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","epistemic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-32c367aabba7d254` score `0.980783`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.966919756926, "hint_id": "modal-synthesis-733b6c809d68329e", "predicted_family": "frame", "priority": 0.998221174165, "sample_id": "us-code-2-141b-878bad9540f78ffc", "target_family": "temporal", "target_probability": 0.001778825835}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-cf5895b20f3efc7e", "predicted_family": "deontic", "priority": 0.590193532682, "sample_id": "us-code-25-4044-053049e05567f13c", "target_family": "deontic", "target_probability": 0.409806467318}`
  evidence: `{"family_margin": -0.99580361114, "hint_id": "modal-synthesis-de333c1f7926caf1", "predicted_family": "epistemic", "priority": 0.999791929953, "sample_id": "us-code-42-6928.-fc1e9d40184ee8c6", "target_family": "conditional_normative", "target_probability": 0.000208070047}`
- `program-e7631707645b6c0b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-32c367aabba7d254` score `0.978174`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.53369122802, "hint_id": "modal-synthesis-0f5654afdfe61626", "predicted_family": "temporal", "priority": 0.990816232337, "sample_id": "us-code-15-7407-a39ea8637eeb8bc6", "target_family": "deontic", "target_probability": 0.009183767663}`
  evidence: `{"family_margin": -0.125156415541, "hint_id": "modal-synthesis-149d8042f4ff4d18", "predicted_family": "temporal", "priority": 0.791405974099, "sample_id": "us-code-50-3040.-9d91aee75289e33b", "target_family": "conditional_normative", "target_probability": 0.208594025901}`
  evidence: `{"family_margin": -0.840692295338, "hint_id": "modal-synthesis-51f1f230b1595de5", "predicted_family": "frame", "priority": 0.982872446681, "sample_id": "us-code-26-6050J-5b6ef7c634b15989", "target_family": "temporal", "target_probability": 0.017127553319}`
  evidence: `{"family_margin": -0.941814049738, "hint_id": "modal-synthesis-da5c85cd91836f7d", "predicted_family": "frame", "priority": 0.982381901632, "sample_id": "us-code-42-1320a-19cde0462c72cc39", "target_family": "temporal", "target_probability": 0.017618098368}`
- `program-00dd1621b91c58c6` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","deontic->conditional_normative","frame->deontic","frame->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-32c367aabba7d254` score `0.97282`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.224697529935, "hint_id": "modal-synthesis-9aaaea1e9a00ecbf", "predicted_family": "frame", "priority": 0.64801707134, "sample_id": "us-code-22-7402-f13b16a29fa68295", "target_family": "deontic", "target_probability": 0.35198292866}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-a39509a74244efc8", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-42-5175.-c1ba3aebd0c22026", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.012389592663, "hint_id": "modal-synthesis-e2c5b6b3e7679522", "predicted_family": "conditional_normative", "priority": 0.640701812774, "sample_id": "us-code-20-1078-10-192bae91a06078eb", "target_family": "deontic", "target_probability": 0.359298187226}`
  evidence: `{"family_margin": -0.830738257014, "hint_id": "modal-synthesis-ea9ba18df36c9310", "predicted_family": "deontic", "priority": 0.960753453397, "sample_id": "us-code-33-1276-78104eb1d3b59bd3", "target_family": "conditional_normative", "target_probability": 0.039246546603}`
- `program-fc929f061f604201` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-32c367aabba7d254` score `0.966096`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.819948970608, "hint_id": "modal-synthesis-beffc4671feece4b", "predicted_family": "frame", "priority": 0.947107502397, "sample_id": "us-code-26-45L-42236fa7dda0591e", "target_family": "conditional_normative", "target_probability": 0.052892497603}`
  evidence: `{"family_margin": -0.738638395995, "hint_id": "modal-synthesis-bf858ef03ac99066", "predicted_family": "deontic", "priority": 0.951753539806, "sample_id": "us-code-16-410n-d27716bf4667f350", "target_family": "conditional_normative", "target_probability": 0.048246460194}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
