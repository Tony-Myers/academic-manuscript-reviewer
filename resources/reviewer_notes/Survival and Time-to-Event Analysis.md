# Survival and Time-to-Event Analysis

## Purpose

This guide helps reviewers assess analyses of the time until an event: death, injury, return to play, relapse, dropout. It covers censoring, Kaplan–Meier curves, the interpretation and limits of the hazard ratio, the proportional hazards assumption, restricted mean survival time, competing risks, immortal time bias and time-varying exposures.

## What reviewers should look for

- Are the start of follow-up, the event and the reasons for censoring defined?
- Could censoring be related to the risk of the event?
- Do survival plots show numbers at risk and some indication of uncertainty?
- Is a hazard ratio interpreted as a ratio of risks or of survival times?
- Was the proportional hazards assumption examined, and what was done if it was doubtful?
- Are there competing events, and were they treated as censored?
- Was exposure or group membership defined using information from after the start of follow-up?
- Is the number of events, not only the number of participants, reported?

## What is censoring and why does it need special methods?

A participant is **censored** when follow-up ends before the event has occurred: the study closes, the participant withdraws or is lost. All that is known is that the event had not happened by that time.

Ignoring this goes wrong in predictable ways. Analysing only those who had the event discards information and biases times downwards. Comparing the proportion with the event ignores that participants were followed for different lengths of time. Time-to-event methods use each participant's information for as long as they were observed.

These methods assume that censoring is **non-informative**: those censored at a given time have the same future risk as those who remain under observation. The assumption fails if, for example, athletes withdraw from follow-up because of symptoms that precede injury. Reviewers should expect the number censored and the reasons to be reported by group.

```references
- cite: Clark, T. G., Bradburn, M. J., Love, S. B., & Altman, D. G. (2003). Survival analysis part I: Basic concepts and first analyses. British Journal of Cancer, 89(2), 232–238.
  doi: 10.1038/sj.bjc.6601118
  supports: Censoring, why time-to-event data need special methods, and the assumption of non-informative censoring.
  short: censoring, Kaplan–Meier estimation and the log-rank test
  type: Journal article
  checked: 2026-11-14, Crossref
```

## How should Kaplan–Meier curves be presented and read?

A Kaplan–Meier curve estimates the proportion still event-free over time, allowing for censoring. Reviewers should check that:

- the number at risk in each group is shown beneath the plot at intervals;
- some measure of uncertainty is given, such as confidence intervals at key times;
- the plot is not extended to times when very few participants remain, where the curve becomes unstable and a single event produces a large step;
- the extent and completeness of follow-up are reported;
- conclusions are not drawn from the separation of the curves at one chosen time point or from their appearance in the tail.

The log-rank test compares whole curves. It is most powerful when the hazards are proportional, and can miss real differences when the curves cross.

```references
- cite: Pocock, S. J., Clayton, T. C., & Altman, D. G. (2002). Survival plots of time-to-event outcomes in clinical trials: Good practice and pitfalls. The Lancet, 359(9318), 1686–1689.
  doi: 10.1016/S0140-6736(02)08594-X
  supports: Good practice in presenting survival plots, including numbers at risk, uncertainty and curtailing the time axis.
  short: good practice in presenting survival plots
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Clark, T. G., Bradburn, M. J., Love, S. B., & Altman, D. G. (2003). Survival analysis part I: Basic concepts and first analyses. British Journal of Cancer, 89(2), 232–238.
  doi: 10.1038/sj.bjc.6601118
  supports: Kaplan–Meier estimation and the log-rank test.
  short: censoring, Kaplan–Meier estimation and the log-rank test
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What does a hazard ratio mean?

The **hazard** is the instantaneous rate of the event among those who have not yet had it. The **hazard ratio** compares that rate between groups.

It is frequently misread. A hazard ratio of 0.5 does not show that the risk of the event by the end of follow-up is halved, that half as many people will have the event, or that people remain event-free for twice as long. It shows that, at any given time, the event rate among those still at risk is half as large, if the ratio is constant over time.

Because the hazard ratio is a relative measure of rates, it should be accompanied by absolute quantities: the estimated proportion event-free in each group at clinically relevant times, or the median time to event where it is reached.

```references
- cite: Clark, T. G., Bradburn, M. J., Love, S. B., & Altman, D. G. (2003). Survival analysis part I: Basic concepts and first analyses. British Journal of Cancer, 89(2), 232–238.
  doi: 10.1038/sj.bjc.6601118
  supports: The hazard function and the interpretation of the hazard ratio.
  short: censoring, Kaplan–Meier estimation and the log-rank test
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Hernán, M. A. (2010). The hazards of hazard ratios. Epidemiology, 21(1), 13–15.
  doi: 10.1097/EDE.0b013e3181c1ea43
  supports: Why the hazard ratio should not be read as a ratio of risks and should be accompanied by absolute measures.
  short: why a single hazard ratio can mislead
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What are the limits of a single hazard ratio?

Two problems arise even when the analysis is correctly carried out.

First, the hazard ratio often changes over time: an intervention may carry early harm and later benefit, or an early benefit that fades. A single reported hazard ratio is then a weighted average of the period-specific ratios, and its value depends on how long the study happened to follow people.

Second, hazard ratios have a built-in selection effect. After the first events, those still at risk in each group are no longer comparable, because the more susceptible individuals have been removed faster from the group with the higher hazard. This applies in randomised trials too, so a period-specific hazard ratio later in follow-up does not have a simple causal interpretation.

For both reasons, survival curves and differences in event-free proportions or in restricted mean survival time are often more informative than the hazard ratio alone.

```references
- cite: Hernán, M. A. (2010). The hazards of hazard ratios. Epidemiology, 21(1), 13–15.
  doi: 10.1097/EDE.0b013e3181c1ea43
  supports: The dependence of the hazard ratio on the length of follow-up and its built-in selection bias.
  short: why a single hazard ratio can mislead
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Stensrud, M. J., & Hernán, M. A. (2020). Why test for proportional hazards? JAMA, 323(14), 1401–1402.
  doi: 10.1001/jama.2020.1267
  supports: Why hazards are rarely proportional and why effect measures other than the hazard ratio should be reported.
  short: why proportional hazards tests are of limited use
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

## How should the proportional hazards assumption be assessed?

The Cox model assumes that the hazard ratio between groups is constant over time. It can be examined with plots of scaled Schoenfeld residuals against time, with log-minus-log survival plots, by including an interaction between the covariate and time, and by simply looking at whether the survival curves cross or converge.

A formal test should not be relied on alone. In a small study it has little power, so a result that is not significant does not show that the hazards are proportional; in a large study it will detect departures too small to matter.

Where the assumption is doubtful, options include reporting period-specific or time-varying hazard ratios, stratifying on the offending covariate, using a model that does not assume proportionality, or reporting a measure that does not depend on it. Reviewers should expect authors to say what was checked and what was done, not only that "the assumption was met".

```references
- cite: Grambsch, P. M., & Therneau, T. M. (1994). Proportional hazards tests and diagnostics based on weighted residuals. Biometrika, 81(3), 515–526.
  doi: 10.1093/biomet/81.3.515
  supports: Tests and diagnostic plots for proportional hazards based on scaled Schoenfeld residuals.
  short: Schoenfeld-residual checks of proportional hazards
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Bradburn, M. J., Clark, T. G., Love, S. B., & Altman, D. G. (2003). Survival analysis part III: Multivariate data analysis – choosing a model and assessing its adequacy and fit. British Journal of Cancer, 89(4), 605–611.
  doi: 10.1038/sj.bjc.6601120
  supports: Assessing the adequacy and fit of a survival model.
  short: choosing a survival model and checking its fit
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Stensrud, M. J., & Hernán, M. A. (2020). Why test for proportional hazards? JAMA, 323(14), 1401–1402.
  doi: 10.1001/jama.2020.1267
  supports: Why testing for proportional hazards is of limited value and what to report instead.
  short: why proportional hazards tests are of limited use
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
```

## What is restricted mean survival time?

The **restricted mean survival time** is the average event-free time up to a specified time point: the area under the survival curve to that point. The difference between groups is the average event-free time gained over that period, for example "on average 23 more days free of injury over the 12-month season".

It does not require proportional hazards, it is an absolute measure on the time scale, and it is readily understood. Its value depends on the chosen time horizon, which should be prespecified, clinically meaningful and within the range where enough participants remain under observation.

```references
- cite: Royston, P., & Parmar, M. K. B. (2013). Restricted mean survival time: An alternative to the hazard ratio for the design and analysis of randomized trials with a time-to-event outcome. BMC Medical Research Methodology, 13, 152.
  doi: 10.1186/1471-2288-13-152
  supports: Restricted mean survival time as an alternative to the hazard ratio, and the choice of time horizon.
  short: restricted mean survival time
  type: Journal article
  checked: 2026-11-14, Crossref
```

## How should competing risks be handled?

A **competing event** prevents the event of interest from occurring: death from another cause, retirement before injury, a different injury that ends the season. Competing events are not the same as censoring, because the participant is no longer at risk of the event of interest at all.

Treating competing events as censored in a Kaplan–Meier analysis overestimates the probability of the event of interest, since it describes a hypothetical world in which the competing event could not happen. The appropriate estimate of absolute risk is the **cumulative incidence function**.

For regression, the two standard approaches answer different questions. The cause-specific hazard model describes the rate of the event among those still at risk and suits questions about aetiology. The subdistribution hazard (Fine–Gray) model relates covariates to the cumulative incidence and suits prediction of absolute risk. Reviewers should expect competing events to be identified, counted and handled with a stated approach.

```references
- cite: Austin, P. C., Lee, D. S., & Fine, J. P. (2016). Introduction to the analysis of survival data in the presence of competing risks. Circulation, 133(6), 601–609.
  doi: 10.1161/CIRCULATIONAHA.115.017719
  supports: Why treating competing events as censored overestimates incidence, and the choice between cause-specific and subdistribution hazard models.
  short: analysing survival data with competing risks
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Fine, J. P., & Gray, R. J. (1999). A proportional hazards model for the subdistribution of a competing risk. Journal of the American Statistical Association, 94(446), 496–509.
  doi: 10.1080/01621459.1999.10474144
  supports: The proportional subdistribution hazards model for cumulative incidence.
  short: the subdistribution hazard model
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What is immortal time bias?

**Immortal time** is a period of follow-up during which, by the way the groups are defined, the event cannot occur. It arises when group membership depends on something that happens after the start of follow-up: starting a treatment, completing a programme, attending a minimum number of sessions, surviving long enough to be classified as a "responder".

Participants in the group so defined must have remained event-free until they qualified. If that waiting time is counted as exposed follow-up, or excluded, the exposed group acquires a spurious advantage. The bias always favours the exposure defined by the later event and can be large enough to create an apparent benefit from an ineffective intervention.

The remedy is to align the start of follow-up with the time at which group membership is determined: treat exposure as time-varying, so that person-time before exposure counts as unexposed, or use a landmark analysis that classifies participants by their status at a fixed time and follows them only from then.

```references
- cite: Suissa, S. (2008). Immortal time bias in pharmacoepidemiology. American Journal of Epidemiology, 167(4), 492–499.
  doi: 10.1093/aje/kwm324
  supports: How immortal time arises in cohort studies, the direction of the bias and how to avoid it.
  short: immortal time bias
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Lévesque, L. E., Hanley, J. A., Kezouh, A., & Suissa, S. (2010). Problem of immortal time bias in cohort studies: Example using statins for preventing progression of diabetes. BMJ, 340, b5087.
  doi: 10.1136/bmj.b5087
  supports: A worked example showing an apparent protective effect produced by immortal time bias.
  short: a worked example of immortal time bias
  type: Journal article
  checked: 2026-11-14, Crossref
```

## How should exposures that change over time be analysed?

Many exposures of interest are not fixed at baseline: training load, medication, body mass, playing position. Classifying participants by their baseline value, or by an average over the whole of follow-up, misrepresents exposure and, in the second case, uses information from the future.

A time-to-event model can include exposures as time-varying covariates, so that each participant's risk at a given time is related to their exposure up to that time. Reviewers should check that the exposure is measured before the period of risk it is used to explain, that the time scale and its origin are stated, and that a change in exposure caused by early symptoms of the outcome (reverse causation) has been considered.

Where the same participant can have the event more than once, as with repeated injuries, the events are not independent and analysing only the first event, or treating all events as independent, both lose or misstate information.

```references
- cite: Nielsen, R. O., Bertelsen, M. L., Ramskov, D., et al. (2019). Time-to-event analysis for sports injury research part 1: Time-varying exposures. British Journal of Sports Medicine, 53(1), 61–68.
  doi: 10.1136/bjsports-2018-099408
  supports: Time-to-event analysis with time-varying exposures in sports injury research.
  short: time-to-event analysis with time-varying exposures in sports injury research
  type: Journal article
  checked: 2026-11-14, Crossref
```

## What should a time-to-event analysis report?

- The time origin, the definition of the event and the end of follow-up.
- The number of participants, the number of events and the number censored in each group, with reasons.
- The length and completeness of follow-up.
- Survival or cumulative incidence curves with numbers at risk.
- Absolute measures at stated times as well as any hazard ratio, with confidence intervals.
- How proportional hazards was assessed.
- How competing events, time-varying exposures and repeated events were handled.

The amount of information is governed by the number of events. A study of many participants with few events supports few covariates and gives imprecise estimates.

```references
- cite: Peduzzi, P., Concato, J., Feinstein, A. R., & Holford, T. R. (1995). Importance of events per independent variable in proportional hazards regression analysis II. Accuracy and precision of regression estimates. Journal of Clinical Epidemiology, 48(12), 1503–1510.
  doi: 10.1016/0895-4356(95)00048-8
  supports: The loss of accuracy and precision in Cox regression when there are few events per variable.
  short: events per variable in Cox regression
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Pocock, S. J., Clayton, T. C., & Altman, D. G. (2002). Survival plots of time-to-event outcomes in clinical trials: Good practice and pitfalls. The Lancet, 359(9318), 1686–1689.
  doi: 10.1016/S0140-6736(02)08594-X
  supports: What should accompany survival plots.
  short: good practice in presenting survival plots
  type: Journal article
  checked: 2026-11-14, Crossref
```

## Common misconceptions

**"A hazard ratio of 0.5 means half the risk."** Incorrect. It is a ratio of rates among those still at risk, not of cumulative risks.

**"Censored participants can be left out."** Incorrect. Omitting them biases the results; they contribute information up to the time of censoring.

**"The proportional hazards test was not significant, so the assumption holds."** Not established, particularly in small studies.

**"Competing events can be treated as censoring."** Not when absolute risk is wanted; it overestimates the incidence.

**"Participants who completed the programme had fewer events, so the programme works."** Possibly immortal time bias: they had to stay event-free to complete it.

**"A large sample guarantees a precise survival analysis."** Precision depends on the number of events.

## Common reviewer red flags

- Time origin, event definition or censoring rules unclear.
- Time-to-event data analysed as a simple proportion, or by comparing mean times among those who had the event.
- Survival plots without numbers at risk, or extended into sparse tails.
- Hazard ratios described as risk ratios, with no absolute measures.
- Proportional hazards asserted without evidence, or crossing curves summarised by a single hazard ratio.
- Competing events censored without comment.
- Groups defined by events or behaviour after the start of follow-up.
- Exposure averaged over follow-up used to predict events during it.
- Repeated events treated as independent.
- Many covariates relative to the number of events.

## Quick reviewer checklist

□ Time origin, event and censoring are defined.

□ Events and censoring are reported by group, with reasons.

□ Survival plots show numbers at risk and uncertainty.

□ Hazard ratios are interpreted correctly and accompanied by absolute measures.

□ Proportional hazards has been examined and departures addressed.

□ Competing events are handled appropriately for the question.

□ Group membership and exposures do not use future information.

□ The number of events supports the complexity of the model.

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Clark, T. G., Bradburn, M. J., Love, S. B., & Altman, D. G. (2003). Survival analysis part I: Basic concepts and first analyses. British Journal of Cancer, 89(2), 232–238.
  doi: 10.1038/sj.bjc.6601118
  supports: Basic concepts of survival analysis.
  short: censoring, Kaplan–Meier estimation and the log-rank test
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Bradburn, M. J., Clark, T. G., Love, S. B., & Altman, D. G. (2003). Survival analysis part III: Multivariate data analysis – choosing a model and assessing its adequacy and fit. British Journal of Cancer, 89(4), 605–611.
  doi: 10.1038/sj.bjc.6601120
  supports: Choosing a survival model and assessing its fit.
  short: choosing a survival model and checking its fit
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Pocock, S. J., Clayton, T. C., & Altman, D. G. (2002). Survival plots of time-to-event outcomes in clinical trials: Good practice and pitfalls. The Lancet, 359(9318), 1686–1689.
  doi: 10.1016/S0140-6736(02)08594-X
  supports: Presenting survival plots.
  short: good practice in presenting survival plots
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Hernán, M. A. (2010). The hazards of hazard ratios. Epidemiology, 21(1), 13–15.
  doi: 10.1097/EDE.0b013e3181c1ea43
  supports: The limits of the hazard ratio.
  short: why a single hazard ratio can mislead
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Stensrud, M. J., & Hernán, M. A. (2020). Why test for proportional hazards? JAMA, 323(14), 1401–1402.
  doi: 10.1001/jama.2020.1267
  supports: Testing for proportional hazards.
  short: why proportional hazards tests are of limited use
  type: Journal article
  checked: 2026-11-14, Crossref (some page, volume or co-author details are not in the Crossref record)
- cite: Grambsch, P. M., & Therneau, T. M. (1994). Proportional hazards tests and diagnostics based on weighted residuals. Biometrika, 81(3), 515–526.
  doi: 10.1093/biomet/81.3.515
  supports: Diagnostics for proportional hazards.
  short: Schoenfeld-residual checks of proportional hazards
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Royston, P., & Parmar, M. K. B. (2013). Restricted mean survival time: An alternative to the hazard ratio for the design and analysis of randomized trials with a time-to-event outcome. BMC Medical Research Methodology, 13, 152.
  doi: 10.1186/1471-2288-13-152
  supports: Restricted mean survival time.
  short: restricted mean survival time
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Austin, P. C., Lee, D. S., & Fine, J. P. (2016). Introduction to the analysis of survival data in the presence of competing risks. Circulation, 133(6), 601–609.
  doi: 10.1161/CIRCULATIONAHA.115.017719
  supports: Competing risks.
  short: analysing survival data with competing risks
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Fine, J. P., & Gray, R. J. (1999). A proportional hazards model for the subdistribution of a competing risk. Journal of the American Statistical Association, 94(446), 496–509.
  doi: 10.1080/01621459.1999.10474144
  supports: The subdistribution hazard model.
  short: the subdistribution hazard model
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Suissa, S. (2008). Immortal time bias in pharmacoepidemiology. American Journal of Epidemiology, 167(4), 492–499.
  doi: 10.1093/aje/kwm324
  supports: Immortal time bias.
  short: immortal time bias
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Lévesque, L. E., Hanley, J. A., Kezouh, A., & Suissa, S. (2010). Problem of immortal time bias in cohort studies: Example using statins for preventing progression of diabetes. BMJ, 340, b5087.
  doi: 10.1136/bmj.b5087
  supports: An example of immortal time bias.
  short: a worked example of immortal time bias
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Nielsen, R. O., Bertelsen, M. L., Ramskov, D., et al. (2019). Time-to-event analysis for sports injury research part 1: Time-varying exposures. British Journal of Sports Medicine, 53(1), 61–68.
  doi: 10.1136/bjsports-2018-099408
  supports: Time-varying exposures in sports injury research.
  short: time-to-event analysis with time-varying exposures in sports injury research
  type: Journal article
  checked: 2026-11-14, Crossref
- cite: Peduzzi, P., Concato, J., Feinstein, A. R., & Holford, T. R. (1995). Importance of events per independent variable in proportional hazards regression analysis II. Accuracy and precision of regression estimates. Journal of Clinical Epidemiology, 48(12), 1503–1510.
  doi: 10.1016/0895-4356(95)00048-8
  supports: Events per variable in Cox regression.
  short: events per variable in Cox regression
  type: Journal article
  checked: 2026-11-14, Crossref
```

*This note was generated by Fable 5.2 (an Anthropic Claude model) at Tony Myers's request, and its bibliographic references have been checked; that check covered the references, not every methodological statement. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
