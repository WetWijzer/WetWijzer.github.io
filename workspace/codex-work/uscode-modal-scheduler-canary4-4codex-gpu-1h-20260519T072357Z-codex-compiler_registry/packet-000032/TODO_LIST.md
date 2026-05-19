# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-2124a7c07d22049a`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2124a7c07d22049a` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.999866590816`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-10222.-4e5a89f05abf6e43, us-code-12-2121-2f87de947818271b`
  evidence: `{"family_margin": -0.879553798991, "hint_id": "modal-synthesis-1211e03713d9b615", "predicted_family": "temporal", "priority": 0.999735499684, "sample_id": "us-code-12-2121-2f87de947818271b", "target_family": "conditional_normative", "target_probability": 0.000264500316}`
  evidence: `{"family_margin": -0.999862926894, "hint_id": "modal-synthesis-8c94b663645bb1ec", "predicted_family": "temporal", "priority": 0.999997681947, "sample_id": "us-code-42-10222.-4e5a89f05abf6e43", "target_family": "deontic", "target_probability": 2.318053e-06}`
- `program-9b7cac730dbc34ba`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2124a7c07d22049a` score `0.985879`
  loss: `autoencoder_residual_cluster` = `0.707953223292`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-10104.-34d355a29ae42574, us-code-42-280b-a217bc610e10ef34`
  evidence: `{"family_margin": -0.78969827777, "hint_id": "modal-synthesis-3a28182403da0f39", "predicted_family": "frame", "priority": 0.912003318214, "sample_id": "us-code-42-10104.-34d355a29ae42574", "target_family": "deontic", "target_probability": 0.087996681786}`
  evidence: `{"family_margin": 0.249742455922, "hint_id": "modal-synthesis-4757dce40f635e77", "predicted_family": "conditional_normative", "priority": 0.50390312837, "sample_id": "us-code-42-280b-a217bc610e10ef34", "target_family": "conditional_normative", "target_probability": 0.49609687163}`
- `program-bf13151d8f4b4cb7`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","temporal->conditional_normative","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2124a7c07d22049a` score `0.980876`
  loss: `autoencoder_residual_cluster` = `0.706989814127`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-50-3734.-53bf86760d22cdad, us-code-12-214a-71d543320eec73fc, us-code-10-870-de3be5699d46964e`
  evidence: `{"family_margin": -0.558201193929, "hint_id": "modal-synthesis-00f31ad568580d37", "predicted_family": "temporal", "priority": 0.912631664946, "sample_id": "us-code-50-3734.-53bf86760d22cdad", "target_family": "conditional_normative", "target_probability": 0.087368335054}`
  evidence: `{"family_margin": 0.159198155487, "hint_id": "modal-synthesis-9127bf33156e56a5", "predicted_family": "deontic", "priority": 0.5856861617, "sample_id": "us-code-10-870-de3be5699d46964e", "target_family": "deontic", "target_probability": 0.4143138383}`
  evidence: `{"family_margin": -0.068489551327, "hint_id": "modal-synthesis-c695e978017e913c", "predicted_family": "temporal", "priority": 0.622651615735, "sample_id": "us-code-12-214a-71d543320eec73fc", "target_family": "deontic", "target_probability": 0.377348384265}`
- `program-59734408d7460513`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2124a7c07d22049a` score `0.978462`
  loss: `autoencoder_residual_cluster` = `0.944566038829`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-16-410i-fc1cbdffd88df051, us-code-21-355d-0d0fb4408e391f8e, us-code-48-2196.-8730b7fd1745de7d`
  evidence: `{"family_margin": -0.994891566401, "hint_id": "modal-synthesis-0c9477d36ef138f4", "predicted_family": "temporal", "priority": 0.998663210471, "sample_id": "us-code-16-410i-fc1cbdffd88df051", "target_family": "conditional_normative", "target_probability": 0.001336789529}`
  evidence: `{"family_margin": -0.425051397629, "hint_id": "modal-synthesis-486b42b77e004230", "predicted_family": "frame", "priority": 0.939317112713, "sample_id": "us-code-21-355d-0d0fb4408e391f8e", "target_family": "deontic", "target_probability": 0.060682887287}`
  evidence: `{"family_margin": -0.701346671703, "hint_id": "modal-synthesis-f124709d820f80ff", "predicted_family": "deontic", "priority": 0.895717793303, "sample_id": "us-code-48-2196.-8730b7fd1745de7d", "target_family": "temporal", "target_probability": 0.104282206697}`
- `program-76414449aa8e109b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->deontic","frame->deontic","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2124a7c07d22049a` score `0.976808`
  loss: `autoencoder_residual_cluster` = `0.889284763583`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-28-524-445e0313d6f19fea, us-code-22-2291n-ac54fa9d2b9461be, us-code-12-4105-36d07b104cbb3372`
  evidence: `{"family_margin": -0.073728924867, "hint_id": "modal-synthesis-4725959bca6fe58a", "predicted_family": "conditional_normative", "priority": 0.668219838098, "sample_id": "us-code-12-4105-36d07b104cbb3372", "target_family": "deontic", "target_probability": 0.331780161902}`
  evidence: `{"family_margin": -1.0, "hint_id": "modal-synthesis-5caf385768533b32", "predicted_family": "temporal", "priority": 1.0, "sample_id": "us-code-28-524-445e0313d6f19fea", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.99922543422, "hint_id": "modal-synthesis-b85a56cd716c8b99", "predicted_family": "frame", "priority": 0.999634452651, "sample_id": "us-code-22-2291n-ac54fa9d2b9461be", "target_family": "deontic", "target_probability": 0.000365547349}`
- `program-1201b4cca05492da`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","temporal->conditional_normative"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2124a7c07d22049a` score `0.971469`
  loss: `autoencoder_residual_cluster` = `0.865406664264`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-20-9133-1be94617ef12a512, us-code-38-7405-5a48188b1b79bce0, us-code-16-450e-1-c701fe3463da7053`
  evidence: `{"family_margin": 0.139673778321, "hint_id": "modal-synthesis-082a310712da23d9", "predicted_family": "deontic", "priority": 0.636498431597, "sample_id": "us-code-16-450e-1-c701fe3463da7053", "target_family": "deontic", "target_probability": 0.363501568403}`
  evidence: `{"family_margin": -0.871848671962, "hint_id": "modal-synthesis-b07ebe2578f210df", "predicted_family": "frame", "priority": 0.959805038036, "sample_id": "us-code-38-7405-5a48188b1b79bce0", "target_family": "deontic", "target_probability": 0.040194961964}`
  evidence: `{"family_margin": -0.999537374177, "hint_id": "modal-synthesis-baef32b8c7881786", "predicted_family": "temporal", "priority": 0.999916523158, "sample_id": "us-code-20-9133-1be94617ef12a512", "target_family": "conditional_normative", "target_probability": 8.3476842e-05}`
