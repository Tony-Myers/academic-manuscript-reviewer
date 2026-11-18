# Transformations and Back-transformations

#### Purpose

This guide helps reviewers evaluate the use of data transformations, transformed statistical models and back-transformation of results. It focuses on why transformations are used, when they are appropriate, how transformed coefficients should be interpreted and how results should be reported transparently. The principles apply equally to frequentist and Bayesian analyses.

#### What reviewers should look for

✓ The manuscript clearly explains **why** a transformation was applied rather than simply stating that the data were transformed.

✓ The transformation is appropriate for the outcome, predictor or model assumptions.

✓ Regression coefficients, effect estimates and confidence or credible intervals are interpreted on the correct scale.

✓ Back-transformed estimates are reported where they improve interpretability.

✓ The manuscript discusses any limitations introduced by the transformation.

#### Common reviewer questions

##### Why transform data?

Transformations are commonly used to:

- reduce positive skewness;
- stabilise variance (homoscedasticity);
- improve approximate normality of residuals;
- linearise relationships;
- satisfy modelling assumptions;
- improve numerical stability.

Reviewers should ask whether a transformation is preferable to fitting a model with a more appropriate probability distribution (e.g., Gamma rather than log-transforming positive continuous outcomes).

##### Should the outcome or predictor be transformed?

Either may be transformed depending on the scientific question.

Transforming the **outcome** changes the interpretation of regression coefficients.

Transforming a **predictor** changes the scale on which the predictor is measured but does not change the outcome scale.

The manuscript should explain which variables were transformed and why.

##### What is a logarithmic (log) transformation?

A **log transformation** replaces each observation with its logarithm (commonly the natural logarithm, ln, or log10).

Log transformations are commonly used for:

- positively skewed continuous outcomes;
- multiplicative biological processes;
- ratio-scale measurements;
- variables with increasing variance.

Log transformations require positive values unless an offset has been added.

##### How are coefficients interpreted after a log transformation?

Interpretation depends on which variable has been transformed.

- **log(Y) ~ X**: coefficients represent proportional or percentage changes in the outcome. With natural logarithms, a coefficient *b* corresponds to a change of 100 × (exp(*b*) − 1) per cent for a one-unit increase in X; reading *b* × 100 directly as a percentage is an approximation that is adequate only when *b* is small (roughly below 0.1 in absolute value).
- **Y ~ log(X)**: coefficients represent changes in the outcome associated with proportional changes in the predictor.
- **log(Y) ~ log(X)**: coefficients are elasticities, representing proportional changes in both variables.

Reviewers should ensure that authors interpret coefficients on the transformed scale correctly.

##### What is back-transformation?

**Back-transformation** converts estimates from the transformed scale back to the original measurement scale.

Examples include:

- exponentiating log-transformed estimates;
- squaring square-root transformed values;
- applying the inverse Box-Cox transformation.

Back-transformed estimates are generally easier for readers to interpret, but what they estimate changes: see the next two sections.
##### Does back-transformation give the arithmetic mean on the original scale?

No. Back-transforming the mean of log-transformed data gives the **geometric mean**, not the arithmetic mean. For a right-skewed outcome the geometric mean is smaller than the arithmetic mean, and for a log-normal outcome it estimates the median.

The same applies to predictions from a model fitted to a log-transformed outcome: exponentiating a predicted value gives a predicted median, which underestimates the average on the original scale. Recovering it requires a correction that depends on the residual variance, such as multiplying by exp(σ²/2) when the residuals are Normal, or a smearing estimate when they are not.

This matters most where the total or the average on the original scale is the quantity of interest, as with costs, total workloads or cumulative exposure. Where it is, a generalised linear model with a log link, which models that average directly, avoids the problem. Reviewers should check that back-transformed values are labelled as geometric means or medians and are not compared with arithmetic means from elsewhere.

```references
- cite: Bland, J. M., & Altman, D. G. (1996). Statistics notes: Transformations, means, and confidence intervals. BMJ, 312(7038), 1079.
  doi: 10.1136/bmj.312.7038.1079
  supports: Why the back-transformed mean of logged data is the geometric mean, and how its confidence interval is obtained.
  short: back-transforming means and confidence intervals
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Duan, N. (1983). Smearing estimate: A nonparametric retransformation method. Journal of the American Statistical Association, 78(383), 605–610.
  doi: 10.1080/01621459.1983.10478017
  supports: Retransformation bias and the smearing estimate for recovering the mean on the original scale.
  short: retransformation bias and the smearing estimate
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Manning, W. G., & Mullahy, J. (2001). Estimating log models: To transform or not to transform? Journal of Health Economics, 20(4), 461–494.
  doi: 10.1016/S0167-6296(01)00086-8
  supports: The choice between log-transformed models and generalised linear models when the arithmetic mean is of interest.
  short: log-transformed models compared with generalised linear models
  type: Journal article
  checked: 2026-11-13, Crossref
```

##### How is a difference on the log scale back-transformed?

A difference between two means on the log scale back-transforms to a **ratio** of geometric means, not to a difference in the original units. A difference of 0.2 in natural logarithms corresponds to a ratio of exp(0.2) ≈ 1.22, that is, a value about 22% higher. Its confidence limits back-transform to limits for the ratio.

There is no simple way to convert that ratio into a difference in the original units, because the absolute difference it implies depends on the level at which it is evaluated. A manuscript that analyses log-transformed data and then reports the effect as a difference in original units should explain how that difference and its interval were obtained.

This direct interpretation as a ratio is particular to the logarithm. Differences on square-root, reciprocal or Box-Cox scales have no comparably simple meaning after back-transformation.

```references
- cite: Bland, J. M., & Altman, D. G. (1996). Statistics notes: Transformations, means, and confidence intervals. BMJ, 312(7038), 1079.
  doi: 10.1136/bmj.312.7038.1079
  supports: Back-transforming a difference in log means to a ratio of geometric means with its confidence interval.
  short: back-transforming means and confidence intervals
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Keene, O. N. (1995). The log transformation is special. Statistics in Medicine, 14(8), 811–819.
  doi: 10.1002/sim.4780140810
  supports: Why the log transformation is the only one giving a directly interpretable back-transformed treatment effect, as a ratio.
  short: why the log transformation is uniquely interpretable
  type: Journal article
  checked: 2026-11-13, Crossref
```

##### What about adding a constant before taking logarithms?

When a variable contains zeros, authors often analyse log(Y + 1) or log(Y + c). The constant is arbitrary, the results can change with its value, and the coefficients no longer have a clean interpretation as proportional changes.

For counts, the better course is usually a model for counts (Poisson, negative binomial, or a zero-inflated or hurdle model where zeros arise from a separate process) instead of a transformed linear model. For continuous outcomes with true zeros, a two-part model or a distribution that accommodates zeros may be appropriate.

Where a constant has been added, reviewers should expect its value, its justification and a check that the conclusions do not depend on it.

```references
- cite: O'Hara, R. B., & Kotze, D. J. (2010). Do not log-transform count data. Methods in Ecology and Evolution, 1(2), 118–122.
  doi: 10.1111/j.2041-210X.2010.00021.x
  supports: Why log-transforming counts after adding a constant performs poorly compared with models for count data.
  short: why counts should be modelled rather than log-transformed
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### Should confidence intervals or credible intervals also be back-transformed?

Usually **yes**.

If effect estimates are back-transformed, associated confidence intervals or credible intervals should normally be transformed using the same inverse transformation.

Reviewers should ensure that uncertainty is presented on the same scale as the reported estimates.

##### What are geometric means?

For log-transformed outcomes, **geometric means** are often more appropriate than arithmetic means.

Geometric means describe the central tendency on the original measurement scale while respecting multiplicative relationships.

Reviewers should check that arithmetic and geometric means are not confused.

##### What is the Box-Cox transformation?

The **Box-Cox transformation** is a family of power transformations used to improve approximate normality and variance homogeneity.

The transformation parameter (λ) is estimated from the data.

Different λ values correspond to familiar transformations:

- λ = 1 → no transformation
- λ = 0 → logarithmic transformation
- λ = 0.5 → square-root transformation

##### What is the Yeo-Johnson transformation?

The **Yeo-Johnson transformation** extends the Box-Cox transformation to allow zero and negative values.

It is often preferred when data contain observations that cannot be log-transformed.

##### When should transformation be avoided?

Transformation is not always the best solution.

Reviewers should consider whether an alternative statistical model would better reflect the data-generating process, for example:

- Gamma regression instead of log transformation;
- Negative binomial regression instead of transforming count data;
- Beta regression for proportions;
- Student's *t* models for heavy-tailed continuous data.

Choosing an appropriate probability distribution is often preferable to transforming the data solely to satisfy model assumptions.

```references
- cite: Manning, W. G., & Mullahy, J. (2001). Estimating log models: To transform or not to transform? Journal of Health Economics, 20(4), 461–494.
  doi: 10.1016/S0167-6296(01)00086-8
  supports: When a generalised linear model is preferable to a log-transformed linear model.
  short: log-transformed models compared with generalised linear models
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Xiao, X., White, E. P., Hooten, M. B., & Durham, S. L. (2011). On the use of log-transformation vs. nonlinear regression for analyzing biological power laws. Ecology, 92(10), 1887–1894.
  doi: 10.1890/11-0538.1
  supports: Why the choice between log transformation and a model on the original scale should follow the error structure of the data.
  short: log transformation compared with nonlinear regression
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: O'Hara, R. B., & Kotze, D. J. (2010). Do not log-transform count data. Methods in Ecology and Evolution, 1(2), 118–122.
  doi: 10.1111/j.2041-210X.2010.00021.x
  supports: Modelling counts directly instead of transforming them.
  short: why counts should be modelled rather than log-transformed
  type: Journal article
  checked: 2026-11-13, Crossref
```


#### Common misconceptions

##### "Transformation makes non-normal data normal."

Incorrect.

Transformations may improve approximate normality but do not guarantee normally distributed data or residuals.

##### "A log transformation fixes every assumption."

Incorrect.

Transformations may reduce skewness or heteroscedasticity but cannot correct poor model specification, influential observations or dependence.

##### "Back-transformation restores the original analysis."

Incorrect.

Back-transformed estimates improve interpretation but the statistical model was still fitted on the transformed scale.

##### "Transformation is always preferable to using another distribution."

Incorrect.

Many modern statistical models directly accommodate skewed, bounded or count data without requiring transformation.

##### "All transformations are equally interpretable."

Incorrect.

Some transformations produce coefficients that are straightforward to interpret (e.g., logarithms), whereas others may make scientific interpretation considerably more difficult.

#### Common terminology

**Transformation** – mathematical modification of a variable before analysis.

**Back-transformation** – inverse transformation used to return estimates to the original measurement scale.

**Natural logarithm (ln)** – logarithm to base *e*.

**Log10 transformation** – logarithm to base 10.

**Square-root transformation** – transformation commonly used for moderately skewed count-like data.

**Reciprocal transformation** – inverse transformation (1/X), usually applied to strongly skewed positive variables.

**Box-Cox transformation** – family of power transformations for positive continuous data.

**Yeo-Johnson transformation** – Box-Cox extension allowing zero and negative values.

**Geometric mean** – average on the multiplicative scale, commonly reported after log transformation.

**Standardisation (z-score transformation)** – subtracting the mean and dividing by the standard deviation to place variables on a common scale.

**Centring** – subtracting a constant (often the mean) from a predictor to improve interpretation or numerical stability.

**Scaling** – changing measurement units without altering relationships between observations.

#### Common reviewer red flags

- Transformation applied without explanation.
- Choice of transformation not justified.
- Regression coefficients interpreted on the wrong scale.
- Back-transformed estimates reported without back-transforming confidence or credible intervals.
- Back-transformed means presented as arithmetic means, or a back-transformed difference presented as a difference in original units instead of a ratio.
- A constant added before log transformation without justification or sensitivity analysis.
- Log transformation applied to variables containing zero or negative values without explanation.
- Transformation used solely to force normality when a more appropriate statistical distribution exists.
- Authors fail to specify which logarithm (ln or log10) was used.

#### Quick reviewer checklist

□ The manuscript explains why transformation was necessary.

□ The transformation is appropriate for the variable and scientific question.

□ Regression coefficients are interpreted correctly on the transformed scale.

□ Back-transformed estimates and associated confidence or credible intervals are reported where appropriate.

□ Alternative probability distributions were considered where relevant.

□ The chosen transformation improves interpretation rather than obscuring it.

□ Conclusions are presented on the original measurement scale whenever practical.

#### References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Bland, J. M., & Altman, D. G. (1996). Statistics notes: Transformations, means, and confidence intervals. BMJ, 312(7038), 1079.
  doi: 10.1136/bmj.312.7038.1079
  supports: Transformations, geometric means and confidence intervals.
  short: back-transforming means and confidence intervals
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Keene, O. N. (1995). The log transformation is special. Statistics in Medicine, 14(8), 811–819.
  doi: 10.1002/sim.4780140810
  supports: The special status of the log transformation.
  short: why the log transformation is uniquely interpretable
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Duan, N. (1983). Smearing estimate: A nonparametric retransformation method. Journal of the American Statistical Association, 78(383), 605–610.
  doi: 10.1080/01621459.1983.10478017
  supports: Retransformation and the smearing estimate.
  short: retransformation bias and the smearing estimate
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Manning, W. G., & Mullahy, J. (2001). Estimating log models: To transform or not to transform? Journal of Health Economics, 20(4), 461–494.
  doi: 10.1016/S0167-6296(01)00086-8
  supports: Log-transformed models compared with generalised linear models.
  short: log-transformed models compared with generalised linear models
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Xiao, X., White, E. P., Hooten, M. B., & Durham, S. L. (2011). On the use of log-transformation vs. nonlinear regression for analyzing biological power laws. Ecology, 92(10), 1887–1894.
  doi: 10.1890/11-0538.1
  supports: Log transformation compared with nonlinear regression.
  short: log transformation compared with nonlinear regression
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: O'Hara, R. B., & Kotze, D. J. (2010). Do not log-transform count data. Methods in Ecology and Evolution, 1(2), 118–122.
  doi: 10.1111/j.2041-210X.2010.00021.x
  supports: Why counts should not be log-transformed.
  short: why counts should be modelled rather than log-transformed
  type: Journal article
  checked: 2026-11-13, Crossref
```

---

*Based on:* Duan, N. (1983). Smearing estimate: a nonparametric retransformation method. *JASA*, 78, 605-610. https://doi.org/10.1080/01621459.1983.10478017; Xiao, X., et al. (2011). On the use of log-transformation vs nonlinear regression. *Ecology*, 92, 1887-1894. https://doi.org/10.1890/11-0538.1

*This note was initially drafted by Tony Myers with assistance from ChatGPT. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
