# Choosing Statistical Distributions

#### Purpose

This guide helps reviewers evaluate whether the chosen probability distribution (likelihood) is appropriate for the outcome being analysed. It focuses on selecting distributions that reflect the data-generating process rather than transforming data to satisfy model assumptions. The principles apply equally to frequentist and Bayesian analyses because the likelihood plays the same role in both frameworks.

#### What reviewers should look for

✓ The manuscript explains why the selected probability distribution is appropriate for the outcome.

✓ The distribution reflects the scale of the data (continuous, count, binary, ordinal, proportion or time-to-event).

✓ Distributional assumptions are discussed and, where possible, assessed.

✓ Alternative distributions are considered where obvious departures from assumptions exist.

✓ The interpretation of model parameters is consistent with the chosen distribution and link function.

#### Common reviewer questions

##### Why does the choice of distribution matter?

The probability distribution (likelihood) describes how the observed outcome is assumed to arise.

An inappropriate distribution may lead to:

- biased parameter estimates;
- incorrect standard errors;
- misleading confidence or credible intervals;
- poor predictions;
- invalid statistical inference.

Reviewers should ask whether the chosen distribution reflects the scientific process that generated the data rather than simply whether it satisfies statistical assumptions.

##### When is the Normal (Gaussian) distribution appropriate?

The **Normal (Gaussian) distribution** is commonly used for continuous outcomes that are approximately symmetric.

Typical examples include:

- height;
- body mass;
- blood pressure;
- many physiological measurements.

The Normal distribution assumes residuals (or outcomes, depending on the model) are approximately normally distributed with constant variance.

Small departures from normality are often unimportant, particularly in large samples.

##### When should Student's *t* distribution be used?

The **Student's *t* distribution** resembles the Normal distribution but has heavier tails.

It is often preferable when:

- outliers are present;
- extreme observations occur more frequently than expected under Normality;
- robust estimation is desired.

Student's *t* models often provide greater robustness without removing observations.

##### When is a Gamma distribution appropriate?

The **Gamma distribution** is commonly used for continuous positive outcomes that are right-skewed.

Examples include:

- waiting times;
- healthcare costs;
- reaction times;
- biological concentrations.

Gamma regression with a log link is often preferable to log-transforming a positive continuous outcome, because it models the arithmetic mean on the original scale directly and no back-transformation of the mean is needed.

```references
- cite: Manning, W. G., & Mullahy, J. (2001). Estimating log models: To transform or not to transform? Journal of Health Economics, 20(4), 461–494.
  doi: 10.1016/S0167-6296(01)00086-8
  supports: The choice between a log-transformed linear model and a generalised linear model with a log link for skewed positive outcomes.
  short: log-transformed models compared with generalised linear models
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### When is a Lognormal distribution appropriate?

The **Lognormal distribution** assumes that the logarithm of the outcome follows a Normal distribution.

It is appropriate when:

- outcomes are strictly positive;
- variability increases with the mean;
- multiplicative rather than additive processes generate the data.

Lognormal models are common for income, environmental exposure and some biomedical outcomes.

##### When should Poisson regression be used?

The **Poisson distribution** is appropriate for count data.

Examples include:

- injuries;
- hospital admissions;
- goals scored;
- adverse events.

Poisson models assume that, conditional on the predictors, the variance equals the mean.

Reviewers should assess whether this assumption appears reasonable.

##### What is overdispersion?

**Overdispersion** occurs when the observed variance exceeds that expected under a Poisson model.

Common consequences include:

- underestimated standard errors;
- inflated Type I error rates;
- misleading statistical significance.

When substantial overdispersion exists, reviewers should consider whether a Negative Binomial model, a quasi-Poisson model or robust standard errors would be more appropriate. Overdispersion can also be a symptom of an omitted predictor, clustering or excess zeros, and should prompt a check of the model before a change of distribution.

```references
- cite: Ver Hoef, J. M., & Boveng, P. L. (2007). Quasi-Poisson vs. negative binomial regression: How should we model overdispersed count data? Ecology, 88(11), 2766–2772.
  doi: 10.1890/07-0043.1
  supports: Overdispersed count data and the choice between quasi-Poisson and negative binomial models.
  short: modelling overdispersed counts
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### When should a Negative Binomial distribution be used?

The **Negative Binomial distribution** extends the Poisson distribution by allowing the variance to exceed the mean.

It is commonly preferred when analysing overdispersed count data.

Reviewers should expect authors to justify using Poisson regression when clear overdispersion is present.
##### How should rates and differing exposure be modelled?

Counts are often observed over differing amounts of exposure: injuries per 1000 hours of play, events per person-year, errors per number of attempts. Modelling the raw count ignores this, and dividing the count by the exposure and analysing the ratio as a continuous outcome discards the information that a rate based on little exposure is less precise.

The usual approach is a count model with the logarithm of exposure included as an **offset**, so that the model describes the rate while the count keeps its natural distribution. The coefficients are then interpreted as rate ratios.

Reviewers should expect the exposure variable and its use as an offset to be stated whenever exposure differs between units.


##### What are zero-inflated and hurdle models?

Some count outcomes contain more zero observations than expected under standard count models.

Examples include:

- injuries in low-risk populations;
- hospital admissions;
- disease episodes.

**Zero-inflated models** assume that some observations are structurally unable to experience the event.

**Hurdle models** assume that zero and positive counts arise from different processes.

Reviewers should look for justification when these more complex models are used.

##### When should Beta regression be used?

The **Beta distribution** is appropriate for proportions and percentages bounded between 0 and 1 (exclusive).

Examples include:

- body fat proportion;
- adherence rates;
- questionnaire proportions.

Standard Beta regression cannot accommodate exact 0 or 1 values without modification.

```references
- cite: Smithson, M., & Verkuilen, J. (2006). A better lemon squeezer? Maximum-likelihood regression with beta-distributed dependent variables. Psychological Methods, 11(1), 54–71.
  doi: 10.1037/1082-989X.11.1.54
  supports: Beta regression for continuous outcomes bounded between 0 and 1, including the treatment of values at the boundaries.
  short: beta regression for bounded outcomes
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### When should Binomial or Bernoulli models be used?

**Bernoulli models** describe single binary outcomes.

Examples include:

- success or failure;
- injured or not injured;
- disease present or absent.

**Binomial models** describe the number of successes from multiple trials.

Examples include:

- number of successful free throws;
- number of correct answers;
- treatment responders.

##### When should ordinal models be used?

Ordinal regression models are appropriate when response categories have a natural order but the distances between categories are unknown or cannot be assumed equal.

Examples include:

- Likert scales;
- disease severity;
- pain scores.

Reviewers should avoid treating ordinal outcomes as continuous without justification. Analysing ordinal responses with models that assume a metric scale can distort effect sizes and, in some configurations, produce false positives, missed effects or even reversed differences.

```references
- cite: Liddell, T. M., & Kruschke, J. K. (2018). Analyzing ordinal data with metric models: What could possibly go wrong? Journal of Experimental Social Psychology, 79, 328–348.
  doi: 10.1016/j.jesp.2018.08.009
  supports: The errors that can arise from analysing ordinal outcomes as though they were metric.
  short: the errors that arise from analysing ordinal data as metric
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### When should survival distributions be used?

Time-to-event outcomes require methods that account for censoring.

Common approaches include:

- Cox proportional hazards models;
- Weibull models;
- Exponential models;
- flexible parametric survival models.

Reviewers should ensure that censoring has been handled appropriately.

#### Common misconceptions

##### "All continuous outcomes should use a Normal distribution."

Incorrect.

Many continuous outcomes are positively skewed or heavy-tailed and may be better modelled using Gamma, Lognormal or Student's *t* distributions.

##### "Transforming the data is always better than changing the distribution."

Incorrect.

Modern regression models often allow an appropriate distribution to be modelled directly.

##### "Poisson regression is suitable for every count outcome."

Incorrect.

Overdispersion and excess zeros frequently require alternative count distributions.

##### "Beta regression can analyse any percentage."

Incorrect.

Standard Beta regression does not naturally accommodate observations equal to exactly 0 or exactly 1.

##### "The same distribution should always be used in Bayesian and frequentist analyses."

Incorrect.

Although the likelihood may be identical, Bayesian and frequentist analyses may differ in priors, estimation and interpretation.

The choice of probability distribution should be driven by the scientific characteristics of the outcome rather than by the inferential framework.

#### Common terminology

**Likelihood** – probability model describing the observed outcome conditional on model parameters.

**Distribution** – mathematical description of how observations are expected to vary.

**Gaussian distribution** – another name for the Normal distribution.

**Student's *t* distribution** – continuous distribution with heavier tails than the Normal distribution.

**Gamma distribution** – distribution for positive continuous skewed outcomes.

**Lognormal distribution** – distribution where the logarithm of the outcome is Normally distributed.

**Poisson distribution** – distribution for count data where the mean equals the variance.

**Negative Binomial distribution** – count distribution allowing overdispersion.

**Overdispersion** – observed variance greater than expected under a Poisson model.

**Bernoulli distribution** – probability distribution for a single binary outcome.

**Binomial distribution** – distribution for the number of successes in repeated trials.

**Beta distribution** – distribution for continuous proportions between 0 and 1.

**Ordinal regression** – regression model for ordered categorical outcomes.

**Link function** – mathematical function connecting the expected outcome to the linear predictor (e.g., identity, log, logit, probit or complementary log-log).

#### Common reviewer red flags

- Distribution not justified.
- Distribution inconsistent with the outcome scale.
- Count data analysed using Normal regression without justification.
- Clear overdispersion ignored.
- Excess zeros ignored.
- Beta regression used with observed 0 or 1 values without explanation.
- Continuous outcomes transformed when a more suitable distribution could have been modelled directly.
- Ordinal outcomes analysed as continuous without justification.
- Link function not reported.

#### Quick reviewer checklist

□ The probability distribution matches the outcome type.

□ Distributional assumptions appear reasonable.

□ Alternative distributions have been considered where appropriate.

□ The chosen likelihood reflects the scientific process generating the data.

□ Model interpretation is consistent with the chosen distribution and link function.

□ The distribution is justified rather than selected by convention.

□ Conclusions remain scientifically plausible given the assumptions of the fitted model.

#### References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Ver Hoef, J. M., & Boveng, P. L. (2007). Quasi-Poisson vs. negative binomial regression: How should we model overdispersed count data? Ecology, 88(11), 2766–2772.
  doi: 10.1890/07-0043.1
  supports: Modelling overdispersed counts.
  short: modelling overdispersed counts
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: O'Hara, R. B., & Kotze, D. J. (2010). Do not log-transform count data. Methods in Ecology and Evolution, 1(2), 118–122.
  doi: 10.1111/j.2041-210X.2010.00021.x
  supports: Why count data should be modelled with a count distribution instead of being log-transformed.
  short: why counts should be modelled rather than log-transformed
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Manning, W. G., & Mullahy, J. (2001). Estimating log models: To transform or not to transform? Journal of Health Economics, 20(4), 461–494.
  doi: 10.1016/S0167-6296(01)00086-8
  supports: Log-transformed models compared with generalised linear models.
  short: log-transformed models compared with generalised linear models
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Smithson, M., & Verkuilen, J. (2006). A better lemon squeezer? Maximum-likelihood regression with beta-distributed dependent variables. Psychological Methods, 11(1), 54–71.
  doi: 10.1037/1082-989X.11.1.54
  supports: Beta regression for bounded outcomes.
  short: beta regression for bounded outcomes
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Regression modelling for continuous, binary, ordinal and time-to-event outcomes.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
- cite: Liddell, T. M., & Kruschke, J. K. (2018). Analyzing ordinal data with metric models: What could possibly go wrong? Journal of Experimental Social Psychology, 79, 328–348.
  doi: 10.1016/j.jesp.2018.08.009
  supports: Analysing ordinal outcomes with ordinal instead of metric models.
  short: the errors that arise from analysing ordinal data as metric
  type: Journal article
  checked: 2026-11-13, Crossref
```

---

*Based on:* General statistical-modelling literature; no single source.

*This note was initially drafted by Tony Myers with assistance from ChatGPT. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
