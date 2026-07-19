# Quant Decision Portfolio

Private workspace for developing reproducible projects in business analytics, decision science, and data engineering.

This repository is not the final public showcase. It is the workspace where I turn scattered coursework, research, and internship materials into reproducible analytical projects that I can explain clearly.

## North Star

I try to approach every project the same way: start with a business question, build the data, test the analysis, and understand the decision.

The goal is to make each project reproducible, interpretable, and grounded in a real analytical question.

## Project Workflow

```text
Idea
-> Business question
-> Literature or business context
-> Data collection or reconstruction
-> Cleaning and validation
-> Exploratory analysis
-> Feature engineering
-> Model or analytical method
-> Evaluation and robustness checks
-> Project README
-> Public repository
```

## Repository Structure

```text
quant-decision-portfolio/
├── python-basics/              # pandas, visualization, regression, backtesting drills
├── sql-basics/                 # joins, aggregations, windows, funnel/cohort query drills
├── project-drills/
│   ├── industry-rotation/      # financial decision analytics
│   ├── a-share-quadrant-rotation/ # A-share industry quadrant reconstruction
│   ├── esg-disclosure/         # ESG data engineering and completeness analysis
│   └── trade-policy-did/       # panel data and DID analysis
├── templates/                  # reusable README and project documentation templates
└── notes/                      # learning notes, assumptions, and project decisions
```

## Skill Targets

### Python

- Data ingestion and inspection
- Data cleaning and transformation
- Feature construction
- Time-series analysis
- Visualization
- Regression
- Backtesting

### SQL

- Relational querying and filtering
- Joins and subqueries
- Aggregation and KPI logic
- CASE WHEN feature construction
- CTE-based query organization
- Window functions
- Funnel and cohort analysis
- Reproducible reporting queries

### Applied Methods

#### Data Engineering

- Missingness analysis
- Completeness scoring
- Indicator dictionaries
- Data validation

#### Statistical Modeling

- Regression
- Panel data
- Difference-in-differences
- Robustness checks

#### Decision Analytics

- Financial backtesting
- Performance evaluation
- Signal construction
- Scenario comparison

#### Behavioral Analytics

- Survey analysis
- Mediation analysis
- Adoption and trust modeling

## Public Project Pipeline

Work should only move from this private lab to a public repository when it satisfies the checklist:

- Use only public, synthetic, or properly anonymized data.
- Remove confidential company materials, tokens, private reports, and third-party restricted files.
- Document the question, data, methods, results, role, and limitations.
- Ensure notebooks or scripts can be rerun.
- Generate reproducible figures and tables.
- Explain every design decision without relying on AI output as a black box.

## Planned Public Repositories

### `industry-rotation-backtest`

Objective: Reconstruct an industry rotation strategy using public data.

Deliverables: Signal construction notebook, backtesting report, performance metrics, robustness checks.

Methods: Python, pandas, time-series analysis, backtesting.

### `a-share-quadrant-rotation`

Objective: Reconstruct an A-share industry quadrant framework using prosperity and valuation signals.

Deliverables: Quadrant signal pipeline, weekly rotation backtest, latest quadrant distribution, migration analysis.

Methods: Rolling percentiles, PE/PB valuation scoring, prosperity scoring, weekly backtesting.

Release note: This remains private until the input data is replaced by public, synthetic, or properly anonymized data.

### `esg-disclosure-analytics`

Objective: Build an ESG disclosure dataset and evaluate disclosure completeness.

Deliverables: Indicator dictionary, completeness scoring, missingness heatmap, firm and industry comparison.

Methods: Data cleaning, indicator design, missingness analysis, visualization.

### `trade-policy-did-analysis`

Objective: Evaluate policy impact using panel data and difference-in-differences.

Deliverables: Model assumptions, regression tables, robustness diagnostics, limitations note.

Methods: Panel data, DID, regression, robustness checks.

## Working Principle

Every project should be reproducible, interpretable, and explainable.

If I cannot explain the data, assumptions, methodology, results, and limitations, then I do not yet understand the project well enough.
