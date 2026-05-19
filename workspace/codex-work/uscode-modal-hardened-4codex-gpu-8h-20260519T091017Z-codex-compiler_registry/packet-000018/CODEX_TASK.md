# packet-000018

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000018/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000018/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000018-20260519_103603

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-a60a5a7581718884` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-a60a5a7581718884` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.482589725284, "hint_id": "modal-synthesis-26042683bb265997", "predicted_family": "frame", "priority": 0.946224658601, "sample_id": "us-code-54-306104.-a124186569120f30", "target_family": "conditional_normative", "target_probability": 0.053775341399}`
  evidence: `{"family_margin": -0.679959655186, "hint_id": "modal-synthesis-314da7c3354b6be7", "predicted_family": "deontic", "priority": 0.99431854623, "sample_id": "us-code-30-1301-12a766bbc248466b", "target_family": "frame", "target_probability": 0.00568145377}`
  evidence: `{"family_margin": -0.934312567156, "hint_id": "modal-synthesis-ba1016c153155756", "predicted_family": "frame", "priority": 0.978947911836, "sample_id": "us-code-49-5128.-3253d68185883faf", "target_family": "deontic", "target_probability": 0.021052088164}`
- `program-959b1d9a7fe2da1f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-a60a5a7581718884` score `0.98241`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.21898271845, "hint_id": "modal-synthesis-0455086127ea1f15", "predicted_family": "temporal", "priority": 0.928324587318, "sample_id": "us-code-22-290h-7-fc7abec921bbc03b", "target_family": "frame", "target_probability": 0.071675412682}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-5c6e9d1627b99658", "predicted_family": "deontic", "priority": 0.559746660672, "sample_id": "us-code-21-205-62b4ecc5f3c47e77", "target_family": "deontic", "target_probability": 0.440253339328}`
  evidence: `{"family_margin": -0.230665609524, "hint_id": "modal-synthesis-9c045288807c3037", "predicted_family": "frame", "priority": 0.644430327874, "sample_id": "us-code-48-487 to 487b.-20c793cbf965675e", "target_family": "deontic", "target_probability": 0.355569672126}`
- `program-e8ab2e8ad1399751` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->frame","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-a60a5a7581718884` score `0.980194`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.195978788183, "hint_id": "modal-synthesis-119d72b107b20adb", "predicted_family": "deontic", "priority": 0.832018181557, "sample_id": "us-code-25-2506-59a8f56049b580cb", "target_family": "conditional_normative", "target_probability": 0.167981818443}`
  evidence: `{"family_margin": -0.311599345975, "hint_id": "modal-synthesis-14ceb384f73023e8", "predicted_family": "frame", "priority": 0.910503396576, "sample_id": "us-code-16-404c-2-6d913f18513c192a", "target_family": "deontic", "target_probability": 0.089496603424}`
  evidence: `{"family_margin": -0.805392295729, "hint_id": "modal-synthesis-de6e2670559d56f4", "predicted_family": "deontic", "priority": 0.9721934293, "sample_id": "us-code-16-460a-9-10cd613b63863e33", "target_family": "frame", "target_probability": 0.0278065707}`
- `program-578f8fadada078c5` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->epistemic","frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-a60a5a7581718884` score `0.977971`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.994033783251, "hint_id": "modal-synthesis-9777d468ec41b750", "predicted_family": "frame", "priority": 0.998493260087, "sample_id": "us-code-26-585-a91fbae7f3fcdcb3", "target_family": "conditional_normative", "target_probability": 0.001506739913}`
  evidence: `{"family_margin": -0.330135897918, "hint_id": "modal-synthesis-a0f636de7e06e024", "predicted_family": "frame", "priority": 0.721287086366, "sample_id": "us-code-11-1224-68dfb0ff97792385", "target_family": "temporal", "target_probability": 0.278712913634}`
  evidence: `{"family_margin": -0.544360096723, "hint_id": "modal-synthesis-e4ab0b23ae194fa1", "predicted_family": "deontic", "priority": 0.997037115573, "sample_id": "us-code-5-6120-d6895339c5166af1", "target_family": "epistemic", "target_probability": 0.002962884427}`
- `program-334beea7ba41d149` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->conditional_normative","deontic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-a60a5a7581718884` score `0.977129`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-35d310b028cf4a24", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-44-1335.-edbedca6b9a81220", "target_family": "deontic", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.844760733598, "hint_id": "modal-synthesis-9b7e079f6afa6ed1", "predicted_family": "alethic", "priority": 0.999738326027, "sample_id": "us-code-42-1382c.-317fd26d2273011a", "target_family": "conditional_normative", "target_probability": 0.000261673973}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-c798345a4ead9df1", "predicted_family": "deontic", "priority": 0.523775425532, "sample_id": "us-code-16-460ww-3-b0ba72d66eca5ae0", "target_family": "deontic", "target_probability": 0.476224574468}`
- `program-4b2c8994db9e633c` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-a60a5a7581718884` score `0.974843`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 2
  evidence: `{"family_margin": -0.874623237248, "hint_id": "modal-synthesis-299f888b8b681a8c", "predicted_family": "deontic", "priority": 0.995386187404, "sample_id": "us-code-12-1975-9de95ba2da51c9bc", "target_family": "temporal", "target_probability": 0.004613812596}`
  evidence: `{"family_margin": -0.512578970616, "hint_id": "modal-synthesis-a64489a5bb1d3e59", "predicted_family": "frame", "priority": 0.969515246651, "sample_id": "us-code-26-224-4cbc6b9203a4f7a2", "target_family": "conditional_normative", "target_probability": 0.030484753349}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
