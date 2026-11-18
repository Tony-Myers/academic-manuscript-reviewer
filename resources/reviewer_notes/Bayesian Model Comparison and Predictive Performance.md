# Bayesian Model Comparison and Predictive Performance

## Purpose

This guide helps reviewers evaluate Bayesian model comparison and predictive performance. It focuses on leave-one-out cross-validation (LOO), Pareto-smoothed importance sampling (PSIS), expected log predictive density (ELPD), the leave-one-out information criterion (LOOIC), the widely applicable information criterion (WAIC), and related diagnostics. The emphasis is on correct interpretation, reporting and common reviewer questions.

---

## What reviewers should look for

✓ The manuscript explains **why** model comparison was undertaken and whether the goal is prediction, explanation or model selection.

✓ The manuscript reports the method used for model comparison (e.g., PSIS-LOO, exact LOO, WAIC, Bayes factors or posterior predictive checks).

✓ The manuscript interprets model comparison statistics correctly and consistently.

✓ Uncertainty in model comparison (e.g., standard errors of ELPD differences) is reported where appropriate.

✓ The limitations of each method are acknowledged, particularly when importance sampling diagnostics indicate unreliable estimates.

---

## Common reviewer questions

### Which direction is better?

This is one of the most common sources of confusion.

| Statistic                                          | Better model                                                 |
| -------------------------------------------------- | ------------------------------------------------------------ |
| **ELPD (Expected Log Predictive Density)**         | **Higher** values indicate better expected out-of-sample predictive performance. |
| **LOOIC (Leave-One-Out Information Criterion)**    | **Lower** values indicate better predictive performance because LOOIC is reported on a deviance scale (approximately −2 × ELPD). |
| **WAIC (Widely Applicable Information Criterion)** | **Lower** values indicate better predictive performance because WAIC is also reported on a deviance scale. |
| **Bayes factor**                                   | Larger values provide stronger evidence for the numerator model, but interpretation depends on the comparison being made. |

---

### What is ELPD?

**Expected Log Predictive Density (ELPD)** estimates how well a fitted Bayesian model is expected to predict new, unseen data.

Higher ELPD values indicate better expected predictive performance.

Small differences in ELPD should be interpreted together with their estimated standard errors rather than treated as absolute evidence for one model.

---

### What is LOO?

**Leave-One-Out Cross-Validation (LOO)** estimates predictive performance by repeatedly fitting or approximating the model while leaving out one observation at a time.

Modern Bayesian analyses usually estimate LOO using **Pareto-Smoothed Importance Sampling (PSIS-LOO)** rather than repeatedly refitting the model.

---

### What is PSIS?

**Pareto-Smoothed Importance Sampling (PSIS)** provides an efficient approximation to leave-one-out cross-validation.

Its reliability should be assessed using the **Pareto *k*** diagnostic.

---

### What is Pareto *k*?

The **Pareto *k*** diagnostic evaluates the reliability of the importance-sampling approximation used by PSIS-LOO. Larger values indicate that the approximation is becoming less reliable and that particular observations may have a strong influence on the leave-one-out estimate.

Current versions of the `loo` package use a **sample-size-dependent diagnostic threshold** for Pareto *k*, rather than treating the older fixed 0.5 and 0.7 cut-offs as universal decision rules. Reviewers should therefore use the diagnostic thresholds and recommendations reported by the current software rather than mechanically applying older fixed categories.

Values approaching or exceeding **0.7** warrant particular attention, and **k ≥ 1** indicates serious problems with the importance-sampling approximation. When problematic observations are present, reviewers should expect authors to report and investigate them and, where appropriate, consider methods recommended by the current `loo` guidance, such as moment matching, exact leave-one-out refitting for problematic observations, or model revision.

Older literature commonly described fixed categories such as *k* < 0.5, 0.5–0.7, 0.7–1.0 and ≥1.0. These can be useful for understanding older reports, but they should **not** be presented as the current universal `loo` diagnostic thresholds.

```references
- cite: Vehtari, A., Gelman, A., & Gabry, J. (2017). Practical Bayesian model evaluation using leave-one-out cross-validation and WAIC. Statistics and Computing, 27(5), 1413–1432.
  doi: 10.1007/s11222-016-9696-4
  supports: PSIS-LOO and the Pareto k diagnostic for the reliability of the importance-sampling approximation.
  short: PSIS-LOO and WAIC in practice
  type: Journal article
  access: repository
  access_url: https://arxiv.org/abs/1507.04544
  access_checked: 2026-10-01, OpenAlex: green, submitted version on arXiv
  checked: 2026-10-01, Crossref (published online 2016; volume 27 is 2017)
```


---

### What is WAIC?

The **Widely Applicable Information Criterion (WAIC)** estimates expected predictive performance using the posterior distribution.

Like LOOIC, **smaller WAIC values indicate better expected predictive performance**.

WAIC and PSIS-LOO often produce similar conclusions, although PSIS-LOO is generally preferred when reliable Pareto diagnostics are available.

---
### How large a difference between models matters?

Software reports the difference in ELPD between models together with a standard error. Neither should be treated as a significance test.

As a guide, an ELPD difference smaller than about 4 indicates models with very similar predictive performance, and in that range the standard error is itself unreliable. For larger differences, the difference should be compared with its standard error: a difference several times its standard error is persuasive, and one of similar size to its standard error is not.

The standard error can be too small when the sample is small (fewer than about 100 observations) or when the models are misspecified, for example in the presence of outliers. Where models cannot be clearly separated, selecting one "winner" is not required; reporting the more complete model, or combining predictions by stacking, can be more defensible.

---

```references
- cite: Sivula, T., Magnusson, M., Matamoros, A. A., & Vehtari, A. (2025). Uncertainty in Bayesian leave-one-out cross-validation based model comparison. Bayesian Analysis. Advance online publication.
  doi: 10.1214/25-BA1569
  supports: When the standard error of an ELPD difference is reliable, including the guidance on differences smaller than 4, small samples and misspecified models.
  short: when the standard error of an ELPD difference can be trusted
  type: Journal article
  checked: 2026-11-13, Crossref (advance online publication; no volume or pages assigned)
- cite: Yao, Y., Vehtari, A., Simpson, D., & Gelman, A. (2018). Using stacking to average Bayesian predictive distributions (with discussion). Bayesian Analysis, 13(3), 917–1007.
  doi: 10.1214/17-BA1091
  supports: Stacking as an alternative to selecting a single model.
  short: stacking and pseudo-BMA weights for combining models
  type: Journal article
  checked: 2026-11-13, Crossref
```


## Common misconceptions

### "The model with the highest WAIC is best."

Incorrect.

Lower WAIC indicates better expected predictive performance.

---

### "The model with the lowest ELPD is best."

Incorrect.

Higher ELPD indicates better predictive performance.

---

### "LOOIC and ELPD should move in the same direction."

Incorrect.

LOOIC is approximately **−2 × ELPD**, so they move in opposite directions.

Higher ELPD corresponds to lower LOOIC.

---

### "A small difference proves one model is superior."

Not necessarily.

Differences should be interpreted together with their uncertainty (standard errors or confidence/credible intervals where reported).

Very small differences may have little practical importance.

---

### "Model comparison proves a model is true."

Incorrect.

Model comparison evaluates **relative predictive performance**, not whether a model is true.

All models remain approximations.

## Common terminology

**ELPD (Expected Log Predictive Density)** estimates out-of-sample predictive accuracy. Higher values are better.

**LOO (Leave-One-Out Cross-Validation)** estimates predictive performance by systematically leaving out one observation at a time.

**PSIS (Pareto-Smoothed Importance Sampling)** provides an efficient approximation to LOO.

**Pareto *k*** assesses whether PSIS-LOO is reliable.

**LOOIC (Leave-One-Out Information Criterion)** is reported on a deviance scale; lower values indicate better predictive performance.

**WAIC (Widely Applicable Information Criterion)** estimates predictive performance using the posterior distribution; lower values indicate better performance.

**Stacking** combines predictions from multiple Bayesian models using weights chosen to maximise predictive performance rather than selecting a single "best" model.

**Pseudo-BMA (Pseudo Bayesian Model Averaging)** averages predictions across models using weights derived from predictive performance measures such as LOO.

---

## Common reviewer red flags

- Direction of ELPD, WAIC or LOOIC interpreted incorrectly.
- Pareto *k* diagnostics not reported when PSIS-LOO is used.
- High Pareto *k* values ignored.
- Model comparison reported without uncertainty estimates.
- WAIC or LOOIC interpreted as hypothesis tests.
- Model comparison used to claim that a model is "true".
- Predictive performance confused with causal validity or scientific plausibility.

---

## Quick reviewer checklist

□ The manuscript explains why Bayesian model comparison was performed.

□ ELPD is interpreted correctly (higher values indicate better predictive performance).

□ LOOIC is interpreted correctly (lower values indicate better predictive performance).

□ WAIC is interpreted correctly (lower values indicate better predictive performance).

□ PSIS-LOO diagnostics, including Pareto *k*, are reported when appropriate.

□ High Pareto *k* observations are discussed or investigated.

□ Differences between competing models are interpreted together with their uncertainty.

□ Conclusions are based on predictive performance rather than claiming any model is "true".

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Vehtari, A., Gelman, A., & Gabry, J. (2017). Practical Bayesian model evaluation using leave-one-out cross-validation and WAIC. Statistics and Computing, 27(5), 1413–1432.
  doi: 10.1007/s11222-016-9696-4
  supports: PSIS-LOO, WAIC and the Pareto k diagnostic.
  short: PSIS-LOO and WAIC in practice
  type: Journal article
  access: repository
  access_url: https://arxiv.org/abs/1507.04544
  access_checked: 2026-10-01, OpenAlex: green, submitted version on arXiv
  checked: 2026-10-01, Crossref (published online 2016; volume 27 is 2017)
- cite: Gelman, A., Hwang, J., & Vehtari, A. (2013). Understanding predictive information criteria for Bayesian models. Statistics and Computing, 24(6), 997–1016.
  doi: 10.1007/s11222-013-9416-2
  supports: Predictive information criteria, including WAIC, for Bayesian models.
  short: AIC, DIC and WAIC compared
  type: Journal article
  access: subscription
  access_checked: 2026-10-01, OpenAlex: closed
  checked: 2026-10-01, OpenAlex (Crossref unavailable; OpenAlex gives 2013, the year of online publication); confirmed by hand by Tony Myers
- cite: Sivula, T., Magnusson, M., Matamoros, A. A., & Vehtari, A. (2025). Uncertainty in Bayesian leave-one-out cross-validation based model comparison. Bayesian Analysis. Advance online publication.
  doi: 10.1214/25-BA1569
  supports: Uncertainty in LOO-based model comparison.
  short: when the standard error of an ELPD difference can be trusted
  type: Journal article
  checked: 2026-11-13, Crossref (advance online publication; no volume or pages assigned)
- cite: Yao, Y., Vehtari, A., Simpson, D., & Gelman, A. (2018). Using stacking to average Bayesian predictive distributions (with discussion). Bayesian Analysis, 13(3), 917–1007.
  doi: 10.1214/17-BA1091
  supports: Stacking and pseudo-BMA weights.
  short: stacking and pseudo-BMA weights for combining models
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Kruschke, J. K. (2021). Bayesian analysis reporting guidelines. Nature Human Behaviour, 5(10), 1282–1291.
  doi: 10.1038/s41562-021-01177-7
  supports: Reporting of Bayesian model comparison.
  short: reporting guidelines for Bayesian analyses
  type: Journal article
  access: open
  access_checked: 2026-10-01, OpenAlex: open (hybrid, CC BY)
  checked: 2026-09-30, Crossref
```

---

*Based on:* Kruschke, J. K. (2021), https://doi.org/10.1038/s41562-021-01177-7; and the `loo` package documentation for PSIS-LOO and Pareto k diagnostics.

*This note was initially drafted by Tony Myers with assistance from ChatGPT. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
