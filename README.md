# RateCycle India Nepal

Predicting interest rate cycles under political and macroeconomic uncertainty: an explainable machine learning study of India and Nepal, built for a macroeconomics course and designed to research publication standards.

## Status

Planning stage. No data has been downloaded and no model has been trained. Nothing in this repository is yet an empirical result.

## Where to start

* `docs/implementation_plan.md`: practicality assessment, architecture, targets, overfitting and underfitting methodology, the policy suggestion engine, the five year blind test, dashboard design and step gates.
* `docs/research_protocol.md`: research questions, hypotheses and the blind test protocol.
* `docs/literature_review.md` and `docs/literature_matrix.csv`: search strategy and screening log.
* `docs/variable_log.md` and `data/source_registry/variable_registry.csv`: every variable considered, used or excluded, with reasons.
* `docs/decision_log.md`: methodological decisions and why they were made.

## Principles

* Zero cost: open source software, free official data, runs on a laptop without a GPU.
* No leakage: every feature is joined on its publication date, and the last five years are sealed until a preregistered configuration is committed.
* Prediction, causal inference and simulation are kept separate and labelled separately.

## Repository layout

```
configs/      experiment and blind test configuration
data/         source_registry, raw (immutable), interim, processed, events, external
docs/         plan, protocol, literature, logs
src/          ingestion, validation, events, features, models, policy, econometrics, simulation, evaluation, visualization
app/          Streamlit dashboard
tests/        automated tests
reports/      figures, tables, manuscript
```
