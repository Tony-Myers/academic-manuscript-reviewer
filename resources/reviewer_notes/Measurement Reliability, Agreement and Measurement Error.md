# Measurement Reliability, Agreement and Measurement Error

## Purpose

This guide helps reviewers assess claims about the reliability of a measurement, the agreement between two methods or raters, and the consequences of measurement error for a study's conclusions. It covers the intraclass correlation coefficient (ICC), the standard error of measurement (SEM) or typical error, the minimal detectable change, the coefficient of variation, Bland–Altman limits of agreement, kappa, and the effect of measurement error on estimated associations.

## What reviewers should look for

- Is the question one of reliability (repeatability of the same method) or agreement (interchangeability of two methods), and does the statistic match it?
- Is a correlation coefficient or a paired test that is not significant offered as evidence of agreement?
- Is the form of the ICC stated, with a confidence interval?
- Is an absolute measure of error (SEM, typical error, limits of agreement) reported in the units of the measurement as well as a relative one?
- Are the limits of agreement judged against a difference stated in advance to be acceptable?
- Was systematic change between trials (learning, fatigue) examined?
- Do the reliability data come from a sample and protocol comparable to the study in which the measure is used?

## What is the difference between reliability, agreement and validity?

**Reliability** concerns how consistently a method distinguishes between individuals when measurement is repeated, relative to the measurement error. **Agreement** concerns how close repeated measurements, or measurements by two methods or raters, are to each other in the units of measurement. **Validity** concerns whether the method measures what it is intended to measure.

The three are distinct. A method can be highly reliable and wrong (a consistently miscalibrated scale), and two methods can be highly correlated and still disagree by an important amount. Reviewers should check that the evidence presented addresses the property being claimed.

```references
- cite: Kottner, J., Audigé, L., Brorson, S., et al. (2011). Guidelines for Reporting Reliability and Agreement Studies (GRRAS) were proposed. Journal of Clinical Epidemiology, 64(1), 96–106.
  doi: 10.1016/j.jclinepi.2010.03.002
  supports: The distinction between reliability and agreement and what should be reported for each.
  short: reporting guidelines for reliability and agreement studies
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Atkinson, G., & Nevill, A. M. (1998). Statistical methods for assessing measurement error (reliability) in variables relevant to sports medicine. Sports Medicine, 26(4), 217–238.
  doi: 10.2165/00007256-199826040-00002
  supports: Relative and absolute reliability in sports medicine measurements.
  short: assessing measurement error in sports medicine
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Why is a correlation coefficient not evidence of agreement?

A Pearson correlation measures the strength of a linear relationship, not agreement. Two methods can correlate almost perfectly while one reads consistently higher than the other, or while the difference between them grows with the size of the measurement.

A correlation also depends on the spread of the sample. The same measurement error gives a high correlation in a heterogeneous sample and a low one in a homogeneous sample, such as a squad of elite athletes.

A paired *t*-test that is not significant is not evidence of agreement either. It examines only the mean difference, and a large random error makes the test less likely to reach significance, so poorer methods pass more easily.

```references
- cite: Bland, J. M., & Altman, D. G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement. The Lancet, 327(8476), 307–310.
  doi: 10.1016/S0140-6736(86)90837-8
  supports: Why correlation and tests of the mean difference do not measure agreement between two methods.
  short: limits of agreement between two methods
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Atkinson, G., & Nevill, A. M. (1998). Statistical methods for assessing measurement error (reliability) in variables relevant to sports medicine. Sports Medicine, 26(4), 217–238.
  doi: 10.2165/00007256-199826040-00002
  supports: The dependence of correlation-based reliability on sample heterogeneity.
  short: assessing measurement error in sports medicine
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What should be reported about an intraclass correlation coefficient?

"The ICC" is a family of coefficients that can give different values for the same data. A report should state:

- the **model** (one-way random, two-way random or two-way mixed effects), which depends on whether the same raters or trials measured every participant and whether they are treated as a sample of possible raters;
- the **type** (the reliability of a single measurement or of the mean of several);
- the **definition** (consistency or absolute agreement), which determines whether systematic differences between trials or raters count as error;
- a **confidence interval**.

An ICC for the mean of several trials is larger than for a single trial, and should not be quoted in support of a study that used single measurements. Verbal labels for ICC values (for example below 0.5 poor, 0.5 to 0.75 moderate, 0.75 to 0.9 good, above 0.9 excellent) are conventions; where they are used they should be applied to the confidence interval, not only to the point estimate.

```references
- cite: Shrout, P. E., & Fleiss, J. L. (1979). Intraclass correlations: Uses in assessing rater reliability. Psychological Bulletin, 86(2), 420–428.
  doi: 10.1037/0033-2909.86.2.420
  supports: The different forms of the intraclass correlation and when each applies.
  short: the forms of the intraclass correlation
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients for reliability research. Journal of Chiropractic Medicine, 15(2), 155–163.
  doi: 10.1016/j.jcm.2016.02.012
  supports: Selecting the ICC model, type and definition, reporting them, and conventional interpretive labels applied to the confidence interval.
  short: choosing and reporting an intraclass correlation
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Why can a high ICC coexist with large measurement error?

The ICC is a ratio: between-participant variance divided by total variance. It is high when participants differ greatly from one another relative to the measurement error, and low when they are similar, even if the error is unchanged.

Two consequences follow. An ICC estimated in a heterogeneous sample overstates how well the measure will discriminate within a homogeneous one. And a high ICC does not show that the error is small enough for the intended use, such as detecting a training-induced change in an individual.

For that reason an ICC should be accompanied by an absolute measure of error in the units of the measurement.

```references
- cite: Weir, J. P. (2005). Quantifying test-retest reliability using the intraclass correlation coefficient and the SEM. Journal of Strength and Conditioning Research, 19(1), 231–240.
  doi: 10.1519/00124278-200502000-00038
  supports: The dependence of the ICC on between-participant variability and the need to report the SEM with it.
  short: the intraclass correlation and the standard error of measurement
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Atkinson, G., & Nevill, A. M. (1998). Statistical methods for assessing measurement error (reliability) in variables relevant to sports medicine. Sports Medicine, 26(4), 217–238.
  doi: 10.2165/00007256-199826040-00002
  supports: Why relative reliability statistics cannot be transferred between samples of differing heterogeneity.
  short: assessing measurement error in sports medicine
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What are the standard error of measurement and the typical error?

The **standard error of measurement (SEM)** estimates the standard deviation of repeated measurements on the same individual: the typical size of the random error in a single measurement. It can be calculated from the error mean square of a repeated-measures analysis of variance, or as SD × √(1 − ICC). The **typical error** used in sport science is the same quantity, commonly calculated as the standard deviation of the difference scores divided by √2.

The SEM is expressed in the units of the measurement and, unlike the ICC, does not depend strongly on the heterogeneity of the sample. It is not the standard error of the mean, with which it is sometimes confused.

Reviewers should expect the SEM or typical error to be reported with a confidence interval, and to come from a retest interval and protocol relevant to the study.

```references
- cite: Weir, J. P. (2005). Quantifying test-retest reliability using the intraclass correlation coefficient and the SEM. Journal of Strength and Conditioning Research, 19(1), 231–240.
  doi: 10.1519/00124278-200502000-00038
  supports: Calculating the standard error of measurement and its relation to the ICC.
  short: the intraclass correlation and the standard error of measurement
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Hopkins, W. G. (2000). Measures of reliability in sports medicine and science. Sports Medicine, 30(1), 1–15.
  doi: 10.2165/00007256-200030010-00001
  supports: The typical error and its calculation from difference scores.
  short: typical error and other reliability measures
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What is the minimal detectable change?

The **minimal detectable change** (also smallest detectable difference or smallest real difference) is the change in an individual's score that exceeds measurement error with a stated confidence. For 95% confidence it is commonly calculated as 1.96 × √2 × SEM; the √2 arises because a change score contains the error of two measurements.

An observed individual change smaller than this cannot be distinguished from measurement error. It applies to individuals; changes in group means can be detected with much smaller differences because averaging reduces error.

The minimal detectable change is a statement about measurement error. It is not the smallest change that matters, which has to be justified on practical or clinical grounds (see the note on equivalence and the smallest effect size of interest). A measure is of limited use for monitoring individuals when its minimal detectable change is larger than the smallest change that matters.

```references
- cite: Weir, J. P. (2005). Quantifying test-retest reliability using the intraclass correlation coefficient and the SEM. Journal of Strength and Conditioning Research, 19(1), 231–240.
  doi: 10.1519/00124278-200502000-00038
  supports: The minimal difference needed to be considered real, derived from the SEM.
  short: the intraclass correlation and the standard error of measurement
  type: Journal article
  checked: 2026-11-13, Crossref
```

## How should Bland–Altman limits of agreement be reported and judged?

For two methods (or two trials) measured on the same individuals, the Bland–Altman approach reports the mean difference (the bias) and the 95% limits of agreement: bias ± 1.96 × the standard deviation of the differences. About 95% of differences between the methods are expected to lie within those limits.

Reviewers should check that:

- the limits are compared with a difference judged acceptable **in advance** on practical grounds; the method does not itself say whether agreement is good;
- the plot of differences against means has been examined for a relationship between the size of the difference and the size of the measurement;
- where the differences grow with the measurement, the analysis used log-transformed data (giving ratio limits of agreement) or modelled the trend, since ordinary limits will then be too wide for small values and too narrow for large ones;
- confidence intervals are given for the bias and for the limits, which are imprecise in small samples;
- several measurements per individual, if present, were handled with the repeated-measurements form of the method and not treated as independent pairs.

```references
- cite: Bland, J. M., & Altman, D. G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement. The Lancet, 327(8476), 307–310.
  doi: 10.1016/S0140-6736(86)90837-8
  supports: The limits of agreement method for comparing two methods of measurement.
  short: limits of agreement between two methods
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Bland, J. M., & Altman, D. G. (1999). Measuring agreement in method comparison studies. Statistical Methods in Medical Research, 8(2), 135–160.
  doi: 10.1191/096228099673819272
  supports: Limits of agreement when differences depend on magnitude and when there are repeated measurements per individual.
  short: limits of agreement, including repeated measurements
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Atkinson, G., & Nevill, A. M. (1998). Statistical methods for assessing measurement error (reliability) in variables relevant to sports medicine. Sports Medicine, 26(4), 217–238.
  doi: 10.2165/00007256-199826040-00002
  supports: Ratio limits of agreement for heteroscedastic measurement error.
  short: assessing measurement error in sports medicine
  type: Journal article
  checked: 2026-11-13, Crossref
```

## When is a coefficient of variation appropriate?

A within-participant coefficient of variation expresses the typical error as a percentage of the mean. It is a natural summary when the error is proportional to the size of the measurement, as is common for physiological and performance measures, and it allows comparison across measures with different units.

It is misleading where the error does not scale with the measurement, where the scale has no true zero, or where values near zero occur. A threshold such as "a coefficient of variation below 10% is acceptable" has no general justification; whether the error is acceptable depends on the size of the change or difference the measure is intended to detect.

```references
- cite: Hopkins, W. G. (2000). Measures of reliability in sports medicine and science. Sports Medicine, 30(1), 1–15.
  doi: 10.2165/00007256-200030010-00001
  supports: Expressing typical error as a coefficient of variation.
  short: typical error and other reliability measures
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Atkinson, G., & Nevill, A. M. (1998). Statistical methods for assessing measurement error (reliability) in variables relevant to sports medicine. Sports Medicine, 26(4), 217–238.
  doi: 10.2165/00007256-199826040-00002
  supports: Why arbitrary thresholds for the coefficient of variation are not a sound criterion of acceptable reliability.
  short: assessing measurement error in sports medicine
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Was systematic change between trials examined?

Reliability statistics describe random error, but repeated trials often also differ systematically. Performance tests commonly improve from the first to the second trial through learning or familiarisation, and may decline with fatigue or loss of motivation.

Reviewers should expect the mean of each trial to be reported and the change between trials to be estimated with a confidence interval. Where a learning effect is present, familiarisation trials are needed before the measure is used in an intervention study, and an uncontrolled pre–post change may partly reflect it.

An absolute-agreement ICC counts systematic change as error; a consistency ICC ignores it. The choice should be stated and should suit the intended use.

```references
- cite: Hopkins, W. G. (2000). Measures of reliability in sports medicine and science. Sports Medicine, 30(1), 1–15.
  doi: 10.2165/00007256-200030010-00001
  supports: Systematic change in the mean between trials as a component of reliability.
  short: typical error and other reliability measures
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Atkinson, G., & Nevill, A. M. (1998). Statistical methods for assessing measurement error (reliability) in variables relevant to sports medicine. Sports Medicine, 26(4), 217–238.
  doi: 10.2165/00007256-199826040-00002
  supports: Examining systematic bias between repeated trials.
  short: assessing measurement error in sports medicine
  type: Journal article
  checked: 2026-11-13, Crossref
```

## How is agreement assessed for categorical ratings?

Percentage agreement between raters overstates agreement because some agreement occurs by chance. Cohen's **kappa** corrects for the agreement expected by chance; a weighted kappa is used for ordered categories so that near-misses count as partial agreement.

Kappa depends on the prevalence of the categories: for the same rater accuracy it is lower when one category is rare. Kappa values are therefore not directly comparable across samples with different prevalence, and the table of ratings should be reported alongside the coefficient.

Internal consistency (for example Cronbach's alpha) is a different property again. It describes how items of a scale relate to one another at one time point, and is not evidence of test–retest reliability or of agreement between raters.

```references
- cite: Cohen, J. (1960). A coefficient of agreement for nominal scales. Educational and Psychological Measurement, 20(1), 37–46.
  doi: 10.1177/001316446002000104
  supports: The kappa coefficient as chance-corrected agreement for nominal ratings.
  short: the kappa coefficient of agreement
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Kottner, J., Audigé, L., Brorson, S., et al. (2011). Guidelines for Reporting Reliability and Agreement Studies (GRRAS) were proposed. Journal of Clinical Epidemiology, 64(1), 96–106.
  doi: 10.1016/j.jclinepi.2010.03.002
  supports: Reporting requirements for reliability and agreement studies, including categorical ratings.
  short: reporting guidelines for reliability and agreement studies
  type: Journal article
  checked: 2026-11-13, Crossref
```

## How does measurement error affect a study's conclusions?

Random measurement error has predictable consequences:

- in an **outcome**, it adds noise, widening intervals and reducing power, without biasing a difference in means;
- in an **exposure or predictor**, it biases the estimated slope or correlation towards zero (regression dilution), so a true association is underestimated;
- in a **confounder**, it leaves residual confounding after adjustment, which can bias the adjusted estimate in either direction;
- in a **baseline value used to select or classify participants**, it produces regression to the mean and misclassification.

Reviewers should be cautious when a weak association is interpreted as evidence of a weak relationship without considering the reliability of the measures, and when an unreliable variable is said to have been "controlled for". Error that is not random, such as error related to the outcome or differing between groups, can bias results in any direction.

```references
- cite: Hutcheon, J. A., Chiolero, A., & Hanley, J. A. (2010). Random measurement error and regression dilution bias. BMJ, 340, c2289.
  doi: 10.1136/bmj.c2289
  supports: Regression dilution bias from random measurement error in an exposure and when correction is appropriate.
  short: how measurement error attenuates associations
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Common misconceptions

**"The two methods were highly correlated, so they agree."** Incorrect. Correlation measures association, not agreement, and depends on the spread of the sample.

**"There was no significant difference between trials, so the test is reliable."** Incorrect. A difference in means that is not significant says nothing about random error, and imprecise methods are less likely to show a significant difference.

**"The ICC was 0.90, so the measure can detect individual changes."** Not necessarily. That depends on the SEM and the minimal detectable change relative to the change of interest.

**"Reliability is a fixed property of a test."** Incorrect. It depends on the population, the protocol, the raters and the retest interval.

**"The minimal detectable change is the smallest worthwhile change."** Incorrect. One describes measurement error; the other describes what matters.

## Common reviewer red flags

- Agreement or validity claimed from a correlation coefficient alone.
- A paired test that is not significant presented as evidence that two methods agree.
- An ICC reported without its form or without a confidence interval.
- A relative reliability statistic with no absolute measure of error.
- Limits of agreement reported without a prior statement of what difference would be acceptable.
- Heteroscedastic differences ignored in a Bland–Altman analysis.
- Reliability quoted from a different population, protocol or retest interval.
- An average-measures ICC used to support single measurements.
- Individual "responders" identified from changes smaller than the minimal detectable change.
- A reliability study too small to estimate the ICC or limits of agreement with useful precision.

## Quick reviewer checklist

□ The statistic matches the question: reliability, agreement or validity.

□ The ICC model, type and definition are stated, with a confidence interval.

□ An absolute measure of error is reported in the units of measurement.

□ Limits of agreement are judged against a prespecified acceptable difference.

□ Dependence of error on the size of the measurement has been examined.

□ Systematic change between trials has been examined.

□ Reliability evidence comes from a comparable sample and protocol.

□ The consequences of measurement error for the main analysis are considered.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Bland, J. M., & Altman, D. G. (1986). Statistical methods for assessing agreement between two methods of clinical measurement. The Lancet, 327(8476), 307–310.
  doi: 10.1016/S0140-6736(86)90837-8
  supports: The limits of agreement method and why correlation does not measure agreement.
  short: limits of agreement between two methods
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Bland, J. M., & Altman, D. G. (1999). Measuring agreement in method comparison studies. Statistical Methods in Medical Research, 8(2), 135–160.
  doi: 10.1191/096228099673819272
  supports: Extensions of the limits of agreement method.
  short: limits of agreement, including repeated measurements
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Atkinson, G., & Nevill, A. M. (1998). Statistical methods for assessing measurement error (reliability) in variables relevant to sports medicine. Sports Medicine, 26(4), 217–238.
  doi: 10.2165/00007256-199826040-00002
  supports: Statistical methods for assessing measurement error in sports medicine.
  short: assessing measurement error in sports medicine
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Hopkins, W. G. (2000). Measures of reliability in sports medicine and science. Sports Medicine, 30(1), 1–15.
  doi: 10.2165/00007256-200030010-00001
  supports: Typical error, change in the mean and retest correlation as measures of reliability.
  short: typical error and other reliability measures
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Weir, J. P. (2005). Quantifying test-retest reliability using the intraclass correlation coefficient and the SEM. Journal of Strength and Conditioning Research, 19(1), 231–240.
  doi: 10.1519/00124278-200502000-00038
  supports: The intraclass correlation, the standard error of measurement and the minimal difference.
  short: the intraclass correlation and the standard error of measurement
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Shrout, P. E., & Fleiss, J. L. (1979). Intraclass correlations: Uses in assessing rater reliability. Psychological Bulletin, 86(2), 420–428.
  doi: 10.1037/0033-2909.86.2.420
  supports: The forms of the intraclass correlation.
  short: the forms of the intraclass correlation
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Koo, T. K., & Li, M. Y. (2016). A guideline of selecting and reporting intraclass correlation coefficients for reliability research. Journal of Chiropractic Medicine, 15(2), 155–163.
  doi: 10.1016/j.jcm.2016.02.012
  supports: Selecting and reporting intraclass correlation coefficients.
  short: choosing and reporting an intraclass correlation
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Cohen, J. (1960). A coefficient of agreement for nominal scales. Educational and Psychological Measurement, 20(1), 37–46.
  doi: 10.1177/001316446002000104
  supports: Kappa for categorical agreement.
  short: the kappa coefficient of agreement
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Kottner, J., Audigé, L., Brorson, S., et al. (2011). Guidelines for Reporting Reliability and Agreement Studies (GRRAS) were proposed. Journal of Clinical Epidemiology, 64(1), 96–106.
  doi: 10.1016/j.jclinepi.2010.03.002
  supports: Guidelines for reporting reliability and agreement studies.
  short: reporting guidelines for reliability and agreement studies
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Hutcheon, J. A., Chiolero, A., & Hanley, J. A. (2010). Random measurement error and regression dilution bias. BMJ, 340, c2289.
  doi: 10.1136/bmj.c2289
  supports: The effect of random measurement error on estimated associations.
  short: how measurement error attenuates associations
  type: Journal article
  checked: 2026-11-13, Crossref
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
