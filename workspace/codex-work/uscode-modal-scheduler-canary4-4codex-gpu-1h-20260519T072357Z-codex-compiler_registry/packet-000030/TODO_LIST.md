# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-scheduler-canary4-4codex-gpu-1h-20260519T072357Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-2fc45b2e9caa1268`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal","temporal->frame"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2fc45b2e9caa1268` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.97665009918`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-48-1401 to 1401e.-1dadd607f4660f80, us-code-10-2686-307cb92f2d3705e2, us-code-38-7315-c771bec603cdd386, us-code-31-752-e21314fdb8298fb0`
  evidence: `{"family_margin": -0.908038226995, "hint_id": "modal-synthesis-328a2beb5ebb4222", "predicted_family": "frame", "priority": 0.962231328382, "sample_id": "us-code-31-752-e21314fdb8298fb0", "target_family": "deontic", "target_probability": 0.037768671618}`
  evidence: `{"family_margin": -0.949451098605, "hint_id": "modal-synthesis-755eb77b0dadc7d0", "predicted_family": "temporal", "priority": 0.975931153877, "sample_id": "us-code-38-7315-c771bec603cdd386", "target_family": "frame", "target_probability": 0.024068846123}`
  evidence: `{"family_margin": -0.924813751676, "hint_id": "modal-synthesis-e2c0bccd738b44e5", "predicted_family": "frame", "priority": 0.981158627324, "sample_id": "us-code-10-2686-307cb92f2d3705e2", "target_family": "deontic", "target_probability": 0.018841372676}`
  evidence: `{"family_margin": -0.92479320096, "hint_id": "modal-synthesis-ffb9d5a9d8e31680", "predicted_family": "frame", "priority": 0.987279287136, "sample_id": "us-code-48-1401 to 1401e.-1dadd607f4660f80", "target_family": "temporal", "target_probability": 0.012720712864}`
- `program-aa184791b130b28e`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2fc45b2e9caa1268` score `0.991132`
  loss: `autoencoder_residual_cluster` = `0.844171700573`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-22-4210-84a1442bd9c70a2c, us-code-25-1680p-0f3db7fd6700af7f, us-code-20-78a-e776385e2a7fe165, us-code-16-552a-5158b7b4f84afb51`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-006b5f312bef6982", "predicted_family": "frame", "priority": 0.851064907891, "sample_id": "us-code-25-1680p-0f3db7fd6700af7f", "target_family": "temporal", "target_probability": 0.148935092109}`
  evidence: `{"family_margin": -0.284750434111, "hint_id": "modal-synthesis-244b95cad9770681", "predicted_family": "frame", "priority": 0.759603170542, "sample_id": "us-code-16-552a-5158b7b4f84afb51", "target_family": "deontic", "target_probability": 0.240396829458}`
  evidence: `{"family_margin": -0.277597579055, "hint_id": "modal-synthesis-381b0f7df133e486", "predicted_family": "deontic", "priority": 0.770062992821, "sample_id": "us-code-20-78a-e776385e2a7fe165", "target_family": "temporal", "target_probability": 0.229937007179}`
  evidence: `{"family_margin": -0.985555718125, "hint_id": "modal-synthesis-fb24afcb20baffb2", "predicted_family": "frame", "priority": 0.995955731037, "sample_id": "us-code-22-4210-84a1442bd9c70a2c", "target_family": "deontic", "target_probability": 0.004044268963}`
- `program-0de1a69779d68e3e`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2fc45b2e9caa1268` score `0.988016`
  loss: `autoencoder_residual_cluster` = `0.873100486091`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-15-6307b-80d228e7d0b2dc48, us-code-12-57-34419cf11091e65d, us-code-6-238-5ea2504de5e7b983, us-code-20-9562-b0d93b3fff15dd56`
  evidence: `{"family_margin": -0.849347066385, "hint_id": "modal-synthesis-0f3dfe13a7abc922", "predicted_family": "frame", "priority": 0.969248331627, "sample_id": "us-code-6-238-5ea2504de5e7b983", "target_family": "deontic", "target_probability": 0.030751668373}`
  evidence: `{"family_margin": -0.996172137662, "hint_id": "modal-synthesis-265e1cd252922de5", "predicted_family": "frame", "priority": 0.998760632287, "sample_id": "us-code-15-6307b-80d228e7d0b2dc48", "target_family": "deontic", "target_probability": 0.001239367713}`
  evidence: `{"family_margin": -0.969786681592, "hint_id": "modal-synthesis-77c2e952ff2e8bc4", "predicted_family": "frame", "priority": 0.995134934277, "sample_id": "us-code-12-57-34419cf11091e65d", "target_family": "temporal", "target_probability": 0.004865065723}`
  evidence: `{"family_margin": 0.030026284792, "hint_id": "modal-synthesis-bf9878549101ebb1", "predicted_family": "deontic", "priority": 0.529258046175, "sample_id": "us-code-20-9562-b0d93b3fff15dd56", "target_family": "deontic", "target_probability": 0.470741953825}`
- `program-2a282bef906cc00d`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2fc45b2e9caa1268` score `0.984409`
  loss: `autoencoder_residual_cluster` = `0.822893116606`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-12-1701q-1-7363f6565593d464, us-code-6-533-f1d9319c09926fa6, us-code-15-713a-1-8b5e17a928c198e1, us-code-28-755-d77e49748d22301e`
  evidence: `{"family_margin": -0.927175206504, "hint_id": "modal-synthesis-321dc3a47933e465", "predicted_family": "frame", "priority": 0.991908356278, "sample_id": "us-code-6-533-f1d9319c09926fa6", "target_family": "temporal", "target_probability": 0.008091643722}`
  evidence: `{"family_margin": -0.199221055742, "hint_id": "modal-synthesis-bcb055739260b566", "predicted_family": "frame", "priority": 0.728305167674, "sample_id": "us-code-15-713a-1-8b5e17a928c198e1", "target_family": "temporal", "target_probability": 0.271694832326}`
  evidence: `{"family_margin": 0.116498490285, "hint_id": "modal-synthesis-e5524aa3eee49544", "predicted_family": "deontic", "priority": 0.571433273516, "sample_id": "us-code-28-755-d77e49748d22301e", "target_family": "deontic", "target_probability": 0.428566726484}`
  evidence: `{"family_margin": -0.996442309715, "hint_id": "modal-synthesis-ed637c60a0b60b0c", "predicted_family": "temporal", "priority": 0.999925668956, "sample_id": "us-code-12-1701q-1-7363f6565593d464", "target_family": "deontic", "target_probability": 7.4331044e-05}`
- `program-b13bdebbe074a517`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2fc45b2e9caa1268` score `0.984299`
  loss: `autoencoder_residual_cluster` = `0.95683801277`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-3028.-a48920161b1e7a31, us-code-20-1011f-4582f720da22b8fa, us-code-7-136b-83377b73058cb0ad, us-code-25-380-a7cb3da37ceba607`
  evidence: `{"family_margin": -0.999999999846, "hint_id": "modal-synthesis-4dd5142267487834", "predicted_family": "temporal", "priority": 1.0, "sample_id": "us-code-42-3028.-a48920161b1e7a31", "target_family": "deontic", "target_probability": 0.0}`
  evidence: `{"family_margin": -0.997555242754, "hint_id": "modal-synthesis-705039807f2bf6d8", "predicted_family": "frame", "priority": 0.999966448001, "sample_id": "us-code-20-1011f-4582f720da22b8fa", "target_family": "temporal", "target_probability": 3.3551999e-05}`
  evidence: `{"family_margin": -0.363165125612, "hint_id": "modal-synthesis-739a98859e2cb73d", "predicted_family": "deontic", "priority": 0.884236154611, "sample_id": "us-code-25-380-a7cb3da37ceba607", "target_family": "temporal", "target_probability": 0.115763845389}`
  evidence: `{"family_margin": -0.832441698483, "hint_id": "modal-synthesis-d87470c8cd685459", "predicted_family": "frame", "priority": 0.943149448469, "sample_id": "us-code-7-136b-83377b73058cb0ad", "target_family": "temporal", "target_probability": 0.056850551531}`
- `program-49908e4f3e0643c8`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","frame->temporal","temporal->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-2fc45b2e9caa1268` score `0.983302`
  loss: `autoencoder_residual_cluster` = `0.884807273006`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-2-607-2e9d6e27189ecc14, us-code-15-4656-8948f7d6d7ef22ee, us-code-22-290n-3-2b067e975d5b088d, us-code-43-4-71ea028bee67bb72`
  evidence: `{"family_margin": -0.998448998074, "hint_id": "modal-synthesis-304e3a75e1971f3e", "predicted_family": "frame", "priority": 0.999447467868, "sample_id": "us-code-2-607-2e9d6e27189ecc14", "target_family": "deontic", "target_probability": 0.000552532132}`
  evidence: `{"family_margin": -0.797111365677, "hint_id": "modal-synthesis-3bae40ed22020bde", "predicted_family": "deontic", "priority": 0.942146547057, "sample_id": "us-code-22-290n-3-2b067e975d5b088d", "target_family": "temporal", "target_probability": 0.057853452943}`
  evidence: `{"family_margin": -0.987659830267, "hint_id": "modal-synthesis-49a69e6ed4e7929f", "predicted_family": "temporal", "priority": 0.998428113233, "sample_id": "us-code-15-4656-8948f7d6d7ef22ee", "target_family": "deontic", "target_probability": 0.001571886767}`
  evidence: `{"family_margin": -0.042151771569, "hint_id": "modal-synthesis-972b956bccbee497", "predicted_family": "frame", "priority": 0.599206963866, "sample_id": "us-code-43-4-71ea028bee67bb72", "target_family": "temporal", "target_probability": 0.400793036134}`
