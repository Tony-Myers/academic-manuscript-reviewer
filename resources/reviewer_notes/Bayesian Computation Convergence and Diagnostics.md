# Bayesian Computation, Convergence and Diagnostics

#### Purpose

This guide helps reviewers evaluate Bayesian computation, Markov chain Monte Carlo (MCMC) convergence, Hamiltonian Monte Carlo (HMC) diagnostics and computational reproducibility. It focuses on whether posterior estimates are likely to be reliable and whether the computational methods have been reported transparently.

##### What reviewers should look for

✓ The manuscript reports the Bayesian software, package and version (e.g., Stan, brms, CmdStanR, JAGS or PyMC).

✓ The manuscript reports sufficient computational details, including the number of chains, warm-up (burn-in), sampling iterations, thinning (if used), random seed and sampler settings where appropriate.

✓ The manuscript reports convergence diagnostics such as R-hat (potential scale reduction factor, PSRF), effective sample size (ESS), trace plots or equivalent diagnostics.

✓ Hamiltonian Monte Carlo (HMC) diagnostics, including divergent transitions, maximum tree depth and Bayesian Fraction of Missing Information (BFMI), are reported where Stan or NUTS is used.

✓ Posterior summaries are based on adequately converged Markov chains.

#### Common reviewer questions

##### What is Markov chain Monte Carlo (MCMC)?

**Markov chain Monte Carlo (MCMC)** is a computational method that generates samples from the posterior distribution when direct calculation is difficult or impossible. Posterior estimates are reliable only if the Markov chains have converged and mixed well.

##### What is Hamiltonian Monte Carlo (HMC)?

**Hamiltonian Monte Carlo (HMC)** is an efficient MCMC algorithm that uses gradient information to explore the posterior distribution more efficiently than traditional random-walk samplers.

Many Bayesian analyses using **Stan** or **brms** employ HMC through the **No-U-Turn Sampler (NUTS)**.

##### What is NUTS?

**NUTS (No-U-Turn Sampler)** is an adaptive version of Hamiltonian Monte Carlo that automatically selects an appropriate trajectory length during sampling. NUTS is the default sampler used by Stan.

##### What is R-hat?

**R-hat (potential scale reduction factor, PSRF)** compares variation within Markov chains to variation between chains.

Typical interpretation:

- R-hat ≈ 1.00 → good convergence
- R-hat ≤ 1.01 → generally considered acceptable
- Larger values suggest incomplete convergence

Reviewers should expect R-hat values close to 1.00 for all important parameters.

Current practice is to compute a rank-normalised split R-hat from at least four chains and to require values below 1.01. The older rule that values below 1.1 are acceptable is now regarded as too lenient, and the original statistic can miss problems when chains have heavy tails or differ in variance. Manuscripts reporting only "R-hat < 1.1" should be read with that in mind.

```references
- cite: Vehtari, A., Gelman, A., Simpson, D., Carpenter, B., & Bürkner, P.-C. (2021). Rank-normalization, folding, and localization: An improved R-hat for assessing convergence of MCMC (with discussion). Bayesian Analysis, 16(2), 667–718.
  doi: 10.1214/20-BA1221
  supports: The rank-normalised split R-hat, the recommended threshold of 1.01, and the weaknesses of the original statistic.
  short: rank-normalised R-hat and bulk and tail effective sample size
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Gelman, A., & Rubin, D. B. (1992). Inference from iterative simulation using multiple sequences. Statistical Science, 7(4), 457–472.
  doi: 10.1214/ss/1177011136
  supports: The original potential scale reduction factor comparing between-chain and within-chain variation.
  short: the original potential scale reduction factor
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### What is Effective Sample Size (ESS)?

**Effective Sample Size (ESS)** estimates how many independent samples are represented by the correlated MCMC draws.

Because MCMC samples are autocorrelated, the effective sample size is usually smaller than the total number of iterations.

Larger ESS generally produces more stable posterior summaries.

Many software packages report:

- Bulk ESS (accuracy of posterior means and medians)
- Tail ESS (accuracy of credible interval tails)

A common recommendation is a bulk ESS and a tail ESS of at least 100 per chain (400 for four chains) before R-hat and the posterior summaries are relied on. Precise estimates of extreme quantiles need more. A total ESS quoted without saying whether it is bulk or tail, or for which parameters, is hard to assess.

```references
- cite: Vehtari, A., Gelman, A., Simpson, D., Carpenter, B., & Bürkner, P.-C. (2021). Rank-normalization, folding, and localization: An improved R-hat for assessing convergence of MCMC (with discussion). Bayesian Analysis, 16(2), 667–718.
  doi: 10.1214/20-BA1221
  supports: Bulk and tail effective sample size and the recommended minimum of 400.
  short: rank-normalised R-hat and bulk and tail effective sample size
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### What are trace plots?

**Trace plots** display sampled parameter values against iteration number.

Well-converged chains should show:

- good mixing
- stable behaviour
- no long-term trends
- substantial overlap between chains

Poor mixing or drifting chains may indicate lack of convergence.

##### What is autocorrelation?

**Autocorrelation** measures similarity between successive MCMC samples.

High autocorrelation reduces the effective sample size and increases Monte Carlo error.

Modern HMC algorithms usually exhibit lower autocorrelation than older Gibbs or Metropolis samplers.

##### What is Monte Carlo Standard Error (MCSE)?

**Monte Carlo Standard Error (MCSE)** estimates uncertainty arising from finite MCMC sampling rather than statistical uncertainty in the model itself.

Small MCSE indicates that posterior summaries have been estimated precisely.

##### What are divergent transitions?

A **divergent transition** occurs when Hamiltonian Monte Carlo cannot accurately follow the posterior geometry.

Divergent transitions suggest that posterior summaries may be unreliable.

Common causes include:

- poorly scaled parameters
- difficult posterior geometry
- inadequate parameterisation

Reviewers should expect authors either to eliminate divergent transitions or explain their impact.

##### What is maximum tree depth?

**Maximum tree depth** limits how far NUTS explores each trajectory.

Repeated tree-depth warnings may indicate inefficient sampling or a difficult posterior geometry.

Increasing tree depth alone does not necessarily solve the underlying modelling problem.

##### What is BFMI?

**Bayesian Fraction of Missing Information (BFMI)** measures how efficiently Hamiltonian Monte Carlo explores the posterior energy distribution.

Low BFMI suggests inefficient exploration and possible sampling problems. Current Stan tools warn when a chain's value falls below about 0.3 (0.2 in earlier versions).

BFMI should be considered together with divergent transitions and other HMC diagnostics rather than interpreted in isolation.

#### Common misconceptions

##### "The model converged because the software finished."

Incorrect.

Successful completion of MCMC sampling does not guarantee convergence.

##### "R-hat = 1 proves convergence."

Incorrect.

R-hat close to 1 is reassuring but should be interpreted together with ESS, trace plots and other diagnostics.

---

##### "A very large number of iterations guarantees convergence."

Incorrect.

Longer chains cannot compensate for poor model specification or pathological posterior geometry.

---

##### "No divergent transitions means the model is perfect."

Incorrect.

Absence of divergent transitions is reassuring but does not guarantee that the model is correctly specified.

---

##### "Thinning improves inference."

Usually incorrect.

Modern Bayesian software rarely requires thinning, as increasing the number of posterior draws is generally preferable unless storage limitations are important.

---

#### Common terminology

**MCMC (Markov chain Monte Carlo)** generates samples from the posterior distribution.

**HMC (Hamiltonian Monte Carlo)** uses gradients to improve sampling efficiency.

**NUTS (No-U-Turn Sampler)** automatically adapts HMC trajectory length.

**R-hat (Potential Scale Reduction Factor; PSRF)** assesses agreement between Markov chains.

**ESS (Effective Sample Size)** estimates the number of effectively independent posterior samples.

**Bulk ESS** assesses precision of posterior location estimates.

**Tail ESS** assesses precision of posterior tail probabilities and credible intervals.

**MCSE (Monte Carlo Standard Error)** measures simulation error due to finite MCMC sampling.

**BFMI (Bayesian Fraction of Missing Information)** assesses whether HMC efficiently explores posterior energy.

**Trace plot** visualises sampling behaviour across iterations.

**Divergent transition** indicates numerical difficulties during Hamiltonian Monte Carlo sampling.



---

#### Common reviewer red flags

- Software or package versions not reported.
- Number of chains or iterations omitted.
- R-hat not reported.
- Effective sample size (ESS) not reported.
- Trace plots unavailable when convergence is uncertain.
- Divergent transitions ignored.
- Tree-depth warnings ignored.
- BFMI warnings ignored.
- Convergence stated without supporting diagnostics.
- Computational settings insufficient for reproduction.

---

#### Quick reviewer checklist

□ Software, package and version are reported.

□ Number of chains, warm-up, iterations and random seed are reported.

□ R-hat (PSRF) values indicate adequate convergence.

□ Effective sample size (ESS) is adequate for key parameters.

□ Trace plots show good mixing.

□ Divergent transitions are absent or appropriately addressed.

□ Maximum tree depth warnings are investigated.

□ BFMI is acceptable when using Stan or HMC.

□ Posterior summaries appear based on well-converged Markov chains.

□ Computational methods are reproducible.

#### References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Vehtari, A., Gelman, A., Simpson, D., Carpenter, B., & Bürkner, P.-C. (2021). Rank-normalization, folding, and localization: An improved R-hat for assessing convergence of MCMC (with discussion). Bayesian Analysis, 16(2), 667–718.
  doi: 10.1214/20-BA1221
  supports: Improved R-hat and effective sample size diagnostics, with recommended thresholds.
  short: rank-normalised R-hat and bulk and tail effective sample size
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Gelman, A., & Rubin, D. B. (1992). Inference from iterative simulation using multiple sequences. Statistical Science, 7(4), 457–472.
  doi: 10.1214/ss/1177011136
  supports: The original potential scale reduction factor.
  short: the original potential scale reduction factor
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Kruschke, J. K. (2021). Bayesian analysis reporting guidelines. Nature Human Behaviour, 5(10), 1282–1291.
  doi: 10.1038/s41562-021-01177-7
  supports: What should be reported about computation in a Bayesian analysis.
  short: reporting guidelines for Bayesian analyses
  type: Journal article
  access: open
  access_checked: 2026-10-01, OpenAlex: open (hybrid, CC BY)
  checked: 2026-09-30, Crossref
- cite: van Doorn, J., van den Bergh, D., Böhm, U., et al. (2021). The JASP guidelines for conducting and reporting a Bayesian analysis. Psychonomic Bulletin & Review, 28(3), 813–826.
  doi: 10.3758/s13423-020-01798-5
  supports: Guidelines for conducting and reporting a Bayesian analysis.
  short: guidelines for conducting and reporting a Bayesian analysis
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Carpenter, B., Gelman, A., Hoffman, M. D., et al. (2017). Stan: A probabilistic programming language. Journal of Statistical Software, 76(1).
  doi: 10.18637/jss.v076.i01
  supports: The Stan language and its Hamiltonian Monte Carlo sampler.
  short: the Stan language and its samplers
  type: Journal article
  checked: 2026-11-13, Crossref
```

---

*Based on:* Kruschke, J. K. (2021), https://doi.org/10.1038/s41562-021-01177-7; van Doorn, J., et al. (2021). The JASP guidelines for conducting and reporting a Bayesian analysis. *Psychonomic Bulletin & Review*, 28, 813-826. https://doi.org/10.3758/s13423-020-01798-5. See also the note on model fit, information criteria and R² for DIC.

*This note was initially drafted by Tony Myers with assistance from ChatGPT. It summarises and restates guidance from the sources above; it does not reproduce them. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
