# Multicollinearity, Variable Selection and Overfitting

## Purpose

This guide helps reviewers assess how the predictors in a regression model were chosen and whether the fitted model can be trusted. It covers multicollinearity and variance inflation factors, why an overall test and individual coefficient tests can disagree, suppression, stepwise and univariable selection, overfitting, the number of observations or events needed per candidate parameter, and internal validation. It applies to linear, logistic, Cox and other regression models, frequentist or Bayesian.

## What reviewers should look for

- Is the purpose of the model stated: description, prediction, or estimation of the effect of a particular exposure?
- Were the candidate predictors chosen in advance on substantive grounds, and are all of them reported, including those not retained?
- Was a data-driven selection method used (stepwise, univariable screening, "significant predictors only"), and are its consequences acknowledged?
- Is the number of candidate parameters reasonable for the sample size or number of events?
- Has a predictor been dropped solely because of a variance inflation factor?
- Are the coefficients of adjustment variables interpreted as though each were an effect in its own right?
- For a prediction model, is performance reported after internal validation that repeats the selection process?

## What is multicollinearity and what does it affect?

Multicollinearity is strong correlation among predictors, so that one predictor is nearly a linear combination of others. The model then has little information with which to separate their individual contributions.

Its effect is on the **precision of the affected coefficients**: their standard errors are inflated, their estimates can change markedly with small changes in the data or the model, and their signs can be unstable. It does not bias the coefficients, it does not reduce the overall fit of the model, and it does not harm predictions made within the range of the data used to fit it.

Collinearity among covariates that are included only for adjustment is therefore usually harmless for the coefficient of the exposure of interest, provided the exposure itself is not strongly collinear with them.

```references
- cite: O'Brien, R. M. (2007). A caution regarding rules of thumb for variance inflation factors. Quality & Quantity, 41(5), 673–690.
  doi: 10.1007/s11135-006-9018-6
  supports: What collinearity does and does not affect, and why it should be judged in the context of the other influences on a coefficient's variance.
  short: why variance inflation factor cut-offs mislead
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Collinearity in regression modelling and its effect on individual coefficients as opposed to predictions.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
```

## How should variance inflation factors be interpreted?

The variance inflation factor (VIF) for a predictor is 1/(1 − R²), where R² comes from regressing that predictor on all the others. It is the factor by which the variance of the coefficient is inflated relative to a model in which the predictor is uncorrelated with the rest; its square root applies to the standard error. Tolerance is the reciprocal of the VIF.

Thresholds such as 5 or 10 are rules of thumb. A VIF describes only one of the things that determine a coefficient's precision; a large sample or a strong predictor can give a precise estimate despite a high VIF, and a small study can be hopelessly imprecise with a low one. A high VIF is a reason to look at the affected confidence intervals, not an automatic reason to change the model.

High VIFs among a variable, its square and its product terms are a structural consequence of how those terms are built. Centring reduces them without changing the fitted model, and they do not indicate a problem with the data.

```references
- cite: O'Brien, R. M. (2007). A caution regarding rules of thumb for variance inflation factors. Quality & Quantity, 41(5), 673–690.
  doi: 10.1007/s11135-006-9018-6
  supports: Why rules of thumb for variance inflation factors are unreliable and how such factors should be interpreted.
  short: why variance inflation factor cut-offs mislead
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What should authors do about collinearity?

The response depends on the purpose of the model.

- If the collinear variables are adjustment variables and the exposure of interest is estimated with acceptable precision, nothing need be done.
- If two variables measure essentially the same construct, they can be combined, or one chosen on substantive grounds stated in advance.
- If the scientific question requires separating the effects of two variables that move together in the data, the honest conclusion may be that the study cannot separate them. More data, or a design that varies them independently, is the remedy.
- Penalised estimation such as ridge regression trades some bias for stability and can be appropriate for prediction.

Removing a variable because its VIF exceeds a threshold is not a neutral act. If that variable is a confounder, removing it trades an honest wide interval for a biased narrow one. Letting an automated procedure choose which of two collinear variables to keep produces an arbitrary and unstable choice.

```references
- cite: O'Brien, R. M. (2007). A caution regarding rules of thumb for variance inflation factors. Quality & Quantity, 41(5), 673–690.
  doi: 10.1007/s11135-006-9018-6
  supports: Why eliminating variables or otherwise altering a model because of a high variance inflation factor can do more harm than the collinearity.
  short: why variance inflation factor cut-offs mislead
  type: Journal article
  checked: 2026-11-13, Crossref
```

## Why can the overall F-test be significant when no individual coefficient is?

The overall test asks whether the predictors together explain variation in the outcome. Each coefficient's test asks whether that predictor explains variation **beyond** all the others in the model. When predictors are correlated, they may jointly explain a great deal while none adds much uniquely, so the overall test is significant and the individual tests are not.

The reverse can also happen: with many predictors, one may be significant while the overall test is not.

Neither pattern is an error or a contradiction. Individual coefficients that are not significant in such a model do not show that those predictors are unrelated to the outcome, and the pattern is not a reason to delete them one at a time.

## What is a suppression effect?

Suppression occurs when adding a predictor makes another predictor's coefficient larger, or reverses its sign, compared with the model without it. It arises because each coefficient describes the association of a predictor with the outcome **conditional on** the other predictors, which can differ in size and direction from its unadjusted association.

A sign reversal after adjustment is not in itself a statistical artefact, and it is not in itself a discovery. Reviewers should ask which of the two quantities, adjusted or unadjusted, answers the scientific question, whether the adjustment set is justified, and whether the change reflects collinearity with wide intervals rather than a stable finding.

## Can every coefficient in a multivariable model be interpreted as an effect?

Usually not. A model built to estimate the effect of one exposure, adjusted for confounders, supports a causal interpretation of the exposure's coefficient only, and only under the assumptions of the adjustment. The coefficients of the confounders are not adjusted for *their* confounders, and may partly represent effects transmitted through the exposure, so they generally do not estimate the total effect of each variable.

Presenting all the coefficients in one table and interpreting each as "the independent effect" of that variable has been called the Table 2 fallacy. Reviewers should expect the interpretation to be restricted to the exposure the model was designed for, or a separate justified model for each exposure of interest. See also the note on causal inference in observational studies.

```references
- cite: Westreich, D., & Greenland, S. (2013). The Table 2 fallacy: Presenting and interpreting confounder and modifier coefficients. American Journal of Epidemiology, 177(4), 292–298.
  doi: 10.1093/aje/kws412
  supports: The Table 2 fallacy: why the coefficients of confounders in an adjusted model should not be interpreted as effects.
  short: why covariate coefficients are not all interpretable effects
  type: Journal article
  checked: 2026-11-13, Crossref
```

## What is wrong with stepwise selection?

Stepwise procedures (forward, backward or both) add or remove predictors according to significance tests or an information criterion applied repeatedly to the same data. The model that results is then reported as though it had been specified in advance. The consequences are well documented:

- retained coefficients are biased away from zero, because variables are kept partly for having large estimates by chance;
- standard errors and confidence intervals are too narrow and p-values too small, because they ignore the selection;
- the selected set is unstable: small changes to the data select a different model;
- genuine predictors and confounders are often dropped, especially in small samples;
- among correlated predictors, the choice between them is close to arbitrary.

The problems are worst in small samples with many candidates, which is where the method is most often used. Selection by an information criterion is not exempt: it is the same procedure with a different threshold.

```references
- cite: Steyerberg, E. W., Eijkemans, M. J. C., & Habbema, J. D. F. (1999). Stepwise selection in small data sets: A simulation study of bias in logistic regression analysis. Journal of Clinical Epidemiology, 52(10), 935–942.
  doi: 10.1016/S0895-4356(99)00103-1
  supports: Bias in coefficients and loss of true predictors under stepwise selection in small data sets.
  short: bias from stepwise selection in small data sets
  type: Journal article
  checked: 2026-11-13, Crossref (title, journal, volume, issue and pages; the Crossref record lists the first author only)
- cite: Heinze, G., Wallisch, C., & Dunkler, D. (2018). Variable selection – A review and recommendations for the practicing statistician. Biometrical Journal, 60(3), 431–449.
  doi: 10.1002/bimj.201700067
  supports: The consequences of data-driven variable selection, including instability and biased estimates, and when selection is defensible.
  short: recommendations on variable selection
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: The problems of stepwise variable selection for estimates, standard errors and p-values.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
```

## Is screening predictors by univariable tests acceptable?

No. Entering into the multivariable model only those predictors that were significant in separate univariable analyses is a form of data-driven selection with the same faults as stepwise methods, and one more: a predictor's univariable association can differ greatly from its association conditional on other variables. A confounder or a predictor that matters only after adjustment for another can be wrongly excluded, and a variable with no conditional association can be wrongly kept.

A common variant, reporting a final model containing only "the significant predictors", has the same problems. The full set of candidates and the full model should be reported.

```references
- cite: Sun, G.-W., Shook, T. L., & Kay, G. L. (1996). Inappropriate use of bivariable analysis to screen risk factors for use in multivariable analysis. Journal of Clinical Epidemiology, 49(8), 907–916.
  doi: 10.1016/0895-4356(96)00025-X
  supports: Why bivariable screening wrongly rejects important variables and is an unreliable basis for a multivariable model.
  short: why univariable screening of predictors is unreliable
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Heinze, G., Wallisch, C., & Dunkler, D. (2018). Variable selection – A review and recommendations for the practicing statistician. Biometrical Journal, 60(3), 431–449.
  doi: 10.1002/bimj.201700067
  supports: Why univariable preselection is not recommended.
  short: recommendations on variable selection
  type: Journal article
  checked: 2026-11-13, Crossref
```

## How should predictors be chosen instead?

It depends on the purpose.

- **Estimating the effect of an exposure.** The adjustment set should come from subject-matter knowledge of the causal structure, ideally stated in advance, not from statistical selection.
- **Prediction.** Candidate predictors should be chosen in advance on the basis of prior evidence, availability and cost. Where selection or shrinkage is needed, penalised methods such as the lasso, ridge or elastic net are preferable to stepwise selection, and the whole procedure must be validated.
- **Description or exploration.** Selection may be used, but the result should be labelled exploratory, the instability of the selected set investigated (for example by repeating the selection in bootstrap samples), and the reported uncertainty acknowledged as too optimistic.

In every case, prespecifying a full model of a size the data can support is a respectable choice and avoids the problem.

```references
- cite: Heinze, G., Wallisch, C., & Dunkler, D. (2018). Variable selection – A review and recommendations for the practicing statistician. Biometrical Journal, 60(3), 431–449.
  doi: 10.1002/bimj.201700067
  supports: Recommendations on when and how to select variables, the role of background knowledge, and stability investigations.
  short: recommendations on variable selection
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Prespecification of the model, data reduction and penalisation as alternatives to stepwise selection.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
```

## What is overfitting?

A model is overfitted when it has more flexibility than the data can support, so that it describes chance features of the sample as well as the underlying relationship. An overfitted model looks better in the data used to build it than it will in new data: R², discrimination and apparent effect sizes are optimistic, and predictions are too extreme.

Overfitting is driven by the number of **candidate** parameters examined, relative to the amount of information in the data, and not only by the number in the final model. Parameters screened and discarded, categories of categorical variables, nonlinear terms and interactions all count. For a binary or time-to-event outcome, the information is governed mainly by the number of events (or of the less frequent outcome category), not the total sample size.

```references
- cite: Babyak, M. A. (2004). What you see may not be what you get: A brief, nontechnical introduction to overfitting in regression-type models. Psychosomatic Medicine, 66(3), 411–421.
  doi: 10.1097/00006842-200405000-00021
  supports: What overfitting is, why candidate predictors count, and how it produces findings that fail to replicate.
  short: overfitting in regression models
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Overfitting, the effective sample size for different outcome types, and shrinkage.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
```

## How many observations or events are needed per predictor?

Rules of thumb such as ten events per candidate predictor for logistic or Cox models, or ten to twenty observations per candidate parameter for linear models, are rough guides. They do not guarantee a stable model, and they are routinely miscounted by using the number of predictors retained instead of the number considered.

For prediction models, sample size is better justified by criteria that target small overfitting, a small difference between apparent and adjusted model fit, and precise estimation of the overall outcome risk or mean. These depend on the number of candidate parameters, the outcome prevalence and the anticipated model performance, and often require more data than the ten-events rule suggests.

Reviewers should ask for the number of participants, the number of events and the number of candidate parameters, and treat a model with few events per candidate parameter as exploratory.

```references
- cite: Riley, R. D., Ensor, J., Snell, K. I. E., et al. (2020). Calculating the sample size required for developing a clinical prediction model. BMJ, 368, m441.
  doi: 10.1136/bmj.m441
  supports: Sample size criteria for developing a prediction model that go beyond events per variable.
  short: sample size for developing a prediction model
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
- cite: Babyak, M. A. (2004). What you see may not be what you get: A brief, nontechnical introduction to overfitting in regression-type models. Psychosomatic Medicine, 66(3), 411–421.
  doi: 10.1097/00006842-200405000-00021
  supports: Rules of thumb for the number of observations or events per candidate predictor and their limits.
  short: overfitting in regression models
  type: Journal article
  checked: 2026-11-13, Crossref
```

## How should model performance be validated?

Apparent performance, measured in the data used to fit the model, is optimistic. Internal validation by bootstrapping or cross-validation estimates how much. To be valid, every data-driven step, including any variable selection, choice of transformations or tuning, must be repeated within each resample; validating only the final model after selection understates the optimism.

A single random split into development and validation sets wastes data and gives an unstable estimate in all but very large samples. External validation in different data is stronger evidence than any internal method.

Reviewers should expect optimism-corrected performance, and for prediction models both discrimination and calibration, since a model can rank individuals well while predicting risks that are systematically too high or too low.

```references
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Internal validation by resampling, the need to repeat all modelling steps, and calibration as well as discrimination.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
- cite: Riley, R. D., Ensor, J., Snell, K. I. E., et al. (2020). Calculating the sample size required for developing a clinical prediction model. BMJ, 368, m441.
  doi: 10.1136/bmj.m441
  supports: Overfitting, optimism and shrinkage in prediction model development.
  short: sample size for developing a prediction model
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

## Common misconceptions

**"A VIF above 10 means the variable must be removed."** Incorrect. The VIF describes imprecision in that coefficient. Removing a needed variable can introduce bias.

**"Collinearity biases the coefficients."** Incorrect. It inflates their variance. The estimates remain unbiased but imprecise and unstable.

**"Stepwise selection finds the important predictors."** Incorrect. It finds a set that fits this sample well, and it overstates the size and certainty of the associations.

**"Variables that were not significant can be dropped without consequence."** Incorrect. Non-significance does not show that a variable is unimportant, and dropping a confounder changes what the remaining coefficients estimate.

**"Each coefficient is the independent effect of that variable."** Usually incorrect. Each is a conditional association, and only the exposure the adjustment was designed for has a claim to a causal reading.

**"The model explains 80% of the variance, so it will predict well."** Not necessarily. Apparent fit in the development data is optimistic, most of all when many candidate predictors were examined.

## Common reviewer red flags

- Purpose of the model not stated, or prediction and causal explanation mixed.
- Stepwise selection, or univariable screening at a p-value threshold, with the final model reported as if prespecified.
- Only "significant predictors" reported, with the candidate set not listed.
- Many candidate parameters relative to the sample size or the number of events.
- Events per variable calculated from the final model.
- A predictor or confounder removed because of a VIF threshold.
- Adjustment-variable coefficients interpreted as effects.
- Sign reversals or large changes in coefficients after adjustment reported without examining collinearity or the adjustment set.
- Prediction performance reported only in the development data, or validated without repeating the selection.
- Continuous predictors assumed linear, or categorised, without justification.

## Quick reviewer checklist

□ The purpose of the model is stated.

□ Candidate predictors and their rationale are reported in full.

□ The selection method, if any, is described and its consequences acknowledged.

□ The sample size or number of events is adequate for the number of candidate parameters.

□ Collinearity is assessed in terms of its effect on the estimates of interest.

□ Coefficients are interpreted in line with what the model was built to estimate.

□ Performance is corrected for optimism by validation that includes all modelling steps.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Regression modelling strategy: prespecification, overfitting, variable selection, validation and nonlinear terms.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
- cite: Heinze, G., Wallisch, C., & Dunkler, D. (2018). Variable selection – A review and recommendations for the practicing statistician. Biometrical Journal, 60(3), 431–449.
  doi: 10.1002/bimj.201700067
  supports: A review of variable selection methods with recommendations.
  short: recommendations on variable selection
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Steyerberg, E. W., Eijkemans, M. J. C., & Habbema, J. D. F. (1999). Stepwise selection in small data sets: A simulation study of bias in logistic regression analysis. Journal of Clinical Epidemiology, 52(10), 935–942.
  doi: 10.1016/S0895-4356(99)00103-1
  supports: Bias from stepwise selection in small data sets.
  short: bias from stepwise selection in small data sets
  type: Journal article
  checked: 2026-11-13, Crossref (title, journal, volume, issue and pages; the Crossref record lists the first author only)
- cite: Sun, G.-W., Shook, T. L., & Kay, G. L. (1996). Inappropriate use of bivariable analysis to screen risk factors for use in multivariable analysis. Journal of Clinical Epidemiology, 49(8), 907–916.
  doi: 10.1016/0895-4356(96)00025-X
  supports: The unreliability of univariable screening.
  short: why univariable screening of predictors is unreliable
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Babyak, M. A. (2004). What you see may not be what you get: A brief, nontechnical introduction to overfitting in regression-type models. Psychosomatic Medicine, 66(3), 411–421.
  doi: 10.1097/00006842-200405000-00021
  supports: A non-technical account of overfitting.
  short: overfitting in regression models
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Riley, R. D., Ensor, J., Snell, K. I. E., et al. (2020). Calculating the sample size required for developing a clinical prediction model. BMJ, 368, m441.
  doi: 10.1136/bmj.m441
  supports: Sample size for developing a prediction model.
  short: sample size for developing a prediction model
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
- cite: O'Brien, R. M. (2007). A caution regarding rules of thumb for variance inflation factors. Quality & Quantity, 41(5), 673–690.
  doi: 10.1007/s11135-006-9018-6
  supports: The interpretation of variance inflation factors.
  short: why variance inflation factor cut-offs mislead
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Westreich, D., & Greenland, S. (2013). The Table 2 fallacy: Presenting and interpreting confounder and modifier coefficients. American Journal of Epidemiology, 177(4), 292–298.
  doi: 10.1093/aje/kws412
  supports: The Table 2 fallacy.
  short: why covariate coefficients are not all interpretable effects
  type: Journal article
  checked: 2026-11-13, Crossref
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
