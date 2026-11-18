# Publication Bias and Small-Study Effects in Meta-Analysis

## Purpose

This guide helps reviewers assess how a systematic review or meta-analysis has dealt with the possibility that the available studies are a biased sample of the research conducted. It covers reporting biases, funnel plots and their interpretation, tests for funnel plot asymmetry, trim-and-fill and other adjustment methods, and what can and cannot be concluded from them.

## What reviewers should look for

- Does the review consider reporting biases at all, and by what methods?
- Were unpublished studies, trial registries and protocols searched?
- Is funnel plot asymmetry interpreted as publication bias without considering other explanations?
- Was an asymmetry test used with too few studies, or with studies of similar size?
- Is an asymmetry test that is not significant presented as evidence that there is no bias?
- Is an "adjusted" estimate (for example from trim-and-fill) presented as the corrected truth instead of as a sensitivity analysis?
- Do the conclusions reflect the uncertainty that possible reporting bias adds?

## What are reporting biases and small-study effects?

**Publication bias** arises when whether a study is published depends on its results, typically on statistical significance or direction. It is one of several **reporting biases**: selective reporting of outcomes or analyses within published studies, delayed publication of unfavourable results, and publication in less accessible sources have similar consequences.

**Small-study effects** is the descriptive term for a tendency of smaller studies in a meta-analysis to show larger effects than larger ones. Publication bias is one cause, because small studies need large estimates to reach significance. It is not the only one, which is why the descriptive term is preferred when all that has been observed is the pattern.

The practical consequence is that a pooled estimate can overstate an effect, or show one where none exists, however carefully the meta-analysis is carried out.

```references
- cite: Sterne, J. A. C., Sutton, A. J., Ioannidis, J. P. A., et al. (2011). Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. BMJ, 343, d4002.
  doi: 10.1136/bmj.d4002
  supports: Small-study effects as a broader phenomenon than publication bias, and the forms of reporting bias.
  short: recommendations on funnel plots and asymmetry tests
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Page, M. J., McKenzie, J. E., Bossuyt, P. M., et al. (2021). The PRISMA 2020 statement: An updated guideline for reporting systematic reviews. BMJ, 372, n71.
  doi: 10.1136/bmj.n71
  supports: The expectation that a systematic review reports how risk of bias due to missing results was assessed.
  short: the PRISMA 2020 reporting guideline
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

## What does a funnel plot show?

A funnel plot displays each study's effect estimate against a measure of its precision, usually the standard error. If the studies estimate a common effect and differ only by sampling error, the points should scatter symmetrically around the pooled estimate, more widely for the less precise studies, giving an inverted funnel.

Asymmetry, typically a shortage of small studies on the side of null or unfavourable results, is the pattern expected if such studies are missing. Reading a funnel plot is subjective, and with few studies the eye is easily misled: an apparently lopsided plot of eight studies is unremarkable.

```references
- cite: Sterne, J. A. C., Sutton, A. J., Ioannidis, J. P. A., et al. (2011). Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. BMJ, 343, d4002.
  doi: 10.1136/bmj.d4002
  supports: The construction and interpretation of funnel plots.
  short: recommendations on funnel plots and asymmetry tests
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Egger, M., Davey Smith, G., Schneider, M., & Minder, C. (1997). Bias in meta-analysis detected by a simple, graphical test. BMJ, 315(7109), 629–634.
  doi: 10.1136/bmj.315.7109.629
  supports: Funnel plot asymmetry as a signal of bias in meta-analysis.
  short: the regression test for funnel plot asymmetry
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Does funnel plot asymmetry demonstrate publication bias?

No. Asymmetry shows that smaller studies gave different results from larger ones. Possible reasons include:

- publication and other reporting biases;
- poorer methodological quality in smaller studies, inflating their estimates;
- genuine heterogeneity, where smaller studies differ in population, intervention intensity or setting in ways that change the true effect;
- a mathematical relationship between the effect estimate and its standard error, which holds for odds ratios and for standardised mean differences and can produce asymmetry in the absence of any bias;
- chance.

Reviewers should expect authors to consider these alternatives before attributing asymmetry to unpublished studies, and to examine whether study size is associated with study characteristics.

```references
- cite: Sterne, J. A. C., Sutton, A. J., Ioannidis, J. P. A., et al. (2011). Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. BMJ, 343, d4002.
  doi: 10.1136/bmj.d4002
  supports: The alternative explanations for funnel plot asymmetry and how to distinguish among them.
  short: recommendations on funnel plots and asymmetry tests
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Peters, J. L., Sutton, A. J., Jones, D. R., Abrams, K. R., & Rushton, L. (2008). Contour-enhanced meta-analysis funnel plots help distinguish publication bias from other causes of asymmetry. Journal of Clinical Epidemiology, 61(10), 991–996.
  doi: 10.1016/j.jclinepi.2007.11.010
  supports: Using contours of statistical significance on a funnel plot to judge whether asymmetry is likely to be due to publication bias.
  short: contour-enhanced funnel plots
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What do contour-enhanced funnel plots add?

A contour-enhanced funnel plot overlays regions corresponding to conventional levels of statistical significance. If the studies that appear to be missing would have fallen in the region of results that are not significant, selective publication on the basis of significance is a plausible explanation. If the apparently missing studies would have been statistically significant, publication bias is a less likely cause and other explanations for the asymmetry deserve more weight.

This is an aid to interpretation, not a test, and it shares the limits of any funnel plot when studies are few.

```references
- cite: Peters, J. L., Sutton, A. J., Jones, D. R., Abrams, K. R., & Rushton, L. (2008). Contour-enhanced meta-analysis funnel plots help distinguish publication bias from other causes of asymmetry. Journal of Clinical Epidemiology, 61(10), 991–996.
  doi: 10.1016/j.jclinepi.2007.11.010
  supports: Contour-enhanced funnel plots and how they help distinguish publication bias from other causes of asymmetry.
  short: contour-enhanced funnel plots
  type: Journal article
  checked: 2026-11-13, Crossref
```

## When are tests for funnel plot asymmetry appropriate?

Egger's regression test and related tests examine whether effect estimates are associated with their precision. Published recommendations are that such tests:

- should generally be used only when there are at least ten studies, because with fewer the power is too low to distinguish chance from real asymmetry;
- should not be used when the studies are all of similar size, since there is then little variation in precision to work with;
- should be interpreted cautiously when heterogeneity is substantial;
- should take account of the outcome measure: for odds ratios the standard Egger test has an inflated false-positive rate, and tests designed for binary outcomes are preferable.

A test result should be reported and interpreted together with the funnel plot, never in place of it.

```references
- cite: Sterne, J. A. C., Sutton, A. J., Ioannidis, J. P. A., et al. (2011). Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. BMJ, 343, d4002.
  doi: 10.1136/bmj.d4002
  supports: Recommendations on when asymmetry tests should and should not be used, including the ten-study guidance and the choice of test for binary outcomes.
  short: recommendations on funnel plots and asymmetry tests
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Egger, M., Davey Smith, G., Schneider, M., & Minder, C. (1997). Bias in meta-analysis detected by a simple, graphical test. BMJ, 315(7109), 629–634.
  doi: 10.1136/bmj.315.7109.629
  supports: The regression test for funnel plot asymmetry.
  short: the regression test for funnel plot asymmetry
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Does a non-significant asymmetry test rule out publication bias?

No. Asymmetry tests have low power in the number of studies typical of a meta-analysis, so a non-significant result is weak evidence of symmetry. Publication bias can also operate without producing asymmetry, for example when studies are suppressed on significance in either direction, or when all the studies are small.

Statements such as "Egger's test was not significant (p = 0.21), indicating no publication bias" claim more than the test can deliver. The defensible statement is that no asymmetry was detected, with the number of studies and the limited power acknowledged.

```references
- cite: Sterne, J. A. C., Sutton, A. J., Ioannidis, J. P. A., et al. (2011). Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. BMJ, 343, d4002.
  doi: 10.1136/bmj.d4002
  supports: The low power of asymmetry tests and the caution needed in interpreting their results.
  short: recommendations on funnel plots and asymmetry tests
  type: Journal article
  checked: 2026-11-13, Crossref
```

## How should trim-and-fill results be interpreted?

Trim-and-fill estimates the number of studies "missing" from one side of the funnel plot, imputes them as mirror images of the most extreme observed studies, and recalculates the pooled estimate.

It rests on the assumption that asymmetry is caused entirely by suppression of the most extreme results on one side. Where asymmetry has another cause, such as heterogeneity, it imputes studies that never existed. In simulations it can both under-correct when bias is real and "correct" when there is none.

The adjusted estimate should therefore be read as a sensitivity analysis showing how the conclusion might change under one particular model of missing studies. It is not an unbiased estimate of the true effect, and the number of imputed studies is not a count of unpublished ones.

```references
- cite: Duval, S., & Tweedie, R. (2000). Trim and fill: A simple funnel-plot-based method of testing and adjusting for publication bias in meta-analysis. Biometrics, 56(2), 455–463.
  doi: 10.1111/j.0006-341X.2000.00455.x
  supports: The trim-and-fill method and its assumptions.
  short: the trim-and-fill method
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Carter, E. C., Schönbrodt, F. D., Gervais, W. M., & Hilgard, J. (2019). Correcting for bias in psychology: A comparison of meta-analytic methods. Advances in Methods and Practices in Psychological Science, 2(2), 115–144.
  doi: 10.1177/2515245919847196
  supports: The performance of trim-and-fill and other bias-correction methods under publication bias, questionable research practices and heterogeneity.
  short: how bias-correction methods perform
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Are other bias-adjustment methods more trustworthy?

Several other approaches exist: regression-based adjustments that extrapolate to a study of infinite precision (such as PET-PEESE), selection models that estimate how publication probability depends on the p-value, and methods based on the distribution of significant p-values.

Simulation comparisons find that no method performs well under all conditions. Performance depends on the degree of heterogeneity, the amount and form of selection, and the number of studies, none of which is known in a real meta-analysis. Different methods can give materially different adjusted estimates from the same data.

The reasonable expectation is therefore that authors apply more than one method as sensitivity analyses, report all of them, and treat agreement among methods as reassuring and disagreement as genuine uncertainty. Selecting the adjustment that gives the preferred answer is itself a reporting bias.

```references
- cite: Carter, E. C., Schönbrodt, F. D., Gervais, W. M., & Hilgard, J. (2019). Correcting for bias in psychology: A comparison of meta-analytic methods. Advances in Methods and Practices in Psychological Science, 2(2), 115–144.
  doi: 10.1177/2515245919847196
  supports: A simulation comparison of bias-correction methods showing that none performs well in all conditions and recommending their use as sensitivity analyses.
  short: how bias-correction methods perform
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What should be done beyond statistical methods?

Statistical methods detect patterns in the studies that were found; they cannot find the studies that were not. Stronger protection comes from the conduct of the review:

- searching trial registries, conference proceedings, theses and regulatory documents, and contacting investigators;
- comparing published outcomes with protocols and registry entries to detect selectively reported outcomes;
- noting registered studies with no published results;
- prespecifying the review's own outcomes and analyses in a registered protocol.

Reporting guidance for systematic reviews asks authors to describe how they assessed the risk of bias due to missing results and to present the findings of that assessment for each synthesis.

```references
- cite: Page, M. J., McKenzie, J. E., Bossuyt, P. M., et al. (2021). The PRISMA 2020 statement: An updated guideline for reporting systematic reviews. BMJ, 372, n71.
  doi: 10.1136/bmj.n71
  supports: The reporting items covering the search for unpublished studies, protocol registration and assessment of bias due to missing results.
  short: the PRISMA 2020 reporting guideline
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

## How should possible reporting bias affect the conclusions?

Where reporting bias is plausible, the pooled estimate should be presented as potentially overstated, and the certainty of the evidence lowered accordingly.

Useful checks include whether the conclusion survives restricting the analysis to the larger or to the preregistered studies, and whether fixed-effect and random-effects estimates differ. A random-effects model gives relatively more weight to small studies than a fixed-effect model, so when small studies show larger effects the random-effects estimate is pulled further towards them. A marked difference between the two estimates is itself a sign of small-study effects.

```references
- cite: Sterne, J. A. C., Sutton, A. J., Ioannidis, J. P. A., et al. (2011). Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. BMJ, 343, d4002.
  doi: 10.1136/bmj.d4002
  supports: Comparing fixed-effect and random-effects estimates as a check on the influence of small-study effects.
  short: recommendations on funnel plots and asymmetry tests
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Common misconceptions

**"The funnel plot was asymmetric, so there is publication bias."** Not necessarily. Heterogeneity, study quality, the choice of effect measure and chance can all produce asymmetry.

**"Egger's test was not significant, so there is no publication bias."** Incorrect. The test has low power with few studies, and absence of detected asymmetry is not evidence of absence of bias.

**"Trim-and-fill gives the corrected effect."** Incorrect. It gives the estimate under one assumed mechanism and is best treated as a sensitivity analysis.

**"The fail-safe N is large, so the result is robust to unpublished studies."** Unsafe. The fail-safe N assumes that unpublished studies average exactly zero effect and ignores heterogeneity and study size; it is no longer regarded as an adequate assessment.

**"A comprehensive database search rules out publication bias."** Incorrect. A thorough search of published literature cannot retrieve results that were never published.

## Common reviewer red flags

- No assessment of reporting bias, or none planned in the protocol.
- Asymmetry tests applied to fewer than ten studies without comment.
- Funnel plot asymmetry equated with publication bias.
- A test that is not significant reported as showing no bias.
- A trim-and-fill or other adjusted estimate presented as the main result.
- Only one adjustment method reported.
- Searches limited to published, English-language journal articles.
- No comparison of reported outcomes with protocols or registry entries.
- Conclusions stated with confidence despite signs of small-study effects.

## Quick reviewer checklist

□ Reporting biases are considered and the methods described.

□ Unpublished and registered studies were sought.

□ Funnel plots are shown where there are enough studies, and interpreted with alternative explanations in mind.

□ Asymmetry tests are used only where appropriate and suited to the effect measure.

□ Tests that are not significant are not presented as evidence of no bias.

□ Adjusted estimates are presented as sensitivity analyses, preferably from more than one method.

□ Conclusions and the stated certainty of evidence reflect possible reporting bias.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Sterne, J. A. C., Sutton, A. J., Ioannidis, J. P. A., et al. (2011). Recommendations for examining and interpreting funnel plot asymmetry in meta-analyses of randomised controlled trials. BMJ, 343, d4002.
  doi: 10.1136/bmj.d4002
  supports: Recommendations for examining and interpreting funnel plot asymmetry.
  short: recommendations on funnel plots and asymmetry tests
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Egger, M., Davey Smith, G., Schneider, M., & Minder, C. (1997). Bias in meta-analysis detected by a simple, graphical test. BMJ, 315(7109), 629–634.
  doi: 10.1136/bmj.315.7109.629
  supports: The regression test for funnel plot asymmetry.
  short: the regression test for funnel plot asymmetry
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Peters, J. L., Sutton, A. J., Jones, D. R., Abrams, K. R., & Rushton, L. (2008). Contour-enhanced meta-analysis funnel plots help distinguish publication bias from other causes of asymmetry. Journal of Clinical Epidemiology, 61(10), 991–996.
  doi: 10.1016/j.jclinepi.2007.11.010
  supports: Contour-enhanced funnel plots.
  short: contour-enhanced funnel plots
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Duval, S., & Tweedie, R. (2000). Trim and fill: A simple funnel-plot-based method of testing and adjusting for publication bias in meta-analysis. Biometrics, 56(2), 455–463.
  doi: 10.1111/j.0006-341X.2000.00455.x
  supports: The trim-and-fill method.
  short: the trim-and-fill method
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Carter, E. C., Schönbrodt, F. D., Gervais, W. M., & Hilgard, J. (2019). Correcting for bias in psychology: A comparison of meta-analytic methods. Advances in Methods and Practices in Psychological Science, 2(2), 115–144.
  doi: 10.1177/2515245919847196
  supports: A comparison of methods for correcting meta-analyses for bias.
  short: how bias-correction methods perform
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Page, M. J., McKenzie, J. E., Bossuyt, P. M., et al. (2021). The PRISMA 2020 statement: An updated guideline for reporting systematic reviews. BMJ, 372, n71.
  doi: 10.1136/bmj.n71
  supports: Reporting guidance for systematic reviews, including bias due to missing results.
  short: the PRISMA 2020 reporting guideline
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
