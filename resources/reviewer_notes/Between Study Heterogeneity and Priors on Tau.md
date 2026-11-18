# Between-Study Heterogeneity and Priors on Tau

#### Purpose

This guide helps reviewers evaluate between-study heterogeneity in frequentist and Bayesian meta-analysis. It focuses on the heterogeneity standard deviation τ (tau), heterogeneity variance τ², priors on τ, sensitivity analysis, and why uncertainty about heterogeneity becomes particularly important when few studies are available.

#### What reviewers should look for

✓ The manuscript distinguishes sampling error from genuine between-study heterogeneity.

✓ A random-effects model reports the estimated heterogeneity parameter, usually τ or τ².

✓ In Bayesian meta-analysis, the prior distribution for τ is explicitly reported and justified.

✓ Prior sensitivity is assessed when the number of studies is small or heterogeneity is weakly identified.

✓ The consequences of heterogeneity for interpretation of the pooled effect are discussed.

✓ Prediction intervals are considered where the aim is to understand the range of effects expected in future studies or settings.

#### Common reviewer questions

##### What is between-study heterogeneity?

**Between-study heterogeneity** is genuine variation in underlying study effects beyond sampling error.

In a random-effects meta-analysis, study-specific effects are assumed to vary around an overall mean effect.

Heterogeneity is commonly described using:

- **τ (tau)** – the between-study standard deviation;
- **τ² (tau-squared)** – the between-study variance;
- **I²** – the proportion of observed variation attributed to heterogeneity rather than sampling error.

These quantities are related but are not interchangeable.

```references
- cite: Higgins, J. P. T., & Thompson, S. G. (2002). Quantifying heterogeneity in a meta-analysis. Statistics in Medicine, 21(11), 1539–1558.
  doi: 10.1002/sim.1186
  supports: The I² statistic and its relation to the between-study variance.
  short: the I² statistic and what it measures
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Borenstein, M., Higgins, J. P. T., Hedges, L. V., & Rothstein, H. R. (2017). Basics of meta-analysis: I² is not an absolute measure of heterogeneity. Research Synthesis Methods, 8(1), 5–18.
  doi: 10.1002/jrsm.1230
  supports: Why I² is a proportion and not a measure of how much effects vary.
  short: why I² is not an absolute measure of heterogeneity
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### Why does τ matter?

τ is expressed on the same scale as the meta-analytic effect measure.

A larger τ indicates greater variation in true study effects.

When heterogeneity is substantial, the pooled mean effect may describe the evidence poorly if presented without acknowledging that effects may differ considerably between settings.

##### How is τ estimated in a frequentist meta-analysis?

Several estimators are in use, including DerSimonian-Laird, restricted maximum likelihood (REML) and Paule-Mandel.

They do not give the same answer, and the differences matter most when studies are few. DerSimonian-Laird tends to underestimate heterogeneity in small meta-analyses, which narrows the confidence interval around the pooled effect and overstates precision.

The Hartung-Knapp adjustment is often recommended to give better interval coverage when the number of studies is small. It usually widens the interval, but where the estimated heterogeneity is zero or the studies are very similar it can produce an interval narrower than the unadjusted one, so it is worth checking that the adjusted interval is not the narrower of the two.

Reviewers should expect the estimator, and any adjustment, to be named rather than described only as "a random-effects model".

```references
- cite: Veroniki, A. A., Jackson, D., Viechtbauer, W., et al. (2016). Methods to estimate the between-study variance and its uncertainty in meta-analysis. Research Synthesis Methods, 7(1), 55–79.
  doi: 10.1002/jrsm.1164
  supports: The estimators of the between-study variance and how they compare.
  short: estimators of the between-study variance
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: IntHout, J., Ioannidis, J. P. A., & Borm, G. F. (2014). The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. BMC Medical Research Methodology, 14, 25.
  doi: 10.1186/1471-2288-14-25
  supports: The Hartung–Knapp adjustment and its coverage compared with the DerSimonian–Laird method.
  short: the Hartung–Knapp adjustment compared with DerSimonian–Laird
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### Why does the prior on τ matter in Bayesian meta-analysis?

A Bayesian random-effects model requires a prior distribution for τ.

When many informative studies are available, the likelihood may dominate the prior.

When few studies are available, the data often contain little information about heterogeneity, so the posterior distribution of τ can depend appreciably on the prior.

The choice of prior may therefore affect:

- the estimated heterogeneity;
- uncertainty around the pooled effect;
- credible intervals;
- prediction intervals;
- treatment rankings or other downstream summaries.

##### Why is sensitivity analysis most important when there are few studies?

Estimating heterogeneity is intrinsically difficult with a small number of studies.

A sparse dataset may support a wide range of plausible τ values.

Reviewers should therefore ask whether conclusions remain similar under several reasonable heterogeneity priors rather than relying on a single default prior.

##### What kinds of prior may be used for τ?

Common choices include positive-valued distributions such as:

- half-Normal;
- half-*t*;
- half-Cauchy;
- log-Normal;
- empirically informed heterogeneity priors.

There is no universally correct prior.

The scale of the prior should make sense for the effect measure being synthesised.

```references
- cite: Röver, C., Bender, R., Dias, S., et al. (2021). On weakly informative prior distributions for the heterogeneity parameter in Bayesian random-effects meta-analysis. Research Synthesis Methods, 12(4), 448–474.
  doi: 10.1002/jrsm.1475
  supports: Weakly informative priors for the heterogeneity parameter and how to choose their scale.
  short: weakly informative priors for the heterogeneity parameter
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Turner, R. M., Jackson, D., Wei, Y., Thompson, S. G., & Higgins, J. P. T. (2015). Predictive distributions for between-study heterogeneity and simple methods for their application in Bayesian meta-analysis. Statistics in Medicine, 34(6), 984–998.
  doi: 10.1002/sim.6381
  supports: Empirically informed prior distributions for heterogeneity.
  short: empirically informed priors for heterogeneity
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Gelman, A. (2006). Prior distributions for variance parameters in hierarchical models (comment on article by Browne and Draper). Bayesian Analysis, 1(3), 515–534.
  doi: 10.1214/06-BA117A
  supports: Half-t and related priors for hierarchical standard deviations.
  short: priors for hierarchical variance parameters
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### Are inverse-gamma priors on τ² a safe default?

Not reliably.

An inverse-gamma(ε, ε) prior with a very small ε was a common default for hierarchical variances in BUGS-lineage software, and is often described as uninformative.

It is not. Where studies are few, the posterior for τ can depend appreciably on the value chosen for ε, and the prior can place substantial mass away from zero, inflating apparent heterogeneity.

Where such a prior is used, reviewers should expect a sensitivity analysis across alternative scales and families rather than an assertion that the prior was uninformative.

```references
- cite: Gelman, A. (2006). Prior distributions for variance parameters in hierarchical models (comment on article by Browne and Draper). Bayesian Analysis, 1(3), 515–534.
  doi: 10.1214/06-BA117A
  supports: Why inverse-gamma(ε, ε) priors on a hierarchical variance are not uninformative and are sensitive to ε.
  short: priors for hierarchical variance parameters
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### Is using a software default prior necessarily wrong?

No.

A default prior can be reasonable, but reviewers should still expect authors to:

- report it explicitly;
- explain its implications;
- check whether it is appropriate for the effect-size scale;
- assess sensitivity when the evidence is sparse.

##### What is a prediction interval?

A **prediction interval** estimates the range in which the true effect of a future comparable study may plausibly lie.

This answers a different question from the confidence or credible interval around the pooled mean effect.

Prediction intervals become especially informative when heterogeneity is substantial.

```references
- cite: Riley, R. D., Higgins, J. P. T., & Deeks, J. J. (2011). Interpretation of random effects meta-analyses. BMJ, 342, d549.
  doi: 10.1136/bmj.d549
  supports: Prediction intervals in random-effects meta-analysis and how they differ from the interval for the mean effect.
  short: interpreting random-effects meta-analyses and prediction intervals
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: IntHout, J., Ioannidis, J. P. A., Rovers, M. M., & Goeman, J. J. (2016). Plea for routinely presenting prediction intervals in meta-analysis. BMJ Open, 6(7), e010247.
  doi: 10.1136/bmjopen-2015-010247
  supports: Why prediction intervals should be reported routinely.
  short: why prediction intervals should be reported
  type: Journal article
  checked: 2026-11-13, Crossref
```


#### Common misconceptions

##### "A random-effects model removes heterogeneity."

Incorrect.

It models heterogeneity; it does not make heterogeneous studies homogeneous.

##### "I² tells me everything I need to know about heterogeneity."

Incorrect.

I² depends partly on study precision and does not directly express the absolute magnitude of between-study variation.

τ is often more interpretable for modelling purposes.

##### "The prior on τ cannot matter if the treatment-effect prior is weak."

Incorrect.

The heterogeneity prior is a separate component of the model and can materially influence uncertainty when few studies are available.

##### "A pooled effect is sufficient even when heterogeneity is large."

Not necessarily.

Substantial heterogeneity may make prediction intervals and study-level variation more informative than the pooled mean alone.

#### Common terminology

**Heterogeneity** – genuine variation in effects between studies.

**τ (tau)** – between-study standard deviation.

**τ² (tau-squared)** – between-study variance.

**I²** – relative measure of observed variability attributed to heterogeneity.

**Random-effects meta-analysis** – model allowing true study effects to vary.

**Heterogeneity prior** – prior distribution placed on τ in a Bayesian random-effects model.

**Prediction interval** – interval describing plausible effects in a future comparable study.

**DerSimonian-Laird** – method-of-moments estimator of τ², prone to underestimation when studies are few.

**REML** – restricted maximum likelihood estimation of the heterogeneity variance.

**Hartung-Knapp adjustment** – modification improving confidence-interval coverage for the pooled effect in small meta-analyses.

#### Common reviewer red flags

- τ or τ² not reported in a random-effects analysis.
- Prior on τ omitted from a Bayesian analysis.
- Default heterogeneity prior used without explanation.
- No sensitivity analysis despite very few studies.
- Large heterogeneity ignored when interpreting the pooled effect.
- I² treated as the only relevant measure of heterogeneity.
- Prediction interval omitted despite substantial between-study variability.
- Heterogeneity estimator not named in a frequentist analysis.
- An inverse-gamma prior on τ² described as uninformative.

#### Quick reviewer checklist

□ Between-study heterogeneity is explicitly modelled.

□ τ or τ² is reported.

□ The heterogeneity prior is stated and justified in Bayesian analyses.

□ Sensitivity to alternative priors is examined when studies are few.

□ Heterogeneity is incorporated into interpretation of the pooled effect.

□ Prediction intervals are reported or considered where informative.

□ The heterogeneity estimator, or the prior on τ, is named rather than implied.

#### References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Higgins, J. P. T., & Thompson, S. G. (2002). Quantifying heterogeneity in a meta-analysis. Statistics in Medicine, 21(11), 1539–1558.
  doi: 10.1002/sim.1186
  supports: Quantifying heterogeneity with I².
  short: the I² statistic and what it measures
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Borenstein, M., Higgins, J. P. T., Hedges, L. V., & Rothstein, H. R. (2017). Basics of meta-analysis: I² is not an absolute measure of heterogeneity. Research Synthesis Methods, 8(1), 5–18.
  doi: 10.1002/jrsm.1230
  supports: The interpretation of I².
  short: why I² is not an absolute measure of heterogeneity
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Veroniki, A. A., Jackson, D., Viechtbauer, W., et al. (2016). Methods to estimate the between-study variance and its uncertainty in meta-analysis. Research Synthesis Methods, 7(1), 55–79.
  doi: 10.1002/jrsm.1164
  supports: Estimating the between-study variance.
  short: estimators of the between-study variance
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: IntHout, J., Ioannidis, J. P. A., & Borm, G. F. (2014). The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. BMC Medical Research Methodology, 14, 25.
  doi: 10.1186/1471-2288-14-25
  supports: The Hartung–Knapp adjustment.
  short: the Hartung–Knapp adjustment compared with DerSimonian–Laird
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Riley, R. D., Higgins, J. P. T., & Deeks, J. J. (2011). Interpretation of random effects meta-analyses. BMJ, 342, d549.
  doi: 10.1136/bmj.d549
  supports: Interpreting random-effects meta-analyses.
  short: interpreting random-effects meta-analyses and prediction intervals
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: IntHout, J., Ioannidis, J. P. A., Rovers, M. M., & Goeman, J. J. (2016). Plea for routinely presenting prediction intervals in meta-analysis. BMJ Open, 6(7), e010247.
  doi: 10.1136/bmjopen-2015-010247
  supports: Prediction intervals in meta-analysis.
  short: why prediction intervals should be reported
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Gelman, A. (2006). Prior distributions for variance parameters in hierarchical models (comment on article by Browne and Draper). Bayesian Analysis, 1(3), 515–534.
  doi: 10.1214/06-BA117A
  supports: Priors for variance parameters in hierarchical models.
  short: priors for hierarchical variance parameters
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Röver, C., Bender, R., Dias, S., et al. (2021). On weakly informative prior distributions for the heterogeneity parameter in Bayesian random-effects meta-analysis. Research Synthesis Methods, 12(4), 448–474.
  doi: 10.1002/jrsm.1475
  supports: Weakly informative priors for heterogeneity.
  short: weakly informative priors for the heterogeneity parameter
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Turner, R. M., Jackson, D., Wei, Y., Thompson, S. G., & Higgins, J. P. T. (2015). Predictive distributions for between-study heterogeneity and simple methods for their application in Bayesian meta-analysis. Statistics in Medicine, 34(6), 984–998.
  doi: 10.1002/sim.6381
  supports: Predictive distributions for heterogeneity.
  short: empirically informed priors for heterogeneity
  type: Journal article
  checked: 2026-11-13, Crossref
```

---

*Based on:* Higgins, J. P. T., & Thompson, S. G. (2002). Quantifying heterogeneity in a meta-analysis. *Statistics in Medicine*, 21, 1539-1558; Gelman, A. (2006). Prior distributions for variance parameters in hierarchical models. *Bayesian Analysis*, 1, 515-534; and general meta-analytic guidance on heterogeneity estimation. See also the note on network meta-analysis assumptions.

*This note was initially drafted by Tony Myers with assistance from ChatGPT. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
