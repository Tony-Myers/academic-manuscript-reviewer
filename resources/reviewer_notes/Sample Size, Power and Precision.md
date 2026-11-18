# Sample Size, Power and Precision

## Purpose

This guide helps reviewers assess how a study's sample size was justified and what the achieved sample size allows the authors to conclude. It covers a priori power analysis, the choice of the effect size used for planning, planning for precision, post-hoc power, the consequences of low power for the findings that do reach significance, sequential designs, and Bayesian approaches to sample size. It applies to frequentist and Bayesian studies.

## What reviewers should look for

- Is there a sample size justification, and was it made before the data were collected?
- Is the target effect size justified on substantive grounds, rather than taken from a benchmark, a pilot study or a single published estimate?
- Does the calculation match the primary outcome, the design and the analysis actually used?
- Are attrition, clustering, repeated measurements and multiple primary outcomes reflected in the calculation?
- Is enough detail given (effect size, variability, alpha, power, test, software) for the calculation to be reproduced?
- Is post-hoc or "observed" power used to interpret a result that is not significant?
- Where the sample is small, are the conclusions limited to what the precision of the estimates supports?

## What is statistical power?

Statistical power is the probability that a test will reject the null hypothesis when a specified alternative is true. It is a property of a planned procedure: it depends on the assumed true effect, the variability of the outcome, the sample size, the alpha level, the design and the analysis.

Power is therefore always power *to detect a stated effect*. A study does not have "80% power" in the abstract; it has 80% power for one assumed effect size and less for any smaller effect. Reviewers should expect the assumed effect and its justification to be stated alongside the power figure.

Power is not the probability that a significant result is true, and it is not a property of the observed data.

```references
- cite: Lakens, D. (2022). Sample size justification. Collabra: Psychology, 8(1), 33267.
  doi: 10.1525/collabra.33267
  supports: What a sample size justification is and the forms it can take.
  short: ways of justifying a sample size
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Maxwell, S. E., Kelley, K., & Rausch, J. R. (2008). Sample size planning for statistical power and accuracy in parameter estimation. Annual Review of Psychology, 59, 537–563.
  doi: 10.1146/annurev.psych.59.103006.093735
  supports: Power as a planning quantity that depends on the assumed effect, variability, alpha and design.
  short: planning sample size for power or for precision
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What should a sample size justification contain?

A reproducible a priori power analysis states:

- the primary outcome and the comparison or parameter of interest;
- the effect size the study was designed to detect, on a stated scale, with its justification;
- the assumed variability (and, for paired or repeated designs, the assumed correlation), with its source;
- the alpha level, whether the test is one- or two-sided, and the target power;
- the statistical test or model the calculation is based on;
- the allowance for attrition or exclusions;
- the software or method used.

Power analysis is not the only acceptable justification. A study may plan for the precision of an estimate, may be limited by the available population or resources, or may use a prespecified sequential design. What matters is that the justification is stated honestly and that the conclusions are in proportion to it. A sample that was fixed by resources should be described as such, with a statement of which effects the study could and could not detect or estimate usefully.

```references
- cite: Lakens, D. (2022). Sample size justification. Collabra: Psychology, 8(1), 33267.
  doi: 10.1525/collabra.33267
  supports: The components of a sample size justification, and justifications other than power analysis, including resource constraints.
  short: ways of justifying a sample size
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Abt, G., Boreham, C., Davison, G., Jackson, R., Nevill, A., Wallace, E., & Williams, M. (2020). Power, precision, and sample size estimation in sport and exercise science research. Journal of Sports Sciences, 38(17), 1933–1935.
  doi: 10.1080/02640414.2020.1776002
  supports: The expectation that sport and exercise science manuscripts justify their sample size by power or precision.
  short: sample size expectations in sport and exercise science
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Which effect size should the calculation use?

The most defensible target is the smallest effect that would matter in practice or in theory: the smallest effect size of interest. A study powered for that effect is informative whichever way it turns out.

Three common choices are weaker.

- **A published estimate.** Published effects are on average inflated, because studies that happened to observe large effects were more likely to reach significance and be published. Powering a study for a published estimate tends to produce an underpowered study.
- **A pilot-study estimate.** A pilot study estimates the effect too imprecisely to plan from. Proceeding only when the pilot effect is large adds a further selection bias.
- **A conventional benchmark.** "A medium effect, d = 0.5" is a convention, not a justification. It says nothing about what matters for the outcome and population in question.

Pilot data are more useful for estimating variability, recruitment and attrition than for estimating the effect.

```references
- cite: Albers, C., & Lakens, D. (2018). When power analyses based on pilot data are biased: Inaccurate effect size estimators and follow-up bias. Journal of Experimental Social Psychology, 74, 187–195.
  doi: 10.1016/j.jesp.2017.09.004
  supports: Why effect sizes from pilot studies give biased power analyses, and follow-up bias.
  short: why pilot-study effect sizes bias power analyses
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Lakens, D. (2022). Sample size justification. Collabra: Psychology, 8(1), 33267.
  doi: 10.1525/collabra.33267
  supports: Basing the calculation on the smallest effect size of interest rather than an expected or published effect.
  short: ways of justifying a sample size
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Button, K. S., Ioannidis, J. P. A., Mokrysz, C., et al. (2013). Power failure: Why small sample size undermines the reliability of neuroscience. Nature Reviews Neuroscience, 14(5), 365–376.
  doi: 10.1038/nrn3475
  supports: Why published effect estimates from small studies tend to be inflated.
  short: how low power undermines the reliability of findings
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Is post-hoc or observed power informative?

No. Power calculated after the study from the observed effect size ("observed", "post-hoc" or "retrospective" power) adds nothing to the p-value. For a given test it is a direct function of the p-value: a non-significant result always corresponds to low observed power, and a result exactly at p = 0.05 corresponds to observed power of about 50%.

Observed power therefore cannot explain a non-significant result or show that a study was "adequately powered". Statements such as "the non-significant finding may reflect low power (observed power = 0.31)" are circular.

What is informative after the study is the confidence or credible interval, which shows the effect sizes the data are compatible with, and, where a claim of no meaningful effect is intended, an equivalence test or a comparison of the interval with a prespecified smallest effect of interest. Power for a *prespecified* effect of interest can still be reported after the fact, because it does not depend on the observed estimate.

```references
- cite: Hoenig, J. M., & Heisey, D. M. (2001). The abuse of power: The pervasive fallacy of power calculations for data analysis. The American Statistician, 55(1), 19–24.
  doi: 10.1198/000313001300339897
  supports: Why power calculated from the observed effect is a function of the p-value and cannot aid interpretation.
  short: why post hoc power does not explain a non-significant result
  type: Journal article
  access: subscription
  access_checked: 2026-10-01, OpenAlex: closed
  checked: 2026-09-30, Crossref
```

## What happens to the findings of an underpowered study?

Low power does more than raise the chance of missing a true effect.

- **Exaggeration (Type M error).** When power is low, an estimate can reach significance only if it is much larger than the true effect. Significant findings from small studies are therefore, on average, overestimates, sometimes several-fold.
- **Wrong direction (Type S error).** With very low power, a significant estimate has an appreciable chance of having the wrong sign.
- **Lower credibility of positive findings.** For a given prior plausibility of the hypotheses being tested, the proportion of significant results that reflect true effects falls as power falls.

A significant result from a small study is therefore not stronger evidence because it was "found despite the small sample". The opposite reasoning applies: the estimate is likely to be inflated and deserves replication before it is relied on.

```references
- cite: Gelman, A., & Carlin, J. (2014). Beyond power calculations: Assessing Type S (sign) and Type M (magnitude) errors. Perspectives on Psychological Science, 9(6), 641–651.
  doi: 10.1177/1745691614551642
  supports: Type S (sign) and Type M (magnitude) errors and design calculations after the study.
  short: Type S (sign) and Type M (magnitude) errors
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Button, K. S., Ioannidis, J. P. A., Mokrysz, C., et al. (2013). Power failure: Why small sample size undermines the reliability of neuroscience. Nature Reviews Neuroscience, 14(5), 365–376.
  doi: 10.1038/nrn3475
  supports: How low power lowers the proportion of significant findings that are true and inflates their estimates.
  short: how low power undermines the reliability of findings
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What is planning for precision?

Where the aim is estimation rather than a decision about a null hypothesis, the sample size can be chosen so that the confidence or credible interval for the quantity of interest will be acceptably narrow. This is sometimes called accuracy in parameter estimation.

A precision-based justification states the target interval width, why that width is narrow enough for the purpose, the assumed variability, and the probability of achieving the target width (an interval's width varies from sample to sample, so planning for the expected width alone achieves it only about half the time).

Precision planning suits descriptive, reliability, validation and many observational studies, where "power to detect an effect" is not the natural question.

```references
- cite: Maxwell, S. E., Kelley, K., & Rausch, J. R. (2008). Sample size planning for statistical power and accuracy in parameter estimation. Annual Review of Psychology, 59, 537–563.
  doi: 10.1146/annurev.psych.59.103006.093735
  supports: Sample size planning for accuracy in parameter estimation, as distinct from power.
  short: planning sample size for power or for precision
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Abt, G., Boreham, C., Davison, G., Jackson, R., Nevill, A., Wallace, E., & Williams, M. (2020). Power, precision, and sample size estimation in sport and exercise science research. Journal of Sports Sciences, 38(17), 1933–1935.
  doi: 10.1080/02640414.2020.1776002
  supports: Precision-based sample size justification in sport and exercise science.
  short: sample size expectations in sport and exercise science
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Does the calculation match the design and analysis?

A power calculation is valid only for the analysis it describes. Reviewers should check that:

- the calculation is for the primary outcome and the primary comparison, not a secondary one;
- a clustered or repeated-measures design has been allowed for (ignoring clustering overstates the effective sample size; see the note on repeated measures and clustering);
- a calculation that relied on a baseline–outcome or within-participant correlation states the value assumed and its source;
- the alpha used reflects any multiplicity adjustment across primary outcomes or arms;
- the expected attrition has been added, and the numbers analysed are compared with the target;
- an equivalence or non-inferiority study is powered for its margin, which usually needs more participants than a superiority comparison;
- interaction or subgroup hypotheses, which need substantially larger samples than main effects of the same size, are not presented as adequately powered on the strength of a main-effect calculation.

## How should sequential designs and early stopping be handled?

Looking at the data repeatedly and stopping when the result becomes significant inflates the Type I error rate unless the looks were planned and the error rate is controlled, for example with a group-sequential design and an alpha-spending function. Unplanned or undisclosed interim testing ("optional stopping") is a form of analytic flexibility.

Reviewers should expect the number and timing of interim analyses, the stopping boundaries and the final sample size to be prespecified and reported. A trial stopped early for benefit tends to overestimate the effect, for the same reason as any estimate selected for being large.

In a Bayesian analysis the posterior given the data does not depend on the stopping intention, but how often a decision threshold is crossed over the course of repeated looks does. Where a Bayesian design claims particular error rates or operating characteristics, these need to be demonstrated, usually by simulation.

```references
- cite: Lakens, D. (2014). Performing high-powered studies efficiently with sequential analyses. European Journal of Social Psychology, 44(7), 701–710.
  doi: 10.1002/ejsp.2023
  supports: Sequential analyses that control the Type I error rate across planned interim looks.
  short: sequential analyses with controlled error rates
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant. Psychological Science, 22(11), 1359–1366.
  doi: 10.1177/0956797611417632
  supports: How undisclosed flexibility in stopping data collection inflates false-positive rates.
  short: how undisclosed flexibility inflates false positives
  type: Journal article
  checked: 2026-11-13, Crossref
```

## How is sample size justified in a Bayesian study?

Bayesian studies still need a sample size justification. Common approaches are:

- **Precision or interval-based targets:** the sample size at which the posterior interval is expected to be narrower than a stated width, or to fall inside or outside a region of practical equivalence, with a stated probability.
- **Bayes factor design analysis:** the probability of obtaining a Bayes factor beyond a stated threshold, in a fixed-n or sequential design, under stated assumptions about the effect.
- **Assurance:** the probability of a successful outcome averaged over a prior distribution for the effect, rather than conditional on a single assumed effect as in conventional power.

In each case the prior used for *planning* (which expresses uncertainty about the effect before the study) should be distinguished from the prior used in the *analysis*, and both should be reported. The calculation is usually done by simulation, and the simulation settings should be available.

```references
- cite: Schönbrodt, F. D., & Wagenmakers, E.-J. (2018). Bayes factor design analysis: Planning for compelling evidence. Psychonomic Bulletin & Review, 25(1), 128–142.
  doi: 10.3758/s13423-017-1230-y
  supports: Bayes factor design analysis for fixed-n and sequential designs.
  short: planning a study around Bayes factors
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: O'Hagan, A., Stevens, J. W., & Campbell, M. J. (2005). Assurance in clinical trial design. Pharmaceutical Statistics, 4(3), 187–201.
  doi: 10.1002/pst.175
  supports: Assurance as the unconditional probability of success, averaging power over prior uncertainty about the effect.
  short: assurance: power averaged over prior uncertainty
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Kruschke, J. K. (2018). Rejecting or accepting parameter values in Bayesian estimation. Advances in Methods and Practices in Psychological Science, 1(2), 270–280.
  doi: 10.1177/2515245918771304
  supports: Decisions based on a posterior interval and a region of practical equivalence, which precision-based planning targets.
  short: HDI and ROPE decision rules, and setting a ROPE
  type: Journal article
  access: open
  access_checked: 2026-10-01, OpenAlex: open (bronze, free to read)
  checked: 2026-09-30, Crossref
```

## What if the available sample is unavoidably small?

Some populations are small: elite athletes, rare conditions, specialised occupational groups. A small sample is not in itself a reason to reject a study, but it limits what can be concluded.

Reviewers can reasonably expect authors to: state that the sample was determined by availability; report which effect sizes the design could detect or estimate with useful precision; use designs that increase information per participant (within-participant comparisons, repeated measurements, a reliable outcome measure, adjustment for prognostic baseline covariates); present estimates with intervals and avoid dichotomous claims; and describe the findings as preliminary where the intervals are wide.

What a small study cannot support is a confident claim of no effect from a result that is not significant, or a confident estimate of effect magnitude from a significant one.

```references
- cite: Abt, G., Boreham, C., Davison, G., Jackson, R., Nevill, A., Wallace, E., & Williams, M. (2020). Power, precision, and sample size estimation in sport and exercise science research. Journal of Sports Sciences, 38(17), 1933–1935.
  doi: 10.1080/02640414.2020.1776002
  supports: Sample size expectations and small samples in sport and exercise science research.
  short: sample size expectations in sport and exercise science
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Lakens, D. (2022). Sample size justification. Collabra: Psychology, 8(1), 33267.
  doi: 10.1525/collabra.33267
  supports: Stating which effects a resource-limited study can and cannot detect.
  short: ways of justifying a sample size
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Common misconceptions

**"The result was significant, so the study had enough power."** Incorrect. Underpowered studies sometimes reach significance, and when they do the estimate is likely to be inflated.

**"The study had 80% power, so a result that is not significant shows there is no effect."** Incorrect. The 80% applies only to the effect size assumed in the calculation. A claim of no meaningful effect needs an interval that excludes meaningful effects, or an equivalence test.

**"Thirty participants per group is enough."** Not a justification. No fixed number is adequate regardless of the effect size, the variability of the outcome and the design.

**"Observed power explains why the result was not significant."** Incorrect. Observed power is a restatement of the p-value.

**"A larger sample makes the effect more important."** Incorrect. A larger sample makes the estimate more precise. Importance depends on the size of the effect and its consequences, not on the p-value or the sample size.

## Common reviewer red flags

- No sample size justification, or one evidently written after the results were known.
- Target effect size taken from a benchmark, a pilot study or a single earlier study without discussion.
- Power calculation for a different outcome, test or design from the one analysed.
- Clustering, repeated measures or attrition ignored in the calculation.
- Post-hoc or observed power reported to interpret a result that is not significant.
- A result that is not significant from a small study described as evidence of no effect.
- A large significant effect from a small study presented without caution about overestimation.
- Interim analyses or a flexible stopping rule that were not prespecified.
- A Bayesian study with no sample size rationale, on the grounds that "Bayesian methods work with small samples".

## Quick reviewer checklist

□ A sample size justification is reported and was made before data collection.

□ The target effect size is justified substantively.

□ Variability, alpha, power, test and software are stated so that the calculation can be reproduced.

□ The calculation matches the primary outcome, design and analysis.

□ Attrition, clustering and multiplicity are allowed for.

□ Observed power is not used to interpret results.

□ Conclusions are in proportion to the precision achieved.

□ Sequential looks and stopping rules, if any, were prespecified and are reported.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Lakens, D. (2022). Sample size justification. Collabra: Psychology, 8(1), 33267.
  doi: 10.1525/collabra.33267
  supports: Ways of justifying a sample size, including power, precision and resource constraints.
  short: ways of justifying a sample size
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Maxwell, S. E., Kelley, K., & Rausch, J. R. (2008). Sample size planning for statistical power and accuracy in parameter estimation. Annual Review of Psychology, 59, 537–563.
  doi: 10.1146/annurev.psych.59.103006.093735
  supports: Planning sample size for power and for accuracy in parameter estimation.
  short: planning sample size for power or for precision
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Hoenig, J. M., & Heisey, D. M. (2001). The abuse of power: The pervasive fallacy of power calculations for data analysis. The American Statistician, 55(1), 19–24.
  doi: 10.1198/000313001300339897
  supports: Why observed (post-hoc) power does not help interpret a result.
  short: why post hoc power does not explain a non-significant result
  type: Journal article
  access: subscription
  access_checked: 2026-10-01, OpenAlex: closed
  checked: 2026-09-30, Crossref
- cite: Gelman, A., & Carlin, J. (2014). Beyond power calculations: Assessing Type S (sign) and Type M (magnitude) errors. Perspectives on Psychological Science, 9(6), 641–651.
  doi: 10.1177/1745691614551642
  supports: Type S and Type M errors in underpowered studies.
  short: Type S (sign) and Type M (magnitude) errors
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Button, K. S., Ioannidis, J. P. A., Mokrysz, C., et al. (2013). Power failure: Why small sample size undermines the reliability of neuroscience. Nature Reviews Neuroscience, 14(5), 365–376.
  doi: 10.1038/nrn3475
  supports: The consequences of low power for the reliability of published findings.
  short: how low power undermines the reliability of findings
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Albers, C., & Lakens, D. (2018). When power analyses based on pilot data are biased: Inaccurate effect size estimators and follow-up bias. Journal of Experimental Social Psychology, 74, 187–195.
  doi: 10.1016/j.jesp.2017.09.004
  supports: The bias introduced by basing power analyses on pilot-study effect sizes.
  short: why pilot-study effect sizes bias power analyses
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Abt, G., Boreham, C., Davison, G., Jackson, R., Nevill, A., Wallace, E., & Williams, M. (2020). Power, precision, and sample size estimation in sport and exercise science research. Journal of Sports Sciences, 38(17), 1933–1935.
  doi: 10.1080/02640414.2020.1776002
  supports: Journal expectations for sample size justification in sport and exercise science.
  short: sample size expectations in sport and exercise science
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Lakens, D. (2014). Performing high-powered studies efficiently with sequential analyses. European Journal of Social Psychology, 44(7), 701–710.
  doi: 10.1002/ejsp.2023
  supports: Sequential analyses with controlled error rates.
  short: sequential analyses with controlled error rates
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Schönbrodt, F. D., & Wagenmakers, E.-J. (2018). Bayes factor design analysis: Planning for compelling evidence. Psychonomic Bulletin & Review, 25(1), 128–142.
  doi: 10.3758/s13423-017-1230-y
  supports: Planning a study around Bayes factors.
  short: planning a study around Bayes factors
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: O'Hagan, A., Stevens, J. W., & Campbell, M. J. (2005). Assurance in clinical trial design. Pharmaceutical Statistics, 4(3), 187–201.
  doi: 10.1002/pst.175
  supports: Assurance in trial design.
  short: assurance: power averaged over prior uncertainty
  type: Journal article
  checked: 2026-11-13, Crossref
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
