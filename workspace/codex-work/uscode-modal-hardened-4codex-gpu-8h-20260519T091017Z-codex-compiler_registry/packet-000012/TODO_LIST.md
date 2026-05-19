# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-36096282afb29374`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-36096282afb29374` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.979447453991`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-2-185-c6529db1ffe67109, us-code-16-403h-10-7c44aec3934bc5ea, us-code-25-5615-4aafd143ae323e5f, us-code-29-2861-867fa59420507d0c`
  evidence: `{"family_margin": -0.999999913108, "hint_id": "modal-synthesis-1cb50a2dca6b4d80", "predicted_family": "frame", "priority": 0.999999998658, "sample_id": "us-code-2-185-c6529db1ffe67109", "target_family": "deontic", "target_probability": 1.342e-09}`
  evidence: `{"family_margin": -0.452940790979, "hint_id": "modal-synthesis-3eaa837464123aad", "predicted_family": "temporal", "priority": 0.929106775091, "sample_id": "us-code-29-2861-867fa59420507d0c", "target_family": "deontic", "target_probability": 0.070893224909}`
  evidence: `{"family_margin": -0.973514448762, "hint_id": "modal-synthesis-40876e19e3ff72b8", "predicted_family": "frame", "priority": 0.990183219657, "sample_id": "us-code-25-5615-4aafd143ae323e5f", "target_family": "conditional_normative", "target_probability": 0.009816780343}`
  evidence: `{"family_margin": -0.996330295432, "hint_id": "modal-synthesis-4e9634f99bf18c3e", "predicted_family": "frame", "priority": 0.998499822559, "sample_id": "us-code-16-403h-10-7c44aec3934bc5ea", "target_family": "deontic", "target_probability": 0.001500177441}`
- `program-323efbbc4b914246`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["alethic->deontic","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-36096282afb29374` score `0.981443`
  loss: `autoencoder_residual_cluster` = `0.944617619374`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-28-1-1323e43821f16b4d, us-code-12-635a-5-94c66d0c292866b1, us-code-12-2609-3741ad0634bd5c75, us-code-6-579-96ed0b0f0ea00fac`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-295b76716c9aef48", "predicted_family": "alethic", "priority": 1.0, "sample_id": "us-code-28-1-1323e43821f16b4d", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.605842671816, "hint_id": "modal-synthesis-7e656ac02e53b27c", "predicted_family": "frame", "priority": 0.880523549045, "sample_id": "us-code-6-579-96ed0b0f0ea00fac", "target_family": "deontic", "target_probability": 0.119476450955}`
  evidence: `{"family_margin": -0.998977097124, "hint_id": "modal-synthesis-81ebd99d34a71f85", "predicted_family": "frame", "priority": 0.999764753773, "sample_id": "us-code-12-635a-5-94c66d0c292866b1", "target_family": "deontic", "target_probability": 0.000235246227}`
  evidence: `{"family_margin": -0.714096507625, "hint_id": "modal-synthesis-a06d4bd5febce0df", "predicted_family": "frame", "priority": 0.898182174677, "sample_id": "us-code-12-2609-3741ad0634bd5c75", "target_family": "deontic", "target_probability": 0.101817825323}`
- `program-92659250c34ed8b9`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-36096282afb29374` score `0.969225`
  loss: `autoencoder_residual_cluster` = `0.870200415784`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-37-302d-af121cd3c8117d6c, us-code-42-5196c.-48b009e08e19ab55, us-code-10-4027-159e40ab73891a1f`
  evidence: `{"family_margin": -0.993481745842, "hint_id": "modal-synthesis-0e83a19e93b4eced", "predicted_family": "frame", "priority": 0.997524879597, "sample_id": "us-code-37-302d-af121cd3c8117d6c", "target_family": "deontic", "target_probability": 0.002475120403}`
  evidence: `{"family_margin": -0.22808495536, "hint_id": "modal-synthesis-468cc27c26b171ee", "predicted_family": "frame", "priority": 0.807442259792, "sample_id": "us-code-42-5196c.-48b009e08e19ab55", "target_family": "deontic", "target_probability": 0.192557740208}`
  evidence: `{"family_margin": -0.12407856259, "hint_id": "modal-synthesis-a1446b46b11147f0", "predicted_family": "frame", "priority": 0.805634107963, "sample_id": "us-code-10-4027-159e40ab73891a1f", "target_family": "conditional_normative", "target_probability": 0.194365892037}`
- `program-ce72ff95fbbb5085`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-36096282afb29374` score `0.9596`
  loss: `autoencoder_residual_cluster` = `0.86576324318`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-460bb-3-df133d34a259e547, us-code-41-3306-7d2ec975af5db2d0, us-code-12-1715q-ebcaf4fb3e07f927`
  evidence: `{"family_margin": -0.999387520342, "hint_id": "modal-synthesis-5d723148fb5dda49", "predicted_family": "frame", "priority": 0.999802115288, "sample_id": "us-code-16-460bb-3-df133d34a259e547", "target_family": "deontic", "target_probability": 0.000197884712}`
  evidence: `{"family_margin": -0.116641973985, "hint_id": "modal-synthesis-751e200c0025d50b", "predicted_family": "frame", "priority": 0.624584457945, "sample_id": "us-code-12-1715q-ebcaf4fb3e07f927", "target_family": "deontic", "target_probability": 0.375415542055}`
  evidence: `{"family_margin": -0.895164401832, "hint_id": "modal-synthesis-cf55aeb5c48e508c", "predicted_family": "frame", "priority": 0.972903156307, "sample_id": "us-code-41-3306-7d2ec975af5db2d0", "target_family": "deontic", "target_probability": 0.027096843693}`
- `program-6ae7cc7726cfdfec`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-36096282afb29374` score `0.958186`
  loss: `autoencoder_residual_cluster` = `0.79325557696`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-2-1814-390f121b05230b7e, us-code-38-2301-967c0000415decec, us-code-36-154108-10b5a65ddc888004`
  evidence: `{"family_margin": -0.18771949257, "hint_id": "modal-synthesis-551240fcff75a2e0", "predicted_family": "frame", "priority": 0.710631513026, "sample_id": "us-code-36-154108-10b5a65ddc888004", "target_family": "deontic", "target_probability": 0.289368486974}`
  evidence: `{"family_margin": -0.783951103158, "hint_id": "modal-synthesis-775ff04a0fc166b4", "predicted_family": "frame", "priority": 0.944014910458, "sample_id": "us-code-2-1814-390f121b05230b7e", "target_family": "deontic", "target_probability": 0.055985089542}`
  evidence: `{"family_margin": -0.13020617018, "hint_id": "modal-synthesis-d08a2149a4ffbcef", "predicted_family": "temporal", "priority": 0.725120307397, "sample_id": "us-code-38-2301-967c0000415decec", "target_family": "deontic", "target_probability": 0.274879692603}`
- `program-8317e8c456774884`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-36096282afb29374` score `0.939017`
  loss: `autoencoder_residual_cluster` = `0.769147424319`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-46-41309.-c3abb50984c239b8, us-code-7-3804-064a6153dad82f40`
  evidence: `{"family_margin": 0.065445330881, "hint_id": "modal-synthesis-42d8ece92e7d97cd", "predicted_family": "deontic", "priority": 0.541882683831, "sample_id": "us-code-7-3804-064a6153dad82f40", "target_family": "deontic", "target_probability": 0.458117316169}`
  evidence: `{"family_margin": -0.973329297143, "hint_id": "modal-synthesis-4d180786d8ad07b9", "predicted_family": "frame", "priority": 0.996412164806, "sample_id": "us-code-46-41309.-c3abb50984c239b8", "target_family": "conditional_normative", "target_probability": 0.003587835194}`
