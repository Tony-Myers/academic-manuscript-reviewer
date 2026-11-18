# Non-parametric and Ordinal Methods

## Purpose

This guide helps reviewers assess the use of rank-based tests, bootstrap and permutation methods, and the analysis of ordinal outcomes such as Likert items and rating scales. It covers what rank tests actually test, the assumptions they still make, choosing a test from a preliminary normality test, effect estimates to accompany rank tests, treating ordinal data as numeric, ordinal regression, and the proper use of resampling methods.

## What reviewers should look for

- Is a rank test described as a comparison of medians or means?
- Was the choice between a parametric and a rank test made by a preliminary test of normality?
- Is a rank test reported with a p-value only, and no estimate of the size of the difference?
- Is a rank test described as "assumption-free"?
- Are ordinal responses analysed as numeric without justification, and are single items distinguished from multi-item scale scores?
- Where an ordinal model was used, was its main assumption examined?
- Does a bootstrap or permutation procedure respect the design, such as pairing or clustering?

## What does the Wilcoxon–Mann–Whitney test actually test?

The Wilcoxon–Mann–Whitney test (also called the Mann-Whitney U test or the Wilcoxon rank-sum test) is often described as a test that compares medians. In general it is not. Its null hypothesis is that an observation drawn at random from one group is equally likely to be larger or smaller than one drawn from the other: that the probability of superiority is one half.

It becomes a test of a difference in medians, or in means, only under the additional assumption that the two distributions have the same shape and spread and differ by a shift in location. Without that assumption, two groups with identical medians can give a highly significant result, and two groups with different medians can give none.

Reviewers should therefore expect the result to be described in terms of one group tending to have larger values than the other, unless the location-shift assumption has been justified, for example by showing similarly shaped distributions.

```references
- cite: Divine, G. W., Norton, H. J., Barón, A. E., & Juarez-Colunga, E. (2018). The Wilcoxon–Mann–Whitney procedure fails as a test of medians. The American Statistician, 72(3), 278–286.
  doi: 10.1080/00031305.2017.1305291
  supports: Why the Wilcoxon–Mann–Whitney procedure is not in general a test of medians and what it does test.
  short: why the Wilcoxon–Mann–Whitney test is not a test of medians
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Fagerland, M. W., & Sandvik, L. (2009). The Wilcoxon–Mann–Whitney test under scrutiny. Statistics in Medicine, 28(10), 1487–1497.
  doi: 10.1002/sim.3561
  supports: How the test behaves when the two distributions differ in spread or shape.
  short: the behaviour of the Wilcoxon–Mann–Whitney test when distributions differ in shape
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Are rank-based tests free of assumptions?

No. "Non-parametric" refers to not assuming a particular distribution such as the Normal. Rank tests still assume that observations are independent, so they are as vulnerable to clustering and repeated measures as any other test (see the note on repeated measures and the unit of analysis).

Used as tests of location, they are also sensitive to differences in variance and skewness between groups: when the groups differ in spread, the test can reject far more often than the nominal rate even though the medians or means are equal. Unequal variances are therefore not a reason to prefer a rank test to a *t*-test; Welch's test addresses unequal variances directly.

The Wilcoxon signed-rank test for paired data additionally assumes that the distribution of the differences is symmetric. Heavy ties, as with coarse rating scales, reduce the information in the ranks.

```references
- cite: Fagerland, M. W., & Sandvik, L. (2009). The Wilcoxon–Mann–Whitney test under scrutiny. Statistics in Medicine, 28(10), 1487–1497.
  doi: 10.1002/sim.3561
  supports: The sensitivity of the Wilcoxon–Mann–Whitney test to differences in variance and skewness when used to compare locations.
  short: the behaviour of the Wilcoxon–Mann–Whitney test when distributions differ in shape
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Delacre, M., Lakens, D., & Leys, C. (2017). Why psychologists should by default use Welch's t-test instead of Student's t-test. International Review of Social Psychology, 30(1), 92–101.
  doi: 10.5334/irsp.82
  supports: Welch's test as the remedy for unequal variances.
  short: Welch's test when variances differ
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Should a normality test decide which test is used?

No. A common two-stage procedure applies a test of normality and then uses a *t*-test if it "passes" and a rank test if it "fails". This is unsound for several reasons.

The preliminary test has little power in small samples, where non-normality matters most, and too much in large samples, where it matters least. The two candidate tests address different hypotheses, so the choice changes the question as well as the method. And the properties of the overall procedure are not those of either test applied alone, because the final analysis was selected using the same data.

The method of analysis should be chosen in advance, from what is known about the outcome and from the quantity the study aims to estimate. For comparisons of means in moderate or large samples, methods based on the *t* distribution are robust to non-normality.

```references
- cite: Rochon, J., Gondan, M., & Kieser, M. (2012). To test or not to test: Preliminary assessment of normality when comparing two independent samples. BMC Medical Research Methodology, 12, 81.
  doi: 10.1186/1471-2288-12-81
  supports: The properties of the two-stage procedure in which a normality test selects the main test, and why it is not recommended.
  short: why choosing a test from a preliminary normality test is unsound
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Lumley, T., Diehr, P., Emerson, S., & Chen, L. (2002). The importance of the normality assumption in large public health data sets. Annual Review of Public Health, 23, 151–169.
  doi: 10.1146/annurev.publhealth.23.100901.140546
  supports: Why methods based on means do not require Normally distributed data in sufficiently large samples.
  short: why normality matters little for means in large samples
  type: Journal article
  access: subscription
  access_checked: 2026-10-01, OpenAlex: closed
  checked: 2026-10-01, OpenAlex (Crossref unavailable)
```

## Which test should be preferred in large samples?

In large studies the choice should follow the estimand. If the scientific question concerns the average, for example mean cost, mean training load or mean change, a *t*-test or linear model is appropriate even for skewed data, because the sampling distribution of the mean is close to Normal and the result is expressed as a difference in means with a confidence interval.

A rank test in a large sample can reject its null hypothesis with near certainty when the means and the medians are equal but the distributions differ in spread or shape. Reported as "a significant difference between the groups", this is easily misread as a difference in level.

A rank test is the better choice when the question really is whether one group tends to have higher values, or when the outcome is ordinal and averages have no clear meaning.

```references
- cite: Fagerland, M. W. (2012). t-tests, non-parametric tests, and large studies—a paradox of statistical practice? BMC Medical Research Methodology, 12, 78.
  doi: 10.1186/1471-2288-12-78
  supports: Why t-tests are appropriate for comparing means in large studies and how rank tests can mislead there.
  short: t-tests and rank tests in large studies
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What effect estimate should accompany a rank test?

A p-value from a rank test says nothing about how large the difference is. An estimate with an interval should accompany it. Options that match what the test examines include:

- the **probability of superiority**: the estimated probability that a randomly chosen member of one group has a higher value than a randomly chosen member of the other (0.5 indicates no tendency either way);
- the **Hodges–Lehmann estimate** of the location shift, with its confidence interval, where a shift model is reasonable.

Reporting the two group medians alongside a rank-test p-value is common but can be inconsistent: the test does not compare the medians, and the difference between two sample medians is not the same thing as the Hodges–Lehmann estimate. Where a difference in medians is the quantity of interest, it can be estimated directly, for example by quantile regression or with a bootstrap interval.

```references
- cite: Acion, L., Peterson, J. J., Temple, S., & Arndt, S. (2006). Probabilistic index: An intuitive non-parametric approach to measuring the size of treatment effects. Statistics in Medicine, 25(4), 591–602.
  doi: 10.1002/sim.2256
  supports: The probability of superiority as an interpretable non-parametric measure of the size of a treatment effect.
  short: the probability of superiority as an effect size
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Divine, G. W., Norton, H. J., Barón, A. E., & Juarez-Colunga, E. (2018). The Wilcoxon–Mann–Whitney procedure fails as a test of medians. The American Statistician, 72(3), 278–286.
  doi: 10.1080/00031305.2017.1305291
  supports: Why group medians do not summarise what the Wilcoxon–Mann–Whitney test compares.
  short: why the Wilcoxon–Mann–Whitney test is not a test of medians
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Can ordinal data such as Likert responses be analysed as numeric?

Opinion differs, and reviewers should not apply a blanket rule in either direction.

One view is that parametric methods are robust enough that Likert-type data can be analysed with means, t-tests and regression without serious error. This is most defensible for **scores formed by summing or averaging several items**, which take many values and behave approximately like continuous measurements.

The opposing evidence is that treating ordinal responses as metric can distort effect sizes and, in some circumstances, produce false positives, missed effects or reversed differences, particularly when responses pile up at one end of the scale or when groups differ in variability. This risk is greatest for **single items** with few categories.

A reasonable expectation is that authors say which they have, justify a numeric analysis for composite scores, show the distribution of responses, and use an ordinal model, or at least a sensitivity analysis with one, for single items and for markedly skewed or bounded responses.

```references
- cite: Norman, G. (2010). Likert scales, levels of measurement and the "laws" of statistics. Advances in Health Sciences Education, 15(5), 625–632.
  doi: 10.1007/s10459-010-9222-y
  supports: The argument that parametric methods are robust for Likert-type data.
  short: the case that parametric methods are robust for Likert data
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Liddell, T. M., & Kruschke, J. K. (2018). Analyzing ordinal data with metric models: What could possibly go wrong? Journal of Experimental Social Psychology, 79, 328–348.
  doi: 10.1016/j.jesp.2018.08.009
  supports: The errors that can arise from analysing ordinal data with metric models.
  short: the errors that arise from analysing ordinal data as metric
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Sullivan, G. M., & Artino, A. R., Jr. (2013). Analyzing and interpreting data from Likert-type scales. Journal of Graduate Medical Education, 5(4), 541–542.
  doi: 10.4300/JGME-5-4-18
  supports: The distinction between single Likert items and multi-item scale scores.
  short: single Likert items compared with multi-item scale scores
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What should be checked when an ordinal regression model is used?

The most common ordinal model is the cumulative (proportional odds) model. It describes the odds of being in a higher rather than a lower category, and assumes that the effect of each predictor is the same at every division between categories: the **proportional odds** assumption. The result is a single odds ratio per predictor, interpreted as the multiplicative change in the odds of a higher response.

Reviewers should expect:

- a statement of which model was fitted and how the coefficients are to be read;
- an assessment of the proportional odds assumption, preferably by comparison with a model that relaxes it or by a graphical check, since formal tests reject readily in large samples;
- where the assumption is clearly violated for a predictor of interest, a model that allows that effect to vary across categories;
- results translated into predicted probabilities of each category, which are easier to interpret than odds ratios.

With two groups and no covariates, the proportional odds model gives essentially the same test as the Wilcoxon–Mann–Whitney test, and it extends naturally to covariates and more complex designs.

```references
- cite: McCullagh, P. (1980). Regression models for ordinal data. Journal of the Royal Statistical Society: Series B (Methodological), 42(2), 109–127.
  doi: 10.1111/j.2517-6161.1980.tb01109.x
  supports: The proportional odds model for ordinal outcomes.
  short: the proportional odds model
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Bürkner, P.-C., & Vuorre, M. (2019). Ordinal regression models in psychology: A tutorial. Advances in Methods and Practices in Psychological Science, 2(1), 77–101.
  doi: 10.1177/2515245918823199
  supports: Fitting, checking and interpreting cumulative and other ordinal regression models.
  short: ordinal regression models and their assumptions
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: The proportional odds model as a generalisation of rank tests that accommodates covariates.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
```

## When is the bootstrap appropriate, and what are its limits?

The bootstrap estimates the sampling variability of a statistic by repeatedly resampling the observed data. It is useful for statistics without a convenient standard error, such as medians, ratios and indirect effects.

It is not a remedy for a small sample. The bootstrap treats the sample as a stand-in for the population, and a small sample is a poor stand-in; intervals from very small samples can be too narrow. It also performs poorly for extreme quantiles and for the minimum or maximum.

Reviewers should check that the type of interval is stated (simple percentile intervals can be inaccurate for skewed statistics, where bias-corrected and accelerated intervals do better), that the number of resamples is adequate, and that the resampling **respects the design**: participants, not individual observations, should be resampled when there are repeated measures or clusters, and pairs kept together in paired designs.

```references
- cite: Carpenter, J., & Bithell, J. (2000). Bootstrap confidence intervals: When, which, what? A practical guide for medical statisticians. Statistics in Medicine, 19(9), 1141–1164.
  doi: 10.1002/(SICI)1097-0258(20000515)19:9<1141::AID-SIM479>3.0.CO;2-F
  supports: The bootstrap, the different types of bootstrap confidence interval and when each is appropriate.
  short: bootstrap confidence intervals and their variants
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What do permutation tests assume?

A permutation (randomisation) test obtains its reference distribution by reallocating the observed values among groups. In a randomised experiment this mirrors the random assignment that was actually performed, so the test is valid without assuming a distribution or random sampling from a population.

The hypothesis tested is that the group labels are exchangeable: that the distributions are the same. As with rank tests, a significant result can therefore reflect a difference in spread or shape, and a permutation test of a difference in means is not guaranteed its nominal error rate when variances and group sizes are unequal.

The permutation scheme has to match the design: permuting within pairs, blocks or clusters where these exist. In observational comparisons, where groups were not formed by randomisation, the test is a convenient approximation and its justification is weaker.

```references
- cite: Ludbrook, J., & Dudley, H. (1998). Why permutation tests are superior to t and F tests in biomedical research. The American Statistician, 52(2), 127–132.
  doi: 10.2307/2685470
  supports: The rationale for permutation tests in randomised biomedical experiments.
  short: permutation tests for randomised experiments
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

## Common misconceptions

**"The Mann–Whitney test compares medians."** Only if the distributions have the same shape. In general it tests whether one group tends to have larger values.

**"Non-parametric tests make no assumptions."** Incorrect. They assume independence, and as tests of location they are affected by unequal spread.

**"The data failed a normality test, so a rank test is required."** Incorrect. The choice should follow the question and be made in advance.

**"Rank tests are safer in small samples."** Not necessarily. With very small samples they may be unable to reach conventional significance at all, and they still need an effect estimate.

**"Likert data must never be averaged."** Too strong for multi-item scale scores; a real concern for single items.

**"Bootstrapping fixes a small sample."** Incorrect. It cannot supply information the sample does not contain.

## Common reviewer red flags

- A rank test described as showing a difference in medians or means without justification.
- Choice of test made by a preliminary normality test.
- Rank-test p-values with no estimate or interval.
- A rank test applied to clustered or repeated data as if independent.
- A rank test chosen because variances were unequal.
- Single ordinal or Likert items analysed with means and t-tests, with no view of the response distribution.
- An ordinal model with no assessment of proportional odds.
- Bootstrap or permutation ignoring pairing or clustering.
- Bootstrap intervals from a very small sample presented as robust.

## Quick reviewer checklist

□ The hypothesis tested by the chosen method matches the scientific question.

□ The method was chosen in advance, not by a preliminary test.

□ An effect estimate with an interval accompanies any rank test.

□ Independence, and for location claims similar shape, have been considered.

□ Ordinal outcomes are analysed in a way suited to single items or composite scores.

□ The assumptions of any ordinal model were examined.

□ Resampling methods respect the design and are not used to compensate for a small sample.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Divine, G. W., Norton, H. J., Barón, A. E., & Juarez-Colunga, E. (2018). The Wilcoxon–Mann–Whitney procedure fails as a test of medians. The American Statistician, 72(3), 278–286.
  doi: 10.1080/00031305.2017.1305291
  supports: The Wilcoxon–Mann–Whitney test and medians.
  short: why the Wilcoxon–Mann–Whitney test is not a test of medians
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Fagerland, M. W., & Sandvik, L. (2009). The Wilcoxon–Mann–Whitney test under scrutiny. Statistics in Medicine, 28(10), 1487–1497.
  doi: 10.1002/sim.3561
  supports: The Wilcoxon–Mann–Whitney test when distributions differ.
  short: the behaviour of the Wilcoxon–Mann–Whitney test when distributions differ in shape
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Fagerland, M. W. (2012). t-tests, non-parametric tests, and large studies—a paradox of statistical practice? BMC Medical Research Methodology, 12, 78.
  doi: 10.1186/1471-2288-12-78
  supports: Parametric and rank tests in large studies.
  short: t-tests and rank tests in large studies
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Rochon, J., Gondan, M., & Kieser, M. (2012). To test or not to test: Preliminary assessment of normality when comparing two independent samples. BMC Medical Research Methodology, 12, 81.
  doi: 10.1186/1471-2288-12-81
  supports: Preliminary tests of normality.
  short: why choosing a test from a preliminary normality test is unsound
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Acion, L., Peterson, J. J., Temple, S., & Arndt, S. (2006). Probabilistic index: An intuitive non-parametric approach to measuring the size of treatment effects. Statistics in Medicine, 25(4), 591–602.
  doi: 10.1002/sim.2256
  supports: The probability of superiority.
  short: the probability of superiority as an effect size
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Norman, G. (2010). Likert scales, levels of measurement and the "laws" of statistics. Advances in Health Sciences Education, 15(5), 625–632.
  doi: 10.1007/s10459-010-9222-y
  supports: Parametric analysis of Likert data.
  short: the case that parametric methods are robust for Likert data
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Liddell, T. M., & Kruschke, J. K. (2018). Analyzing ordinal data with metric models: What could possibly go wrong? Journal of Experimental Social Psychology, 79, 328–348.
  doi: 10.1016/j.jesp.2018.08.009
  supports: Ordinal data analysed with metric models.
  short: the errors that arise from analysing ordinal data as metric
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Sullivan, G. M., & Artino, A. R., Jr. (2013). Analyzing and interpreting data from Likert-type scales. Journal of Graduate Medical Education, 5(4), 541–542.
  doi: 10.4300/JGME-5-4-18
  supports: Likert items and scales.
  short: single Likert items compared with multi-item scale scores
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: McCullagh, P. (1980). Regression models for ordinal data. Journal of the Royal Statistical Society: Series B (Methodological), 42(2), 109–127.
  doi: 10.1111/j.2517-6161.1980.tb01109.x
  supports: Regression models for ordinal data.
  short: the proportional odds model
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Bürkner, P.-C., & Vuorre, M. (2019). Ordinal regression models in psychology: A tutorial. Advances in Methods and Practices in Psychological Science, 2(1), 77–101.
  doi: 10.1177/2515245918823199
  supports: A tutorial on ordinal regression.
  short: ordinal regression models and their assumptions
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Carpenter, J., & Bithell, J. (2000). Bootstrap confidence intervals: When, which, what? A practical guide for medical statisticians. Statistics in Medicine, 19(9), 1141–1164.
  doi: 10.1002/(SICI)1097-0258(20000515)19:9<1141::AID-SIM479>3.0.CO;2-F
  supports: Bootstrap confidence intervals.
  short: bootstrap confidence intervals and their variants
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Ludbrook, J., & Dudley, H. (1998). Why permutation tests are superior to t and F tests in biomedical research. The American Statistician, 52(2), 127–132.
  doi: 10.2307/2685470
  supports: Permutation tests.
  short: permutation tests for randomised experiments
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
