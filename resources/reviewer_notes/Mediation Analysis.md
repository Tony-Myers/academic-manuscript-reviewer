# Mediation Analysis

## Purpose

This guide helps reviewers assess claims that an exposure or intervention affects an outcome *through* an intermediate variable. It covers what mediation analysis estimates, the causal-steps approach and its weaknesses, the assumptions needed for a causal interpretation, why randomising the exposure is not enough, cross-sectional mediation, inference for indirect effects, the proportion mediated, sensitivity analysis and reporting. Mediation is also touched on in the note on causal inference in observational studies, which explains why a mediator should not be adjusted for when the total effect is wanted.

## What reviewers should look for

- Is the mediation hypothesis stated in advance, with a rationale for the causal order of exposure, mediator and outcome?
- Was the mediator measured after the exposure and before the outcome?
- Are confounders of the mediator–outcome relationship identified and adjusted for?
- Is mediation claimed from cross-sectional data?
- Is the indirect effect reported with a confidence interval obtained by an appropriate method?
- Are the labels "full" and "partial" mediation based on significance tests?
- Was any sensitivity analysis done for unmeasured confounding of the mediator and outcome?
- Is a statistical decomposition described as having established the mechanism?

## What does a mediation analysis estimate?

Mediation analysis divides the total effect of an exposure on an outcome into an **indirect effect**, transmitted through a specified mediator, and a **direct effect**, which is everything else: effects through other pathways, measured or not.

In the simplest linear case, the indirect effect is the product of two coefficients: the effect of the exposure on the mediator, and the effect of the mediator on the outcome with the exposure held fixed. Each of those is a causal quantity, and the second is estimated from an association between two variables neither of which was assigned by the investigator.

Mediation is distinct from **moderation**, where a third variable changes the size of the effect, and from **confounding**, where a third variable causes both exposure and outcome. The three can produce similar regression output and are separated by the causal structure assumed, not by the statistics.

```references
- cite: Baron, R. M., & Kenny, D. A. (1986). The moderator–mediator variable distinction in social psychological research: Conceptual, strategic, and statistical considerations. Journal of Personality and Social Psychology, 51(6), 1173–1182.
  doi: 10.1037/0022-3514.51.6.1173
  supports: The distinction between mediators and moderators and the regression framework for mediation.
  short: the causal-steps approach to mediation
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: VanderWeele, T. J. (2016). Mediation analysis: A practitioner's guide. Annual Review of Public Health, 37, 17–32.
  doi: 10.1146/annurev-publhealth-032315-021402
  supports: What direct and indirect effects are and how they are defined.
  short: causal mediation analysis and its assumptions
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What are the problems with the causal-steps approach?

The traditional approach tests a sequence of regressions: the exposure predicts the outcome, the exposure predicts the mediator, the mediator predicts the outcome given the exposure, and the exposure's coefficient shrinks when the mediator is added. It remains common and has known weaknesses.

- Requiring a significant total effect first is unnecessary. An indirect effect can exist when the total effect is small or not significant, for instance when direct and indirect effects have opposite signs.
- The approach does not estimate the indirect effect or its uncertainty; it infers mediation from a pattern of separate significance tests, and has low power.
- "Full mediation" declared because the direct effect is no longer significant confuses absence of evidence with evidence of absence, and depends on sample size.

The quantity of interest is the indirect effect itself, with an interval.

```references
- cite: Zhao, X., Lynch, J. G., Jr., & Chen, Q. (2010). Reconsidering Baron and Kenny: Myths and truths about mediation analysis. Journal of Consumer Research, 37(2), 197–206.
  doi: 10.1086/651257
  supports: Why a significant total effect is not required and why the full and partial mediation labels are unsound.
  short: problems with the causal-steps criteria
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Fritz, M. S., & MacKinnon, D. P. (2007). Required sample size to detect the mediated effect. Psychological Science, 18(3), 233–239.
  doi: 10.1111/j.1467-9280.2007.01882.x
  supports: The low power of the causal-steps approach compared with direct tests of the indirect effect.
  short: sample size needed to detect a mediated effect
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Baron, R. M., & Kenny, D. A. (1986). The moderator–mediator variable distinction in social psychological research: Conceptual, strategic, and statistical considerations. Journal of Personality and Social Psychology, 51(6), 1173–1182.
  doi: 10.1037/0022-3514.51.6.1173
  supports: The original causal-steps criteria.
  short: the causal-steps approach to mediation
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What assumptions does a causal interpretation need?

For the direct and indirect effects to have a causal meaning, there must be no unmeasured confounding of:

1. the exposure–outcome relationship;
2. the exposure–mediator relationship;
3. the **mediator–outcome** relationship;

and, in addition, no confounder of the mediator–outcome relationship that is itself affected by the exposure.

The third assumption is the one most often ignored. Anything that influences both the mediator and the outcome, and is not adjusted for, biases both the direct and the indirect effect. The fourth is frequently violated when the exposure acts through several related intermediate variables, and it cannot be dealt with by ordinary regression adjustment.

The variables must also be in the assumed temporal order, and the models correctly specified, including any interaction between exposure and mediator. Reviewers should expect these assumptions to be stated and their plausibility argued.

```references
- cite: VanderWeele, T. J. (2016). Mediation analysis: A practitioner's guide. Annual Review of Public Health, 37, 17–32.
  doi: 10.1146/annurev-publhealth-032315-021402
  supports: The no-unmeasured-confounding assumptions required for direct and indirect effects.
  short: causal mediation analysis and its assumptions
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Richiardi, L., Bellocco, R., & Zugna, D. (2013). Mediation analysis in epidemiology: Methods, interpretation and bias. International Journal of Epidemiology, 42(5), 1511–1519.
  doi: 10.1093/ije/dyt127
  supports: Mediator–outcome confounding, exposure–mediator interaction and confounders affected by the exposure as sources of bias.
  short: sources of bias in mediation analysis
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Does randomising the exposure make the mediation analysis causal?

No. Randomisation removes confounding of the exposure's effects on the mediator and on the outcome. It does nothing about confounding between the mediator and the outcome, because participants were not randomised to levels of the mediator.

Within a randomised trial, the mediation analysis is therefore an observational analysis. Individuals whose mediator changed more may differ from those whose mediator changed less in ways that also affect the outcome. An intervention can change both a proposed mediator and the outcome through separate routes, giving a non-zero product of coefficients when the mediator plays no causal role.

Stronger evidence that a variable is on the pathway comes from designs that manipulate the mediator itself, alongside consistency with other evidence about the mechanism.

```references
- cite: Bullock, J. G., Green, D. P., & Ha, S. E. (2010). Yes, but what's the mechanism? (Don't expect an easy answer). Journal of Personality and Social Psychology, 98(4), 550–558.
  doi: 10.1037/a0018933
  supports: Why randomising the exposure does not identify the mechanism and why mediator–outcome confounding remains.
  short: why randomising the exposure does not identify the mechanism
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Imai, K., Keele, L., & Tingley, D. (2010). A general approach to causal mediation analysis. Psychological Methods, 15(4), 309–334.
  doi: 10.1037/a0020761
  supports: The sequential ignorability assumption, which randomisation of the exposure alone does not satisfy.
  short: sequential ignorability and sensitivity analysis for mediation
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Can mediation be established from cross-sectional data?

Rarely. Mediation is a process that unfolds over time: the exposure changes the mediator, which then changes the outcome. Data collected at one time point cannot show that order, and the same associations are compatible with the outcome influencing the mediator, or with all three reflecting a common cause.

Beyond the question of order, cross-sectional estimates of mediated effects are generally biased for the longitudinal effects they are meant to represent. They can indicate substantial mediation when there is none over time, and none when it is substantial.

Reviewers should expect a cross-sectional mediation analysis to be described as showing that the pattern of associations is compatible with a hypothesised pathway, not as evidence for it.

```references
- cite: Maxwell, S. E., & Cole, D. A. (2007). Bias in cross-sectional analyses of longitudinal mediation. Psychological Methods, 12(1), 23–44.
  doi: 10.1037/1082-989X.12.1.23
  supports: The bias in cross-sectional estimates of longitudinal mediation.
  short: bias in cross-sectional mediation analyses
  type: Journal article
  checked: 2026-11-14, Crossref
```

## How should the indirect effect be tested and reported?

The indirect effect is a product of coefficients, and its sampling distribution is skewed, particularly in small samples. A test that assumes it is Normal (the Sobel test) is therefore inaccurate and has low power. Intervals based on the distribution of the product, or on bootstrap resampling, are preferred.

The indirect effect should be reported as an estimate with a confidence or credible interval, in interpretable units, together with the component paths and the direct and total effects.

Detecting an indirect effect needs a larger sample than detecting either path, because it depends on both. Where the two paths are small, several hundred participants can be needed for adequate power. A mediation analysis in a small study will usually be inconclusive, and a "significant" indirect effect in such a study is likely to be an overestimate.

```references
- cite: MacKinnon, D. P., Lockwood, C. M., & Williams, J. (2004). Confidence limits for the indirect effect: Distribution of the product and resampling methods. Multivariate Behavioral Research, 39(1), 99–128.
  doi: 10.1207/s15327906mbr3901_4
  supports: Why Normal-theory tests of the indirect effect are inaccurate and how distribution-of-the-product and resampling intervals perform.
  short: confidence intervals for an indirect effect
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Fritz, M. S., & MacKinnon, D. P. (2007). Required sample size to detect the mediated effect. Psychological Science, 18(3), 233–239.
  doi: 10.1111/j.1467-9280.2007.01882.x
  supports: The sample sizes needed to detect mediated effects with different methods.
  short: sample size needed to detect a mediated effect
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What about binary outcomes, interactions and the proportion mediated?

The product-of-coefficients and difference-in-coefficients methods agree for linear models without interaction. They need not agree, and neither need equal a meaningful effect, when the outcome or mediator is binary and modelled with logistic regression, or when the effect of the mediator differs between exposure groups. Methods based on counterfactual definitions of natural direct and indirect effects handle these cases and allow for exposure–mediator interaction. Reviewers should expect the method to be named and to suit the type of outcome.

The **proportion mediated** is widely reported and frequently misleading. It is a ratio of two uncertain quantities and is very imprecise unless the total effect is large and precisely estimated. It is not meaningful when direct and indirect effects have opposite signs, and it can exceed 100% or be negative. It should be given with an interval, or not at all.

```references
- cite: VanderWeele, T. J. (2016). Mediation analysis: A practitioner's guide. Annual Review of Public Health, 37, 17–32.
  doi: 10.1146/annurev-publhealth-032315-021402
  supports: Mediation with binary outcomes and exposure–mediator interaction, and the interpretation and instability of the proportion mediated.
  short: causal mediation analysis and its assumptions
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Richiardi, L., Bellocco, R., & Zugna, D. (2013). Mediation analysis in epidemiology: Methods, interpretation and bias. International Journal of Epidemiology, 42(5), 1511–1519.
  doi: 10.1093/ije/dyt127
  supports: Why traditional methods fail with non-linear models and interaction.
  short: sources of bias in mediation analysis
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What sensitivity analyses should be expected?

Because the assumption of no unmeasured mediator–outcome confounding cannot be tested, a sensitivity analysis is the main way of judging how much weight the result can bear. Such an analysis asks how strong an unmeasured confounder would have to be to remove the indirect effect, or reverse its sign.

A result that would be overturned by a weak confounder deserves little confidence; one that would need implausibly strong confounding is more persuasive.

Measurement error in the mediator also matters. Random error in the mediator tends to bias the indirect effect towards zero and the direct effect away from it, so an unreliable measure of the mediator will understate mediation.

```references
- cite: Imai, K., Keele, L., & Tingley, D. (2010). A general approach to causal mediation analysis. Psychological Methods, 15(4), 309–334.
  doi: 10.1037/a0020761
  supports: Sensitivity analysis for violation of sequential ignorability in mediation.
  short: sequential ignorability and sensitivity analysis for mediation
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: VanderWeele, T. J. (2016). Mediation analysis: A practitioner's guide. Annual Review of Public Health, 37, 17–32.
  doi: 10.1146/annurev-publhealth-032315-021402
  supports: Sensitivity analysis for unmeasured confounding and the consequences of measurement error in the mediator.
  short: causal mediation analysis and its assumptions
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What should a mediation analysis report?

Reporting guidance for mediation analyses (AGReMA) asks for:

- the rationale for the proposed mediator and the assumed causal model, preferably as a diagram;
- whether the analysis was prespecified;
- how and when the exposure, mediator, outcome and confounders were measured, and their temporal order;
- the causal assumptions and the confounders adjusted for in each relationship;
- the statistical method, including how interaction was handled and how uncertainty was estimated;
- estimates of the indirect, direct and total effects with intervals;
- sensitivity analyses;
- limitations, and conclusions that do not go beyond what the assumptions permit.

```references
- cite: Lee, H., Cashin, A. G., Lamb, S. E., et al. (2021). A guideline for reporting mediation analyses of randomized trials and observational studies: The AGReMA statement. JAMA, 326(11), 1045–1056.
  doi: 10.1001/jama.2021.14075
  supports: The AGReMA reporting guideline for mediation analyses of trials and observational studies.
  short: the AGReMA reporting guideline for mediation analyses
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

## Common misconceptions

**"The intervention was randomised, so the mediation result is causal."** Incorrect. The mediator was not randomised.

**"The direct effect was no longer significant, so there is full mediation."** Incorrect. Loss of significance is not evidence that the direct effect is zero.

**"There was no significant total effect, so there is nothing to mediate."** Incorrect. Opposing pathways can cancel.

**"The indirect effect was significant, so the mechanism is established."** Incorrect. The analysis shows that the data are compatible with the pathway under untestable assumptions.

**"Mediation can be tested in a cross-sectional survey."** Only as a description of associations.

**"Sixty per cent of the effect was mediated."** Check the interval; such proportions are usually very imprecise.

## Common reviewer red flags

- Mediation claimed from cross-sectional data, with causal wording.
- No confounders of the mediator–outcome relationship considered.
- Mediator and outcome measured at the same time, or mediator measured after the outcome.
- Causal-steps conclusions with no estimate of the indirect effect.
- A Sobel test in a small sample.
- "Full" or "partial" mediation labels based on significance.
- A proportion mediated with no interval.
- Linear-model methods applied to binary outcomes without comment.
- A post hoc mediator chosen after the main results were known.
- No sensitivity analysis, and mechanism stated as established.

## Quick reviewer checklist

□ The causal model and temporal order are stated and plausible.

□ Confounders of all three relationships are addressed.

□ The method suits the outcome type and allows for interaction where relevant.

□ The indirect effect has an appropriate interval.

□ The sample size is adequate for an indirect effect.

□ Sensitivity to unmeasured mediator–outcome confounding is examined.

□ Conclusions are worded in line with the assumptions.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: VanderWeele, T. J. (2016). Mediation analysis: A practitioner's guide. Annual Review of Public Health, 37, 17–32.
  doi: 10.1146/annurev-publhealth-032315-021402
  supports: A practitioner's guide to causal mediation analysis.
  short: causal mediation analysis and its assumptions
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Imai, K., Keele, L., & Tingley, D. (2010). A general approach to causal mediation analysis. Psychological Methods, 15(4), 309–334.
  doi: 10.1037/a0020761
  supports: Identification, estimation and sensitivity analysis for causal mediation.
  short: sequential ignorability and sensitivity analysis for mediation
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Richiardi, L., Bellocco, R., & Zugna, D. (2013). Mediation analysis in epidemiology: Methods, interpretation and bias. International Journal of Epidemiology, 42(5), 1511–1519.
  doi: 10.1093/ije/dyt127
  supports: Bias in mediation analysis.
  short: sources of bias in mediation analysis
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Bullock, J. G., Green, D. P., & Ha, S. E. (2010). Yes, but what's the mechanism? (Don't expect an easy answer). Journal of Personality and Social Psychology, 98(4), 550–558.
  doi: 10.1037/a0018933
  supports: Why mechanisms are hard to establish from mediation analysis of experiments.
  short: why randomising the exposure does not identify the mechanism
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Maxwell, S. E., & Cole, D. A. (2007). Bias in cross-sectional analyses of longitudinal mediation. Psychological Methods, 12(1), 23–44.
  doi: 10.1037/1082-989X.12.1.23
  supports: Cross-sectional analyses of longitudinal mediation.
  short: bias in cross-sectional mediation analyses
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Baron, R. M., & Kenny, D. A. (1986). The moderator–mediator variable distinction in social psychological research: Conceptual, strategic, and statistical considerations. Journal of Personality and Social Psychology, 51(6), 1173–1182.
  doi: 10.1037/0022-3514.51.6.1173
  supports: The causal-steps approach.
  short: the causal-steps approach to mediation
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Zhao, X., Lynch, J. G., Jr., & Chen, Q. (2010). Reconsidering Baron and Kenny: Myths and truths about mediation analysis. Journal of Consumer Research, 37(2), 197–206.
  doi: 10.1086/651257
  supports: A critique of the causal-steps criteria.
  short: problems with the causal-steps criteria
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: MacKinnon, D. P., Lockwood, C. M., & Williams, J. (2004). Confidence limits for the indirect effect: Distribution of the product and resampling methods. Multivariate Behavioral Research, 39(1), 99–128.
  doi: 10.1207/s15327906mbr3901_4
  supports: Confidence limits for the indirect effect.
  short: confidence intervals for an indirect effect
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Fritz, M. S., & MacKinnon, D. P. (2007). Required sample size to detect the mediated effect. Psychological Science, 18(3), 233–239.
  doi: 10.1111/j.1467-9280.2007.01882.x
  supports: Sample size for detecting mediated effects.
  short: sample size needed to detect a mediated effect
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Lee, H., Cashin, A. G., Lamb, S. E., et al. (2021). A guideline for reporting mediation analyses of randomized trials and observational studies: The AGReMA statement. JAMA, 326(11), 1045–1056.
  doi: 10.1001/jama.2021.14075
  supports: The AGReMA reporting guideline.
  short: the AGReMA reporting guideline for mediation analyses
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
