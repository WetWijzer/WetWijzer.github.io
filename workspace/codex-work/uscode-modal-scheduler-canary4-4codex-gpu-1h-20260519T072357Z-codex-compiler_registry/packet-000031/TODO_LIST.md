# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-bd8fa04d16843d8a`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bd8fa04d16843d8a` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999982693896`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-207.-a133f8f59a5be5bc, us-code-22-2152j-1-b13faa2e4f52f3a5`
  evidence: `{"family_margin": -0.999997419106, "hint_id": "modal-synthesis-25447310d96191da", "predicted_family": "temporal", "priority": 0.999999006417, "sample_id": "us-code-42-207.-a133f8f59a5be5bc", "target_family": "deontic", "target_probability": 9.93583e-07}`
  evidence: `{"family_margin": -0.999536120613, "hint_id": "modal-synthesis-c6978628839c5ac7", "predicted_family": "frame", "priority": 0.999966381376, "sample_id": "us-code-22-2152j-1-b13faa2e4f52f3a5", "target_family": "temporal", "target_probability": 3.3618624e-05}`
- `program-08736c7db9c9e009`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bd8fa04d16843d8a` score `0.987835`
  loss: `autoencoder_residual_cluster` = `0.987936666163`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-18-831-fbe15f1f8d8eafb3, us-code-22-2083-30f65b26f389e617`
  evidence: `{"family_margin": -0.999208624451, "hint_id": "modal-synthesis-38009faab0907f91", "predicted_family": "frame", "priority": 0.999964862235, "sample_id": "us-code-18-831-fbe15f1f8d8eafb3", "target_family": "deontic", "target_probability": 3.5137765e-05}`
  evidence: `{"family_margin": -0.941192519958, "hint_id": "modal-synthesis-68cb6ae43c362e9d", "predicted_family": "frame", "priority": 0.975908470091, "sample_id": "us-code-22-2083-30f65b26f389e617", "target_family": "deontic", "target_probability": 0.024091529909}`
- `program-1820ce8e20d1b017`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bd8fa04d16843d8a` score `0.986427`
  loss: `autoencoder_residual_cluster` = `0.985202871553`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-4901-2ad5a8db3570b4d3, us-code-16-460z-8-a67203ffef3c484d`
  evidence: `{"family_margin": -0.99999999986, "hint_id": "modal-synthesis-1083d2802d84a82f", "predicted_family": "temporal", "priority": 0.999999999999, "sample_id": "us-code-10-4901-2ad5a8db3570b4d3", "target_family": "deontic", "target_probability": 1e-12}`
  evidence: `{"family_margin": -0.733651687966, "hint_id": "modal-synthesis-f2f2d5e61771f9c7", "predicted_family": "conditional_normative", "priority": 0.970405743107, "sample_id": "us-code-16-460z-8-a67203ffef3c484d", "target_family": "temporal", "target_probability": 0.029594256893}`
- `program-91d3b9b3219707b4`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","temporal->alethic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bd8fa04d16843d8a` score `0.983236`
  loss: `autoencoder_residual_cluster` = `0.940792754645`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-2-1826-eb548767c1332240, us-code-29-161-7b18abb2ab2605ea, us-code-25-1778f-00c2a17384f95d42`
  evidence: `{"family_margin": -0.605183972302, "hint_id": "modal-synthesis-22be29afa07cd994", "predicted_family": "frame", "priority": 0.826180925386, "sample_id": "us-code-25-1778f-00c2a17384f95d42", "target_family": "deontic", "target_probability": 0.173819074614}`
  evidence: `{"family_margin": -0.996266083265, "hint_id": "modal-synthesis-6d05ce448ea0db77", "predicted_family": "frame", "priority": 0.998512248296, "sample_id": "us-code-2-1826-eb548767c1332240", "target_family": "deontic", "target_probability": 0.001487751704}`
  evidence: `{"family_margin": -0.931586336941, "hint_id": "modal-synthesis-b96afe386ffdeda3", "predicted_family": "temporal", "priority": 0.997685090252, "sample_id": "us-code-29-161-7b18abb2ab2605ea", "target_family": "alethic", "target_probability": 0.002314909748}`
- `program-ec22f304afc8c723`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bd8fa04d16843d8a` score `0.982095`
  loss: `autoencoder_residual_cluster` = `0.965157447242`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-33-1516-3803c560f593fc1e, us-code-25-344-eef9c2928ad7515a`
  evidence: `{"family_margin": -0.804723328443, "hint_id": "modal-synthesis-7b631f929d87fe87", "predicted_family": "deontic", "priority": 0.941594079299, "sample_id": "us-code-25-344-eef9c2928ad7515a", "target_family": "conditional_normative", "target_probability": 0.058405920701}`
  evidence: `{"family_margin": -0.518764260388, "hint_id": "modal-synthesis-dd55700f6bc8c6c4", "predicted_family": "deontic", "priority": 0.988720815185, "sample_id": "us-code-33-1516-3803c560f593fc1e", "target_family": "frame", "target_probability": 0.011279184815}`
- `program-bbca6346a95abdec`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-bd8fa04d16843d8a` score `0.981316`
  loss: `autoencoder_residual_cluster` = `0.925434372022`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-33-405-f31c9ec3aa899498, us-code-42-300e-538148287b29314d, us-code-46-13106.-1fd00cdf20630972`
  evidence: `{"family_margin": -0.308462327773, "hint_id": "modal-synthesis-681ca0ede8b4294e", "predicted_family": "frame", "priority": 0.781371895982, "sample_id": "us-code-46-13106.-1fd00cdf20630972", "target_family": "temporal", "target_probability": 0.218628104018}`
  evidence: `{"family_margin": -0.968591331278, "hint_id": "modal-synthesis-82faea0029436f23", "predicted_family": "frame", "priority": 0.996429629647, "sample_id": "us-code-42-300e-538148287b29314d", "target_family": "conditional_normative", "target_probability": 0.003570370353}`
  evidence: `{"family_margin": -0.995156173451, "hint_id": "modal-synthesis-9066a351244b357b", "predicted_family": "frame", "priority": 0.998501590438, "sample_id": "us-code-33-405-f31c9ec3aa899498", "target_family": "temporal", "target_probability": 0.001498409562}`
