# Autoencoder TODO List

These TODOs were generated from autoencoder introspection and claimed from the supervisor queue.

- Queue run: `uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder`
- Queue path: `/home/barberb/portland-laws.github.io/workspace/todo-queues/uscode-modal-vector-5scope-1h-20260518T191418Z-autoencoder.jsonl`
- TODO count: `3`

## TODOs
- `program-79dedd6562972547`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-79dedd6562972547` score `1.0`
  loss: `autoencoder_residual_cluster` = `0.488529770497`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-15-145-7b620ef453a3c3c7, us-code-43-270-9753303f57791aad, us-code-7-1631-2e645b217b50b0bc, us-code-31-5312-039372e5e9300b7d`
  evidence: `{"frame_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing", "flogic:candidate_ontology_term:agency"], "hint_id": "modal-synthesis-4af847abc9a13d99", "priority": 0.439265081335, "sample_id": "us-code-7-1631-2e645b217b50b0bc"}`
  evidence: `{"frame_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing", "flogic:candidate_ontology_term:agency"], "hint_id": "modal-synthesis-5fc536942ae8bfb8", "priority": 0.678445187698, "sample_id": "us-code-15-145-7b620ef453a3c3c7"}`
  evidence: `{"frame_features": ["family:selected_frame:conditional_normative", "flogic:citation_section_number_has_zero_digit:true", "flogic:citation_section_number_has_zero_digit_positioned:1:true", "flogic:citation_section_number_zero_digit_count:1", "flogic:citation_section_number_zero_digit_count_positioned:1:1", "flogic:citation_section_primary_number_has_zero_digit:true", "flogic:citation_section_primary_number_zero_digit_count:1"], "hint_id": "modal-synthesis-b75d872d8ce1f1c8", "priority": 0.644212582322, "sample_id": "us-code-43-270-9753303f57791aad"}`
  evidence: `{"frame_features": ["family:selected_frame:conditional_normative", "family:selected_frame:deontic", "flogic:citation_title_number_has_zero_digit:false", "flogic:citation_title_number_trailing_zero_count:0", "flogic:citation_title_number_zero_digit_count:0"], "hint_id": "modal-synthesis-ecdb84245c2ea832", "priority": 0.192196230632, "sample_id": "us-code-31-5312-039372e5e9300b7d"}`
- `program-23c89f652bdd38da`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-79dedd6562972547` score `0.979245`
  loss: `autoencoder_residual_cluster` = `0.470306733794`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-5-8464a-7b232fae83466b72, us-code-10-508-3c4daeb3fdaf30d2, us-code-7-8758-6c50bb2c1676bbf9, us-code-2-1516-e49d03132a8b32ab`
  evidence: `{"frame_features": ["family:selected_frame:temporal", "flogic:candidate_ontology_frame:administrative_notice_hearing", "flogic:candidate_ontology_frame:criminal_penalty_enforcement", "flogic:candidate_ontology_frame:housing_voucher_benefits", "flogic:candidate_ontology_term:accommodation", "flogic:candidate_ontology_term:administrative", "flogic:candidate_ontology_term:administrative_notice_hearing", "flogic:candidate_ontology_term:agency"], "hint_id": "modal-synthesis-7bbd1502a3c3eeea", "priority": 0.582112001088, "sample_id": "us-code-5-8464a-7b232fae83466b72"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_parity:even", "flogic:citation_section_number_parity_positioned:1:even", "flogic:citation_section_primary_number_parity:even", "flogic:citation_section_terminal_number_parity:even", "flogic:predicate_token_count:1", "flogic:source_id_section_number_parity:even"], "hint_id": "modal-synthesis-b6819ce63d27c4dd", "priority": 0.531739974903, "sample_id": "us-code-10-508-3c4daeb3fdaf30d2"}`
  evidence: `{"frame_features": ["flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_number_has_zero_digit:false", "flogic:citation_section_number_has_zero_digit_positioned:1:false", "flogic:citation_section_number_zero_digit_count:0", "flogic:citation_section_number_zero_digit_count_positioned:1:0", "flogic:citation_section_primary_number_has_zero_digit:false", "flogic:citation_section_primary_number_zero_digit_count:0", "flogic:citation_section_punctuation_style:clean"], "hint_id": "modal-synthesis-c4c24824423b62cf", "priority": 0.371278499662, "sample_id": "us-code-2-1516-e49d03132a8b32ab"}`
  evidence: `{"frame_features": ["flogic:citation_title_section_primary_number_span_trailing_zero_count:0", "flogic:citation_title_section_terminal_number_span_trailing_zero_count:0", "flogic:source_id_title_section_primary_number_span_trailing_zero_count:0", "flogic:source_id_title_section_terminal_number_span_trailing_zero_count:0"], "hint_id": "modal-synthesis-ecf6c577a6e17e92", "priority": 0.396096459524, "sample_id": "us-code-7-8758-6c50bb2c1676bbf9"}`
- `program-b6c496f09caa14d6`
  action: `audit_frame_logic_terms`
  role: `program_synthesis`
  target: `modal.frame_logic`
  scope: `frame_logic`
  bundle: `{"action":"audit_frame_logic_terms","family_pairs":[],"program_synthesis_scope":"frame_logic","target_component":"modal.frame_logic"}`
  vector_bundle: `program-79dedd6562972547` score `0.886619`
  loss: `autoencoder_residual_cluster` = `0.469643336594`
  objective: Frame-linked features influenced reconstruction or family scoring and should be audited as ontology terms.
  samples: `us-code-34-11294-0a6981caa505e06b, us-code-29-1662-e7516434dca445ba, us-code-22-2078-b00052cd8a98ed8d, us-code-16-831r-67ffc5b229e2bd75`
  evidence: `{"frame_features": ["flogic:citation_title_section_primary_number_span_trailing_zero_count:0", "flogic:citation_title_section_terminal_number_span_trailing_zero_count:0", "flogic:source_id_title_section_primary_number_span_trailing_zero_count:0", "flogic:source_id_title_section_terminal_number_span_trailing_zero_count:0"], "hint_id": "modal-synthesis-3acb7d981400aaf7", "priority": 0.319096629099, "sample_id": "us-code-16-831r-67ffc5b229e2bd75"}`
  evidence: `{"frame_features": ["flogic:citation_section_number_leading_digit:1", "flogic:citation_section_number_leading_digit_positioned:1:1", "flogic:citation_section_primary_number_leading_digit:1", "flogic:citation_section_terminal_number_leading_digit:1", "flogic:citation_title_section_primary_number_span_leading_digit:1", "flogic:citation_title_section_primary_number_span_trailing_zero_count:1", "flogic:citation_title_section_terminal_number_span_leading_digit:1", "flogic:citation_title_section_terminal_number_span_trailing_zero_count:1"], "hint_id": "modal-synthesis-52fb504bd7417057", "priority": 0.687328500451, "sample_id": "us-code-34-11294-0a6981caa505e06b"}`
  evidence: `{"frame_features": ["flogic:citation_section_has_trailing_punct:false", "flogic:citation_section_punctuation_style:clean", "flogic:citation_section_style:single_numeric_clean", "flogic:citation_section_style_alnum_segment:clean", "flogic:citation_section_style_alnum_segment_count:3", "flogic:citation_section_style_alnum_segment_positioned:3:clean", "flogic:citation_section_style_alnum_segment_suffix:clean"], "hint_id": "modal-synthesis-9c269afe2510d2c3", "priority": 0.407276740782, "sample_id": "us-code-22-2078-b00052cd8a98ed8d"}`
  evidence: `{"frame_features": ["flogic:citation_title_section_primary_number_span_has_zero_digit:false", "flogic:citation_title_section_primary_number_span_zero_digit_count:0", "flogic:citation_title_section_terminal_number_span_has_zero_digit:false", "flogic:citation_title_section_terminal_number_span_zero_digit_count:0", "flogic:source_id_title_section_primary_number_span_has_zero_digit:false", "flogic:source_id_title_section_primary_number_span_zero_digit_count:0", "flogic:source_id_title_section_terminal_number_span_has_zero_digit:false", "flogic:source_id_title_section_terminal_number_span_zero_digit_count:0"], "hint_id": "modal-synthesis-f2e558f0c1662e74", "priority": 0.464871476043, "sample_id": "us-code-29-1662-e7516434dca445ba"}`
