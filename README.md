# Quant Decision Portfolio

Private working lab for rebuilding applied quantitative skills and preparing a decision analytics portfolio for graduate applications.

This repository is not the final public showcase. It is the workspace where I turn scattered coursework, research, and internship materials into reproducible analytical projects that I can explain clearly.

## North Star

Business problems -> structured data -> analytical models -> evidence-based decisions.

The goal is to build projects that show applied quantitative reasoning in business systems, not coding for its own sake.

## Repository Structure

```text
quant-decision-portfolio/
├── python-basics/              # pandas, visualization, regression, backtesting drills
├── sql-basics/                 # joins, aggregations, windows, funnel/cohort query drills
├── project-drills/
│   ├── industry-rotation/      # financial decision analytics
│   ├── esg-disclosure/         # ESG data engineering and completeness analysis
│   └── trade-policy-did/       # panel data and DID analysis
├── templates/                  # reusable README and project documentation templates
└── notes/                      # learning notes, assumptions, and project decisions
```

## Skill Targets

### Python

- read and inspect CSV / Excel data
- clean missing values and inconsistent labels
- merge, group, pivot, and reshape data
- construct rolling indicators
- visualize trends and distributions
- run basic regression models
- compute backtest metrics

### SQL

- select, where, group by, order by
- joins and subqueries
- case when logic
- common table expressions
- window functions
- funnel and cohort analysis patterns

### Applied Methods

- financial backtesting
- performance evaluation
- missingness and completeness analysis
- panel data regression
- difference-in-differences
- survey and mediation analysis

## Public Project Pipeline

Work should only move from this private lab to a public repository when it satisfies the checklist:

- the data source is public, synthetic, or properly anonymized
- no internal company files, tokens, private reports, or third-party confidential materials are included
- the README explains the question, data, method, result, role, and limitations
- notebooks or scripts can be rerun
- figures and tables can be reproduced
- I can explain the assumptions, code, results, and limitations without relying on AI output as a black box

## Planned Public Repositories

1. `industry-rotation-backtest`
   - public-data reconstruction of an industry rotation strategy
   - signal construction, backtesting, performance metrics, robustness checks

2. `esg-disclosure-analytics`
   - ESG disclosure data engineering and completeness analysis
   - indicator dictionary, missingness heatmap, firm / industry comparison

3. `trade-policy-did-analysis`
   - panel-data project using DID for policy impact evaluation
   - model assumptions, regression tables, robustness diagnostics

## Working Principle

Every project should be reproducible, interpretable, and explainable.

If I cannot explain the data, assumptions, methodology, results, and limitations, then I do not yet understand the project well enough.
