# Network Meta-Analysis Assumptions and Consistency

#### Purpose

This guide helps reviewers assess the assumptions underlying network meta-analysis (NMA). It focuses on connectedness, transitivity, direct and indirect evidence, consistency or coherence, effect modifiers, multi-arm trials and whether the network supports the comparisons being made.

#### What reviewers should look for

✓ The treatment network is sufficiently connected to estimate the comparisons of interest.

✓ The transitivity assumption is scientifically plausible.

✓ Important effect modifiers are similarly distributed across treatment comparisons.

✓ Agreement between direct and indirect evidence is assessed where both are available.

✓ Multi-arm trials are analysed using methods that preserve the correlation between comparisons sharing a common group.

✓ Claims based largely on indirect evidence are distinguished from those supported directly.

#### Common reviewer questions

##### What is transitivity?

**Transitivity** is the assumption that studies comparing different treatments are sufficiently similar that indirect comparisons are meaningful.

For example, if studies compare A versus B and other studies compare B versus C, an indirect A-versus-C comparison requires the studies to be comparable with respect to factors that modify treatment effects.

Potential effect modifiers may include:

- age;
- baseline severity;
- disease duration;
- intervention intensity;
- follow-up duration;
- risk of bias;
- concomitant treatment.

```references
- cite: Salanti, G. (2012). Indirect and mixed-treatment comparison, network, or multiple-treatments meta-analysis: Many names, many benefits, many concerns for the next generation evidence synthesis tool. Research Synthesis Methods, 3(2), 80–97.
  doi: 10.1002/jrsm.1037
  supports: The transitivity assumption and how its plausibility can be assessed.
  short: the assumptions of network meta-analysis
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### What is consistency or coherence?

**Consistency** (also called **coherence**) means that direct and indirect evidence estimate compatible treatment effects.

For example, the directly observed A-versus-C effect should broadly agree with the effect implied indirectly through A-versus-B and B-versus-C evidence.

Important disagreement is called **inconsistency** or **incoherence**.

##### How should inconsistency be assessed?

Possible approaches include:

- node-splitting;
- unrelated mean effects models;
- design-by-treatment interaction models;
- local inconsistency checks;
- comparison of direct and indirect estimates.

Reviewers should consider both statistical evidence and the scientific explanation for any inconsistency.

```references
- cite: Dias, S., Welton, N. J., Caldwell, D. M., & Ades, A. E. (2010). Checking consistency in mixed treatment comparison meta-analysis. Statistics in Medicine, 29(7–8), 932–944.
  doi: 10.1002/sim.3767
  supports: Node-splitting to compare direct and indirect evidence.
  short: node-splitting to check consistency
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Higgins, J. P. T., Jackson, D., Barrett, J. K., Lu, G., Ades, A. E., & White, I. R. (2012). Consistency and inconsistency in network meta-analysis: Concepts and models for multi-arm studies. Research Synthesis Methods, 3(2), 98–110.
  doi: 10.1002/jrsm.1044
  supports: Design-by-treatment interaction models and inconsistency involving multi-arm studies.
  short: design-by-treatment inconsistency and multi-arm studies
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Dias, S., Sutton, A. J., Ades, A. E., & Welton, N. J. (2013). Evidence synthesis for decision making 2: A generalized linear modeling framework for pairwise and network meta-analysis of randomized controlled trials. Medical Decision Making, 33(5), 607–617.
  doi: 10.1177/0272989X12458724
  supports: Models for detecting inconsistency in networks of evidence.
  short: DIC in network meta-analysis
  type: Journal article
  access: open
  access_checked: 2026-10-01, OpenAlex: open (hybrid, CC BY-NC, free to read at the publisher)
  checked: 2026-10-01, Crossref (published online 2012; volume 33 is 2013)
```


##### What is a connected network?

A treatment network is **connected** when every treatment included in a comparative analysis can be linked through at least one chain of treatment comparisons.

Disconnected components cannot provide relative treatment effects across the disconnected parts without additional assumptions.

##### Why do effect modifiers matter?

If an effect modifier is distributed differently across treatment comparisons, indirect comparisons may be biased.

For example, if high-dose interventions are studied mainly in younger populations and low-dose interventions mainly in older populations, the apparent treatment difference may partly reflect age rather than treatment.

##### How should multi-arm trials be handled?

Comparisons from a multi-arm trial share participants in the common treatment group and are statistically correlated.

Treating these comparisons as independent double-counts information and can underestimate uncertainty.

NMA software should account for this covariance structure.

##### What is direct versus indirect evidence?

**Direct evidence** comes from studies directly comparing two interventions.

**Indirect evidence** estimates a comparison through one or more common comparators.

Network estimates may combine both.

Reviewers should be wary when apparently precise conclusions are driven almost entirely by indirect evidence from a sparse network.

##### What do treatment rankings such as SUCRA mean?

Ranking statistics summarise the probability that each treatment occupies each rank. SUCRA (the surface under the cumulative ranking curve) condenses those probabilities into one number between 0 and 1 for each treatment; the P-score is its frequentist counterpart. A SUCRA of 1 would mean that a treatment is certain to be the best and a SUCRA of 0 that it is certain to be the worst; a SUCRA value is not the probability that the treatment is best.

They are frequently over-interpreted. A ranking:

- conveys order only, not the size of the differences between treatments or whether those differences matter;
- is itself uncertain, often very uncertain, and that uncertainty is rarely reported;
- is sensitive to the precision of each estimate, so a sparsely studied treatment with a wide interval can obtain a high probability of being best;
- can impose a definite order on effects that are close to indistinguishable;
- takes no account of the quality of the evidence, or of harms and costs, unless these are modelled.

Reviewers should expect rankings to be presented alongside the estimated effects and their uncertainty, and should be cautious wherever the ranking is itself the main claim.

```references
- cite: Salanti, G., Ades, A. E., & Ioannidis, J. P. A. (2011). Graphical methods and numerical summaries for presenting results from multiple-treatment meta-analysis: An overview and tutorial. Journal of Clinical Epidemiology, 64(2), 163–171.
  doi: 10.1016/j.jclinepi.2010.03.016
  supports: Rank probabilities, rankograms and SUCRA.
  short: rankograms and SUCRA
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Trinquart, L., Attiche, N., Bafeta, A., Porcher, R., & Ravaud, P. (2016). Uncertainty in treatment rankings: Reanalysis of network meta-analyses of randomized trials. Annals of Internal Medicine, 164(10), 666–673.
  doi: 10.7326/M15-2521
  supports: How uncertain treatment rankings are when the uncertainty is quantified.
  short: how uncertain treatment rankings are
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Mbuagbaw, L., Rochwerg, B., Jaeschke, R., et al. (2017). Approaches to interpreting and choosing the best treatments in network meta-analyses. Systematic Reviews, 6, 79.
  doi: 10.1186/s13643-017-0473-z
  supports: The limits of ranking statistics and how they should be interpreted alongside effect estimates.
  short: interpreting rankings in network meta-analysis
  type: Journal article
  checked: 2026-11-13, Crossref
```


##### Does random-effects NMA guarantee transitivity?

No.

Random effects model unexplained variation between studies.

They do not correct systematic imbalance in effect modifiers across treatment comparisons.

A random-effects NMA also commonly assumes a single heterogeneity parameter shared across every comparison in the network. That is a further assumption, not a consequence of the model, and it is rarely tested. See the note on between-study heterogeneity.

#### Common misconceptions

##### "A connected network is automatically a valid network."

Incorrect.

Connectedness is necessary but does not establish transitivity or consistency.

##### "No statistically significant inconsistency means the network is consistent."

Incorrect.

Inconsistency tests may have low power, especially in sparse networks.

Scientific assessment of effect modifiers remains essential.

##### "Direct and indirect evidence are interchangeable."

Incorrect.

They rely on different evidence structures and assumptions.

##### "A random-effects model solves violations of transitivity."

Incorrect.

Heterogeneity and transitivity are different issues.

#### Common terminology

**NMA (Network Meta-Analysis)** – simultaneous synthesis of evidence across multiple interventions.

**Direct evidence** – evidence from head-to-head comparisons.

**Indirect evidence** – evidence inferred through common comparators.

**Transitivity** – assumption allowing valid indirect comparison across sufficiently comparable studies.

**Consistency / coherence** – agreement between direct and indirect evidence.

**Inconsistency / incoherence** – disagreement between direct and indirect evidence.

**Effect modifier** – study or participant characteristic that changes treatment effect.

**Node-splitting** – comparison of direct and indirect evidence for a particular treatment contrast.

**Multi-arm trial** – study containing three or more treatment groups.

**SUCRA / P-score** – summary statistics describing a treatment's position in the ranking distribution, not the magnitude of its effect.

#### Common reviewer red flags

- Transitivity never discussed.
- Important effect modifiers differ markedly across comparisons.
- No assessment of direct versus indirect agreement.
- Sparse network interpreted with excessive certainty.
- Multi-arm trial comparisons treated as independent.
- Disconnected network used to estimate unsupported contrasts.
- Treatment rankings emphasised without discussing network uncertainty.

#### Quick reviewer checklist

□ The network is connected for the comparisons being estimated.

□ Transitivity is scientifically plausible.

□ Important effect modifiers are examined.

□ Direct and indirect evidence are distinguished.

□ Consistency or incoherence is assessed.

□ Multi-arm trial dependence is handled correctly.

□ Conclusions reflect the strength and structure of the network evidence.

#### References

Checked sources for this topic. A section with its own list shows that list instead. Each entry says what it supports; a source is listed for that purpose only, not as support for every sentence in the note.

```references
- cite: Salanti, G. (2012). Indirect and mixed-treatment comparison, network, or multiple-treatments meta-analysis: Many names, many benefits, many concerns for the next generation evidence synthesis tool. Research Synthesis Methods, 3(2), 80–97.
  doi: 10.1002/jrsm.1037
  supports: The assumptions of network meta-analysis.
  short: the assumptions of network meta-analysis
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Dias, S., Welton, N. J., Caldwell, D. M., & Ades, A. E. (2010). Checking consistency in mixed treatment comparison meta-analysis. Statistics in Medicine, 29(7–8), 932–944.
  doi: 10.1002/sim.3767
  supports: Checking consistency by node-splitting.
  short: node-splitting to check consistency
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Higgins, J. P. T., Jackson, D., Barrett, J. K., Lu, G., Ades, A. E., & White, I. R. (2012). Consistency and inconsistency in network meta-analysis: Concepts and models for multi-arm studies. Research Synthesis Methods, 3(2), 98–110.
  doi: 10.1002/jrsm.1044
  supports: Consistency, inconsistency and multi-arm studies.
  short: design-by-treatment inconsistency and multi-arm studies
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Dias, S., Sutton, A. J., Ades, A. E., & Welton, N. J. (2013). Evidence synthesis for decision making 2: A generalized linear modeling framework for pairwise and network meta-analysis of randomized controlled trials. Medical Decision Making, 33(5), 607–617.
  doi: 10.1177/0272989X12458724
  supports: Inconsistency in networks of evidence.
  short: DIC in network meta-analysis
  type: Journal article
  access: open
  access_checked: 2026-10-01, OpenAlex: open (hybrid, CC BY-NC, free to read at the publisher)
  checked: 2026-10-01, Crossref (published online 2012; volume 33 is 2013)
- cite: Salanti, G., Ades, A. E., & Ioannidis, J. P. A. (2011). Graphical methods and numerical summaries for presenting results from multiple-treatment meta-analysis: An overview and tutorial. Journal of Clinical Epidemiology, 64(2), 163–171.
  doi: 10.1016/j.jclinepi.2010.03.016
  supports: Presenting and ranking results from network meta-analysis.
  short: rankograms and SUCRA
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Trinquart, L., Attiche, N., Bafeta, A., Porcher, R., & Ravaud, P. (2016). Uncertainty in treatment rankings: Reanalysis of network meta-analyses of randomized trials. Annals of Internal Medicine, 164(10), 666–673.
  doi: 10.7326/M15-2521
  supports: Uncertainty in treatment rankings.
  short: how uncertain treatment rankings are
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Mbuagbaw, L., Rochwerg, B., Jaeschke, R., et al. (2017). Approaches to interpreting and choosing the best treatments in network meta-analyses. Systematic Reviews, 6, 79.
  doi: 10.1186/s13643-017-0473-z
  supports: Interpreting treatment rankings.
  short: interpreting rankings in network meta-analysis
  type: Journal article
  checked: 2026-11-13, Crossref
- cite: Hutton, B., Salanti, G., Caldwell, D. M., et al. (2015). The PRISMA extension statement for reporting of systematic reviews incorporating network meta-analyses of health care interventions: Checklist and explanations. Annals of Internal Medicine, 162(11), 777–784.
  doi: 10.7326/M14-2385
  supports: The PRISMA reporting extension for network meta-analyses.
  short: the PRISMA reporting extension for network meta-analysis
  type: Journal article
  checked: 2026-11-13, Crossref
```

---

*Based on:* General network meta-analysis methodological literature; no single source. See also the notes on between-study heterogeneity and on dose-response coverage.

*This note was initially drafted by Tony Myers with assistance from ChatGPT. It is part of the reviewer-notes collection, licensed under CC BY 4.0; see LICENCE.md in this folder.*
