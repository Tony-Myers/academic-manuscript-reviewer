# Dichotomisation, Responder Analyses and Regression to the Mean

## Purpose

This guide helps reviewers assess analyses that split continuous measurements into categories, that classify individuals as "responders" and "non-responders", or that interpret change from baseline. It covers the cost of dichotomising, data-driven cut-points, what is needed to show that individuals differ in their response to an intervention, regression to the mean, and the choice between change scores, percentage change and adjustment for baseline.

## What reviewers should look for

- Has a continuous outcome or predictor been dichotomised or grouped for analysis, and is there a justification that outweighs the loss of information?
- Was the cut-point chosen in advance, or from the data?
- Are individuals labelled responders or non-responders on the basis of observed change in a single intervention group?
- Is variation in observed change interpreted as variation in true response without a comparison with a control group or with measurement error?
- Could an improvement in a group selected for extreme baseline values be regression to the mean?
- Is a correlation between baseline and change interpreted substantively?
- In a randomised comparison, was the outcome adjusted for baseline, or analysed as change or percentage change?

## What is lost when a continuous variable is dichotomised?

Splitting a continuous variable at a cut-point treats everyone on the same side as identical and treats people just either side of the cut-point as different. The consequences are:

- **loss of information and power**: a median split of a normally distributed variable is commonly estimated to discard about a third of the information, equivalent to throwing away a third of the sample, and splits away from the median lose more;
- **a distorted relationship**: a smooth dose–response relationship is replaced by a step, and any nonlinearity is hidden;
- **residual confounding**: a dichotomised confounder is only partly adjusted for;
- **results that depend on the cut-point**, which limits comparison across studies using different thresholds.

Splitting into several groups loses less than splitting into two, but still loses information and still imposes steps. The alternative is to keep the variable continuous and, where the relationship may not be linear, model it flexibly.

```references
- cite: Altman, D. G., & Royston, P. (2006). The cost of dichotomising continuous variables. BMJ, 332(7549), 1080.
  doi: 10.1136/bmj.332.7549.1080
  supports: The loss of power, the assumption of a step relationship and the other costs of dichotomising continuous variables.
  short: the cost of dichotomising continuous variables
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: MacCallum, R. C., Zhang, S., Preacher, K. J., & Rucker, D. D. (2002). On the practice of dichotomization of quantitative variables. Psychological Methods, 7(1), 19–40.
  doi: 10.1037/1082-989X.7.1.19
  supports: The loss of information and effect size from dichotomising quantitative variables, and the rare circumstances in which it is justified.
  short: what dichotomising quantitative variables does
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Royston, P., Altman, D. G., & Sauerbrei, W. (2006). Dichotomizing continuous predictors in multiple regression: A bad idea. Statistics in Medicine, 25(1), 127–141.
  doi: 10.1002/sim.2331
  supports: Dichotomised predictors in regression, residual confounding, and the alternative of keeping variables continuous.
  short: dichotomised predictors in regression
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Are data-driven cut-points acceptable?

A cut-point chosen by examining many candidate thresholds and keeping the one that gives the smallest p-value or the largest group difference (an "optimal" cut-point) is a multiple-testing procedure. The reported p-value is too small, the effect at that threshold is overestimated, and the threshold is unlikely to be reproduced in other data.

A median split is also sample-dependent: the median differs between studies, so the "high" group in one study is not the "high" group in another.

Where a threshold is needed, for example for a clinical decision rule, it should be prespecified from external evidence or from the consequences of the decision, and the underlying analysis should still use the continuous measurement.

```references
- cite: Altman, D. G., & Royston, P. (2006). The cost of dichotomising continuous variables. BMJ, 332(7549), 1080.
  doi: 10.1136/bmj.332.7549.1080
  supports: The inflation of false-positive results from choosing an "optimal" cut-point and the sample dependence of median splits.
  short: the cost of dichotomising continuous variables
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Royston, P., Altman, D. G., & Sauerbrei, W. (2006). Dichotomizing continuous predictors in multiple regression: A bad idea. Statistics in Medicine, 25(1), 127–141.
  doi: 10.1002/sim.2331
  supports: The problems of data-derived cut-points and the case for retaining continuous predictors.
  short: dichotomised predictors in regression
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Can responders and non-responders be identified from observed changes?

Not from a single intervention group. An individual's observed change is the sum of any true effect of the intervention, random measurement error at both time points, and day-to-day biological variation unrelated to the intervention. Observed changes therefore vary between individuals even when the intervention has exactly the same effect on everyone, or no effect at all.

Classifying those whose observed change exceeds a threshold as "responders" and the rest as "non-responders" consequently labels noise. The same classification applied to an untreated control group would also produce "responders". The proportion classified depends on the threshold, the reliability of the measure and the mean effect, and is not an estimate of the proportion of people who benefit.

Reviewers should treat claims about individual response, and analyses of the characteristics of "responders", as unsupported unless the variation in true response has been separated from the variation expected without it.

```references
- cite: Senn, S. (2004). Individual response to treatment: Is it a valid assumption? BMJ, 329(7472), 966–968.
  doi: 10.1136/bmj.329.7472.966
  supports: Why variation in observed outcomes in a parallel-group trial does not show that individuals respond differently.
  short: why individual response cannot be read from a parallel-group trial
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Atkinson, G., & Batterham, A. M. (2015). True and false interindividual differences in the physiological response to an intervention. Experimental Physiology, 100(6), 577–588.
  doi: 10.1113/EP085070
  supports: How random within-subject variation produces apparent responders and non-responders, and why a comparator group is needed.
  short: separating true response differences from random variation
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Hecksteden, A., Kraushaar, J., Scharhag-Rosenberger, F., Theisen, D., Senn, S., & Meyer, T. (2015). Individual response to exercise training – a statistical perspective. Journal of Applied Physiology, 118(12), 1450–1459.
  doi: 10.1152/japplphysiol.00714.2014
  supports: The statistical requirements for claims about individual response to exercise training.
  short: individual response to exercise training
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What evidence would support individual differences in response?

Two designs can address the question.

- **Comparison with a control group.** If individuals truly differ in response, the standard deviation of the change scores should be larger in the intervention group than in the control group. The standard deviation attributable to individual response can be estimated as the square root of the difference between the two variances. If the two standard deviations are similar, the data give no evidence of individual differences in response, however variable the observed changes look. The estimate is imprecise in small studies and should be given with an interval.
- **Repeated administration.** A replicated crossover design, in which each participant receives the intervention and the control more than once, allows the participant-by-treatment interaction to be estimated directly.

A change that exceeds the measurement error for an individual (see the note on measurement reliability) shows that the individual changed. It does not show that the intervention caused the change, which again needs a comparison with what happens without it.

```references
- cite: Atkinson, G., & Batterham, A. M. (2015). True and false interindividual differences in the physiological response to an intervention. Experimental Physiology, 100(6), 577–588.
  doi: 10.1113/EP085070
  supports: Estimating the standard deviation of individual responses by comparing the variability of change in intervention and control groups.
  short: separating true response differences from random variation
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Hecksteden, A., Kraushaar, J., Scharhag-Rosenberger, F., Theisen, D., Senn, S., & Meyer, T. (2015). Individual response to exercise training – a statistical perspective. Journal of Applied Physiology, 118(12), 1450–1459.
  doi: 10.1152/japplphysiol.00714.2014
  supports: Designs, including repeated interventions, that can separate individual response from within-subject variation.
  short: individual response to exercise training
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Senn, S. (2004). Individual response to treatment: Is it a valid assumption? BMJ, 329(7472), 966–968.
  doi: 10.1136/bmj.329.7472.966
  supports: The need for repeated-treatment designs to identify individual response.
  short: why individual response cannot be read from a parallel-group trial
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What is regression to the mean?

When a variable is measured with error or fluctuates naturally, individuals who are extreme on one occasion will, on average, be less extreme on the next, with no intervention at all. This is regression to the mean. It is a statistical consequence of imperfect correlation between repeated measurements, not a biological process.

It matters whenever participants are selected, or select themselves, because of an extreme value: patients recruited when symptoms are at their worst, athletes selected for a low baseline score, or a subgroup defined by high baseline values. Such a group will tend to improve at follow-up regardless of treatment. An uncontrolled pre–post improvement in such a group cannot be attributed to the intervention.

The size of the effect is larger when the measure is less reliable and when the selection threshold is more extreme.

```references
- cite: Barnett, A. G., van der Pols, J. C., & Dobson, A. J. (2005). Regression to the mean: What it is and how to deal with it. International Journal of Epidemiology, 34(1), 215–220.
  doi: 10.1093/ije/dyh299
  supports: What regression to the mean is, when it arises, how large it can be, and how to reduce or allow for it.
  short: regression to the mean
  type: Journal article
  checked: 2026-11-13, Crossref (co-authors confirmed from the Crossref record of the published correction, 10.1093/ije/dyv161)
```

## How can regression to the mean be dealt with?

By design, where possible: a randomised concurrent control group experiences the same regression to the mean, so the between-group comparison removes it. Selecting participants on the mean of two or more baseline measurements, or on a measurement separate from the one used as the analysis baseline, reduces it.

By analysis: adjusting follow-up for baseline (analysis of covariance) in a controlled comparison accounts for it. The expected regression to the mean can also be estimated from the reliability of the measure and the selection threshold, to show how much of an uncontrolled change it could explain.

Reviewers should expect authors of uncontrolled before–after studies in selected groups to discuss regression to the mean explicitly, alongside natural history, learning effects and other explanations for change.

```references
- cite: Barnett, A. G., van der Pols, J. C., & Dobson, A. J. (2005). Regression to the mean: What it is and how to deal with it. International Journal of Epidemiology, 34(1), 215–220.
  doi: 10.1093/ije/dyh299
  supports: Design and analysis methods for limiting and quantifying regression to the mean.
  short: regression to the mean
  type: Journal article
  checked: 2026-11-13, Crossref (co-authors confirmed from the Crossref record of the published correction, 10.1093/ije/dyv161)
```

## Is a correlation between baseline and change meaningful?

Usually it is not. Change is calculated as follow-up minus baseline, so baseline appears in both variables. Measurement error in the baseline value pushes baseline and change in opposite directions, producing a negative correlation even when there is no real relationship. The finding that "those with the lowest baseline values improved the most" is therefore expected from regression to the mean alone.

The same applies to comparing change between subgroups defined by baseline level. A claim that an intervention works better in people who start lower needs a control group, so that the relationship between baseline and outcome can be compared between intervention and control, in effect a baseline-by-treatment interaction.

```references
- cite: Barnett, A. G., van der Pols, J. C., & Dobson, A. J. (2005). Regression to the mean: What it is and how to deal with it. International Journal of Epidemiology, 34(1), 215–220.
  doi: 10.1093/ije/dyh299
  supports: Why those with extreme baseline values show the largest change in the absence of any effect.
  short: regression to the mean
  type: Journal article
  checked: 2026-11-13, Crossref (co-authors confirmed from the Crossref record of the published correction, 10.1093/ije/dyv161)
```

## Should a trial be analysed with change scores, percentage change or baseline adjustment?

For a randomised comparison of a continuous outcome measured at baseline and follow-up, analysis of covariance (follow-up, or change, as the outcome with baseline as a covariate) is generally the most efficient choice. It gives a more precise estimate than comparing follow-up scores alone or comparing change scores, and it is not misled by chance baseline imbalance. Using change as the outcome with baseline as a covariate gives the same treatment estimate as using follow-up as the outcome with baseline as a covariate.

A simple comparison of change scores is valid in a randomised trial but less efficient, and loses out to a comparison of follow-up scores when the correlation between baseline and follow-up is low. It does not remove the influence of baseline imbalance.

**Percentage change from baseline** performs worst: it is statistically inefficient, its distribution is often skewed, and it behaves badly when baseline values are small. It may be reported descriptively, but should not be the basis of the primary analysis.

In non-randomised comparisons, change-score and baseline-adjusted analyses answer different questions and can disagree; neither is automatically correct, and the choice needs a causal justification.

```references
- cite: Vickers, A. J., & Altman, D. G. (2001). Statistics notes: Analysing controlled trials with baseline and follow up measurements. BMJ, 323(7321), 1123–1124.
  doi: 10.1136/bmj.323.7321.1123
  supports: Why analysis of covariance is preferred to change scores or follow-up scores alone in trials with baseline and follow-up measurements.
  short: ANCOVA compared with change scores in trials
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Vickers, A. J. (2001). The use of percentage change from baseline as an outcome in a controlled trial is statistically inefficient: A simulation study. BMC Medical Research Methodology, 1, 6.
  doi: 10.1186/1471-2288-1-6
  supports: The statistical inefficiency of percentage change from baseline.
  short: why percentage change from baseline is inefficient
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Senn, S. (2006). Change from baseline and analysis of covariance revisited. Statistics in Medicine, 25(24), 4334–4344.
  doi: 10.1002/sim.2682
  supports: Change from baseline, analysis of covariance, and why baseline adjustment remains appropriate in randomised trials.
  short: change from baseline and analysis of covariance
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Is comparing within-group changes a valid test of a group difference?

No. Reporting that the intervention group improved significantly from baseline while the control group did not is not a comparison of the groups. One within-group test can be significant and the other not when the two changes are similar, simply because of differences in variability or sample size. The comparison of interest is the between-group difference in outcome, with its confidence interval.

Within-group changes in a controlled trial also include regression to the mean, learning and natural history, which is the reason for having a control group.

```references
- cite: Gelman, A., & Stern, H. (2006). The difference between "significant" and "not significant" is not itself statistically significant. The American Statistician, 60(4), 328--331.
  doi: 10.1198/000313006X152649
  supports: Why a significant result in one group and a result that is not significant in another do not show that the groups differ.
  short: why significant versus non-significant does not establish a difference
  type: Journal article
  checked: 2026-10-03
```

## Common misconceptions

**"Dichotomising makes the results easier to interpret, at no cost."** Incorrect. It discards information, reduces power and can create or hide associations.

**"A median split is objective."** Incorrect. It is sample-dependent, and comparable across studies only by accident.

**"Some participants improved and some did not, so there are responders and non-responders."** Not established. That pattern is expected from measurement error and natural variation alone.

**"Participants with the worst baseline scores improved most, so the intervention helps them most."** Not established. That is the signature of regression to the mean.

**"Analysing change scores removes the effect of baseline differences."** Incorrect. Change scores remain related to baseline; adjustment for baseline is needed.

**"The group improved after the intervention, so the intervention worked."** Not established without a control group.

## Common reviewer red flags

- Continuous variables split at the median, tertiles or an unexplained threshold for the main analysis.
- A cut-point selected to maximise significance.
- Responder and non-responder groups defined from observed change, then compared on other characteristics.
- A responder proportion reported for the intervention group with none for the control group.
- No reference to measurement error or to the control group's variability when individual response is claimed.
- An uncontrolled pre–post improvement in a group selected for extreme baseline values.
- A negative correlation between baseline and change given a physiological interpretation.
- Percentage change used as the primary outcome.
- Separate within-group tests in place of a between-group comparison.

## Quick reviewer checklist

□ Continuous variables are analysed as continuous, or categorisation is justified.

□ Any cut-points were specified in advance.

□ Claims about individual response rest on a comparison with control-group variability or on repeated administration.

□ Regression to the mean has been considered wherever participants were selected on baseline values.

□ Relationships between baseline and change are interpreted with a control comparison.

□ Randomised comparisons adjust for baseline.

□ Conclusions about treatment effects rest on between-group comparisons.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Altman, D. G., & Royston, P. (2006). The cost of dichotomising continuous variables. BMJ, 332(7549), 1080.
  doi: 10.1136/bmj.332.7549.1080
  supports: The cost of dichotomising continuous variables.
  short: the cost of dichotomising continuous variables
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: MacCallum, R. C., Zhang, S., Preacher, K. J., & Rucker, D. D. (2002). On the practice of dichotomization of quantitative variables. Psychological Methods, 7(1), 19–40.
  doi: 10.1037/1082-989X.7.1.19
  supports: The practice and consequences of dichotomising quantitative variables.
  short: what dichotomising quantitative variables does
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Royston, P., Altman, D. G., & Sauerbrei, W. (2006). Dichotomizing continuous predictors in multiple regression: A bad idea. Statistics in Medicine, 25(1), 127–141.
  doi: 10.1002/sim.2331
  supports: Dichotomised continuous predictors in regression.
  short: dichotomised predictors in regression
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Senn, S. (2004). Individual response to treatment: Is it a valid assumption? BMJ, 329(7472), 966–968.
  doi: 10.1136/bmj.329.7472.966
  supports: Individual response to treatment in parallel-group trials.
  short: why individual response cannot be read from a parallel-group trial
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Atkinson, G., & Batterham, A. M. (2015). True and false interindividual differences in the physiological response to an intervention. Experimental Physiology, 100(6), 577–588.
  doi: 10.1113/EP085070
  supports: True and apparent individual differences in response to an intervention.
  short: separating true response differences from random variation
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Hecksteden, A., Kraushaar, J., Scharhag-Rosenberger, F., Theisen, D., Senn, S., & Meyer, T. (2015). Individual response to exercise training – a statistical perspective. Journal of Applied Physiology, 118(12), 1450–1459.
  doi: 10.1152/japplphysiol.00714.2014
  supports: A statistical perspective on individual response to exercise training.
  short: individual response to exercise training
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Barnett, A. G., van der Pols, J. C., & Dobson, A. J. (2005). Regression to the mean: What it is and how to deal with it. International Journal of Epidemiology, 34(1), 215–220.
  doi: 10.1093/ije/dyh299
  supports: Regression to the mean.
  short: regression to the mean
  type: Journal article
  checked: 2026-11-13, Crossref (co-authors confirmed from the Crossref record of the published correction, 10.1093/ije/dyv161)
- cite: Vickers, A. J., & Altman, D. G. (2001). Statistics notes: Analysing controlled trials with baseline and follow up measurements. BMJ, 323(7321), 1123–1124.
  doi: 10.1136/bmj.323.7321.1123
  supports: Analysing trials with baseline and follow-up measurements.
  short: ANCOVA compared with change scores in trials
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Vickers, A. J. (2001). The use of percentage change from baseline as an outcome in a controlled trial is statistically inefficient: A simulation study. BMC Medical Research Methodology, 1, 6.
  doi: 10.1186/1471-2288-1-6
  supports: Percentage change from baseline as an outcome.
  short: why percentage change from baseline is inefficient
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Senn, S. (2006). Change from baseline and analysis of covariance revisited. Statistics in Medicine, 25(24), 4334–4344.
  doi: 10.1002/sim.2682
  supports: Change from baseline and analysis of covariance.
  short: change from baseline and analysis of covariance
  type: Journal article
  checked: 2026-11-13, Crossref
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
