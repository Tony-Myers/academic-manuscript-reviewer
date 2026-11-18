# Repeated Measures, Clustering and the Unit of Analysis

This guide helps reviewers identify problems arising when multiple observations are obtained from the same participant, experimental unit, cluster or other higher-level unit. It focuses on distinguishing experimental and observational units, recognising dependence, avoiding pseudoreplication, and assessing whether the statistical analysis reflects the structure of the data.

## Reviewer checklist

✓ The experimental or independent units are clearly identified.

✓ The observational units and repeated measurements are distinguished from independent replication.

✓ The numbers of independent units and observations are reported clearly.

✓ Dependence created by repeated measurements, clustering or nesting is represented appropriately in the analysis.

✓ The analytical approach matches the study design, outcome, estimand and research question.

✓ Mixed-effects models specify and justify relevant random-effects and, where applicable, residual correlation structures.

✓ Marginal approaches such as GEE specify the clustering unit and working correlation structure and consider whether the number of independent clusters is adequate for the inferential method used.

✓ Cluster-robust standard errors are distinguished from ordinary heteroscedasticity-robust standard errors.

✓ Longitudinal analyses consider whether correlation changes with time or measurement spacing rather than assuming a particular temporal structure automatically.

✓ Summary measures or aggregation are used only when the resulting summary corresponds to the scientific question.

---

## What are the experimental unit, observational unit and unit of analysis?

These concepts are related but should not automatically be treated as interchangeable.

The **experimental unit** is the smallest unit that can independently receive or be assigned to an experimental condition. Depending on the design, this might be a participant, athlete, team, school, clinic, animal, litter, cage, limb or other unit.

The **observational or measurement unit** is the entity on which a measurement is made. There may be multiple observational units or measurements within one experimental unit.

The **unit of analysis** describes the level represented in the statistical analysis. A valid analysis should preserve the dependence structure created by the design rather than treating lower-level observations as independent merely because they appear as separate rows in a dataset.

In a simple individually randomised study with one measurement per participant, these units may coincide. In repeated, nested or cluster designs they often do not.

For example, 30 athletes each measured on five occasions provide 150 observations, but they do not thereby become 150 independent athletes.

---

## Why are repeated or clustered observations generally dependent?

Measurements belonging to the same higher-level unit commonly share characteristics or exposures.

Repeated observations from the same participant may share stable participant characteristics and may also be related through time. Players from the same team may share coaching and environment. Patients from the same clinic may share clinicians or procedures. Measurements from multiple cells taken from one animal share the same animal-level biology.

Consequently, observations within a cluster or experimental unit may be correlated even though they appear as separate observations in the dataset.

The form and magnitude of that dependence are empirical and design-dependent. Repeated observations should therefore not automatically be assigned one particular correlation structure.

---

## What is pseudoreplication?

**Pseudoreplication** broadly refers to treating observations as providing independent replication when the design does not provide that independent replication.

In its original experimental-design formulation, pseudoreplication includes using inferential statistics to test treatment effects when treatments have not been independently replicated or when purported replicates are not statistically independent.

A common example occurs when several technical measurements, subsamples or repeated observations from each experimental unit are entered into an analysis as though every measurement represented a separate independent experimental unit.

The term should nevertheless be used carefully. The existence of repeated observations is not itself pseudoreplication. The problem arises when the design or analysis treats non-independent information as independent replication for the inference being made.

```references
- cite: Hurlbert, S. H. (1984). Pseudoreplication and the design of ecological field experiments. Ecological Monographs, 54(2), 187–211.
  doi: 10.2307/1942661
  supports: Pseudoreplication: treating non-independent observations as independent replicates.
  short: pseudoreplication
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Lazic, S. E. (2010). The problem of pseudoreplication in neuroscientific studies: Is it affecting your analysis? BMC Neuroscience, 11, 5.
  doi: 10.1186/1471-2202-11-5
  supports: How pseudoreplication arises in laboratory studies and how to recognise it from the reported degrees of freedom.
  short: pseudoreplication in laboratory studies
  type: Journal article
  checked: 2026-11-13, Crossref
```


---

## What happens if dependence is ignored?

Ignoring relevant dependence can give incorrect uncertainty estimates and therefore misleading statistical inference.

Depending on the design, correlation structure and estimand, consequences can include:

- incorrect standard errors;
- misleading confidence intervals;
- misleading hypothesis tests and p-values;
- incorrect effective-information calculations; and
- inappropriate weighting of units contributing different numbers of observations.

With the positive within-cluster correlations common in many clustered designs, treating observations as independent often understates uncertainty and can produce confidence intervals that are too narrow and Type I error rates above their nominal level.

This direction is not a universal mathematical consequence of every possible dependence structure. Reviewers should therefore avoid replacing the more general problem—incorrect uncertainty caused by an inappropriate independence assumption—with an unconditional claim that clustering must always reduce standard errors or p-values in one particular direction.

The estimated regression coefficient itself is conceptually separate from its estimated uncertainty. In some settings ignoring dependence primarily damages standard errors and inference; in others, misspecification may also affect coefficient estimates.

---

## Does having more observations mean having a larger independent sample?

Not necessarily.

The number of rows or measurements in a dataset is not automatically the number of independent units contributing information.

For example, measuring 1,000 cells from one animal can provide detailed information about that animal or sample, but it does not provide the same information about between-animal variation as measuring independent animals.

Additional measurements within an independent unit can improve estimation of that unit's characteristics and may increase precision for some estimands. They are therefore not necessarily useless or equivalent to duplicates.

However, increasing the number of within-unit observations generally does not provide the same information as increasing the number of independent higher-level units.

The relevant amount of information depends on the sampling structure, correlation among observations, estimand and statistical model.

---

## How should repeated or clustered data be analysed?

There is no single correct analysis merely because data are repeated or clustered.

The appropriate method depends on:

- the research question and estimand;
- which units are independent;
- the number and structure of clusters or participants;
- whether observations are repeated over time or nested hierarchically;
- the outcome distribution;
- the pattern of within-unit dependence;
- whether effects are intended to have population-averaged or unit-specific interpretations;
- missing-data assumptions; and
- whether relevant predictors vary within or between units.

Possible approaches include:

1. **Summary-measure approaches**, in which repeated observations are converted into a scientifically meaningful participant- or cluster-level quantity.
2. **Mixed-effects or multilevel models**, which model hierarchical variation using random effects and, where needed, additional covariance structures.
3. **Marginal models such as Generalized Estimating Equations (GEE)**, which estimate population-averaged effects while accounting for within-cluster association.
4. **Cluster-robust variance estimation**, which can provide inference robust to certain forms of within-cluster dependence when its assumptions and sample-size requirements are appropriate.
5. Other specialised repeated-measures, longitudinal or time-series methods where their assumptions and estimands match the design.

The presence of clustering does not by itself establish which of these approaches should be used.

---

## When are mixed-effects models useful?

Mixed-effects models are useful when the structure of the data contains meaningful levels of variation, such as repeated observations within athletes or patients within clinics.

They can represent variation between higher-level units while retaining the individual observations rather than requiring them to be averaged.

Mixed models can also accommodate unequal numbers of observations and many unbalanced longitudinal designs. Likelihood-based inference about incomplete longitudinal data commonly relies on assumptions such as Missing at Random (MAR), conditional on the variables represented in the model. Mixed models do not automatically remove bias from missing data, particularly when the missingness mechanism is not adequately represented.

Whether a mixed model gives a subject-specific or cluster-specific interpretation depends on the model and outcome distribution. Reviewers should not assume that a mixed model and a marginal model necessarily estimate the same quantity, particularly for nonlinear models.

---

## What do random intercepts and random slopes represent?

A **random intercept** allows the modelled baseline or intercept to vary across higher-level units. For repeated measurements within participants, this can represent persistent between-participant differences.

A **random slope** allows the association with a predictor, such as time, to vary across higher-level units.

For example, participants may differ both in their baseline outcome and in how that outcome changes over time.

Random slopes should not be added automatically simply because repeated measurements exist. Their inclusion should reflect the study design, scientific question, available information and plausible variation between units.

Similarly, a random intercept does not necessarily capture every form of within-unit dependence. Residual temporal or other covariance structures may remain relevant.

```references
- cite: Barr, D. J., Levy, R., Scheepers, C., & Tily, H. J. (2013). Random effects structure for confirmatory hypothesis testing: Keep it maximal. Journal of Memory and Language, 68(3), 255–278.
  doi: 10.1016/j.jml.2012.11.001
  supports: Why omitting random slopes for within-unit effects inflates Type I error in confirmatory tests.
  short: why random slopes matter for confirmatory tests
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Matuschek, H., Kliegl, R., Vasishth, S., Baayen, H., & Bates, D. (2017). Balancing Type I error and power in linear mixed models. Journal of Memory and Language, 94, 305–315.
  doi: 10.1016/j.jml.2017.01.001
  supports: The loss of power from random-effects structures more complex than the data support.
  short: the cost of over-specified random effects
  type: Journal article
  checked: 2026-11-13, Crossref
```


---

## When are marginal models such as GEE useful?

Generalized Estimating Equations are commonly used for marginal or **population-averaged** modelling of correlated observations.

The analyst specifies a working correlation structure describing the assumed association among observations within the same cluster. With suitable regularity conditions and sufficiently many independent clusters, sandwich variance estimation can provide inference that is robust to some misspecification of this working correlation structure.

This robustness should not be interpreted as unlimited. With a small number of independent clusters, conventional sandwich standard errors can be biased and confidence intervals and hypothesis tests may perform poorly. Small-sample corrections or alternative approaches may therefore be required.

The choice between GEE and mixed-effects models should be driven partly by the estimand and desired interpretation rather than by treating one method as universally preferable.

```references
- cite: Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models. Biometrika, 73(1), 13–22.
  doi: 10.1093/biomet/73.1.13
  supports: Generalised estimating equations for correlated outcomes.
  short: generalised estimating equations
  type: Journal article
  checked: 2026-11-13, Crossref
```


---

## What are cluster-robust standard errors?

Cluster-robust standard errors adjust estimated uncertainty to allow observations within specified clusters to be dependent under appropriate conditions.

They should not be confused with ordinary heteroscedasticity-consistent robust standard errors, which address unequal residual variance but do not by themselves account for arbitrary within-cluster dependence.

Cluster-robust inference generally relies on having enough independent clusters for its asymptotic approximation. Conventional cluster-robust standard errors can perform poorly when the number of clusters is small, and appropriate finite-sample corrections or alternative methods may be needed.

The number of observations within clusters does not substitute for having an adequate number of independent clusters.

```references
- cite: Cameron, A. C., & Miller, D. L. (2015). A practitioner's guide to cluster-robust inference. Journal of Human Resources, 50(2), 317–372.
  doi: 10.3368/jhr.50.2.317
  supports: Cluster-robust standard errors and their unreliability when clusters are few.
  short: cluster-robust inference and few clusters
  type: Journal article
  checked: 2026-11-13, Crossref
```


---

## Can repeated observations simply be averaged?

Sometimes.

A **summary-measure approach** converts each participant's or cluster's repeated observations into a scientifically meaningful quantity, such as a mean, change, slope, area under the curve or another prespecified summary.

This can remove the repeated-measure structure from the subsequent between-unit analysis because each independent unit contributes one summary value.

However, averaging is not automatically appropriate. The summary must answer the research question.

For example, a mean may obscure a treatment-by-time interaction or important changes over time. Other summaries may be more appropriate when the scientific question concerns trajectories, peaks, rates of change or cumulative exposure.

Aggregation also discards information about within-unit variation and may handle incomplete observation schedules poorly. It is therefore a legitimate analytical strategy for some questions, not a generic correction for clustered data.

---

## What role does the intraclass correlation play?

An **intraclass or intracluster correlation coefficient (ICC)** can quantify similarity among observations belonging to the same cluster.

In a simple two-level random-intercept model for a continuous outcome, an ICC is commonly expressed as the proportion of variance attributable to differences between clusters:

\[
ICC = \frac{\sigma^2_{\text{between}}}
{\sigma^2_{\text{between}}+\sigma^2_{\text{within}}}.
\]

Under that model, a larger ICC indicates greater similarity among observations within the same cluster and less independent information contributed by additional observations within that cluster.

However, ICC is not one universal quantity with an identical definition in every design. Its interpretation and calculation depend on the outcome, model and hierarchical structure. More complicated longitudinal or multilevel designs may contain several relevant correlation or variance components.

An ICC estimate is useful for describing dependence and for planning many clustered studies, but estimating an ICC is not a prerequisite for recognising that the design contains repeated or clustered observations.

---

## What is the design effect?

For some simple cluster-sampling and cluster-randomised settings with approximately equal cluster sizes and a common intracluster correlation, the loss of information from clustering is often summarised using the **design effect**:

\[
DE = 1 + (m-1)ICC,
\]

where \(m\) is the cluster size.

This expression is useful in its intended setting, particularly for sample-size planning.

It should not be treated as a universal formula for the bias in a regression coefficient's standard error, for arbitrary repeated-measures designs, unequal clusters, complex covariance structures or arbitrary estimands.

In particular, it does not justify a general claim that an ignored repeated-measures structure underestimates every regression standard error by exactly \(\sqrt{DE}\).

```references
- cite: Killip, S., Mahfoud, Z., & Pearce, K. (2004). What is an intracluster correlation coefficient? Crucial concepts for primary care researchers. Annals of Family Medicine, 2(3), 204–208.
  doi: 10.1370/afm.141
  supports: The intracluster correlation coefficient and the design effect.
  short: the intracluster correlation and the design effect
  type: Journal article
  checked: 2026-11-13, Crossref (title, journal, volume, issue and pages; the Crossref record lists the first author only)
```


---

## What about longitudinal or temporal dependence?

Repeated measurements over time may exhibit correlation that depends on measurement timing or separation, but this pattern should be investigated or justified rather than assumed.

Possible covariance structures include:

- exchangeable or compound-symmetric structures;
- autoregressive structures such as AR(1);
- unstructured covariance matrices; and
- other structures appropriate to the design and measurement schedule.

An AR(1) structure represents one particular assumption: correlations decline according to lag under that model. It is not automatically required merely because measurements were collected longitudinally.

Random effects and residual temporal correlation also represent different aspects of dependence. A random intercept alone imposes a particular form of within-unit association and may not adequately represent a longitudinal covariance pattern.

Irregularly spaced observations, nonlinear trajectories and complex time dependence may require different modelling choices.

---

## Do the degrees of freedom simply equal the number of clusters?

No.

For clustered or repeated data, it is important that inferential procedures recognise the limited amount of independent information, but there is no universal rule that the degrees of freedom must simply equal the number of clusters.

Degrees-of-freedom calculations depend on the model and inferential procedure. Mixed models may use approximations such as Satterthwaite or Kenward-Roger methods. Cluster-robust procedures may use cluster-based or other finite-sample adjustments.

A useful reviewer warning is therefore not that the reported degrees of freedom must equal \(N_{\text{clusters}}\), but that inferential degrees of freedom should be compatible with the model, design and number of independent higher-level units.

Very large residual degrees of freedom produced by treating all lower-level observations as independent can indicate a unit-of-analysis problem, but should be investigated rather than diagnosed from the degrees of freedom alone.

---

## What should reviewers expect authors to report?

Authors should report enough information to reconstruct the dependence structure and understand how it was handled analytically.

Depending on the design, this includes:

1. The experimental, observational and analytical units.
2. The number of independent higher-level units and the number of lower-level observations.
3. The number and timing of repeated measurements where relevant.
4. The nesting or clustering structure.
5. The statistical model and why it matches the research question.
6. Random-effects structures for mixed models.
7. Residual or temporal covariance structures where relevant.
8. The clustering variable and working correlation structure for GEE.
9. The clustering level and finite-sample approach used for cluster-robust inference.
10. The method used to calculate inferential degrees of freedom where this materially affects inference.
11. Missing-data assumptions and handling where repeated observations are incomplete.
12. Software and sufficient implementation detail to reproduce the analysis.

Not every item is required for every design. Reporting expectations should follow the analysis actually performed.

---

## Common problematic claims

### "We analysed 500 observations, therefore N = 500."

Not necessarily. The number of observations and the number of independent experimental or sampling units may differ.

### "Repeated measurements give us five times the sample size."

Repeated measurements can add information, but they do not usually provide the same information as five times as many independent units.

### "Because the ordinary regression was significant, dependence does not matter."

Statistical significance does not validate the independence assumption. If the uncertainty calculation is inappropriate, the resulting confidence interval and p-value may also be inappropriate.

### "Ignoring clustering always makes the standard error smaller."

Too strong. Ignoring relevant dependence gives a misspecified uncertainty calculation. Positive within-cluster dependence often produces underestimated uncertainty when ignored, but the direction and magnitude are not universal across all designs and estimands.

### "A random intercept solves the repeated-measures problem."

Not necessarily. A random intercept represents one form of between-unit variation and induces a particular dependence structure. Random slopes, residual covariance structures or other modelling choices may also be relevant.

### "GEE is robust to the correlation structure, so the number of clusters does not matter."

Incorrect. Sandwich-based robustness is principally an asymptotic property. Inference can perform poorly with few independent clusters unless appropriate corrections or other methods are used.

### "Cluster-robust standard errors and robust standard errors are the same thing."

Not generally. Ordinary heteroscedasticity-robust standard errors address unequal variance; cluster-robust methods additionally permit specified within-cluster dependence.

### "We averaged all repeated observations, so the analysis is automatically valid."

Aggregation can be appropriate when the summary measure corresponds to the estimand, but it can discard important temporal or within-unit information and is not a universal solution.

### "Mixed models handle all missing data."

Incorrect. Likelihood-based mixed models can provide valid inference under particular assumptions about the missing-data mechanism and model specification. They do not automatically correct bias from all forms of missingness.

### "Subject was included as a fixed effect, therefore the analysis is wrong."

Too strong. Fixed subject effects can be appropriate for some estimands and designs. Their interpretation and statistical properties differ from random-effects approaches. Their use should be evaluated in relation to the research question and design rather than rejected automatically.

---

## Glossary

**Cluster** – a higher-level grouping containing observations that may be statistically dependent.

**Cluster-robust standard error** – a variance estimator designed to permit dependence among observations within specified clusters under appropriate assumptions.

**Experimental unit** – the smallest unit that can independently receive or be assigned to an experimental condition.

**GEE (Generalized Estimating Equations)** – a framework commonly used to estimate marginal or population-averaged relationships from correlated data.

**ICC (Intraclass/Intracluster Correlation Coefficient)** – a measure of within-cluster similarity whose precise definition depends on the model and setting.

**Mixed-effects model** – a model containing fixed effects and one or more random effects representing variation across units or levels.

**Observational unit** – the entity on which an observation or measurement is made.

**Pseudoreplication** – use of observations as independent replication when the design does not provide corresponding independent replication for the inference being made.

**Random intercept** – a model component allowing intercepts to vary across higher-level units.

**Random slope** – a model component allowing a predictor's slope to vary across higher-level units.

**Repeated measures** – multiple measurements of an outcome or related outcomes obtained from the same experimental or sampling unit.

**Summary-measure approach** – analysis in which repeated observations within each independent unit are reduced to a scientifically meaningful unit-level summary.

**Unit of analysis** – the level at which observations or summaries enter a statistical analysis; it should be considered together with the experimental, observational and inferential units and the dependence represented by the model.

---

## Red flags

- The manuscript reports many more "participants", "samples" or values of \(N\) than there are independent experimental or sampling units.
- Technical replicates, cells, limbs, trials, observations, bouts or repeated measurements are treated as though they necessarily constitute independent replication.
- The Methods describe repeated or nested data but the analysis assumes independent observations without explanation.
- An ordinary heteroscedasticity-robust standard error is presented as correcting arbitrary clustering.
- A mixed model is reported without describing its random-effects structure.
- A random intercept is used automatically without considering whether slopes or residual correlation structures matter.
- GEE or cluster-robust inference is used with very few independent clusters without discussing finite-sample performance.
- Longitudinal data are assigned a covariance structure without explanation.
- Repeated observations are averaged even though the research question concerns change or trajectories.
- Sample-size or power claims count lower-level observations as though they were independent units.
- A large number of observations within a very small number of higher-level units is presented as though it guarantees precise population-level inference.

---

## Detailed reviewer checklist

- [ ] Are the experimental, observational and analytical units identifiable?
- [ ] Does the claimed sample size distinguish independent units from repeated or lower-level observations?
- [ ] Is the nesting, clustering or repeated-measures structure described?
- [ ] Does the analysis represent relevant dependence?
- [ ] Does the analytical method estimate the quantity required by the research question?
- [ ] For mixed models, are relevant random effects and covariance assumptions reported?
- [ ] For GEE, are the clustering unit and working correlation structure reported?
- [ ] For cluster-robust inference, is the number of independent clusters adequate or is an appropriate small-sample approach used?
- [ ] Are temporal dependence assumptions justified rather than automatic?
- [ ] If observations are aggregated, does the chosen summary preserve the quantity of scientific interest?
- [ ] Are missing-data assumptions appropriate to the longitudinal or clustered analysis?
- [ ] Are confidence intervals, p-values and degrees of freedom based on an inferential procedure appropriate to the dependence structure?
- [ ] Do conclusions distinguish the number of observations from the amount of independent information?

## References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Hurlbert, S. H. (1984). Pseudoreplication and the design of ecological field experiments. Ecological Monographs, 54(2), 187–211.
  doi: 10.2307/1942661
  supports: Pseudoreplication.
  short: pseudoreplication
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Lazic, S. E. (2010). The problem of pseudoreplication in neuroscientific studies: Is it affecting your analysis? BMC Neuroscience, 11, 5.
  doi: 10.1186/1471-2202-11-5
  supports: Pseudoreplication in laboratory studies.
  short: pseudoreplication in laboratory studies
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Barr, D. J., Levy, R., Scheepers, C., & Tily, H. J. (2013). Random effects structure for confirmatory hypothesis testing: Keep it maximal. Journal of Memory and Language, 68(3), 255–278.
  doi: 10.1016/j.jml.2012.11.001
  supports: Random-effects structure for confirmatory tests.
  short: why random slopes matter for confirmatory tests
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Matuschek, H., Kliegl, R., Vasishth, S., Baayen, H., & Bates, D. (2017). Balancing Type I error and power in linear mixed models. Journal of Memory and Language, 94, 305–315.
  doi: 10.1016/j.jml.2017.01.001
  supports: Balancing Type I error and power in mixed models.
  short: the cost of over-specified random effects
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Liang, K.-Y., & Zeger, S. L. (1986). Longitudinal data analysis using generalized linear models. Biometrika, 73(1), 13–22.
  doi: 10.1093/biomet/73.1.13
  supports: Generalised estimating equations.
  short: generalised estimating equations
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Cameron, A. C., & Miller, D. L. (2015). A practitioner's guide to cluster-robust inference. Journal of Human Resources, 50(2), 317–372.
  doi: 10.3368/jhr.50.2.317
  supports: Cluster-robust inference.
  short: cluster-robust inference and few clusters
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Killip, S., Mahfoud, Z., & Pearce, K. (2004). What is an intracluster correlation coefficient? Crucial concepts for primary care researchers. Annals of Family Medicine, 2(3), 204–208.
  doi: 10.1370/afm.141
  supports: The intracluster correlation and design effect.
  short: the intracluster correlation and the design effect
  type: Journal article
  checked: 2026-11-13, Crossref (title, journal, volume, issue and pages; the Crossref record lists the first author only)
```

*This note was initially drafted by Tony Myers with assistance from ChatGPT. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
