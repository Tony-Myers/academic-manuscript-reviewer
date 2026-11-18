# Allometric Scaling and Ratio Standards

## Purpose

This guide helps reviewers assess how physiological and performance measurements have been adjusted for differences in body size. It covers the per-kilogram ratio standard and the condition under which it is valid, the bias it introduces when that condition fails, spurious correlation among ratios, allometric (power function) modelling, theoretical and sample-specific exponents, adjustment by analysis of covariance, and how the choice of method can change a study's conclusions. The same reasoning applies to any outcome expressed as a ratio to another variable.

## What reviewers should look for

- Has a variable been divided by body mass (or another size measure) without evidence that the ratio removes the influence of size?
- Is the ratio still correlated with the size variable it was meant to remove?
- Are ratios that share a denominator correlated with one another and the correlation interpreted?
- Is a scaling exponent stated, with its source and, if estimated, its confidence interval?
- Were groups compared using an exponent that may not be common to them?
- Would the conclusion change under a different, defensible scaling method?
- Is the size variable appropriate to the measurement and the question?

## When is a ratio standard valid?

A ratio standard, such as maximal oxygen uptake (VO2max) expressed in ml/kg/min or strength per kg of body mass, removes the influence of body size only if the measurement is **directly proportional** to the size variable: the relationship is a straight line that passes through the origin.

If the relationship is a straight line with a non-zero intercept, or is curved, dividing by body size does not produce a size-independent quantity. The ratio then still varies systematically with size, and comparisons of the ratio between individuals or groups of different size are confounded by the very variable the ratio was meant to remove.

For many physiological and performance measures the proportionality condition does not hold. Reviewers should expect authors who use a ratio to show, or cite evidence, that it does.

```references
- cite: Tanner, J. M. (1949). Fallacy of per-weight and per-surface area standards, and their relation to spurious correlation. Journal of Applied Physiology, 2(1), 1–15.
  doi: 10.1152/jappl.1949.2.1.1
  supports: The condition under which a per-weight ratio standard is valid and the error introduced when it is not.
  short: the fallacy of per-weight ratio standards
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Curran-Everett, D. (2013). Explorations in statistics: The analysis of ratios and normalized data. Advances in Physiology Education, 37(3), 213–219.
  doi: 10.1152/advan.00053.2013
  supports: Why a ratio controls for its denominator only when the relationship is a straight line through the origin.
  short: when a ratio does and does not remove the effect of its denominator
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Albrecht, G. H., Gelvin, B. R., & Hartman, S. E. (1993). Ratios as a size adjustment in morphometrics. American Journal of Physical Anthropology, 91(4), 441–468.
  doi: 10.1002/ajpa.1330910404
  supports: The conditions under which a ratio removes size.
  short: the conditions under which a ratio removes size
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What goes wrong when the ratio standard is used inappropriately?

Many measures, including maximal oxygen uptake (VO2max) and muscle strength, increase with body mass less than proportionally. Dividing by body mass then **over-corrects**: the ratio is negatively related to body mass, so lighter individuals obtain higher values and heavier individuals lower ones, for reasons of arithmetic and not of physiology.

The consequences are predictable. Heavier athletes or groups appear less fit or weaker per kilogram than they are. Differences between groups that differ in size, such as children and adults, men and women, or playing positions, are distorted. Apparent changes over time in a growing or weight-changing group partly reflect the change in mass.

A simple check is available: a properly scaled variable should be uncorrelated with the size variable. A clear negative correlation between a per-kg ratio and body mass shows that the ratio has not done its job, and that comparing individuals or groups on VO2max per kg, or on any similar ratio, is not a fair comparison.

```references
- cite: Nevill, A. M., Ramsbottom, R., & Williams, C. (1992). Scaling physiological measurements for individuals of different body size. European Journal of Applied Physiology and Occupational Physiology, 65(2), 110–117.
  doi: 10.1007/BF00705066
  supports: How the per-kilogram ratio standard over-corrects for body mass and penalises heavier individuals.
  short: log-linear allometric scaling of physiological measurements
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Tanner, J. M. (1949). Fallacy of per-weight and per-surface area standards, and their relation to spurious correlation. Journal of Applied Physiology, 2(1), 1–15.
  doi: 10.1152/jappl.1949.2.1.1
  supports: The systematic error in per-weight standards for individuals who differ in size.
  short: the fallacy of per-weight ratio standards
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Nevill, A. M., & Holder, R. L. (1995). Scaling, normalizing, and per ratio standards: An allometric modeling approach. Journal of Applied Physiology, 79(3), 1027–1031.
  doi: 10.1152/jappl.1995.79.3.1027
  supports: Why a correctly scaled variable should be independent of body size.
  short: allometric modelling compared with ratio standards and linear adjustment
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Why can correlations between ratios be spurious?

When two ratios share a denominator, they are correlated through it even if their numerators are unrelated. The same occurs when a ratio is correlated with its own denominator, or with another variable that contains it. Two per-kilogram measures will tend to correlate simply because both were divided by body mass.

Such a correlation says little about the relationship between the underlying quantities. The same issue affects regression analyses in which ratios appear as outcome or predictor.

The sounder approach is to analyse the numerator as the outcome and include the denominator as a covariate, so that the relationship with size is estimated from the data instead of being imposed by division.

```references
- cite: Kronmal, R. A. (1993). Spurious correlation and the fallacy of the ratio standard revisited. Journal of the Royal Statistical Society: Series A (Statistics in Society), 156(3), 379–392.
  doi: 10.2307/2983064
  supports: Spurious correlation among ratios with a common denominator and the recommendation to use the denominator as a covariate.
  short: spurious correlation among ratio variables
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Tanner, J. M. (1949). Fallacy of per-weight and per-surface area standards, and their relation to spurious correlation. Journal of Applied Physiology, 2(1), 1–15.
  doi: 10.1152/jappl.1949.2.1.1
  supports: The relation between per-weight standards and spurious correlation.
  short: the fallacy of per-weight ratio standards
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Curran-Everett, D. (2013). Explorations in statistics: The analysis of ratios and normalized data. Advances in Physiology Education, 37(3), 213–219.
  doi: 10.1152/advan.00053.2013
  supports: Analysing the numerator with the denominator as a covariate in place of a ratio.
  short: when a ratio does and does not remove the effect of its denominator
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What is allometric scaling?

Allometric scaling models a measurement Y as a power function of body size: Y = a × M^b, where b is the scaling exponent. Taking logarithms gives a straight line, log Y = log a + b × log M, which can be fitted by linear regression. Dividing Y by M raised to the power b gives a "power function ratio" that is, in the sample, independent of body size.

The model has two properties that suit physiological data. It passes through the origin, so a body of zero mass is predicted to have zero output. And fitting it on the log scale assumes a multiplicative error, which accommodates the usual pattern in which the scatter of the measurement increases with body size.

The ratio standard is the special case in which b equals 1. Whether b can be taken as 1 is therefore an empirical question that the model can answer.

```references
- cite: Nevill, A. M., Ramsbottom, R., & Williams, C. (1992). Scaling physiological measurements for individuals of different body size. European Journal of Applied Physiology and Occupational Physiology, 65(2), 110–117.
  doi: 10.1007/BF00705066
  supports: The log-linear allometric model and the power function ratio for scaling physiological measurements.
  short: log-linear allometric scaling of physiological measurements
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Nevill, A. M., & Holder, R. L. (1995). Scaling, normalizing, and per ratio standards: An allometric modeling approach. Journal of Applied Physiology, 79(3), 1027–1031.
  doi: 10.1152/jappl.1995.79.3.1027
  supports: The allometric model with multiplicative error compared with ratio standards and linear regression adjustment.
  short: allometric modelling compared with ratio standards and linear adjustment
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Which exponent should be used?

Two approaches are in use and each has weaknesses.

**Theoretical exponents** come from dimensional reasoning. Geometric similarity predicts that areas, and therefore quantities such as muscle force and maximal oxygen uptake, scale with body mass raised to the power two-thirds; an exponent of three-quarters is also widely cited for metabolic rate. These values are independent of the sample but may not describe a particular population or measurement.

**Sample-specific exponents** are estimated from the study data. They fit the sample, but they are estimates with sampling error, they are influenced by the sample's range of body size and its composition, and they do not transfer reliably to other samples.

Reviewers should expect the exponent to be stated with its source, an estimated exponent to be given with a confidence interval, and the conclusions not to depend on a value chosen without justification. A pooled analysis of studies of maximal oxygen uptake found a body mass exponent well below 1, at approximately 0.7.

```references
- cite: Jaric, S., Mirkov, D., & Markovic, G. (2005). Normalizing physical performance tests for body size: A proposal for standardization. Journal of Strength and Conditioning Research, 19(2), 467–474.
  doi: 10.1519/R-15064.1
  supports: Theoretical exponents for normalising different types of physical performance test for body size.
  short: theoretical exponents for normalising performance tests
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Lolli, L., Batterham, A. M., Weston, K. L., & Atkinson, G. (2017). Size exponents for scaling maximal oxygen uptake in over 6500 humans: A systematic review and meta-analysis. Sports Medicine, 47(7), 1405–1419.
  doi: 10.1007/s40279-016-0655-1
  supports: Empirical estimates of the size exponent for maximal oxygen uptake from a systematic review and meta-analysis.
  short: empirical size exponents for maximal oxygen uptake
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Nevill, A. M., Ramsbottom, R., & Williams, C. (1992). Scaling physiological measurements for individuals of different body size. European Journal of Applied Physiology and Occupational Physiology, 65(2), 110–117.
  doi: 10.1007/BF00705066
  supports: Estimating the mass exponent from sample data.
  short: log-linear allometric scaling of physiological measurements
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Can groups be compared after allometric scaling?

Only with care. Comparing groups on a power function ratio assumes that a single exponent applies to all of them. If the relationship with body size differs between groups, scaling everyone by one exponent leaves size-related bias in the comparison.

The common-exponent assumption can be examined by fitting the log-linear model with group as a factor and testing, or better estimating, the interaction between group and log body size. Where a common exponent is reasonable, the group difference can be estimated within the same model, which is preferable to computing ratios first and comparing them afterwards because the uncertainty in the exponent is carried into the comparison.

Body mass is not always the right size variable. Fat-free mass, stature or limb dimensions may be more relevant, and more than one can be included. In samples that differ in body composition, scaling by total body mass penalises those with more fat mass.

```references
- cite: Nevill, A. M., Bate, S., & Holder, R. L. (2005). Modeling physiological and anthropometric variables known to vary with body size and other confounding variables. American Journal of Physical Anthropology, 128(S41), 141–153.
  doi: 10.1002/ajpa.20356
  supports: Multiplicative allometric models that include group effects and several body size variables, and testing for a common exponent.
  short: multiplicative allometric models with covariates
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Nevill, A. M., & Holder, R. L. (1995). Scaling, normalizing, and per ratio standards: An allometric modeling approach. Journal of Applied Physiology, 79(3), 1027–1031.
  doi: 10.1152/jappl.1995.79.3.1027
  supports: Comparing groups within an allometric model.
  short: allometric modelling compared with ratio standards and linear adjustment
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Is analysis of covariance an acceptable alternative?

Adjusting for body size by including it as a covariate in a linear model avoids the main fault of the ratio standard, because the relationship with size is estimated instead of assumed. It has been recommended in preference to ratios and percentages.

Its limitations are that an ordinary linear model implies a non-zero intercept, which is implausible for many physiological variables when extrapolated, and that it assumes constant scatter across body size, which often does not hold. The allometric model addresses both. In practice the two approaches frequently lead to similar conclusions within the range of the data, and either is preferable to an unexamined ratio.

There is also debate about fitting allometric models on the log scale as opposed to fitting the power function directly on the original scale. The choice should follow the error structure of the data: log-scale fitting suits multiplicative error, and its back-transformed predictions are geometric means (see the note on transformations).

```references
- cite: Packard, G. C., & Boardman, T. J. (1999). The use of percentages and size-specific indices to normalize physiological data for variation in body size: Wasted time, wasted effort? Comparative Biochemistry and Physiology Part A: Molecular & Integrative Physiology, 122(1), 37–44.
  doi: 10.1016/S1095-6433(98)10170-8
  supports: Why ratios and percentages fail to remove body size and why analysis of covariance is preferable.
  short: why ratios fail to remove body size and analysis of covariance is preferable
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Nevill, A. M., & Holder, R. L. (1995). Scaling, normalizing, and per ratio standards: An allometric modeling approach. Journal of Applied Physiology, 79(3), 1027–1031.
  doi: 10.1152/jappl.1995.79.3.1027
  supports: The limitations of linear regression adjustment compared with the allometric model.
  short: allometric modelling compared with ratio standards and linear adjustment
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Packard, G. C. (2009). On the use of logarithmic transformations in allometric analyses. Journal of Theoretical Biology, 257(3), 515–518.
  doi: 10.1016/j.jtbi.2008.10.016
  supports: Criticism of fitting allometric relationships on the logarithmic scale.
  short: criticism of fitting allometric models on the log scale
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Xiao, X., White, E. P., Hooten, M. B., & Durham, S. L. (2011). On the use of log-transformation vs. nonlinear regression for analyzing biological power laws. Ecology, 92(10), 1887–1894.
  doi: 10.1890/11-0538.1
  supports: Choosing between log-linear and nonlinear fitting according to the error structure.
  short: log transformation compared with nonlinear regression
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Can the choice of scaling method change the conclusions?

Yes, and this is the main reason the issue matters to a reviewer. The same data can show a group difference under one scaling method and none, or the opposite, under another. Comparisons of peak oxygen uptake (peak VO2) between children and adults, and between males and females, are established examples: conclusions drawn from per-kg values differ from those obtained with allometric modelling.

Where a study's finding depends on a size-adjusted comparison, reviewers should ask whether the authors have shown it to be robust to the method of adjustment. A finding that appears only with the ratio standard, in groups that differ in body size, should be treated as unsafe.

The same applies to correlations and regression analyses that use per-kilogram variables, and to longitudinal studies in which body mass changes.

```references
- cite: Welsman, J. R., Armstrong, N., Nevill, A. M., Winter, E. M., & Kirby, B. J. (1996). Scaling peak VO2 for differences in body size. Medicine & Science in Sports & Exercise, 28(2), 259–265.
  doi: 10.1097/00005768-199602000-00016
  supports: How conclusions about differences in peak oxygen uptake between groups change with the method of scaling for body size.
  short: how conclusions about peak oxygen uptake change with the scaling method
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Atkinson, G., & Batterham, A. M. (2012). The use of ratios and percentage changes in sports medicine: Time for a rethink? International Journal of Sports Medicine, 33(7), 505–506.
  doi: 10.1055/s-0032-1316355
  supports: The problems created by ratios and percentage changes in sports medicine research.
  short: problems with ratios and percentage changes in sports medicine
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What should be reported?

- The size variable used and why it suits the measurement.
- For a ratio standard, evidence that the measurement is proportional to the size variable in this population, such as the absence of a correlation between the ratio and size.
- For allometric scaling, the model, the exponent with its confidence interval or its theoretical source, and a check that the scaled variable is independent of size.
- Where groups are compared, whether a common exponent was assumed and how that was examined.
- The unscaled measurements and the body size data, so that readers can apply other methods.
- Whether the main conclusions hold under an alternative method of adjustment.

## Common misconceptions

**"Dividing by body mass removes the effect of body mass."** Only when the measurement is directly proportional to body mass.

**"Per-kilogram values allow fair comparison between people of different size."** Often they do not; they tend to favour lighter individuals.

**"Two per-kilogram measures were correlated, so the capacities are related."** The shared denominator can produce that correlation.

**"The allometric exponent estimated in this sample is the correct one."** It is an estimate, with uncertainty, specific to the sample.

**"An exponent of 0.67 (or 0.75) applies to everything."** Different measurements and populations scale differently.

**"The method of scaling is a matter of presentation."** It can determine the conclusion.

## Common reviewer red flags

- Per-kilogram ratios used without any check of proportionality.
- Groups of clearly different body size compared on ratio-scaled values.
- A ratio that remains correlated with body mass.
- Correlations between ratios sharing a denominator interpreted substantively.
- A scaling exponent used without source or interval.
- One exponent applied across groups without examining whether it is common to them.
- Ratios computed first and then analysed, instead of size being modelled.
- Scaling by total body mass where body composition differs markedly between groups.
- Conclusions that rest on one scaling method with no sensitivity analysis.

## Quick reviewer checklist

□ The method of adjusting for body size is stated and justified.

□ The adjusted variable has been shown to be independent of body size.

□ Any exponent is reported with its source or interval.

□ A common exponent across groups has been examined where groups are compared.

□ Ratios with shared denominators are not correlated and interpreted.

□ Conclusions are robust to a defensible alternative method.

□ Unscaled data are available.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Tanner, J. M. (1949). Fallacy of per-weight and per-surface area standards, and their relation to spurious correlation. Journal of Applied Physiology, 2(1), 1–15.
  doi: 10.1152/jappl.1949.2.1.1
  supports: The fallacy of per-weight and per-surface-area standards.
  short: the fallacy of per-weight ratio standards
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Nevill, A. M., Ramsbottom, R., & Williams, C. (1992). Scaling physiological measurements for individuals of different body size. European Journal of Applied Physiology and Occupational Physiology, 65(2), 110–117.
  doi: 10.1007/BF00705066
  supports: Scaling physiological measurements for body size.
  short: log-linear allometric scaling of physiological measurements
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Nevill, A. M., & Holder, R. L. (1995). Scaling, normalizing, and per ratio standards: An allometric modeling approach. Journal of Applied Physiology, 79(3), 1027–1031.
  doi: 10.1152/jappl.1995.79.3.1027
  supports: Allometric modelling compared with ratio standards.
  short: allometric modelling compared with ratio standards and linear adjustment
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Nevill, A. M., Bate, S., & Holder, R. L. (2005). Modeling physiological and anthropometric variables known to vary with body size and other confounding variables. American Journal of Physical Anthropology, 128(S41), 141–153.
  doi: 10.1002/ajpa.20356
  supports: Allometric models with covariates and several size variables.
  short: multiplicative allometric models with covariates
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Welsman, J. R., Armstrong, N., Nevill, A. M., Winter, E. M., & Kirby, B. J. (1996). Scaling peak VO2 for differences in body size. Medicine & Science in Sports & Exercise, 28(2), 259–265.
  doi: 10.1097/00005768-199602000-00016
  supports: Scaling peak oxygen uptake.
  short: how conclusions about peak oxygen uptake change with the scaling method
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Curran-Everett, D. (2013). Explorations in statistics: The analysis of ratios and normalized data. Advances in Physiology Education, 37(3), 213–219.
  doi: 10.1152/advan.00053.2013
  supports: The analysis of ratios and normalised data.
  short: when a ratio does and does not remove the effect of its denominator
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Kronmal, R. A. (1993). Spurious correlation and the fallacy of the ratio standard revisited. Journal of the Royal Statistical Society: Series A (Statistics in Society), 156(3), 379–392.
  doi: 10.2307/2983064
  supports: Spurious correlation and ratio standards.
  short: spurious correlation among ratio variables
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Albrecht, G. H., Gelvin, B. R., & Hartman, S. E. (1993). Ratios as a size adjustment in morphometrics. American Journal of Physical Anthropology, 91(4), 441–468.
  doi: 10.1002/ajpa.1330910404
  supports: Ratios as a size adjustment.
  short: the conditions under which a ratio removes size
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Packard, G. C., & Boardman, T. J. (1999). The use of percentages and size-specific indices to normalize physiological data for variation in body size: Wasted time, wasted effort? Comparative Biochemistry and Physiology Part A: Molecular & Integrative Physiology, 122(1), 37–44.
  doi: 10.1016/S1095-6433(98)10170-8
  supports: Ratios and size-specific indices compared with analysis of covariance.
  short: why ratios fail to remove body size and analysis of covariance is preferable
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Packard, G. C. (2009). On the use of logarithmic transformations in allometric analyses. Journal of Theoretical Biology, 257(3), 515–518.
  doi: 10.1016/j.jtbi.2008.10.016
  supports: Logarithmic transformation in allometric analyses.
  short: criticism of fitting allometric models on the log scale
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Jaric, S., Mirkov, D., & Markovic, G. (2005). Normalizing physical performance tests for body size: A proposal for standardization. Journal of Strength and Conditioning Research, 19(2), 467–474.
  doi: 10.1519/R-15064.1
  supports: Normalising performance tests for body size.
  short: theoretical exponents for normalising performance tests
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Lolli, L., Batterham, A. M., Weston, K. L., & Atkinson, G. (2017). Size exponents for scaling maximal oxygen uptake in over 6500 humans: A systematic review and meta-analysis. Sports Medicine, 47(7), 1405–1419.
  doi: 10.1007/s40279-016-0655-1
  supports: Size exponents for maximal oxygen uptake.
  short: empirical size exponents for maximal oxygen uptake
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Atkinson, G., & Batterham, A. M. (2012). The use of ratios and percentage changes in sports medicine: Time for a rethink? International Journal of Sports Medicine, 33(7), 505–506.
  doi: 10.1055/s-0032-1316355
  supports: Ratios and percentage changes in sports medicine.
  short: problems with ratios and percentage changes in sports medicine
  type: Journal article
  checked: 2026-11-14, Crossref
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
