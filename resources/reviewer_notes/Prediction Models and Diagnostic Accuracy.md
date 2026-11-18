# Prediction Models and Diagnostic Accuracy

## Purpose

This guide helps reviewers assess studies that develop or validate a model to predict an outcome for individuals, and studies that evaluate how well a test identifies a condition. It covers what such studies should report, discrimination, calibration, clinical usefulness, validation, the difference between an association and a useful predictor, sensitivity, specificity and predictive values, and the design features that bias estimates of accuracy.

## What reviewers should look for

- Is the aim prediction, and is it kept separate from claims about causes?
- Are the target population, the outcome and the time at which the prediction is to be made defined?
- Would every predictor be available at the moment the prediction is needed?
- Is the full model reported so that others can use and test it?
- Is calibration reported as well as discrimination?
- Was performance estimated in the data used to build the model, and if so was it corrected for optimism?
- Is a significant association presented as evidence that a test can screen or classify individuals?
- For a diagnostic test, were the participants a representative series, was the threshold prespecified, and did everyone receive the same reference standard?

## What should a prediction model study report?

Reporting guidance for prediction models (TRIPOD, updated as TRIPOD+AI to cover machine learning) asks for enough detail to judge and reproduce the work:

- the source of the data and the eligibility criteria;
- the outcome, how and when it was assessed, and whether assessors knew the predictors;
- every candidate predictor, how and when it was measured;
- the sample size, the number of outcome events and how the sample size was arrived at;
- how missing data were handled;
- how predictors were selected and how continuous predictors were modelled;
- the **full model**: all coefficients and the intercept or baseline risk, or the code or tool needed to obtain predictions;
- performance measures with confidence intervals, and how the model was validated.

A paper that reports only which predictors were "significant" and an area under the curve has not reported a usable model.

```references
- cite: Collins, G. S., Reitsma, J. B., Altman, D. G., & Moons, K. G. M. (2015). Transparent reporting of a multivariable prediction model for individual prognosis or diagnosis (TRIPOD): The TRIPOD statement. Annals of Internal Medicine, 162(1), 55–63.
  doi: 10.7326/M14-0697
  supports: The TRIPOD checklist of items to report when developing or validating a prediction model.
  short: the TRIPOD reporting statement for prediction models
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Collins, G. S., Moons, K. G. M., Dhiman, P., et al. (2024). TRIPOD+AI statement: Updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ, 385, e078378.
  doi: 10.1136/bmj-2023-078378
  supports: The updated TRIPOD+AI guidance covering regression and machine learning methods.
  short: the updated TRIPOD+AI reporting guidance
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What does discrimination measure?

**Discrimination** is the ability of a model to give higher predicted risks to those who have the outcome than to those who do not. It is usually summarised by the c-statistic, which for a binary outcome equals the area under the receiver operating characteristic curve (AUC): the probability that a randomly chosen individual with the outcome has a higher predicted risk than a randomly chosen individual without it. A value of 0.5 is no better than chance and 1.0 is perfect separation. An AUC of 0.8 means that the model ranks the two correctly in 80% of such pairs; it does not mean that 80% of predictions are correct, and it is not enough on its own to show that the model predicts well.

The c-statistic has limits. It depends only on the ranking of predictions, so a model can discriminate well while giving predicted risks that are far too high or too low. It depends on how varied the population is, so it is not a fixed property of the model. And it does not say whether using the model would improve decisions. Labels such as "good" or "excellent" for particular values are conventions without a general basis.

```references
- cite: Steyerberg, E. W., Vickers, A. J., Cook, N. R., et al. (2010). Assessing the performance of prediction models: A framework for traditional and novel measures. Epidemiology, 21(1), 128–138.
  doi: 10.1097/EDE.0b013e3181c30fb2
  supports: Discrimination, the c-statistic and its place among other measures of model performance.
  short: measures of prediction model performance
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What is calibration and why is it essential?

**Calibration** is the agreement between predicted risks and observed outcomes: among people given a predicted risk of 20%, about 20% should have the outcome. A poorly calibrated model misinforms every individual it is applied to, however well it ranks them.

Calibration should be assessed at several levels: whether the average predicted risk matches the overall event rate; the calibration slope, where a value below 1 indicates predictions that are too extreme, the usual sign of overfitting; and a flexible calibration curve showing observed against predicted risk across the range.

The Hosmer–Lemeshow test is a poor substitute. It depends on arbitrary grouping, has low power in small samples, and gives no indication of the direction or size of miscalibration. A calibration plot is preferable. Studies that report discrimination alone are incomplete.

```references
- cite: Van Calster, B., McLernon, D. J., van Smeden, M., Wynants, L., & Steyerberg, E. W. (2019). Calibration: The Achilles heel of predictive analytics. BMC Medicine, 17, 230.
  doi: 10.1186/s12916-019-1466-7
  supports: Why calibration matters, the levels at which it should be assessed, and why calibration curves are preferred to the Hosmer–Lemeshow test.
  short: why calibration matters and how to assess it
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Steyerberg, E. W., Vickers, A. J., Cook, N. R., et al. (2010). Assessing the performance of prediction models: A framework for traditional and novel measures. Epidemiology, 21(1), 128–138.
  doi: 10.1097/EDE.0b013e3181c30fb2
  supports: Calibration measures within a framework for assessing prediction models.
  short: measures of prediction model performance
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Does good statistical performance mean the model is useful?

Not by itself. A model is useful if decisions made with it lead to better outcomes than decisions made without it, and that depends on the threshold at which action would be taken and on the relative harms of false positives and false negatives.

**Decision curve analysis** addresses this by calculating the net benefit of using the model across a range of threshold probabilities, compared with acting on everyone or no one. A model with a respectable c-statistic can offer no net benefit at the thresholds that matter.

Measures that depend on a single cut-point, such as sensitivity, specificity or overall accuracy, should be reported at thresholds chosen for stated reasons and not at whichever threshold gives the best figures in the data.

```references
- cite: Vickers, A. J., & Elkin, E. B. (2006). Decision curve analysis: A novel method for evaluating prediction models. Medical Decision Making, 26(6), 565–574.
  doi: 10.1177/0272989X06295361
  supports: Decision curve analysis and net benefit for judging whether a prediction model would improve decisions.
  short: decision curve analysis and net benefit
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Steyerberg, E. W., Vickers, A. J., Cook, N. R., et al. (2010). Assessing the performance of prediction models: A framework for traditional and novel measures. Epidemiology, 21(1), 128–138.
  doi: 10.1097/EDE.0b013e3181c30fb2
  supports: Measures of clinical usefulness alongside discrimination and calibration.
  short: measures of prediction model performance
  type: Journal article
  checked: 2026-11-14, Crossref
```

## How should a prediction model be validated?

Performance measured in the data used to build the model (apparent performance) is optimistic. **Internal validation** estimates the optimism, preferably by bootstrapping or cross-validation in which every modelling step, including variable selection and tuning, is repeated in each resample. Splitting the data once at random into development and test sets is inefficient and gives unstable results unless the sample is very large.

**External validation** tests the model in data from a different time, place or population. It is the stronger test and commonly shows lower discrimination and poorer calibration than the development study reported. A model should be regarded as unproven until it has been validated in data that played no part in its development.

Reviewers should check that a "validation" set was not used to choose predictors, tune the model or select the threshold.

```references
- cite: Steyerberg, E. W., & Harrell, F. E., Jr. (2016). Prediction models need appropriate internal, internal–external, and external validation. Journal of Clinical Epidemiology, 69, 245–247.
  doi: 10.1016/j.jclinepi.2015.04.005
  supports: Why random data splitting is inefficient and how internal, internal–external and external validation should be done.
  short: internal and external validation of prediction models
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Harrell, F. E., Jr. (2015). Regression modeling strategies: With applications to linear models, logistic and ordinal regression, and survival analysis (2nd ed.). Springer.
  doi: 10.1007/978-3-319-19425-7
  supports: Resampling-based internal validation that repeats all modelling steps.
  short: regression modelling strategy, including splines and model building
  type: Book
  checked: 2026-11-13, Crossref
- cite: Riley, R. D., Ensor, J., Snell, K. I. E., et al. (2020). Calculating the sample size required for developing a clinical prediction model. BMJ, 368, m441.
  doi: 10.1136/bmj.m441
  supports: Sample size and overfitting in prediction model development.
  short: sample size for developing a prediction model
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
```

## What commonly biases prediction model studies?

Assessments of published prediction models repeatedly find the same weaknesses:

- too few outcome events for the number of candidate predictors;
- continuous predictors dichotomised, often at cut-points chosen from the data;
- predictors selected by univariable screening or stepwise methods without accounting for the selection;
- participants with missing data simply excluded;
- predictors included that would not be known at the time the prediction is needed, or that are measured with knowledge of the outcome;
- the outcome defined or assessed differently across participants;
- calibration not assessed, and performance not corrected for optimism.

See the note on multicollinearity, variable selection and overfitting for the modelling issues.

```references
- cite: Wolff, R. F., Moons, K. G. M., Riley, R. D., et al. (2019). PROBAST: A tool to assess the risk of bias and applicability of prediction model studies. Annals of Internal Medicine, 170(1), 51–58.
  doi: 10.7326/M18-1376
  supports: The signalling questions used to judge risk of bias in prediction model studies.
  short: the PROBAST risk-of-bias tool for prediction model studies
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Does a significant association make a useful predictor or screening test?

No. A risk factor can be strongly and significantly associated with an outcome and still be nearly useless for identifying which individuals will have it.

Association is judged by a difference between group averages. Prediction for individuals requires that the distributions of the marker in those who do and do not develop the outcome barely overlap. With the odds ratios typical of risk factors, the distributions overlap almost completely, so any cut-point either misses most future cases or flags most of the population.

This is why a pre-season screening test whose scores differ on average between athletes who are later injured and those who are not does not thereby become a tool for identifying who will be injured. That claim needs evidence of discrimination, calibration and classification performance, in a sample other than the one in which the cut-point was derived, and ideally evidence that acting on the test reduces injuries.

```references
- cite: Bahr, R. (2016). Why screening tests to predict injury do not work—and probably never will…: A critical review. British Journal of Sports Medicine, 50(13), 776–780.
  doi: 10.1136/bjsports-2016-096256
  supports: Why a statistical association between a screening test and injury does not make the test able to predict injury in individuals.
  short: why an association does not make a useful screening test
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What do sensitivity, specificity and predictive values tell a reviewer?

**Sensitivity** is the proportion of people with the condition whom the test identifies; **specificity** is the proportion without it whom the test correctly clears. Both are calculated within groups defined by the true state.

The questions that matter in use run the other way. The **positive predictive value** is the proportion of those testing positive who have the condition, and the **negative predictive value** the proportion of those testing negative who do not. Both depend strongly on prevalence: with a rare condition, even a test with high sensitivity and specificity yields mostly false positives. Predictive values from a study therefore apply only to settings with similar prevalence, and those from a case-control sample, where the investigators fixed the ratio of cases to controls, are meaningless.

All of these need confidence intervals and the underlying two-by-two table.

```references
- cite: Altman, D. G., & Bland, J. M. (1994). Statistics notes: Diagnostic tests 1: Sensitivity and specificity. BMJ, 308(6943), 1552.
  doi: 10.1136/bmj.308.6943.1552
  supports: The definitions of sensitivity and specificity.
  short: sensitivity and specificity
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Altman, D. G., & Bland, J. M. (1994). Statistics notes: Diagnostic tests 2: Predictive values. BMJ, 309(6947), 102.
  doi: 10.1136/bmj.309.6947.102
  supports: Predictive values and their dependence on prevalence.
  short: predictive values and their dependence on prevalence
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

## Are sensitivity and specificity fixed properties of a test?

They are often treated as fixed, but they vary. They change with the spectrum of disease severity among those with the condition, with the range of alternative conditions among those without it, with how and by whom the test is carried out, and with the threshold used. They also tend to differ between settings with different prevalence, because the mechanisms that change prevalence, such as referral and prior testing, change the case mix.

Accuracy estimated in one setting, for example in a specialist clinic or in a laboratory sample of confirmed cases and healthy volunteers, should not be assumed to hold in another, such as field screening of an athletic squad.

```references
- cite: Leeflang, M. M. G., Rutjes, A. W. S., Reitsma, J. B., Hooft, L., & Bossuyt, P. M. M. (2013). Variation of a test's sensitivity and specificity with disease prevalence. CMAJ, 185(11), E537–E544.
  doi: 10.1503/cmaj.121286
  supports: How and why sensitivity and specificity vary with prevalence and clinical setting.
  short: how sensitivity and specificity vary between settings
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Which design features bias estimates of diagnostic accuracy?

- **Case-control sampling.** Comparing people with established disease against healthy controls omits the difficult, intermediate cases and inflates accuracy.
- **Partial or differential verification.** If only some participants, or those with positive results, receive the reference standard, or different groups receive different reference standards, accuracy is distorted.
- **Lack of blinding.** Interpreting the index test with knowledge of the reference result, or the reverse, inflates agreement.
- **An imperfect or inappropriate reference standard.**
- **A data-driven threshold.** Choosing the cut-point that maximises accuracy in the study data gives optimistic estimates that will not be reproduced.
- **Exclusion of indeterminate or uninterpretable results.**

Reviewers should expect a consecutive or random series of the people in whom the test would be used, a prespecified threshold, the same reference standard for all, and a flow diagram accounting for every participant.

```references
- cite: Lijmer, J. G., Mol, B. W., Heisterkamp, S., et al. (1999). Empirical evidence of design-related bias in studies of diagnostic tests. JAMA, 282(11), 1061–1066.
  doi: 10.1001/jama.282.11.1061
  supports: Empirical evidence that case-control design and differential verification inflate estimates of diagnostic accuracy.
  short: design-related bias in diagnostic accuracy studies
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Whiting, P. F., Rutjes, A. W. S., Westwood, M. E., et al. (2011). QUADAS-2: A revised tool for the quality assessment of diagnostic accuracy studies. Annals of Internal Medicine, 155(8), 529–536.
  doi: 10.7326/0003-4819-155-8-201110180-00009
  supports: The domains used to judge risk of bias in diagnostic accuracy studies.
  short: the QUADAS-2 tool for diagnostic accuracy studies
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Bossuyt, P. M., Reitsma, J. B., Bruns, D. E., et al. (2015). STARD 2015: An updated list of essential items for reporting diagnostic accuracy studies. BMJ, 351, h5527.
  doi: 10.1136/bmj.h5527
  supports: The items a diagnostic accuracy study should report, including the flow of participants and the cross-tabulation of results.
  short: the STARD 2015 reporting list for diagnostic accuracy studies
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

## Do machine learning models need different standards?

No. The same questions apply: a defined population and outcome, predictors available at the time of prediction, enough events, calibration as well as discrimination, validation in data not used for development, and a model or code that others can run.

Some risks are greater with flexible methods. Overfitting is easier, so small samples are more hazardous, not less. Information can leak from the test data into model development when preprocessing, feature selection or tuning is done before the data are split. And overall accuracy is uninformative when classes are unbalanced: a model that predicts "no injury" for everyone is accurate most of the time.

```references
- cite: Collins, G. S., Moons, K. G. M., Dhiman, P., et al. (2024). TRIPOD+AI statement: Updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ, 385, e078378.
  doi: 10.1136/bmj-2023-078378
  supports: Reporting expectations that apply equally to regression and machine learning prediction models.
  short: the updated TRIPOD+AI reporting guidance
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Common misconceptions

**"The AUC was 0.80, so the model predicts well."** Incomplete. Discrimination says nothing about whether predicted risks are correct or whether using the model helps.

**"The predictor was highly significant, so it can identify who is at risk."** Incorrect. Association at group level does not imply useful classification of individuals.

**"The model was validated because it was tested on a held-out part of the data."** Weak. That is internal validation, and a single split is an inefficient form of it.

**"Sensitivity and specificity do not depend on the population."** Incorrect. They vary with case mix and setting.

**"A positive result on an accurate test means the condition is probably present."** Not when the condition is rare.

**"Machine learning removes the need for a large sample."** The opposite is usually true.

## Common reviewer red flags

- Prediction and causal explanation not distinguished.
- Model equation, intercept or code not provided.
- Discrimination reported with no assessment of calibration.
- Performance reported only in the development data, uncorrected for optimism.
- Few outcome events relative to candidate predictors.
- Cut-points for predictors or for classification chosen from the same data used to evaluate them.
- Predictors that would not be available when the prediction is needed.
- A screening or injury-prediction claim resting on a group difference or odds ratio.
- Diagnostic accuracy estimated from confirmed cases and healthy controls.
- Predictive values reported from a case-control sample.
- No two-by-two table, confidence intervals or participant flow.
- Overall accuracy reported for a rare outcome.

## Quick reviewer checklist

□ The population, outcome and time of prediction are defined.

□ The full model, or the means to obtain predictions, is reported.

□ Sample size and the number of events are adequate and justified.

□ Discrimination and calibration are both reported, with uncertainty.

□ Performance is corrected for optimism or externally validated.

□ Thresholds were prespecified or justified, not optimised in the evaluation data.

□ Claims about screening or classifying individuals rest on classification performance, not association.

□ Diagnostic accuracy comes from a representative series with a common reference standard.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Collins, G. S., Reitsma, J. B., Altman, D. G., & Moons, K. G. M. (2015). Transparent reporting of a multivariable prediction model for individual prognosis or diagnosis (TRIPOD): The TRIPOD statement. Annals of Internal Medicine, 162(1), 55–63.
  doi: 10.7326/M14-0697
  supports: The TRIPOD statement.
  short: the TRIPOD reporting statement for prediction models
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Collins, G. S., Moons, K. G. M., Dhiman, P., et al. (2024). TRIPOD+AI statement: Updated guidance for reporting clinical prediction models that use regression or machine learning methods. BMJ, 385, e078378.
  doi: 10.1136/bmj-2023-078378
  supports: The TRIPOD+AI statement.
  short: the updated TRIPOD+AI reporting guidance
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Steyerberg, E. W., Vickers, A. J., Cook, N. R., et al. (2010). Assessing the performance of prediction models: A framework for traditional and novel measures. Epidemiology, 21(1), 128–138.
  doi: 10.1097/EDE.0b013e3181c30fb2
  supports: Measures of prediction model performance.
  short: measures of prediction model performance
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Van Calster, B., McLernon, D. J., van Smeden, M., Wynants, L., & Steyerberg, E. W. (2019). Calibration: The Achilles heel of predictive analytics. BMC Medicine, 17, 230.
  doi: 10.1186/s12916-019-1466-7
  supports: Calibration of prediction models.
  short: why calibration matters and how to assess it
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Vickers, A. J., & Elkin, E. B. (2006). Decision curve analysis: A novel method for evaluating prediction models. Medical Decision Making, 26(6), 565–574.
  doi: 10.1177/0272989X06295361
  supports: Decision curve analysis.
  short: decision curve analysis and net benefit
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Steyerberg, E. W., & Harrell, F. E., Jr. (2016). Prediction models need appropriate internal, internal–external, and external validation. Journal of Clinical Epidemiology, 69, 245–247.
  doi: 10.1016/j.jclinepi.2015.04.005
  supports: Validation of prediction models.
  short: internal and external validation of prediction models
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Wolff, R. F., Moons, K. G. M., Riley, R. D., et al. (2019). PROBAST: A tool to assess the risk of bias and applicability of prediction model studies. Annals of Internal Medicine, 170(1), 51–58.
  doi: 10.7326/M18-1376
  supports: Risk of bias in prediction model studies.
  short: the PROBAST risk-of-bias tool for prediction model studies
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Riley, R. D., Ensor, J., Snell, K. I. E., et al. (2020). Calculating the sample size required for developing a clinical prediction model. BMJ, 368, m441.
  doi: 10.1136/bmj.m441
  supports: Sample size for prediction model development.
  short: sample size for developing a prediction model
  type: Journal article
  checked: 2026-11-13, Crossref (the volume number is not in the Crossref record)
- cite: Bahr, R. (2016). Why screening tests to predict injury do not work—and probably never will…: A critical review. British Journal of Sports Medicine, 50(13), 776–780.
  doi: 10.1136/bjsports-2016-096256
  supports: Why association does not make a screening test predictive.
  short: why an association does not make a useful screening test
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Altman, D. G., & Bland, J. M. (1994). Statistics notes: Diagnostic tests 1: Sensitivity and specificity. BMJ, 308(6943), 1552.
  doi: 10.1136/bmj.308.6943.1552
  supports: Sensitivity and specificity.
  short: sensitivity and specificity
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Altman, D. G., & Bland, J. M. (1994). Statistics notes: Diagnostic tests 2: Predictive values. BMJ, 309(6947), 102.
  doi: 10.1136/bmj.309.6947.102
  supports: Predictive values.
  short: predictive values and their dependence on prevalence
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Leeflang, M. M. G., Rutjes, A. W. S., Reitsma, J. B., Hooft, L., & Bossuyt, P. M. M. (2013). Variation of a test's sensitivity and specificity with disease prevalence. CMAJ, 185(11), E537–E544.
  doi: 10.1503/cmaj.121286
  supports: Variation in test accuracy with prevalence and setting.
  short: how sensitivity and specificity vary between settings
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Lijmer, J. G., Mol, B. W., Heisterkamp, S., et al. (1999). Empirical evidence of design-related bias in studies of diagnostic tests. JAMA, 282(11), 1061–1066.
  doi: 10.1001/jama.282.11.1061
  supports: Design-related bias in diagnostic studies.
  short: design-related bias in diagnostic accuracy studies
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Whiting, P. F., Rutjes, A. W. S., Westwood, M. E., et al. (2011). QUADAS-2: A revised tool for the quality assessment of diagnostic accuracy studies. Annals of Internal Medicine, 155(8), 529–536.
  doi: 10.7326/0003-4819-155-8-201110180-00009
  supports: Risk of bias in diagnostic accuracy studies.
  short: the QUADAS-2 tool for diagnostic accuracy studies
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Bossuyt, P. M., Reitsma, J. B., Bruns, D. E., et al. (2015). STARD 2015: An updated list of essential items for reporting diagnostic accuracy studies. BMJ, 351, h5527.
  doi: 10.1136/bmj.h5527
  supports: Reporting diagnostic accuracy studies.
  short: the STARD 2015 reporting list for diagnostic accuracy studies
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
