# Dose-Response Coverage and Nonlinear Model Support

#### Purpose

This guide helps reviewers assess whether observed data adequately support a claimed linear or nonlinear dose-response relationship. It focuses on coverage of the dose range, functional-form choice, interpolation versus extrapolation, sparse data at extremes, uncertainty in turning points and claims about optimal doses.

#### What reviewers should look for

✓ The manuscript describes how observations are distributed across the dose range.

✓ The chosen functional form is scientifically plausible and compared with reasonable alternatives.

✓ Nonlinear features are supported by data rather than created mainly by model assumptions.

✓ Sparse data at very low or high doses are reflected in wider uncertainty.

✓ Extrapolation beyond observed doses is clearly distinguished from interpolation.

✓ Claims about thresholds, plateaux or optimal doses include uncertainty.

#### Common reviewer questions

##### What does adequate dose-range coverage mean?

A dose-response model is best supported when observations occur across the range over which the curve is interpreted.

Coverage should be assessed by considering:

- number of studies or observations at each dose;
- gaps in the observed range;
- concentration of data around only a few doses;
- representation of low and high doses;
- sample sizes at each dose.

Where several doses come from the same study, those observations usually share a common comparison group and are correlated, in the same way as the arms of a multi-arm trial. Counting them as independent overstates the coverage as well as the precision.

A smooth fitted curve does not imply equally strong evidence everywhere along that curve.

A reviewer can only judge coverage if the manuscript reports it. What is needed is the number of studies and participants contributing at each dose or dose band rather than in total, a display of the observed doses against the fitted curve with study sizes visible, and an explicit statement of where interpolation ends and extrapolation begins. A useful direct test is whether the curvature survives removing the few studies at the extremes: if the shape depends on two trials at the top of the range, the nonlinearity is a property of those trials rather than of the evidence as a whole.

Where none of this is reported, the honest conclusion is not that coverage is inadequate but that it cannot be assessed, and the distribution should be reported so that it can.

##### Why does sparse coverage matter for nonlinear models?

Nonlinear models can estimate curvature even when relatively little information exists at the extremes.

In sparse regions, the fitted shape may be determined more by:

- the assumed mathematical form;
- prior distributions;
- spline constraints;
- a small number of influential studies;

than by direct evidence.

##### What is interpolation?

**Interpolation** estimates effects between observed doses that are reasonably supported by nearby data.

Interpolation still requires assumptions but is usually better supported than extrapolation.

##### What is extrapolation?

**Extrapolation** predicts beyond the range of observed evidence.

Uncertainty usually increases outside the observed dose range, and conclusions become more dependent on the assumed functional form.

Reviewers should be cautious when authors present extrapolated doses as though they were directly studied.

##### How should the nonlinear functional form be chosen?

Possible approaches include:

- Emax models;
- restricted cubic splines;
- fractional polynomials;
- ordinary polynomials;
- exponential models;
- other biologically motivated functions.

The functional form should ideally be justified before examining the final results.

Alternative plausible forms should be compared when substantive conclusions depend on the curve shape.

```references
- cite: Orsini, N., Li, R., Wolk, A., Khudyakov, P., & Spiegelman, D. (2012). Meta-analysis for linear and nonlinear dose-response relations: Examples, an evaluation of approximations, and software. American Journal of Epidemiology, 175(1), 66–73.
  doi: 10.1093/aje/kwr265
  supports: Restricted cubic splines and other flexible forms in dose-response meta-analysis.
  short: linear and nonlinear dose-response meta-analysis
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Restricted cubic splines and the prespecification of functional form.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
```


##### Does better DIC, WAIC or LOO automatically justify a nonlinear model?

No.

Model-comparison criteria should be considered together with:

- uncertainty in the difference between models;
- graphical model fit;
- predictive checks;
- scientific plausibility;
- stability of the fitted curve.

A numerically preferred model may offer little substantive improvement.

##### How large should a WAIC or LOO difference be?

There is no universal significance-style cut-off.

For predictive criteria, reviewers should compare the estimated model difference with its **standard error**.

A difference that is small relative to its standard error provides weak evidence that predictive performance differs.

A difference several times larger than its standard error is more persuasive.

This advice belongs to the predictive criteria. DIC as ordinarily reported carries no standard error for the difference between models, so a DIC gap cannot be judged in the same way. Where a dose-response model has been selected on DIC alone, reviewers should ask what else supports the choice: graphical fit, posterior predictive checks, stability of the fitted curve under alternative forms, and scientific plausibility.

##### Can an optimal dose be identified from a fitted curve?

Sometimes, but claims should be cautious.

The dose with the largest posterior mean or fitted effect is not automatically a well-established **optimal dose**.

An optimum is weakly identified when:

- the curve is flat near its maximum;
- credible intervals overlap across many doses;
- few observations occur near the estimated maximum;
- the maximum lies near the edge of the observed range;
- the maximum depends strongly on model specification.

##### What should be reported for an estimated optimum?

Where possible, authors should report:

- uncertainty around the optimal dose;
- uncertainty around the predicted effect at that dose;
- observed dose coverage near the optimum;
- sensitivity to alternative functional forms.

##### How narrow do the intervals around an optimum need to be?

There is no width that qualifies in general, and any universal figure would be invented.

The criterion is decision-relative: the interval is narrow enough when a dose at one end and a dose at the other would lead to the same practical recommendation. An interval spanning a range across which the advice to a practitioner would differ is not narrow enough, whatever its numerical width.

Three checks matter more than the width itself:

- whether the curve is flat near its maximum, since an effect at the optimum that cannot be distinguished from effects at doses well away from it does not support the word "optimal" however tight the interval on the dose;
- whether the maximum is interior, with observations near it, rather than at the edge of the observed range where the assumed form is doing the work;
- whether the optimum moves when the functional form changes, because an interval obtained from a single spline or Emax fit is conditional on that fit and understates the uncertainty rather than measuring it.

#### Common misconceptions

##### "A smooth nonlinear curve means the dose-response relationship is well established."

Incorrect.

Smoothness is a property of the model, not necessarily of the evidence.

##### "A statistically preferred nonlinear model proves biological nonlinearity."

Incorrect.

Model comparison provides relative support among fitted models, not proof of the biological mechanism.

##### "Predictions within the plotted curve are all equally reliable."

Incorrect.

Uncertainty depends strongly on where observations actually occur.

##### "The maximum fitted effect identifies the optimal dose."

Not necessarily.

A clinically useful optimum also depends on uncertainty, harms, feasibility, cost and the density of evidence.

#### Common terminology

**Dose-response relationship** – association between dose and outcome or treatment effect.

**Nonlinear model** – model allowing effect changes that are not proportional to dose.

**Emax model** – saturating dose-response model approaching a maximum effect.

**Spline** – flexible piecewise polynomial function used to represent nonlinear relationships.

**Interpolation** – prediction within the observed data range.

**Extrapolation** – prediction beyond the observed data range.

**Dose coverage** – distribution of observed evidence across the range of doses.

**Optimal dose** – dose selected according to a prespecified criterion, not simply the largest fitted point estimate.

#### Common reviewer red flags

- Nonlinear curve shown without displaying dose coverage.
- Few observations at the doses driving the apparent curvature.
- Extrapolated effects discussed as observed evidence.
- Functional form selected only after seeing results.
- Optimal dose reported without uncertainty.
- Uncertainty around an optimum reported from one functional form only.
- Dose distribution not reported, so coverage cannot be assessed.
- Model selected solely because it has the lowest DIC or WAIC.
- Sparse evidence at the dose-range boundaries ignored.
- Multiple doses from one study treated as independent observations.
- A DIC difference interpreted as though it carried a standard error.

#### Quick reviewer checklist

□ Dose coverage is shown or described.

□ The nonlinear functional form is justified.

□ Alternative plausible models are considered.

□ Interpolation is distinguished from extrapolation.

□ Sparse regions of the dose range have appropriately greater uncertainty.

□ Model-comparison differences are interpreted relative to their uncertainty.

□ Claims about thresholds, plateaux and optimal doses are supported by observed evidence.

□ The uncertainty around an optimum is narrow enough that its ends would support the same recommendation.

#### References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Greenland, S., & Longnecker, M. P. (1992). Methods for trend estimation from summarized dose-response data, with applications to meta-analysis. American Journal of Epidemiology, 135(11), 1301–1309.
  doi: 10.1093/oxfordjournals.aje.a116237
  supports: Why doses from one study that share a reference group are correlated, and how trends should be estimated from them.
  short: trend estimation from correlated dose-response data
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Orsini, N., Li, R., Wolk, A., Khudyakov, P., & Spiegelman, D. (2012). Meta-analysis for linear and nonlinear dose-response relations: Examples, an evaluation of approximations, and software. American Journal of Epidemiology, 175(1), 66–73.
  doi: 10.1093/aje/kwr265
  supports: Linear and nonlinear dose-response meta-analysis.
  short: linear and nonlinear dose-response meta-analysis
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Crippa, A., Discacciati, A., Bottai, M., Spiegelman, D., & Orsini, N. (2019). One-stage dose–response meta-analysis for aggregated data. Statistical Methods in Medical Research, 28(5), 1579–1596.
  doi: 10.1177/0962280218773122
  supports: One-stage dose-response meta-analysis, which allows studies with few dose levels to contribute.
  short: one-stage dose-response meta-analysis
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Flexible modelling of continuous predictors with splines.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
- cite: Vehtari, A., Gelman, A., & Gabry, J. (2017). Practical Bayesian model evaluation using leave-one-out cross-validation and WAIC. Statistics and Computing, 27(5), 1413–1432.
  doi: 10.1007/s11222-016-9696-4
  supports: Comparing predictive performance with a standard error for the difference.
  short: PSIS-LOO and WAIC in practice
  type: Journal article
  access: repository
  access_url: https://arxiv.org/abs/1507.04544
  access_checked: 2026-10-01, OpenAlex: green, submitted version on arXiv
  checked: 2026-10-01, Crossref (published online 2016; volume 27 is 2017)
- cite: Spiegelhalter, D. J., Best, N. G., Carlin, B. P., & van der Linde, A. (2002). Bayesian measures of model complexity and fit. Journal of the Royal Statistical Society Series B: Statistical Methodology, 64(4), 583–639.
  doi: 10.1111/1467-9868.00353
  supports: The deviance information criterion.
  short: the paper that introduced DIC and pD
  type: Journal article
  checked: 2026-10-01, Crossref; access not recorded because OpenAlex links this DOI to the published discussion of the paper rather than the paper itself
```

---

*Based on:* General dose-response modelling and predictive model-comparison literature; no single source. See also the notes on Bayesian model comparison and on network meta-analysis assumptions.

*This note was initially drafted by Tony Myers with assistance from ChatGPT. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
