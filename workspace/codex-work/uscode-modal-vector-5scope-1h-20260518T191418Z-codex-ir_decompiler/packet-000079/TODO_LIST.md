# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `1`

## TODOs
- `program-854101de191057d0`
  action: `refine_typed_ir_or_decompiler_slots`
  role: `program_synthesis`
  target: `modal.ir_decompiler`
  scope: `ir_decompiler`
  bundle: `{"action":"refine_typed_ir_or_decompiler_slots","family_pairs":[],"program_synthesis_scope":"ir_decompiler","target_component":"modal.ir_decompiler"}`
  vector_bundle: `program-854101de191057d0` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.488529770497`
  objective: Embedding residuals point to information not well represented by the typed IR/decompiler.
  samples: `us-code-15-145-7b620ef453a3c3c7, us-code-43-270-9753303f57791aad, us-code-7-1631-2e645b217b50b0bc, us-code-31-5312-039372e5e9300b7d`
  evidence: `{"cosine_similarity": -0.698783049386, "hint_id": "modal-synthesis-6f89b54f6f6e6ca6", "priority": 0.644212582322, "reconstruction_loss": 0.644212582322, "sample_id": "us-code-43-270-9753303f57791aad", "top_embedding_features": ["cue:temporal:X:after", "family:selected_frame:conditional_normative", "flogic:citation_section_number_has_zero_digit:true", "flogic:citation_section_number_has_zero_digit_positioned:1:true", "flogic:citation_section_number_zero_digit_count:1", "flogic:citation_section_number_zero_digit_count_positioned:1:1", "flogic:citation_section_primary_number_has_zero_digit:true", "flogic:citation_section_primary_number_zero_digit_count:1"]}`
  evidence: `{"cosine_similarity": 0.158722281683, "hint_id": "modal-synthesis-bcce3ca1e1208bbc", "priority": 0.192196230632, "reconstruction_loss": 0.192196230632, "sample_id": "us-code-31-5312-039372e5e9300b7d", "top_embedding_features": ["cue:conditional_normative:O|:if", "cue:deontic:O:shall", "cue:temporal:X:after", "family:selected_frame:conditional_normative", "family:selected_frame:deontic", "flogic:citation_title_number_has_zero_digit:false", "flogic:citation_title_number_trailing_zero_count:0", "flogic:citation_title_number_zero_digit_count:0"]}`
  evidence: `{"cosine_similarity": 0.054394529742, "hint_id": "modal-synthesis-dfc14997de6571da", "priority": 0.439265081335, "reconstruction_loss": 0.439265081335, "sample_id": "us-code-7-1631-2e645b217b50b0bc", "top_embedding_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing", "flogic:candidate_ontology_term:agency"]}`
  evidence: `{"cosine_similarity": -0.306155516144, "hint_id": "modal-synthesis-f687106fc30206f9", "priority": 0.678445187698, "reconstruction_loss": 0.678445187698, "sample_id": "us-code-15-145-7b620ef453a3c3c7", "top_embedding_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing", "flogic:candidate_ontology_term:agency"]}`
