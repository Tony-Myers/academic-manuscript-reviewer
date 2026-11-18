# Crossover Trials

## Purpose

This guide helps reviewers assess randomised crossover studies, in which each participant receives two or more conditions in sequence. Crossover designs are common in exercise physiology, nutrition and pharmacology. The guide covers when the design is suitable, why the analysis must be within-participant, period effects, carryover and washout, the discredited two-stage analysis, missing periods, and reporting.

## What reviewers should look for

- Is the condition stable and are the effects of the interventions short-lived and reversible, so that a crossover design is suitable?
- Was the order of conditions randomised, and are the numbers allocated to each sequence reported?
- Is the washout period justified on physiological or pharmacological grounds?
- Does the analysis compare conditions within participants, and does it allow for period?
- Was a test for carryover used to decide how to analyse the data?
- How were participants who did not complete all periods handled?
- Could learning, familiarisation, training or seasonal change have produced order effects?

## When is a crossover design appropriate?

In a crossover trial each participant acts as their own control, so differences between participants do not contribute to the error of the treatment comparison. For outcomes that vary much more between people than within a person, this gives far greater precision per participant than a parallel-group design.

The design depends on the participant returning to the same state before each period. It suits stable conditions and interventions whose effects appear quickly and disappear completely after they are withdrawn: an acute supplement, a single exercise bout, a short-acting drug. It is unsuitable when the intervention produces lasting change, such as a training programme, a learned skill or a cure, when the condition progresses or resolves over the study, or when dropout between periods is likely to be high.

```references
- cite: Senn, S. (2002). Cross-over trials in clinical research (2nd ed.). Wiley.
  doi: 10.1002/0470854596
  supports: The rationale for crossover trials and the conditions under which they are suitable.
  short: the design and analysis of crossover trials
  type: Book
  checked: 2026-11-13, Crossref
- cite: Dwan, K., Li, T., Altman, D. G., & Elbourne, D. (2019). CONSORT 2010 statement: Extension to randomised crossover trials. BMJ, 366, l4378.
  doi: 10.1136/bmj.l4378
  supports: The reporting requirement to justify the choice of a crossover design.
  short: the CONSORT extension for crossover trials
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

## Why must the analysis be within-participant?

The two (or more) observations from one participant are correlated. The treatment effect is estimated from within-participant differences, and its precision depends on the within-participant variability.

Analysing the conditions as if they were independent groups, for example with an unpaired *t*-test or by treating each period's observations as separate participants, ignores the pairing. It misstates the precision, usually making the comparison far less precise than the design allows, and it reports the wrong degrees of freedom.

Reviewers should expect a paired analysis or a mixed model with participant as a random effect, the treatment effect reported as a within-participant difference with a confidence interval, and the within-participant standard deviation or the correlation between periods, which later studies and meta-analyses need.

```references
- cite: Senn, S. (2002). Cross-over trials in clinical research (2nd ed.). Wiley.
  doi: 10.1002/0470854596
  supports: Within-participant analysis of crossover trials.
  short: the design and analysis of crossover trials
  type: Book
  checked: 2026-11-13, Crossref
- cite: Dwan, K., Li, T., Altman, D. G., & Elbourne, D. (2019). CONSORT 2010 statement: Extension to randomised crossover trials. BMJ, 366, l4378.
  doi: 10.1136/bmj.l4378
  supports: Reporting a within-participant estimate with its precision, and the within-participant variability.
  short: the CONSORT extension for crossover trials
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

## What are period effects and how are they handled?

A period effect is a systematic difference between the first and later periods that applies whatever the treatment: familiarisation with a test, a change in fitness or the season, habituation to the laboratory, or disease progression.

Randomising participants to sequences in balanced numbers means that a period effect does not bias the treatment comparison, and including period as a term in the analysis removes it from the error. An analysis that ignores period is unbiased only if the sequences are balanced, and is less precise when a period effect exists.

In performance testing, learning effects between the first and second trials are common. Familiarisation sessions before the first period reduce them; they do not replace randomising the order.

```references
- cite: Senn, S. (2002). Cross-over trials in clinical research (2nd ed.). Wiley.
  doi: 10.1002/0470854596
  supports: Period effects and adjusting for period in the analysis of crossover trials.
  short: the design and analysis of crossover trials
  type: Book
  checked: 2026-11-13, Crossref
```

## What is carryover and why does it matter?

Carryover is the persistence of the effect of a treatment given in one period into a later period. If the first treatment is still acting when the second is measured, the comparison between treatments is biased, and in the standard two-treatment, two-period design the bias cannot be removed by analysis.

Carryover is dealt with by design. The washout period between conditions should be long enough for the effect of the earlier condition to have disappeared, and its length should be justified from what is known about the intervention: the half-life of a drug or supplement, the time course of recovery from an exercise bout, the duration of a dietary effect. "A washout of one week was used" without a rationale is not sufficient. In exercise and nutrition studies, residual fatigue, muscle damage, glycogen status, training adaptation and menstrual cycle phase can all carry over or differ between periods.

```references
- cite: Senn, S. (2002). Cross-over trials in clinical research (2nd ed.). Wiley.
  doi: 10.1002/0470854596
  supports: Carryover, washout, and why carryover must be addressed by design.
  short: the design and analysis of crossover trials
  type: Book
  checked: 2026-11-13, Crossref
- cite: Dwan, K., Li, T., Altman, D. G., & Elbourne, D. (2019). CONSORT 2010 statement: Extension to randomised crossover trials. BMJ, 366, l4378.
  doi: 10.1136/bmj.l4378
  supports: The reporting requirement to describe and justify the washout period and to consider carryover.
  short: the CONSORT extension for crossover trials
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

## Should carryover be tested before choosing the analysis?

No. An older two-stage procedure tested for carryover and, if the test was significant, discarded the second period and analysed the first period as a parallel-group trial. This procedure is unsound and should not be used.

The test for carryover in a two-period design compares participants between sequences, so it has low power and will usually miss carryover large enough to matter. And because the choice of final analysis depends on the result of a preliminary test, the overall procedure does not control the Type I error rate at its nominal level; the first-period analysis chosen after a significant pre-test is biased.

A carryover test that is not significant is therefore not evidence that carryover was absent. The case against carryover has to be made from the washout and the pharmacology or physiology.

```references
- cite: Freeman, P. R. (1989). The performance of the two-stage analysis of two-treatment, two-period crossover trials. Statistics in Medicine, 8(12), 1421–1432.
  doi: 10.1002/sim.4780081202
  supports: Why the two-stage analysis that pre-tests for carryover has an inflated error rate and should not be used.
  short: why pre-testing for carryover is unsound
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Senn, S. (2002). Cross-over trials in clinical research (2nd ed.). Wiley.
  doi: 10.1002/0470854596
  supports: The low power of the carryover test and the case for dealing with carryover by design.
  short: the design and analysis of crossover trials
  type: Book
  checked: 2026-11-13, Crossref
```

## How should incomplete participants be handled?

Participants who complete only the first period contribute no within-participant comparison. Excluding them is a complete-case analysis and can bias the result if dropout is related to the treatment received first or to the response to it, for example withdrawal after an adverse reaction.

Reviewers should expect the number of participants randomised to each sequence, the number completing each period, and the reasons for withdrawal by sequence and period. A mixed model can use the available data from incomplete participants under a missing-at-random assumption, which should be stated and, where dropout is appreciable, examined in a sensitivity analysis. See the note on missing data.

```references
- cite: Dwan, K., Li, T., Altman, D. G., & Elbourne, D. (2019). CONSORT 2010 statement: Extension to randomised crossover trials. BMJ, 366, l4378.
  doi: 10.1136/bmj.l4378
  supports: Reporting participant flow by sequence and period and the handling of participants who did not complete all periods.
  short: the CONSORT extension for crossover trials
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

## What should a crossover trial report?

In addition to what is expected of any randomised trial:

- the rationale for a crossover design and the design used (number of treatments, periods and sequences);
- how the order was randomised, and the numbers allocated to each sequence;
- the length of the washout and its justification;
- the analysis, stating that it is within-participant and how period was handled;
- the treatment effect as a within-participant difference with a confidence interval, and a measure of within-participant variability;
- participant flow, losses and exclusions by sequence and period;
- a sample size calculation based on the within-participant standard deviation or the between-period correlation, not on between-participant variability.

```references
- cite: Dwan, K., Li, T., Altman, D. G., & Elbourne, D. (2019). CONSORT 2010 statement: Extension to randomised crossover trials. BMJ, 366, l4378.
  doi: 10.1136/bmj.l4378
  supports: The CONSORT extension checklist for randomised crossover trials.
  short: the CONSORT extension for crossover trials
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

## Common misconceptions

**"The carryover test was not significant, so there was no carryover."** Incorrect. The test has low power, and absence of evidence is not evidence of absence.

**"Each participant did both conditions, so the sample size is doubled."** Incorrect. The number of independent units is the number of participants. The gain in precision comes from removing between-participant variability, not from extra participants.

**"Randomising the order removes carryover."** Incorrect. Balanced randomisation deals with period effects. Carryover that differs between treatments still biases the comparison.

**"Familiarisation trials make order irrelevant."** Incorrect. They reduce learning effects but do not guarantee their absence; the order should still be randomised and period included in the analysis.

**"A crossover design is always more efficient."** Not always. Where effects persist, the condition is unstable or dropout is high, a parallel-group design is the sound choice.

## Common reviewer red flags

- Conditions analysed as independent groups.
- Order of conditions not randomised, or sequence allocation not reported.
- Washout length stated without justification, or no washout.
- A crossover design used for an intervention with lasting effects, such as training.
- A pre-test for carryover used to choose the analysis, or first-period data analysed alone after a significant pre-test.
- Period not considered in the analysis.
- Participants who missed a period excluded without comment.
- No within-participant variability reported.
- Sample size calculated as for a parallel-group trial.

## Quick reviewer checklist

□ The design suits the condition and the intervention.

□ Order was randomised and sequence numbers are reported.

□ The washout is justified.

□ The analysis is within-participant and allows for period.

□ Carryover is addressed by design and argument, not by a pre-test.

□ Incomplete participants are reported and handled appropriately.

□ The effect is reported as a within-participant difference with a confidence interval.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Senn, S. (2002). Cross-over trials in clinical research (2nd ed.). Wiley.
  doi: 10.1002/0470854596
  supports: The design and analysis of crossover trials.
  short: the design and analysis of crossover trials
  type: Book
  checked: 2026-11-13, Crossref
- cite: Dwan, K., Li, T., Altman, D. G., & Elbourne, D. (2019). CONSORT 2010 statement: Extension to randomised crossover trials. BMJ, 366, l4378.
  doi: 10.1136/bmj.l4378
  supports: The CONSORT 2010 extension for randomised crossover trials.
  short: the CONSORT extension for crossover trials
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
- cite: Freeman, P. R. (1989). The performance of the two-stage analysis of two-treatment, two-period crossover trials. Statistics in Medicine, 8(12), 1421–1432.
  doi: 10.1002/sim.4780081202
  supports: The performance of the two-stage analysis of two-period crossover trials.
  short: why pre-testing for carryover is unsound
  type: Journal article
  checked: 2026-11-13, Crossref
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
