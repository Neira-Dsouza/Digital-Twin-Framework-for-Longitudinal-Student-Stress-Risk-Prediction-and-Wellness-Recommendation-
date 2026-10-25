# Automated Test Execution Summary

- **Project:** STUDENT TWIN — Context-Aware Student Stress Intelligence
- **Test Framework:** pytest 9.1.1 & pytest-django 4.14.0
- **Python Version:** 3.14.6 (64-bit Windows)
- **Django Version:** 6.0.7
- **Execution Date:** 2026-10-15
- **Execution Duration:** 13.85 seconds

## Executive Summary

| Category | Count | Percentage |
| :--- | :--- | :--- |
| **Total Tests Executed** | **21** | **100.0%** |
| **Passed** | **21** | **100.0%** |
| **Failed** | **0** | **0.0%** |
| **Skipped / Blocked** | **0** | **0.0%** |

## Test Case Breakdown

| Test ID | Module | Test Case Name | Status |
| :--- | :--- | :--- | :--- |
| **TC13** | Access Control | `test_tc13_cross_student_user_isolation` | **PASS** |
| **TC14** | Access Control | `test_tc14_dashboard_authentication_and_integration` | **PASS** |
| **TC15** | Access Control | `test_tc15_csv_export_student_scoped` | **PASS** |
| **AUTH** | Authentication | `test_user_registration_and_twin_initialization` | **PASS** |
| **TC03** | Digital Twin | `test_tc03_minimum_history_gate` | **PASS** |
| **TC04** | Digital Twin | `test_tc04_history_threshold_transition` | **PASS** |
| **TC05** | Digital Twin | `test_tc05_residual_adaptation_equation` | **PASS** |
| **TC06** | Digital Twin | `test_tc06_adaptation_bounds` | **PASS** |
| **TC07** | Digital Twin | `test_tc07_prediction_chronology_no_leakage` | **PASS** |
| **TC08** | Digital Twin | `test_tc08_persistent_state_in_database` | **PASS** |
| **STATE** | Digital Twin | `test_baseline_ema_update` | **PASS** |
| **FEEDBACK**| Digital Twin | `test_directional_feedback_and_patterns` | **PASS** |
| **INTEG** | Integration | `test_full_longitudinal_adaptation_cycle` | **PASS** |
| **TC10** | Observations | `test_tc10_invalid_input_ranges_rejected` | **PASS** |
| **TC09** | Observations | `test_tc09_repeat_submission_safe` | **PASS** |
| **TC01** | Prediction | `test_tc01_valid_prediction` | **PASS** |
| **TC02** | Prediction | `test_tc02_input_schema_and_feature_contract` | **PASS** |
| **TC11** | Recommendations | `test_tc11_recommendation_traceability_and_grounding` | **PASS** |
| **SEV** | Recommendations | `test_stress_severity_classification` | **PASS** |
| **SHAP** | Explanations | `test_shap_explanation_generation` | **PASS** |
| **TC12** | Explanations | `test_tc12_missing_explanation_graceful` | **PASS** |

## Generated Evidence Artifacts

1. `testing/evidence/test-results.txt` — Raw terminal execution output log
2. `testing/evidence/test-results.xml` — JUnit XML format machine-readable report
3. `testing/evidence/test-summary.md` — This execution summary document
