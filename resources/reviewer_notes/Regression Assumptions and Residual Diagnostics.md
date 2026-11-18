# Regression Assumptions, Residual Diagnostics and Model Checking

#### Purpose

This guide helps reviewers evaluate whether a regression model is appropriate for the data and whether the reported results are likely to be reliable. It focuses on model assumptions, residual diagnostics, influential observations, model misspecification and appropriate alternatives when assumptions are not adequately met. The principles apply to both frequentist and Bayesian regression models, although assessment methods may differ.

#### What reviewers should look for

✓ The manuscript explains why the chosen regression model is appropriate for the outcome and study design.

✓ Model assumptions are assessed using appropriate diagnostic plots or quantitative measures rather than assumed to hold.

✓ Residual diagnostics are reported and interpreted correctly.

✓ Influential observations, outliers and leverage points are investigated where appropriate.

✓ If assumptions appear violated, the manuscript justifies why the model remains appropriate or explains the alternative approach used.

#### Common reviewer questions

##### What are the assumptions of linear regression?

Classical linear regression assumes:

- linearity between predictors and outcome;
- independent observations;
- residuals are approximately Normally distributed;
- constant residual variance (homoscedasticity);
- absence of excessive multicollinearity among predictors (for coefficient estimation);
- no highly influential observations dominating the fitted model.

Not every assumption is equally important. Reviewers should consider whether any departures materially affect the scientific conclusions.

##### Does the outcome (Y) have to be Normally distributed?

Usually **no**.

One of the most common reviewer misconceptions is that the outcome variable itself must be Normally distributed.

For ordinary linear regression, the assumption concerns the **residuals**, not necessarily the observed outcome.

Strongly skewed outcomes may still produce approximately Normal residuals after accounting for predictors.

Reviewers should examine residual diagnostics rather than judging the distribution of the raw outcome alone.

```references
- cite: Schmidt, A. F., & Finan, C. (2018). Linear regression and the normality assumption. Journal of Clinical Epidemiology, 98, 146–151.
  doi: 10.1016/j.jclinepi.2017.12.006
  supports: Why the normality assumption concerns the errors, and how little its violation matters for coefficient estimates and their inference in larger samples.
  short: how little the normality assumption matters in larger samples
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Lumley, T., Diehr, P., Emerson, S., & Chen, L. (2002). The importance of the normality assumption in large public health data sets. Annual Review of Public Health, 23, 151–169.
  doi: 10.1146/annurev.publhealth.23.100901.140546
  supports: Why departures from normality matter little for methods based on means in large samples.
  short: why normality matters little for means in large samples
  type: Journal article
  access: subscription
  access_checked: 2026-10-01, OpenAlex: closed
  checked: 2026-10-01, OpenAlex (Crossref unavailable)
```


##### What are residuals?

**Residuals** are the differences between observed outcomes and the values predicted by the fitted model.

Residuals are used to assess:

- model fit;
- linearity;
- variance assumptions;
- outliers;
- influential observations;
- possible model misspecification.

Most regression assumptions concern residuals rather than the original outcome variable.

##### What does a residual versus fitted plot show?

A **residual versus fitted values plot** helps assess:

- linearity;
- constant variance (homoscedasticity);
- model misspecification.

Reviewers generally hope to see:

- residuals centred around zero;
- approximately constant spread across fitted values;
- no obvious systematic pattern.

Curved patterns suggest non-linearity.

Increasing or decreasing spread suggests heteroscedasticity.

##### What does a Normal Q-Q plot show?

A **Normal quantile-quantile (Q-Q) plot** compares observed residuals with those expected from a Normal distribution.

If residuals are approximately Normal, observations should lie close to the reference line.

Systematic departures may indicate:

- skewness;
- heavy tails;
- outliers;
- model misspecification.

Minor departures are common and often unimportant, particularly in larger samples.

##### What is homoscedasticity?

**Homoscedasticity** means that residual variance remains approximately constant across the range of fitted values.

Unequal variance is called **heteroscedasticity**.

Heteroscedasticity may lead to:

- incorrect standard errors;
- unreliable confidence intervals;
- misleading p-values.

The estimated regression coefficients themselves often remain unbiased.

##### What should authors do if heteroscedasticity is present?

Possible approaches include:

- robust (heteroscedasticity-consistent) standard errors;
- weighted regression;
- transforming the outcome;
- selecting a more appropriate probability distribution (e.g., Gamma regression);
- generalised least squares.

Reviewers should expect authors to justify the chosen approach rather than simply acknowledge unequal variance.

##### What are leverage and influential observations?

Some observations have greater influence on the fitted model than others.

Common diagnostics include:

- leverage;
- Cook's distance;
- DFBETAs;
- DFFITS.

An influential observation is not necessarily an error.

Reviewers should expect authors to investigate influential observations rather than automatically remove them.

##### What is Cook's distance?

**Cook's distance** measures the overall influence of an individual observation on the fitted regression model.

Large Cook's distance values suggest that removing a single observation substantially changes the fitted model.

Cook's distance identifies influential observations but does not automatically justify excluding them.

```references
- cite: Cook, R. D. (1977). Detection of influential observation in linear regression. Technometrics, 19(1), 15–18.
  doi: 10.1080/00401706.1977.10489493
  supports: Cook's distance as a measure of an observation's influence on the fitted regression.
  short: Cook's distance
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### What is model misspecification?

Model misspecification occurs when the statistical model does not adequately represent the underlying data-generating process.

Possible causes include:

- omitted predictors;
- incorrect functional form;
- inappropriate probability distribution;
- omitted interactions;
- dependence between observations.

Residual diagnostics often provide the first indication of model misspecification.

##### When should transformation be considered?

Transformation may improve:

- linearity;
- residual normality;
- variance stability.

However, reviewers should also consider whether selecting a different probability distribution (e.g., Gamma, Negative Binomial or Student's *t*) would better reflect the data without requiring transformation.

##### What if regression assumptions are violated?

Not every violation invalidates the analysis.

Reviewers should consider:

- the severity of the violation;
- sample size;
- robustness of the estimation procedure;
- sensitivity analyses;
- whether conclusions remain unchanged under alternative models.

The appropriate response depends on the scientific consequences rather than the mere presence of assumption violations.

##### What are robust standard errors?

**Robust standard errors** (heteroscedasticity-consistent standard errors or sandwich estimators) adjust standard error estimates when residual variance is unequal.

They improve statistical inference without changing the estimated regression coefficients.

Robust standard errors do not correct model misspecification, omitted variables or non-linearity.

```references
- cite: White, H. (1980). A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity. Econometrica, 48(4), 817–838.
  doi: 10.2307/1912934
  supports: The heteroscedasticity-consistent covariance estimator.
  short: heteroscedasticity-consistent standard errors
  type: Journal article
  checked: 2026-11-13, Crossref (the end page is not in the Crossref record)
- cite: Long, J. S., & Ervin, L. H. (2000). Using heteroscedasticity consistent standard errors in the linear regression model. The American Statistician, 54(3), 217–224.
  doi: 10.1080/00031305.2000.10474549
  supports: The small-sample behaviour of heteroscedasticity-consistent standard errors and which version to prefer.
  short: robust standard errors in small samples
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### What are alternatives to ordinary ANOVA when variances differ?

When variance differs substantially between groups, reviewers should consider whether alternatives are more appropriate, including:

- Welch's ANOVA;
- heteroscedasticity-consistent methods;
- robust regression;
- suitable generalised linear models;
- Bayesian models with appropriate likelihoods.

The choice depends on the study design and outcome type.

```references
- cite: Delacre, M., Lakens, D., & Leys, C. (2017). Why psychologists should by default use Welch's t-test instead of Student's t-test. International Review of Social Psychology, 30(1), 92–101.
  doi: 10.5334/irsp.82
  supports: Why Welch's test is preferable when variances may differ between groups.
  short: Welch's test when variances differ
  type: Journal article
  checked: 2026-11-13, Crossref
```


#### Common misconceptions

##### "The outcome must be Normally distributed."

Incorrect.

For ordinary linear regression, assumptions concern the **residuals**, not necessarily the observed outcome.

##### "Residuals must be perfectly Normal."

Incorrect.

Small departures from Normality are common and often have little practical impact, particularly in moderate or large samples.

##### "Heteroscedasticity biases regression coefficients."

Usually incorrect.

Unequal variance primarily affects standard errors and statistical inference rather than the estimated coefficients themselves.

##### "One influential observation should always be removed."

Incorrect.

Influential observations should be investigated, explained and reported. Removal requires scientific justification.

##### "A significant test of normality proves the model is invalid."

Incorrect.

Formal tests become extremely sensitive in large samples.

Diagnostic plots, effect sizes and scientific judgement are generally more informative than relying solely on significance tests.

#### Common terminology

**Residual** – observed outcome minus fitted value.

**Residual diagnostics** – methods used to assess model assumptions through residual behaviour.

**Residual versus fitted plot** – diagnostic plot assessing linearity and homoscedasticity.

**Normal Q-Q plot** – diagnostic plot assessing whether residuals approximately follow a Normal distribution.

**Homoscedasticity** – approximately constant residual variance.

**Heteroscedasticity** – residual variance changes across fitted values.

**Leverage** – measure of how unusual an observation is with respect to predictor values.

**Cook's distance** – measure of an observation's influence on the fitted model.

**Influential observation** – observation that materially changes model estimates when removed.

**Model misspecification** – mismatch between the fitted statistical model and the underlying data-generating process.

**Robust standard errors** – standard errors adjusted for heteroscedasticity.

#### Common reviewer red flags

- Assumptions stated but never assessed.
- Outcome distribution discussed while residual diagnostics are absent.
- Residual plots omitted.
- Q-Q plots interpreted as requiring perfect Normality.
- Heteroscedasticity identified but ignored.
- Influential observations removed without justification.
- Normality tests reported without diagnostic plots.
- Robust standard errors used without explanation.
- Alternative models not considered despite clear assumption violations.

#### What this guide does **not** cover

This guide explains regression assumptions and diagnostic assessment.

It does **not** explain:

- multicollinearity or variance inflation factors (VIF);
- why an overall regression **F-test** may be significant while individual coefficient **t-tests** are not;
- suppression effects;
- regression model selection;
- choosing probability distributions;
- transformations and back-transformations.

Multicollinearity, the overall F-test, suppression and model selection are covered in the note on multicollinearity, variable selection and overfitting. Distributions and transformations each have their own note.

#### Quick reviewer checklist

□ Model assumptions are appropriate for the chosen regression model.

□ Residual diagnostics have been assessed.

□ Residuals, rather than the raw outcome, are evaluated for Normality.

□ Homoscedasticity appears reasonable or has been appropriately addressed.

□ Influential observations have been investigated.

□ Model misspecification has been considered.

□ Any assumption violations are discussed and justified.

□ Conclusions remain supported despite any departures from assumptions.

#### References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Schmidt, A. F., & Finan, C. (2018). Linear regression and the normality assumption. Journal of Clinical Epidemiology, 98, 146–151.
  doi: 10.1016/j.jclinepi.2017.12.006
  supports: Linear regression and the normality assumption.
  short: how little the normality assumption matters in larger samples
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Lumley, T., Diehr, P., Emerson, S., & Chen, L. (2002). The importance of the normality assumption in large public health data sets. Annual Review of Public Health, 23, 151–169.
  doi: 10.1146/annurev.publhealth.23.100901.140546
  supports: The normality assumption in large samples.
  short: why normality matters little for means in large samples
  type: Journal article
  access: subscription
  access_checked: 2026-10-01, OpenAlex: closed
  checked: 2026-10-01, OpenAlex (Crossref unavailable)
- cite: White, H. (1980). A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity. Econometrica, 48(4), 817–838.
  doi: 10.2307/1912934
  supports: Heteroscedasticity-consistent standard errors.
  short: heteroscedasticity-consistent standard errors
  type: Journal article
  checked: 2026-11-13, Crossref (the end page is not in the Crossref record)
- cite: Long, J. S., & Ervin, L. H. (2000). Using heteroscedasticity consistent standard errors in the linear regression model. The American Statistician, 54(3), 217–224.
  doi: 10.1080/00031305.2000.10474549
  supports: Heteroscedasticity-consistent standard errors in small samples.
  short: robust standard errors in small samples
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Cook, R. D. (1977). Detection of influential observation in linear regression. Technometrics, 19(1), 15–18.
  doi: 10.1080/00401706.1977.10489493
  supports: Influential observations.
  short: Cook's distance
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Delacre, M., Lakens, D., & Leys, C. (2017). Why psychologists should by default use Welch's t-test instead of Student's t-test. International Review of Social Psychology, 30(1), 92–101.
  doi: 10.5334/irsp.82
  supports: Welch's test for unequal variances.
  short: Welch's test when variances differ
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Regression model checking and strategy.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
```

---

*Based on:* General regression-diagnostics literature; no single source.

*This note was initially drafted by Tony Myers with assistance from ChatGPT. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
