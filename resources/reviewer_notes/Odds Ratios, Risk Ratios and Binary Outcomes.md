# Odds Ratios, Risk Ratios and Binary Outcomes

## Purpose

This guide helps reviewers assess analyses of binary outcomes. It covers the risk difference, risk ratio and odds ratio, why odds ratios are misread as risk ratios, non-collapsibility, absolute versus relative effects and the number needed to treat, the dependence of interaction on the scale of measurement, and sparse-data problems in logistic regression.

## What reviewers should look for

- Are the numbers of events and participants in each group reported, so that risks can be seen directly?
- Is an odds ratio described in words that apply to a risk ratio ("twice as likely", "50% higher risk")?
- Is the outcome common, so that the odds ratio and risk ratio differ appreciably?
- Are absolute effects reported alongside relative ones?
- Are odds ratios from models with different covariates compared as though they estimated the same quantity?
- Is a change in the odds ratio after adjustment interpreted as confounding?
- Are very large odds ratios with very wide intervals based on few events?
- Is the reference category, and the unit for any continuous predictor, stated?

## What are the risk difference, risk ratio and odds ratio?

For a binary outcome, the **risk** in a group is the proportion with the event, and the **odds** are the risk divided by one minus the risk. Three measures compare two groups:

- the **risk difference** (absolute risk reduction or increase): one risk minus the other;
- the **risk ratio** (relative risk): one risk divided by the other;
- the **odds ratio**: one odds divided by the other.

With risks of 20% and 10%, the risk difference is 10 percentage points, the risk ratio is 2.0 and the odds ratio is 2.25. The three measures answer different questions and none is correct in general. Reviewers should expect the measure to be named, the direction of the comparison to be stated, and the underlying counts to be available.

```references
- cite: Greenland, S. (1987). Interpretation and choice of effect measures in epidemiologic analyses. American Journal of Epidemiology, 125(5), 761–768.
  doi: 10.1093/oxfordjournals.aje.a114593
  supports: The interpretation of risk differences, risk ratios and odds ratios and the choice among them.
  short: the interpretation and choice of effect measures
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Why does an odds ratio overstate a risk ratio?

The odds ratio is always further from 1 than the risk ratio, and the gap grows as the outcome becomes more common. When the risk is below about 10% in every group being compared, the two are close. When the outcome is common they are not: risks of 60% and 40% give a risk ratio of 1.5 and an odds ratio of 2.25.

The error to look for is an odds ratio described as though it were a risk ratio. An odds ratio of 2.25 does not show that the event is "2.25 times as likely" or that risk is "125% higher"; it shows that the odds are 2.25 times as large. With common outcomes, such as injury over a season in contact sport or adherence to an intervention, that wording can overstate an effect considerably.

```references
- cite: Zhang, J., & Yu, K. F. (1998). What's the relative risk? A method of correcting the odds ratio in cohort studies of common outcomes. JAMA, 280(19), 1690–1691.
  doi: 10.1001/jama.280.19.1690
  supports: How the odds ratio overstates the risk ratio when the outcome is common.
  short: how odds ratios overstate risk ratios when outcomes are common
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Knol, M. J., Le Cessie, S., Algra, A., Vandenbroucke, J. P., & Groenwold, R. H. H. (2012). Overestimation of risk ratios by odds ratios in trials and cohort studies: Alternatives to logistic regression. CMAJ, 184(8), 895–899.
  doi: 10.1503/cmaj.101715
  supports: The size of the overestimation in trials and cohort studies and why odds ratios should not be read as risk ratios.
  short: alternatives to logistic regression for estimating risk ratios
  type: Journal article
  checked: 2026-11-14, Crossref
```

## How should risk ratios be estimated when they are wanted?

In a cohort study or trial, where risks can be estimated, a risk ratio or risk difference can be modelled directly instead of reporting an odds ratio from logistic regression. Options include log-binomial regression, Poisson regression with robust (sandwich) standard errors, sometimes called modified Poisson regression, and standardisation of predicted risks from a logistic model.

Converting an adjusted odds ratio to a risk ratio with a simple formula is not a reliable substitute: applied to adjusted estimates it can give biased risk ratios and confidence intervals that are too narrow.

Logistic regression remains appropriate when the odds ratio is the intended measure, and it is the natural analysis for a case-control study, where risks cannot be estimated and the odds ratio is the quantity available.

```references
- cite: Zou, G. (2004). A modified Poisson regression approach to prospective studies with binary data. American Journal of Epidemiology, 159(7), 702–706.
  doi: 10.1093/aje/kwh090
  supports: Poisson regression with robust standard errors for estimating risk ratios directly.
  short: modified Poisson regression for estimating risk ratios
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Knol, M. J., Le Cessie, S., Algra, A., Vandenbroucke, J. P., & Groenwold, R. H. H. (2012). Overestimation of risk ratios by odds ratios in trials and cohort studies: Alternatives to logistic regression. CMAJ, 184(8), 895–899.
  doi: 10.1503/cmaj.101715
  supports: Alternatives to logistic regression for estimating risk ratios, and the limits of converting odds ratios.
  short: alternatives to logistic regression for estimating risk ratios
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What is non-collapsibility and why does it matter?

The odds ratio is **non-collapsible**: the odds ratio conditional on a covariate differs from the unadjusted (marginal) odds ratio whenever that covariate predicts the outcome, even if the covariate is perfectly balanced between groups and there is no confounding. The conditional odds ratio is generally further from 1. Risk differences and risk ratios do not behave this way.

Three consequences follow.

- A change in the odds ratio after adjustment is not, by itself, evidence of confounding.
- Odds ratios from models with different covariate sets, or from different studies with different adjustments, estimate different quantities and are not directly comparable.
- In a randomised trial, an adjusted odds ratio is a conditional effect and an unadjusted one a marginal effect; both are valid, but they are answers to different questions and the report should say which is given.

The same applies to hazard ratios.

```references
- cite: Greenland, S., Robins, J. M., & Pearl, J. (1999). Confounding and collapsibility in causal inference. Statistical Science, 14(1), 29–46.
  doi: 10.1214/ss/1009211805
  supports: The distinction between confounding and non-collapsibility.
  short: the difference between confounding and non-collapsibility
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Daniel, R., Zhang, J., & Farewell, D. (2021). Making apples from oranges: Comparing noncollapsible effect estimators and their standard errors after adjustment for different covariate sets. Biometrical Journal, 63(3), 528–557.
  doi: 10.1002/bimj.201900297
  supports: Why odds ratios adjusted for different covariate sets are not comparable and how to make them so.
  short: why adjusted and unadjusted odds ratios are not comparable
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Norton, E. C., Dowd, B. E., & Maciejewski, M. L. (2018). Odds ratios—current best practice and use. JAMA, 320(1), 84–85.
  doi: 10.1001/jama.2018.6971
  supports: Why odds ratios cannot be compared across models or studies with different covariates.
  short: the limits of odds ratios and current best practice
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

## Why should absolute effects be reported with relative ones?

A relative effect says nothing about how many people are affected. A risk ratio of 0.5 halves a risk of 40% to 20%, or a risk of 0.2% to 0.1%: the same ratio, a two-hundred-fold difference in absolute benefit. Decisions depend on the absolute change.

Reviewers should expect the risk in each group and the risk difference with its confidence interval, not relative measures alone. Reporting benefits as relative reductions and harms as absolute increases, or the reverse, makes the two look incommensurate.

The **number needed to treat** is the reciprocal of the absolute risk difference. It applies only to the baseline risk and follow-up period from which it was calculated, and it needs a confidence interval. When the interval for the risk difference includes zero, the interval for the number needed to treat is not a single range: it runs from a number needed to treat for benefit, through infinity, to a number needed to harm.

```references
- cite: Altman, D. G. (1998). Confidence intervals for the number needed to treat. BMJ, 317(7168), 1309–1312.
  doi: 10.1136/bmj.317.7168.1309
  supports: The number needed to treat, its confidence interval, and its form when the risk difference is not significant.
  short: confidence intervals for the number needed to treat
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Greenland, S. (1987). Interpretation and choice of effect measures in epidemiologic analyses. American Journal of Epidemiology, 125(5), 761–768.
  doi: 10.1093/oxfordjournals.aje.a114593
  supports: Why relative measures do not convey the size of an effect in absolute terms.
  short: the interpretation and choice of effect measures
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Why does interaction depend on the scale?

Whether two factors interact depends on the scale on which their effects are measured. If each factor multiplies the risk and their joint effect is the product of the two, there is no interaction on the multiplicative scale but there is one on the additive scale, because the joint risk difference exceeds the sum of the separate risk differences. The reverse also holds.

A logistic model tests interaction on the multiplicative (odds) scale only. A product term that is not significant therefore does not show that the effect of one factor is the same at every level of the other in absolute terms, which is usually the scale that matters for deciding whom to treat.

Reviewers should expect analyses of effect modification to present the risks or effects in each combination of the two factors, so that interaction can be judged on both scales.

```references
- cite: Knol, M. J., & VanderWeele, T. J. (2012). Recommendations for presenting analyses of effect modification and interaction. International Journal of Epidemiology, 41(2), 514–520.
  doi: 10.1093/ije/dyr218
  supports: How to present effect modification and interaction on both the additive and multiplicative scales.
  short: presenting interaction on additive and multiplicative scales
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What problems arise with few events?

Maximum-likelihood odds ratios are biased away from 1 when some combinations of outcome and predictor contain few observations, and the bias can be large. The warning signs are implausibly large odds ratios, very wide confidence intervals, and intervals spanning several orders of magnitude.

In the extreme case, a predictor or combination of predictors separates the outcomes completely, the estimate is infinite, and software may report an enormous coefficient and standard error or fail to converge. Deleting the predictor is not a good remedy; penalised likelihood methods give finite, less biased estimates.

The information in a binary outcome lies in the number of events and non-events, whichever is smaller, not in the total sample size. See the note on multicollinearity, variable selection and overfitting for the number of events needed per candidate parameter.

```references
- cite: Greenland, S., Mansournia, M. A., & Altman, D. G. (2016). Sparse data bias: A problem hiding in plain sight. BMJ, 352, i1981.
  doi: 10.1136/bmj.i1981
  supports: Sparse-data bias in odds ratios and other ratio estimates, how to recognise it and how to reduce it.
  short: sparse data bias in ratio estimates
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Heinze, G., & Schemper, M. (2002). A solution to the problem of separation in logistic regression. Statistics in Medicine, 21(16), 2409–2419.
  doi: 10.1002/sim.1047
  supports: Separation in logistic regression and penalised likelihood as a solution.
  short: separation in logistic regression and penalised likelihood
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Peduzzi, P., Concato, J., Kemper, E., Holford, T. R., & Feinstein, A. R. (1996). A simulation study of the number of events per variable in logistic regression analysis. Journal of Clinical Epidemiology, 49(12), 1373–1379.
  doi: 10.1016/S0895-4356(96)00236-3
  supports: Bias and unreliable inference when there are few events per variable in logistic regression.
  short: events per variable in logistic regression
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What should be reported for a binary outcome?

- The number of events and the number of participants in each group, before any modelling.
- The effect measure, named, with its confidence interval, and the direction of the comparison.
- An absolute effect as well as a relative one.
- The model used, the covariates, and whether the estimate is adjusted or unadjusted.
- The reference category for each categorical predictor, and the unit of change for each continuous predictor: an odds ratio "per unit" is uninterpretable without the unit.
- The follow-up period over which the risk was measured. Where follow-up differs between participants, a comparison of risks is not appropriate and rates or time-to-event methods are needed; see the note on survival analysis.

## Common misconceptions

**"An odds ratio of 2 means the event is twice as likely."** Only approximately, and only when the outcome is rare. For common outcomes it overstates the risk ratio.

**"The odds ratio changed after adjustment, so the covariate was a confounder."** Not necessarily. Odds ratios change on adjustment for any prognostic covariate.

**"A 50% reduction in risk is a large effect."** It depends on the baseline risk. Halving a rare risk helps few people.

**"There was no significant interaction, so the effect is the same in everyone."** Incorrect. The test addresses one scale, usually with low power.

**"A very large odds ratio shows a very strong effect."** With few events it more often shows sparse data.

## Common reviewer red flags

- Odds ratios described as risks, likelihoods or probabilities.
- Relative effects reported with no group risks or absolute difference.
- Counts of events per group not given.
- Odds ratios from differently adjusted models or studies compared directly.
- A simple formula used to convert adjusted odds ratios to risk ratios.
- Odds ratios above about 10 with intervals spanning orders of magnitude, or non-convergence ignored.
- A number needed to treat without an interval, baseline risk or time frame.
- Interaction claimed or dismissed from a product term alone.
- Reference category or predictor units not stated.

## Quick reviewer checklist

□ Events and denominators are reported for each group.

□ The effect measure is named and interpreted in terms that fit it.

□ Absolute and relative effects are both given.

□ Adjusted and unadjusted estimates are distinguished, and odds ratios are not compared across different adjustments.

□ Sparse data and separation have been considered.

□ Interaction is presented so that both scales can be judged.

□ Reference categories, units and follow-up time are stated.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Greenland, S. (1987). Interpretation and choice of effect measures in epidemiologic analyses. American Journal of Epidemiology, 125(5), 761–768.
  doi: 10.1093/oxfordjournals.aje.a114593
  supports: The interpretation and choice of effect measures.
  short: the interpretation and choice of effect measures
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Zhang, J., & Yu, K. F. (1998). What's the relative risk? A method of correcting the odds ratio in cohort studies of common outcomes. JAMA, 280(19), 1690–1691.
  doi: 10.1001/jama.280.19.1690
  supports: Odds ratios and risk ratios when outcomes are common.
  short: how odds ratios overstate risk ratios when outcomes are common
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Knol, M. J., Le Cessie, S., Algra, A., Vandenbroucke, J. P., & Groenwold, R. H. H. (2012). Overestimation of risk ratios by odds ratios in trials and cohort studies: Alternatives to logistic regression. CMAJ, 184(8), 895–899.
  doi: 10.1503/cmaj.101715
  supports: Overestimation of risk ratios by odds ratios and alternatives to logistic regression.
  short: alternatives to logistic regression for estimating risk ratios
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Zou, G. (2004). A modified Poisson regression approach to prospective studies with binary data. American Journal of Epidemiology, 159(7), 702–706.
  doi: 10.1093/aje/kwh090
  supports: Modified Poisson regression for risk ratios.
  short: modified Poisson regression for estimating risk ratios
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Greenland, S., Robins, J. M., & Pearl, J. (1999). Confounding and collapsibility in causal inference. Statistical Science, 14(1), 29–46.
  doi: 10.1214/ss/1009211805
  supports: Confounding and collapsibility.
  short: the difference between confounding and non-collapsibility
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Daniel, R., Zhang, J., & Farewell, D. (2021). Making apples from oranges: Comparing noncollapsible effect estimators and their standard errors after adjustment for different covariate sets. Biometrical Journal, 63(3), 528–557.
  doi: 10.1002/bimj.201900297
  supports: Comparing non-collapsible effect estimates after different adjustments.
  short: why adjusted and unadjusted odds ratios are not comparable
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Norton, E. C., Dowd, B. E., & Maciejewski, M. L. (2018). Odds ratios—current best practice and use. JAMA, 320(1), 84–85.
  doi: 10.1001/jama.2018.6971
  supports: Best practice in the use of odds ratios.
  short: the limits of odds ratios and current best practice
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Altman, D. G. (1998). Confidence intervals for the number needed to treat. BMJ, 317(7168), 1309–1312.
  doi: 10.1136/bmj.317.7168.1309
  supports: Confidence intervals for the number needed to treat.
  short: confidence intervals for the number needed to treat
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Knol, M. J., & VanderWeele, T. J. (2012). Recommendations for presenting analyses of effect modification and interaction. International Journal of Epidemiology, 41(2), 514–520.
  doi: 10.1093/ije/dyr218
  supports: Presenting effect modification and interaction.
  short: presenting interaction on additive and multiplicative scales
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Greenland, S., Mansournia, M. A., & Altman, D. G. (2016). Sparse data bias: A problem hiding in plain sight. BMJ, 352, i1981.
  doi: 10.1136/bmj.i1981
  supports: Sparse-data bias.
  short: sparse data bias in ratio estimates
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Heinze, G., & Schemper, M. (2002). A solution to the problem of separation in logistic regression. Statistics in Medicine, 21(16), 2409–2419.
  doi: 10.1002/sim.1047
  supports: Separation in logistic regression.
  short: separation in logistic regression and penalised likelihood
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Peduzzi, P., Concato, J., Kemper, E., Holford, T. R., & Feinstein, A. R. (1996). A simulation study of the number of events per variable in logistic regression analysis. Journal of Clinical Epidemiology, 49(12), 1373–1379.
  doi: 10.1016/S0895-4356(96)00236-3
  supports: Events per variable in logistic regression.
  short: events per variable in logistic regression
  type: Journal article
  checked: 2026-11-14, Crossref
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
