# Strategy: PulseBoard

## Strategic Options
- **Option A: Automated Reconciliation First** - Build the ERP/demand-plan reconciliation engine first, treat alerting as a phase-2 layer on top of clean data.
- **Option B: Noise-Reduced Alerting First** - Focus on rebuilding planner trust with a low-noise, high-precision alert system, treating reconciliation as a background improvement rather than the headline feature.
- **Option C: Full Planning Suite** - Replace the planners' spreadsheet workflow entirely with an integrated planning and alerting suite, competing directly with larger ERP-adjacent platforms.

## Option Evaluation

| Criterion (weight) | Option A: Automated Reconciliation First | Option B: Noise-Reduced Alerting First | Option C: Full Planning Suite |
|---|---|---|---|
| Impact on North Star (x3) | 4 | 5 | 5 |
| Feasibility (x2, lower is better) | 2 | 2 | 5 |
| Time to Value (x2) | 4 | 5 | 1 |
| Risk (x1, lower is better) | 2 | 2 | 5 |
| **Weighted Total** | 30 | 34 | 20 |

## Strategic Bets
- We will build noise-reduced alerting first (Option B, the top-scoring option) because Priya's interview and the Q2 support tickets both point to alert trust - not raw detection capability - as the reason planners revert to manual checking [source: inputs/interviews/priya_planner_2026-07-10.md].
- If we ship alerts planners actually trust, we believe manual reconciliation time will drop because planners will stop double-checking the system's numbers by hand.
- We will still invest in reconciliation accuracy as a supporting workstream, since noisy alerts are often a symptom of the same underlying data mismatches identified in discovery.

## Success Metrics
- Weekly active planners who act on an alert without first manually verifying it in a spreadsheet
- Reduction in stockout-driven expedite shipments per quarter (ties to vision's north star metric)
- Alert precision rate (true positives / total alerts fired)

## Competitive Positioning
PulseBoard positions against the current workaround - manual spreadsheet
reconciliation - rather than existing enterprise ERP suites; per the
secondary research, the segment's adoption blocker is trust in automation,
not lack of an integrated suite, so competing on "more complete platform"
(Option C) would answer a question this segment isn't actually asking [source: inputs/secondary_research/gartner_supply_chain_visibility_2026.md].

## Constraints
- Team can ship one major workstream at a time this year - reconciliation and alerting cannot both be first-class investments in v1
- No dedicated data science headcount yet for advanced anomaly detection - alert logic must be explainable with simple, auditable rules per the SME's note that planners ignore alerts they can't verify by eye
