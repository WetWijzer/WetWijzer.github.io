# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-hardened-4codex-gpu-8h-20260519T091017Z-autoencoder.jsonl`
- TODO count: `6`

## TODOs
- `program-50b97214f6f73021`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->conditional_normative","frame->deontic","frame->epistemic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-50b97214f6f73021` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.995750299137`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-34-20985-a99f5bb23eba7cb9, us-code-7-499b-1-d6f63c7df52c7482, us-code-33-3603-03b0c18b73283e27`
  evidence: `{"family_margin": -0.950521673039, "hint_id": "modal-synthesis-6fe3d5f78f96f82b", "predicted_family": "frame", "priority": 0.999357451687, "sample_id": "us-code-34-20985-a99f5bb23eba7cb9", "target_family": "epistemic", "target_probability": 0.000642548313}`
  evidence: `{"family_margin": -0.990313811796, "hint_id": "modal-synthesis-7cc97c99cd69ee16", "predicted_family": "frame", "priority": 0.99817813652, "sample_id": "us-code-7-499b-1-d6f63c7df52c7482", "target_family": "conditional_normative", "target_probability": 0.00182186348}`
  evidence: `{"family_margin": -0.975055389627, "hint_id": "modal-synthesis-eaf6f2b0a3ba02ba", "predicted_family": "frame", "priority": 0.989715309203, "sample_id": "us-code-33-3603-03b0c18b73283e27", "target_family": "deontic", "target_probability": 0.010284690797}`
- `program-0bcbd8fa310928b3`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["conditional_normative->temporal","frame->conditional_normative","frame->deontic"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-50b97214f6f73021` score `0.985413`
  loss: `autoencoder_residual_cluster` = `0.938011343641`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-29-50-4a33aa3700621816, us-code-28-2407-28b6d685a9fdd642, us-code-22-8401-b6335528658fbe30`
  evidence: `{"family_margin": -0.657562757972, "hint_id": "modal-synthesis-1593a8f83aee017c", "predicted_family": "frame", "priority": 0.881594997342, "sample_id": "us-code-22-8401-b6335528658fbe30", "target_family": "conditional_normative", "target_probability": 0.118405002658}`
  evidence: `{"family_margin": -0.414972526981, "hint_id": "modal-synthesis-706ee766b18ea8ae", "predicted_family": "conditional_normative", "priority": 0.942953150191, "sample_id": "us-code-28-2407-28b6d685a9fdd642", "target_family": "temporal", "target_probability": 0.057046849809}`
  evidence: `{"family_margin": -0.973380385138, "hint_id": "modal-synthesis-e2801b306a23fb5d", "predicted_family": "frame", "priority": 0.989485883389, "sample_id": "us-code-29-50-4a33aa3700621816", "target_family": "deontic", "target_probability": 0.010514116611}`
- `program-b502774b268cbfbd`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-50b97214f6f73021` score `0.98244`
  loss: `autoencoder_residual_cluster` = `0.926728483897`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-21-387f-4b0c7d5eb20848f5, us-code-42-9125.-66edf52c2c4a26ae, us-code-7-1912-fc36229e34b4e587`
  evidence: `{"family_margin": -0.815144126803, "hint_id": "modal-synthesis-58205cc38ad50de4", "predicted_family": "frame", "priority": 0.967305299746, "sample_id": "us-code-21-387f-4b0c7d5eb20848f5", "target_family": "temporal", "target_probability": 0.032694700254}`
  evidence: `{"family_margin": -0.73880192382, "hint_id": "modal-synthesis-9f5cc69f49c709a3", "predicted_family": "frame", "priority": 0.956061025301, "sample_id": "us-code-42-9125.-66edf52c2c4a26ae", "target_family": "temporal", "target_probability": 0.043938974699}`
  evidence: `{"family_margin": -0.24602509287, "hint_id": "modal-synthesis-b50621c0428eda79", "predicted_family": "deontic", "priority": 0.856819126644, "sample_id": "us-code-7-1912-fc36229e34b4e587", "target_family": "conditional_normative", "target_probability": 0.143180873356}`
- `program-85af1ff8fc5bf252`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->conditional_normative","deontic->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-50b97214f6f73021` score `0.981186`
  loss: `autoencoder_residual_cluster` = `0.771653591523`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-10-16161-05656c7ed7f119d4, us-code-42-7473.-317045e2f473b2e5, us-code-34-10726-675518ae1ebeae48`
  evidence: `{"family_margin": 0.0, "hint_id": "modal-synthesis-2845730e85e014d9", "predicted_family": "deontic", "priority": 0.639501933916, "sample_id": "us-code-34-10726-675518ae1ebeae48", "target_family": "deontic", "target_probability": 0.360498066084}`
  evidence: `{"family_margin": -0.079554853007, "hint_id": "modal-synthesis-373281e1eaed9d28", "predicted_family": "deontic", "priority": 0.734817156643, "sample_id": "us-code-42-7473.-317045e2f473b2e5", "target_family": "conditional_normative", "target_probability": 0.265182843357}`
  evidence: `{"family_margin": -0.169611967572, "hint_id": "modal-synthesis-eee3e1f2b8d1390b", "predicted_family": "frame", "priority": 0.940641684009, "sample_id": "us-code-10-16161-05656c7ed7f119d4", "target_family": "temporal", "target_probability": 0.059358315991}`
- `program-097625b3eb0da13b`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-50b97214f6f73021` score `0.979768`
  loss: `autoencoder_residual_cluster` = `0.929878190837`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-42-14042.-0a9611a52b4ee6c7, us-code-16-80d-aff925c919bdb32c, us-code-50-42.-665c7c7be93a2efb`
  evidence: `{"family_margin": -0.78969827777, "hint_id": "modal-synthesis-48baadb9a7f4eb71", "predicted_family": "frame", "priority": 0.912003318214, "sample_id": "us-code-50-42.-665c7c7be93a2efb", "target_family": "temporal", "target_probability": 0.087996681786}`
  evidence: `{"family_margin": -0.913314606897, "hint_id": "modal-synthesis-6dfd92a4f0e79ac5", "predicted_family": "frame", "priority": 0.957528711172, "sample_id": "us-code-42-14042.-0a9611a52b4ee6c7", "target_family": "temporal", "target_probability": 0.042471288828}`
  evidence: `{"family_margin": -0.717014355684, "hint_id": "modal-synthesis-7b1715b194bf2a49", "predicted_family": "frame", "priority": 0.920102543124, "sample_id": "us-code-16-80d-aff925c919bdb32c", "target_family": "deontic", "target_probability": 0.079897456876}`
- `program-102dddf93283bc34`
  action: `refine_modal_family_cue_rules`
  role: `program_synthesis`
  target: `modal.compiler.registry`
  scope: `compiler_registry`
  bundle: `{"action":"refine_modal_family_cue_rules","family_pairs":["deontic->temporal","frame->deontic","frame->temporal"],"program_synthesis_scope":"compiler_registry","target_component":"modal.compiler.registry"}`
  vector_bundle: `program-50b97214f6f73021` score `0.975287`
  loss: `autoencoder_residual_cluster` = `0.908843376522`
  objective: Adaptive family evidence disagrees with, or is weak for, the typed modal family.
  samples: `us-code-6-121-73f643a319081ef3, us-code-46-44104.-0f27ffbe862df46f, us-code-22-262n-1-68b5ecd4b412547e, us-code-42-3614-f985d9bbb892d157`
  evidence: `{"family_margin": -0.313427557169, "hint_id": "modal-synthesis-002303300dd397fc", "predicted_family": "deontic", "priority": 0.791048295221, "sample_id": "us-code-42-3614-f985d9bbb892d157", "target_family": "temporal", "target_probability": 0.208951704779}`
  evidence: `{"family_margin": -0.518545682385, "hint_id": "modal-synthesis-0a6eff3001108df1", "predicted_family": "frame", "priority": 0.851064907891, "sample_id": "us-code-22-262n-1-68b5ecd4b412547e", "target_family": "temporal", "target_probability": 0.148935092109}`
  evidence: `{"family_margin": -0.986613081907, "hint_id": "modal-synthesis-84d8249a3911365c", "predicted_family": "frame", "priority": 0.999999999898, "sample_id": "us-code-6-121-73f643a319081ef3", "target_family": "deontic", "target_probability": 1.02e-10}`
  evidence: `{"family_margin": -0.772263349992, "hint_id": "modal-synthesis-933a30d257f2e696", "predicted_family": "frame", "priority": 0.993260303076, "sample_id": "us-code-46-44104.-0f27ffbe862df46f", "target_family": "temporal", "target_probability": 0.006739696924}`
