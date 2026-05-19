# packet-000019

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000019/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000019/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000019-20260519_104935

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-41ecc3c8fa6a4360` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","frame->epistemic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-41ecc3c8fa6a4360` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.935627725057, "hint_id": "modal-synthesis-31585a1280f8c74c", "predicted_family": "frame", "priority": 0.994386054556, "sample_id": "us-code-16-3812-451810cfb3a10ab2", "target_family": "temporal", "target_probability": 0.005613945444}`
  evidence: `{"family_margin": -0.687134054969, "hint_id": "modal-synthesis-37a5d0d8ee71fb18", "predicted_family": "deontic", "priority": 0.914108243129, "sample_id": "us-code-47-1725.-abc549b16337344d", "target_family": "temporal", "target_probability": 0.085891756871}`
  evidence: `{"family_margin": -0.967469936232, "hint_id": "modal-synthesis-4343f8961a973afb", "predicted_family": "frame", "priority": 0.998543277686, "sample_id": "us-code-16-1701-cabc6adc613cd286", "target_family": "epistemic", "target_probability": 0.001456722314}`
  evidence: `{"family_margin": -0.980961027656, "hint_id": "modal-synthesis-db38209df3c5a924", "predicted_family": "frame", "priority": 0.992655977788, "sample_id": "us-code-12-1701h-04e1fb99bf8877db", "target_family": "deontic", "target_probability": 0.007344022212}`
- `program-1f8af215377f251b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-41ecc3c8fa6a4360` score `0.985431`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-1a91f792213967fe", "predicted_family": "temporal", "priority": 0.638399173587, "sample_id": "us-code-42-12146.-4c26f8dff8d901ea", "target_family": "conditional_normative", "target_probability": 0.361600826413}`
  evidence: `{"family_margin": -0.462986986964, "hint_id": "modal-synthesis-745e260d1474a8d5", "predicted_family": "temporal", "priority": 0.872279451872, "sample_id": "us-code-38-1115-6aa7ee0ac263a2cc", "target_family": "deontic", "target_probability": 0.127720548128}`
  evidence: `{"family_margin": -0.955002039866, "hint_id": "modal-synthesis-87aa4a5aba25c3c6", "predicted_family": "frame", "priority": 0.98395170061, "sample_id": "us-code-28-294-a171a8719480b66f", "target_family": "deontic", "target_probability": 0.01604829939}`
  evidence: `{"family_margin": -0.500865197654, "hint_id": "modal-synthesis-bbd1f28f98e654a3", "predicted_family": "frame", "priority": 0.780008932542, "sample_id": "us-code-18-3608-3f5a1a151ad167fc", "target_family": "deontic", "target_probability": 0.219991067458}`
- `program-47509917eede2c20` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","frame->frame","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-41ecc3c8fa6a4360` score `0.977131`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.241161539133, "hint_id": "modal-synthesis-11a8e9fe0487ac10", "predicted_family": "temporal", "priority": 0.859649601632, "sample_id": "us-code-22-1642c-08c79f76662ee13b", "target_family": "deontic", "target_probability": 0.140350398368}`
  evidence: `{"family_margin": 0.199221055742, "hint_id": "modal-synthesis-183168cef57ce999", "predicted_family": "frame", "priority": 0.529084111933, "sample_id": "us-code-7-1632-0fe56574e33e8c2a", "target_family": "frame", "target_probability": 0.470915888067}`
  evidence: `{"family_margin": -0.999966368036, "hint_id": "modal-synthesis-7e17346b6f1ca0d1", "predicted_family": "frame", "priority": 1.0, "sample_id": "us-code-15-637-0720c1c2250fc9b4", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": 0.031704643574, "hint_id": "modal-synthesis-8fee204eaf27ffb6", "predicted_family": "deontic", "priority": 0.502945303942, "sample_id": "us-code-50-2425.-47b48c36c06bff21", "target_family": "deontic", "target_probability": 0.497054696058}`
- `program-f5face9172d22b8b` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-41ecc3c8fa6a4360` score `0.975632`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.185576758924, "hint_id": "modal-synthesis-325cb91f1bd714f5", "predicted_family": "deontic", "priority": 0.628846482153, "sample_id": "us-code-29-3333-af3c53ca33d3966f", "target_family": "temporal", "target_probability": 0.371153517847}`
  evidence: `{"family_margin": -0.676448880695, "hint_id": "modal-synthesis-5fa35a2c9f8ae826", "predicted_family": "deontic", "priority": 0.972713206719, "sample_id": "us-code-22-10211-a44b5edb2402baa6", "target_family": "temporal", "target_probability": 0.027286793281}`
  evidence: `{"family_margin": 0.025530014827, "hint_id": "modal-synthesis-6dd72217eb5213f4", "predicted_family": "deontic", "priority": 0.599749048414, "sample_id": "us-code-49-26101.-0682d377f9f65dd2", "target_family": "deontic", "target_probability": 0.400250951586}`
  evidence: `{"family_margin": -0.993985286542, "hint_id": "modal-synthesis-9e0f042f3fca08c0", "predicted_family": "frame", "priority": 0.999328070483, "sample_id": "us-code-42-3216.-c0f54ff90ebdd8cf", "target_family": "deontic", "target_probability": 0.000671929517}`
- `program-d6b17414bd66548d` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","deontic->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-41ecc3c8fa6a4360` score `0.97089`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.284605054113, "hint_id": "modal-synthesis-441e795c09c4af76", "predicted_family": "frame", "priority": 0.874995168458, "sample_id": "us-code-42-4056.-a21242e6e0739928", "target_family": "conditional_normative", "target_probability": 0.125004831542}`
  evidence: `{"family_margin": 0.048044090689, "hint_id": "modal-synthesis-7e811accbcbfb6d4", "predicted_family": "deontic", "priority": 0.567603183801, "sample_id": "us-code-26-5207-2d368b5c166dddab", "target_family": "deontic", "target_probability": 0.432396816199}`
  evidence: `{"family_margin": -0.202080983098, "hint_id": "modal-synthesis-b52d9fa3afd012a3", "predicted_family": "deontic", "priority": 0.882393574936, "sample_id": "us-code-18-3192-36d4a59ee2eb96c4", "target_family": "temporal", "target_probability": 0.117606425064}`
  evidence: `{"family_margin": -0.732565725774, "hint_id": "modal-synthesis-da7c38c12d64a3b6", "predicted_family": "frame", "priority": 0.923243665797, "sample_id": "us-code-35-282-92386f3bda95850c", "target_family": "deontic", "target_probability": 0.076756334203}`
- `program-ed07c00e24d5ea7a` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-41ecc3c8fa6a4360` score `0.966331`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.572728998217, "hint_id": "modal-synthesis-337a6585b3dd04c9", "predicted_family": "temporal", "priority": 0.919952289761, "sample_id": "us-code-30-1714-dfe0069fa245799f", "target_family": "deontic", "target_probability": 0.080047710239}`
  evidence: `{"family_margin": -0.764480623882, "hint_id": "modal-synthesis-590d521469e67e20", "predicted_family": "frame", "priority": 0.954533828747, "sample_id": "us-code-42-16395.-8c3254009799e102", "target_family": "conditional_normative", "target_probability": 0.045466171253}`
  evidence: `{"family_margin": -0.979801629208, "hint_id": "modal-synthesis-ba048b43701f6f02", "predicted_family": "frame", "priority": 0.99975644228, "sample_id": "us-code-42-2164.-c02ebd529bffa982", "target_family": "temporal", "target_probability": 0.00024355772}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
