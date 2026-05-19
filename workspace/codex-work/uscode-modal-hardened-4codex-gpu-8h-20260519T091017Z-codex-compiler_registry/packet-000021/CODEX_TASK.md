# packet-000021

## Source
The TODO batch is autoencoder/supervisor output; this file is the Codex-facing work order.
- Raw TODO JSONL: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000021/TODO_LIST.jsonl`
- TODO markdown: `/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/packet-000021/TODO_LIST.md`

## Worktree
/home/barberb/portland-laws.github.io/workspace/codex-work/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-codex-compiler_registry/worktrees/agent-codex-compiler_registry-packet-000021-20260519_110738

## Change Capture
pending: awaiting_codex_changes

## Suggested Files
- `ipfs_datasets_py/logic/modal/compiler.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/modal_registry.py`
- `ipfs_datasets_py/optimizers/logic_theorem_optimizer/spacy_modal_codec.py`

## TODOs
- `program-38188e17685e8a7a` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","deontic->conditional_normative","deontic->frame","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-38188e17685e8a7a` score `1.0`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.443094037392, "hint_id": "modal-synthesis-153ab6509ca79b69", "predicted_family": "deontic", "priority": 0.999093983493, "sample_id": "us-code-42-8834.-21377f76b0372f94", "target_family": "frame", "target_probability": 0.000906016507}`
  evidence: `{"family_margin": -0.572604759408, "hint_id": "modal-synthesis-35936fb88488950e", "predicted_family": "conditional_normative", "priority": 0.99849367075, "sample_id": "us-code-16-410aaa-50-d93ecd7b2c265bca", "target_family": "temporal", "target_probability": 0.00150632925}`
  evidence: `{"family_margin": -0.856149561517, "hint_id": "modal-synthesis-7633f3386d0132fd", "predicted_family": "deontic", "priority": 0.944077933176, "sample_id": "us-code-26-651-ec1f77fec5fb0a62", "target_family": "conditional_normative", "target_probability": 0.055922066824}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-b1c7027984c7d396", "predicted_family": "temporal", "priority": 0.580222408163, "sample_id": "us-code-6-677g-31d2665e1caccc9c", "target_family": "deontic", "target_probability": 0.419777591837}`
- `program-70d0370023e50dcb` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","frame->temporal","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-38188e17685e8a7a` score `0.986955`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.199023551178, "hint_id": "modal-synthesis-3987669e6b54438c", "predicted_family": "frame", "priority": 0.693206373573, "sample_id": "us-code-18-3047-8849b73c29ba4ad6", "target_family": "deontic", "target_probability": 0.306793626427}`
  evidence: `{"family_margin": -0.257100608002, "hint_id": "modal-synthesis-7862146eaae71490", "predicted_family": "frame", "priority": 0.782946174575, "sample_id": "us-code-12-1747b-bd0d4aaaab2be128", "target_family": "conditional_normative", "target_probability": 0.217053825425}`
  evidence: `{"family_margin": -0.995075741369, "hint_id": "modal-synthesis-a8d92681e93f1320", "predicted_family": "frame", "priority": 0.999558128951, "sample_id": "us-code-22-7432-850de69c4770f055", "target_family": "temporal", "target_probability": 0.000441871049}`
  evidence: `{"family_margin": -0.239733197541, "hint_id": "modal-synthesis-aaeaf30b270beaa8", "predicted_family": "temporal", "priority": 0.860480863168, "sample_id": "us-code-42-5420.-00697568aff4296c", "target_family": "conditional_normative", "target_probability": 0.139519136832}`
- `program-ab0e9d247c69026f` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->frame","deontic->temporal","epistemic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-38188e17685e8a7a` score `0.969144`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.580200369329, "hint_id": "modal-synthesis-32c656942f469fa3", "predicted_family": "frame", "priority": 0.833356638801, "sample_id": "us-code-25-656-6c4924729d0853e0", "target_family": "deontic", "target_probability": 0.166643361199}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-55ebcb8e5e6c3cb9", "predicted_family": "epistemic", "priority": 0.722751621849, "sample_id": "us-code-22-283r-976899bf26d8db15", "target_family": "deontic", "target_probability": 0.277248378151}`
  evidence: `{"family_margin": -0.254624624015, "hint_id": "modal-synthesis-8c32d8eef5af7d50", "predicted_family": "deontic", "priority": 0.847225225591, "sample_id": "us-code-7-7982-10d3c84e1544afa8", "target_family": "temporal", "target_probability": 0.152774774409}`
  evidence: `{"family_margin": -0.850785409535, "hint_id": "modal-synthesis-c9462ce23280769d", "predicted_family": "deontic", "priority": 0.988797986947, "sample_id": "us-code-42-12752.-22fb1fe07b4c5173", "target_family": "frame", "target_probability": 0.011202013053}`
- `program-6273a3da4ff28809` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-38188e17685e8a7a` score `0.959783`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 4
  evidence: `{"family_margin": -0.973800421626, "hint_id": "modal-synthesis-0e02270409e77981", "predicted_family": "frame", "priority": 0.990976175711, "sample_id": "us-code-5-561-82a2eab5582e6fab", "target_family": "deontic", "target_probability": 0.009023824289}`
  evidence: `{"family_margin": 0.066879344913, "hint_id": "modal-synthesis-3dc8aace10e857eb", "predicted_family": "deontic", "priority": 0.630116448152, "sample_id": "us-code-35-252-fa7caa868816aa81", "target_family": "deontic", "target_probability": 0.369883551848}`
  evidence: `{"family_margin": -0.555287419513, "hint_id": "modal-synthesis-5c761e60918d7292", "predicted_family": "frame", "priority": 0.997953128759, "sample_id": "us-code-22-6411-ba89ac9fe511e033", "target_family": "temporal", "target_probability": 0.002046871241}`
  evidence: `{"family_margin": -0.699805562615, "hint_id": "modal-synthesis-e1e301af0fae2683", "predicted_family": "alethic", "priority": 0.871659975274, "sample_id": "us-code-16-773i-f00163a41a770798", "target_family": "deontic", "target_probability": 0.128340024726}`
- `program-e89f00fd27ca6ed9` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-38188e17685e8a7a` score `0.955884`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.410394828098, "hint_id": "modal-synthesis-120d27428a937b7c", "predicted_family": "frame", "priority": 0.905992540054, "sample_id": "us-code-5-8K-54652e103b9e1518", "target_family": "deontic", "target_probability": 0.094007459946}`
  evidence: `{"family_margin": -0.567455418399, "hint_id": "modal-synthesis-f6163421ec7d9e30", "predicted_family": "frame", "priority": 0.951939490933, "sample_id": "us-code-5-3315a-09989b04501a91c8", "target_family": "temporal", "target_probability": 0.048060509067}`
  evidence: `{"family_margin": -0.059244309703, "hint_id": "modal-synthesis-fc5826aebafae07d", "predicted_family": "deontic", "priority": 0.703778451485, "sample_id": "us-code-7-1471d-9350e269eb381cda", "target_family": "conditional_normative", "target_probability": 0.296221548515}`
- `program-d017588e8fe912f9` `refine_modal_family_cue_rules`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-38188e17685e8a7a` score `0.946615`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  support: 3
  evidence: `{"family_margin": -0.912021725113, "hint_id": "modal-synthesis-16dea9d6b0dd15e8", "predicted_family": "frame", "priority": 0.968557166452, "sample_id": "us-code-15-2-6d3ed4712172ef72", "target_family": "deontic", "target_probability": 0.031442833548}`
  evidence: `{"family_margin": -0.992318572177, "hint_id": "modal-synthesis-2713006c3d62d313", "predicted_family": "frame", "priority": 0.998518143224, "sample_id": "us-code-49-44747.-8d818087c914239d", "target_family": "temporal", "target_probability": 0.001481856776}`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-dfa1e083f2c201f1", "predicted_family": "temporal", "priority": 0.643757932971, "sample_id": "us-code-33-1201-60f5f89ed95507b4", "target_family": "deontic", "target_probability": 0.356242067029}`

## Finish
Leave the completed edits in the worktree; the daemon captures, applies, and validates the diff.
