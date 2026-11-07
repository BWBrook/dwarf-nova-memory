# Barry
You know, a lot about my background as a computational ecologist interested in contemporary and deep time ecology and evolution, big picture questions, leveraging large data sets, simulation modelling and so on. A working scientist, publishes regularly. But I'm interested in thinking about a kind of hobby project where I could contribute to a different field of science as an amateur, but in a serious way by leveraging codex and Claude agents to produce a preprint or even a paper that contributes to the scientific body of knowledge. And the area I'm thinking of looking into is astronomy and astrophysics given that this is one of my passions as an amateur astrophotographer. And long time observer of astronomy news and having grown up at Siding Spring Observatory and so on. It's another field of science that I have an interest in, even though it's not my area of speciality. At most I did first year physics at university and a second year astronomy unit. But, you know, I haven't done any primary research in astronomy. So anyway, the question, it's just a general question I'm posing to you right now to suggest is, if I was to pick a particular topic to work on with agents, what would be a good candidate? And I'm thinking of something where lots of data has been collected either by professionals or amateurs that's available publicly in databases and suffers from the problem of simply there are too many things to do and not enough people to do it in the professional field. And so questions remain unanswered, data remains unanalyzed. It could be statistical analyses, it could be simulation modelling, some combination of it. And it could be really any topic in astronomy and astrophysics. I'm not particularly concerned. Obviously things like variable star data are widely collected, but there might be even professional data that comes from major telescopes that's deposited on online resources. I don't know. I'm just ideating at this stage. And so I wanted you to have, I think, hunt around and propose a slew of possible ideas, ideally ranked by what you think are interesting, where I could make a contribution, where the data are readily available, where people might be interested in a paper that results from it, where it's neglected, whatever your criteria are for ranking them. And have enough general ideas that I can make a choice ultimately, even if you have your ranked list.

# GPT-6 Pro
Barry, **I think this is a realistic route to a worthwhile scientific contribution**, particularly if you choose a problem involving population dynamics, incomplete observation, historical inference or simulation. Those would let you bring substantial scientific expertise to astronomy while learning the physics of one well-defined system.

My leading recommendations are:

- **Dwarf-nova outbursts** for a manageable first project using long observational records.
- **Meteor streams** for a combination of large public datasets, statistical inference and Solar System history.
- **Gaia star-cluster populations** for the strongest connection to your interests in population dynamics and reconstructing the past.
- **Jupiter’s storms** as an especially attractive connection to your observing and imaging interests.

I looked across official archives and recent research, and assembled **20 ranked possibilities**. The ranking reflects my judgment about the combination of scientific interest, your transferable skills, accessible data, learning burden and the prospect of defining a bounded contribution. These are researched candidate projects; establishing the novelty of the final question would still require a focused literature review.

I have also put the shortlist, archive links, nearby papers and initial feasibility tests into a reference guide: **[astronomy_research_opportunities.pdf](https://chatgpt.com/library?file_id=libfile_c615972540d48191840cd1a44990717f&account_id=personal)**.

## The shortlist at a glance

| Rank | Candidate project | What makes it attractive for you |
|---:|---|---|
| **1** | Dwarf-nova outburst memory and changes in behaviour | Long time series; recurrent events; latent states; a tractable physical system |
| **2** | Which weak meteor showers are persistent debris streams? | Large datasets; clustering; independent prediction; Solar System history |
| **3** | Open-cluster survival, dissolution and formation history | Exceptionally close to population ecology and historical reconstruction |
| **4** | Jupiter storm lifecycles | Feature tracking, population turnover and a direct connection to imaging |
| **5** | Mira evolution versus stochastic period wandering | Century-scale observations; distinguishing directional change from fluctuation |
| **6** | Kuiper-belt model discrimination with OSSOS | Forward simulation and inference about the early Solar System |
| **7** | Century-scale stellar dimming with DASCH | Historical observations; rare events; long-term stellar behaviour |
| **8** | Galaxy quenching and recovery in IllustrisTNG | Population transitions through cosmic time using existing simulations |
| **9** | Exoplanet transit forecast reliability | A bounded, useful prediction problem that could connect to your own observations |
| **10** | Faint stellar tidal streams and galaxy assembly | Images as a fossil record of past interactions |
| **11** | Martian slope-streak turnover | A particularly strong ecological-methods connection in planetary science |
| **12** | Asteroid shape predictions tested against independent occultations | Clear predictions, independent observations and geometric modelling |
| **13** | Young-star variability classes as temporary states | Developmental stages, state changes and heterogeneous observation windows |
| **14** | Satellite-galaxy diversity and quenching with SAGA | Nested populations, environmental effects and variation among hosts |
| **15** | Active and dormant phases in X-ray binaries | Recurrent events and long-term changes in accretion behaviour |
| **16** | Active-asteroid onset, duration and recurrence | Archival images linked to physical mechanisms of dust release |
| **17** | Dusty episodes around mature stars | Rare-event inference connected to planetary-system evolution |
| **18** | Changing-look active galactic nuclei | Dramatic physical transitions; substantial data, but more demanding interpretation |
| **19** | Stellar-flare triggering versus variable background activity | A good modelling problem with a crowded recent literature |
| **20** | One-off fast radio bursts versus rare repeaters | Fascinating population inference, with difficult identifiability and strong competition |

The lower-ranked projects are not necessarily less interesting. Several have higher scientific stakes but also a greater chance that a seemingly fresh statistical idea has already been explored, or that interpretation requires substantial specialist knowledge.

# The six I would investigate first

## 1. Do dwarf novae retain “memory” of previous outbursts?

**The physical question:** Do these systems have stable, characteristic outburst behaviour, or do they move between long-lived accretion states? Does the size or duration of one outburst help predict the next?

A dwarf nova is a binary system in which a white dwarf accretes material from a companion through a disc. Its repeated brightenings give you a natural recurrent-event problem. Relevant observations are available through **AAVSO, ASAS-SN and CRTS**. There is already a published catalogue covering 722 dwarf novae, so there is a substantial observational and classificatory foundation on which to build. AAVSO makes its observations available for research, and ASAS-SN provides programmatic access to its light curves. [heasarc.gsfc.nasa.gov](https://heasarc.gsfc.nasa.gov/W3Browse/all/dncvobcat.html?utm_source=chatgpt.com)

**The proposed contribution** would be a consistent analysis of a carefully selected sample, asking whether apparent changes in recurrence arise from:

- Persistent differences among systems.
- Dependence on the preceding outburst.
- Movement between different accretion states.
- Changes in observation frequency and sensitivity.

That is scientifically useful because these alternatives imply different things about how the disc stores and releases material. A particularly good paper would connect the inferred behaviour to physical subclasses or other system properties.

**Why it suits you:** Recurrent events, individual heterogeneity, imperfect detection and state transitions are close to familiar ecological problems. The physical interpretation is sufficiently bounded to learn alongside the analysis.

**First pilot:** Select approximately 20 well-observed systems. Extract known outbursts, reconstruct the actual observing windows, and simulate competing processes through those windows. Establish whether the available observations can distinguish memory from missed events.

**Main difficulty:** Observing effort can increase when something interesting happens. Measurements also come from different filters and observing methods. That observation process belongs in the model.

**My assessment:** The strongest balance of feasibility, depth and scope for a first astronomy paper.

## 2. Which weak meteor showers are genuine, persistent debris streams?

**The physical question:** When meteors have similar radiants and orbits, how confidently can we infer that they belong to a common debris stream? Which weak streams persist or evolve coherently across years?

The **Global Meteor Network** provides public meteor trajectories, orbits and associated measurements under a CC BY licence. This gives you a substantial dataset without requiring your own observing network. [globalmeteornetwork.org](https://globalmeteornetwork.org/data/?utm_source=chatgpt.com)

There is already serious work on false-positive associations and meteor-shower identification, including recent work combining multiple networks. Consequently, a generic application of a clustering algorithm would have a weak claim to novelty. [arxiv.org](https://arxiv.org/abs/2404.08507?utm_source=chatgpt.com)

**The promising extension** is to make independent prediction central:

> If a weak stream is identified using earlier observations, does its predicted radiant, orbital distribution and seasonal activity recur in later observations?

You could compare plausible debris-stream models against chance structure in the background, propagate orbit uncertainties, and investigate which physical characteristics predict persistence. That could produce a scientifically useful assessment of particular streams and the reliability of their proposed associations.

**Why it suits you:** This combines mixture models, community-like structure, sampling effort, false discovery and temporal validation. It also opens a route towards dynamical simulations of debris evolution if the initial statistical work is productive.

**First pilot:** Use one strong shower as a positive control, three weak candidate showers and matched background samples. Freeze the model after fitting earlier years, then predict later years.

**Main difficulty:** Similar measured orbits do not automatically imply a common parent. Measurement error, selection and the number of possible associations searched all matter.

**My assessment:** Probably the best alternative to dwarf novae, especially if Solar System origins capture your imagination.

## 3. What determines the survival of open star clusters?

**The physical question:** How do cluster mass and Galactic environment influence dissolution, and what can the surviving population reveal about past cluster formation?

This is the project with the clearest connection to your professional interests. You have populations that form, change mass, move through heterogeneous environments and disappear as recognisable groups.

A particularly useful recent development is a published selection function for the **Hunt–Reffert Gaia DR3 cluster census**, based on more than 80,000 injection-and-recovery experiments, with supporting resources. That makes a more defensible treatment of the observation process possible. Existing work has already modelled cluster mass functions and dissolution, so the opportunity is to test a specific extension or robustness question. [arxiv.org](https://arxiv.org/abs/2510.18343?utm_source=chatgpt.com)

**The proposed contribution:** Ask whether an inferred environmental effect on cluster survival persists when formation history, mass evolution, age uncertainty and detection are modelled together. Alternatively, determine which aspects of formation and dissolution can actually be distinguished with the available census.

The crucial issue is that a present-day catalogue contains **survivors**. Its age distribution depends jointly on when clusters formed, how they evolved and dissolved, where they moved, and whether they can now be detected. These processes can imitate one another.

**First pilot:** Restrict attention to a manageable local volume and a defensible mass and age range. Reproduce the published age–mass distribution, then generate synthetic catalogues with known formation and dissolution histories. Test which parameters are recoverable before fitting more elaborate physical models.

**Main difficulty:** Identifiability and the interpretation of stellar ages and cluster masses.

**My assessment:** My strongest recommendation for a longer-term intellectual project. It could become a substantial research programme, although I would begin with a narrow question.

## 4. What governs the lifetimes, mergers and drift of Jupiter’s small storms?

**The physical question:** Within one atmospheric belt, how long do identifiable vortices persist, when do they merge or disappear, and how does their behaviour depend on latitude and surrounding circulation?

This has unusually tangible evidence of unfinished work. A British Astronomical Association report on the **2024–25 apparition** explicitly identifies further detailed analysis of JUPOS latitude measurements as work remaining to be done. That is a more concrete opening than simply assuming an archive must contain neglected science. [britastro.org](https://britastro.org/wp-content/uploads/2026/01/Report-2024-25_no-7_v2-revised.pdf?utm_source=chatgpt.com)

Potential sources include published BAA/JUPOS material, amateur image archives and **Hubble’s OPAL programme**, which provides public images and maps of the outer planets. The availability of the complete underlying JUPOS measurement database would need to be checked; public reports and images do not automatically imply unrestricted bulk access to every measurement. [MAST](https://archive.stsci.edu/hlsp/opal?utm_source=chatgpt.com)

**The proposed contribution:** Construct detection histories for one clearly defined class of feature, then estimate persistence, drift, merger and disappearance while accounting for visibility and image quality.

There is a compelling connection to population ecology here: individual identification, turnover, interactions and environmental dependence. The resulting interpretation would concern atmospheric dynamics.

**First pilot:** Choose one belt and one observing season. Manually establish a set of unambiguous feature histories, preferably with a second independent annotator, before attempting automated tracking.

**Main difficulty:** A feature can become unobservable because of rotation, poor seeing, projection or a change in appearance. Those events need to be distinguished from physical disappearance.

**My assessment:** The most appealing combination of scientific work and your existing enjoyment of planetary imaging. Your own observations could eventually become part of the project.

## 5. When does a Mira’s changing period indicate stellar evolution?

**The physical question:** Which apparent long-term changes in pulsation period are too large or too structured to be explained by stochastic wandering, waveform changes and observational artefacts?

Miras are pulsating evolved stars, and long amateur observing records are especially valuable for them. There is already extensive research: a 2023 study analysed 548 Miras in relation to period behaviour, asymmetry and mass loss. The contribution would therefore need to go beyond identifying stars with changing fitted periods. [arxiv.org](https://arxiv.org/abs/2302.02206?utm_source=chatgpt.com)

**The proposed contribution:** Compare explicit models of stochastic phase wandering, gradual secular change and discrete changes, propagating uncertainties arising from the real observation history. Then ask whether robustly inferred changes associate with independent stellar properties.

This would provide better-calibrated evidence about which stars are plausible candidates for rapid evolutionary change. A period trend alone would be insufficient to establish a particular internal event such as a thermal pulse.

**Why it suits you:** This is closely related to distinguishing directional environmental or evolutionary change from noisy fluctuations, with the additional challenge that the timing of the underlying cycle is itself uncertain.

**First pilot:** Analyse 30–50 stars, including well-known changing-period examples and relatively stable controls. Simulate alternative processes at the actual observation times and compare predictive performance on withheld intervals.

**Main difficulty:** Very flexible stochastic models can absorb genuine evolution, while overly rigid models can turn ordinary variability into apparent evolution. Physical input is needed to constrain both.

**My assessment:** A strong option if you enjoy long historical records and careful inference more than large-scale image processing.

## 6. Which histories of the outer Solar System can OSSOS actually distinguish?

**The physical question:** How much evidence do observed trans-Neptunian populations provide for competing early Solar System histories once survey selection and uncertain population distributions are included?

The **Outer Solar System Origins Survey, OSSOS**, is valuable because its observational selection is characterised and its Survey Simulator is public. This allows you to generate a hypothetical intrinsic population and ask what the survey would have detected. [GitHub](https://github.com/OSSOS/SurveySimulator?utm_source=chatgpt.com)

Published work already uses this machinery to compare models, including models involving a transient rogue planet. The starting point would be a reproducible published comparison, followed by a specific question about model discrimination. [arxiv.org](https://arxiv.org/abs/2306.12847?utm_source=chatgpt.com)

**The proposed contribution:** Determine whether support for one dynamical scenario persists across plausible size, brightness and orbital distributions. Identify which observations genuinely discriminate between scenarios, and which conclusions depend strongly on population assumptions.

This is a good match to your interest in deep-time reconstruction: present observations are filtered remnants of historical processes, and simulation connects the two.

**First pilot:** Reproduce one published model comparison, then generate synthetic detected samples under known alternatives. Establish where the inference succeeds and where different histories become observationally indistinguishable.

**Main difficulty:** The orbital physics requires more learning than the top few projects. A broad catalogue assembled from heterogeneous discoveries also lacks the clean selection model that makes OSSOS useful.

**My assessment:** The strongest simulation-first Solar System option. It could start with existing simulated populations and progress to new dynamical work later.

# Fourteen further serious possibilities

## 7. Century-scale dimming and obscuration episodes in DASCH

**Question:** How frequently do stars in a well-defined population enter prolonged dim states, and do those states recur over decades?

**DASCH** digitises historical Harvard photographic plates, providing observations extending across much of the late nineteenth and twentieth centuries. Its public DR7 data products make unusually long baselines available. [dasch.cfa.harvard.edu](https://dasch.cfa.harvard.edu/dr7/?utm_source=chatgpt.com)

The promising project would select a coherent stellar population and estimate the incidence, duration or recurrence of dimming episodes, with a physical interpretation involving obscuration or stellar behaviour.

A pilot could examine known examples and matched controls before moving to a few hundred independently selected stars. Plate calibration, blends and catalogue associations are central: DASCH documents calibration choices capable of generating spurious trends, and a missing measurement needs careful interpretation. [dasch.cfa.harvard.edu](https://dasch.cfa.harvard.edu/dr7/ki/?utm_source=chatgpt.com)

**Appeal:** Exceptional historical reach.  
**Limitation:** Considerable effort may go into validating the observations before the astrophysical question can be answered.

## 8. How often do galaxies stop forming stars—and subsequently recover?

**Question:** Is quenching usually a persistent transition, or do galaxies cycle through low- and high-star-formation states? How does that depend on environment and assembly history?

**IllustrisTNG** makes simulation catalogues, merger trees and other products publicly available through an account-based service. A project can begin with selected catalogues and histories. It does not require running a cosmological simulation or downloading every snapshot. [Data Access](https://www.tng-project.org/data/?utm_source=chatgpt.com)

The proposed angle would estimate transition and residence times under definitions that remain interpretable when snapshots are widely spaced, then test a specific physical comparison, such as central versus satellite galaxies. Recent papers already study merger-related quenching and rejuvenation, so the exact question needs close positioning. [arxiv.org](https://arxiv.org/abs/2603.12651?utm_source=chatgpt.com)

**Pilot:** A few hundred histories; reproduce a published definition, then deliberately reduce temporal resolution to assess what it loses.

**Appeal:** Outstanding intellectual fit.  
**Limitation:** Results are conditional on the simulation’s physical prescriptions, and this is a competitive field.

## 9. How reliable are exoplanet transit forecasts?

**Question:** Do published uncertainty intervals for future transit times have the coverage they claim, and which new observations would most improve them?

ExoClock already conducts extensive ephemeris maintenance; its fourth major release addresses 620 planets. A fresh contribution could focus on **retrospective forecasting**: use only information available at a historical date, predict later transits, and evaluate the predictions. [arxiv.org](https://arxiv.org/abs/2511.14407?utm_source=chatgpt.com)

You could compare alternative uncertainty models and observing-allocation rules, asking which measurements provide the greatest improvement for a fixed amount of telescope time.

**Pilot:** Thirty to fifty planets with sufficiently long timing records, using strict separation between fitting and evaluation periods.

**Appeal:** A bounded question with practical value, and a possible bridge to your own observations.

**Limitation:** Time standards, correlated timing errors and reused measurements require care. The novelty review must include existing prioritisation methods as well as ephemeris papers.

## 10. What do faint tidal streams reveal about galaxy assembly?

**Question:** How does the incidence or morphology of faint stellar streams vary with galaxy mass or environment after accounting for detectability?

These structures are remnants of interactions and disruption, making them a form of astronomical historical evidence. Recent work such as **STRRINGS** has already inspected a large nearby-galaxy sample and studied narrow streams, providing a foundation and a substantial nearby literature. [arxiv.org](https://arxiv.org/abs/2508.02154?utm_source=chatgpt.com)

A useful extension could measure recovery of realistic stream structures injected into public survey images, then use that calibration to test one previously uncertain physical contrast.

**Pilot:** Roughly 100 galaxies, with blinded recovery of transplanted or simulated structures across different host and background conditions.

**Appeal:** Strong connection to deep-time inference and your interest in faint astronomical imaging.

**Limitation:** Galactic cirrus, scattered light and background subtraction can imitate streams. Converting visible-stream frequency into merger frequency also requires assumptions about visibility lifetimes.

## 11. What controls the formation and fading of Martian slope streaks?

This sits in **planetary geomorphology**, but deserves inclusion because the statistical fit is unusually strong.

**Question:** How long do individual streaks remain visible, and how do formation and fading vary with season, location and dust conditions?

A 2025 study produced a public dataset containing more than two million detections from repeat Mars Reconnaissance Orbiter CTX observations. These include repeated detections of features; the count is not a count of unique streaks. Global rates and environmental relationships have already been investigated. [Nature Communications](https://www.nature.com/articles/s41467-025-65522-4?utm_source=chatgpt.com)

The proposed extension would reconstruct individual histories and distinguish fresh, fading, obscured and absent states.

**Pilot:** Two or three sites with 20–40 useful repeat images each.

**Appeal:** Detection histories, persistence and turnover translate directly from ecology.

**Limitation:** Individual matching has to be established, and changes in illumination or dust cover can resemble changes in the feature itself.

## 12. Do asteroid shape models predict independent observations accurately?

**Question:** How well do shape and rotation models predict subsequent stellar occultations, and are their uncertainties realistic?

**DAMIT** provides asteroid shape models, while the Planetary Data System hosts asteroid occultation observations. These offer a route to independent geometric predictions. [DAMIT](https://damit.cuni.cz/pages/documentation?utm_source=chatgpt.com)

The contribution would need to specify the independence carefully: freeze a model before the test occultation, or rebuild it without that event, then evaluate the predicted silhouette, size or orientation. Comparisons between shapes and occultations already exist, including recent work. [Astronomy & Astrophysics (A&A)](https://doi.org/10.1051/0004-6361/202554476?utm_source=chatgpt.com)

**Pilot:** About 20 objects with suitable model provenance and later occultations.

**Appeal:** Clear predictions and a physically concrete validation problem.

**Limitation:** A current shape model may already incorporate the observation intended for testing. Coordinate conventions, timing and model uncertainty also require care.

## 13. Are young-star variability classes persistent properties or temporary states?

**Question:** Do young stars remain “dippers”, “bursters” or relatively quiet objects, or move between these behaviours as accretion and circumstellar obscuration change?

Public resources include **YSOVAR** and the completed **NEOWISE** mission data. Existing work has already compared variability across short and long observing baselines, so the role of observation timescale is part of the current literature. [irsa.ipac.caltech.edu](https://irsa.ipac.caltech.edu/data/SPITZER/YSOVAR/index.html?utm_source=chatgpt.com)

A possible contribution would estimate transition frequencies or state durations after standardising observation windows, then relate these to independent indicators of disc or stellar properties.

**Pilot:** One well-observed young cluster.

**Appeal:** Developmental states, heterogeneity and transition modelling.

**Limitation:** Accretion, dust extinction and starspots can produce overlapping observational patterns. Unequal sampling can manufacture apparent class changes.

## 14. Why do similar galaxies have different satellite populations?

**Question:** After accounting for observational incompleteness and host properties, how much variation remains among hosts in satellite abundance and star-formation suppression?

The **SAGA Survey** provides public data for 101 hosts and 378 confirmed satellites, alongside additional candidate information. Its existing papers already address abundance, quenching and theoretical comparisons. [SAGA Survey](https://sagasurvey.org/data/?utm_source=chatgpt.com)

The proposed contribution would test a specific explanation for variation among hosts: for example, whether a common model can reproduce the observed diversity, or whether additional host-level variation is required.

**Pilot:** Reproduce a published host-level result and assess alternative models through predictive simulation.

**Appeal:** Nested populations and environmental effects are a strong match to your background.

**Limitation:** The effective independent sample is much closer to the number of hosts than the number of individual satellites. Projected separation also provides incomplete information about a satellite’s history.

## 15. Do X-ray binaries alternate between active and dormant eras?

**Question:** Does a system’s outburst rate change through time, or can the observations be explained by persistent differences in rates among systems?

A recent catalogue of transient neutron-star low-mass X-ray binaries contains 87 systems; many had zero or one observed outburst during the analysed multidecade interval. Public monitoring products, including Swift BAT light curves, provide a basis for examining their histories. [arxiv.org](https://arxiv.org/abs/2407.18867?utm_source=chatgpt.com)

A contribution could distinguish within-system changes from between-system heterogeneity and determine what this implies for long-term accretion behaviour.

**Pilot:** Ten to twenty systems, with simulated outbursts passed through the real monitoring history.

**Appeal:** A rich recurrent-event problem.

**Limitation:** Sensitivity depends on the spectrum and observing instrument, and inclusion in a transient catalogue depends partly on having been detected in outburst. This overlaps methodologically with dwarf novae; I would choose between them according to physical interest.

## 16. When do active asteroids switch on, and how long do they remain active?

**Question:** How do the onset, duration and recurrence of dust release depend on orbital position and object properties?

The **DECam Asteroid Database** provides detections and links to archival exposures. Those are raw material for assessing activity, rather than an already classified census of active and inactive objects. Archival searches are an active research area, including recent published work. [DAD (DECam Asteroid Database)](https://datalab.noirlab.edu/data/decam-asteroid-database?utm_source=chatgpt.com)

A useful project could focus on known recurrent objects and infer when activity becomes detectable across successive orbital passages. Those histories can constrain explanations involving sublimation, impacts or rotational effects.

**Pilot:** Approximately ten objects, beginning with image-level injection tests for detectable coma or tail structure.

**Appeal:** Direct use of images to investigate physical processes.

**Limitation:** Seeing, trailing and viewing geometry affect apparent extension. Nondetections need quantitative sensitivity estimates.

## 17. How common are transient dusty episodes around mature stars?

**Question:** How frequently do independently selected mature stars develop detectable warm-dust excesses, and what are the durations of those episodes?

NEOWISE’s completed observations provide repeated infrared measurements. Recent work on extreme debris discs also supplies a strong physical context, including evidence connected to planetary collisions. [irsa.ipac.caltech.edu](https://irsa.ipac.caltech.edu/data/WISE/docs/release/NEOWISE/index.html?utm_source=chatgpt.com)

The proposed contribution would be a population estimate using a sample defined independently of known dusty events, with a careful model of detection and episode duration.

**Pilot:** A few hundred isolated nearby stars plus known examples and controls.

**Appeal:** Rare-event statistics linked to the evolution of planetary systems.

**Limitation:** Proper motion, background sources, saturation and photospheric modelling can create false excesses. Connecting a particular infrared event to a giant impact requires additional evidence.

## 18. How frequently do active galactic nuclei undergo major state changes?

**Question:** What are the transition and recurrence times of “changing-look” active galactic nuclei, once the way they are selected for follow-up is included?

Public ZTF and infrared time series offer extensive observations, and recent papers continue to identify and characterise transitions. The literature is fast-moving. [ZTF](https://irsa.ipac.caltech.edu/Missions/ztf.html?utm_source=chatgpt.com)

A possible contribution would jointly model the underlying changes and the probability that a source receives the observations needed to confirm them.

**Pilot:** A small, thoroughly documented sample with repeat spectra and matched comparison objects.

**Appeal:** Dramatic changes in accretion onto massive black holes.

**Limitation:** Photometric changes alone do not establish the relevant spectroscopic transition. Host-galaxy contamination, stochastic variability and selective follow-up complicate population estimates.

## 19. Do stellar flares trigger subsequent flares?

**Question:** Is temporal clustering evidence of a physical triggering process, or can it arise from a changing background level of magnetic activity?

TESS provides a natural dataset, but this is an example where the recent literature changes the recommendation. A 2026 analysis already investigates flare clustering and explicitly examines nonstationarity. Assuming that previous authors used only a constant-rate Poisson model would give a misleading impression of novelty. [arxiv.org](https://arxiv.org/abs/2602.20311?utm_source=chatgpt.com)

A defensible extension might compare richer latent-activity models with triggering models, using realistic event overlap and detection to establish when they can be distinguished.

**Pilot:** Reproduce the recent analysis on a subset before adding model complexity.

**Appeal:** Good fit for point-process modelling and simulation.

**Limitation:** Flare segmentation can manufacture short intervals, while flexible background-rate models can mimic triggering. Interesting, but it needs a precise opening.

## 20. Can apparently one-off fast radio bursts be rare repeaters?

**Question:** What can finite observing exposure tell us about a mixture of genuinely nonrepeating sources and sources that repeat rarely or spend long periods dormant?

CHIME’s second catalogue provides thousands of bursts and associated public resources. However, an October 2026 preprint already tackles closely related questions using simulation-based inference. [arxiv.org](https://arxiv.org/abs/2601.09399?utm_source=chatgpt.com)

The possible extension would focus on which conclusions remain identifiable across plausible rate distributions, dormant phases and observing histories.

**Pilot:** First establish whether the available exposure metadata support the proposed time-dependent models; then reproduce an existing population result.

**Appeal:** A fundamental population-inference question about an exciting phenomenon.

**Limitation:** Limited exposure creates profound ambiguity between nonrepetition and very slow repetition. The field is competitive, and specialist collaboration would be especially valuable.

# What makes one of these a good *first paper*?

I would look for four properties together.

**First, a physical question with a bounded answer.** For example: does outburst memory persist after modelling changing observational effort? Do weak meteor streams predict later observations? Does a cluster-environment relationship survive a more complete observation model? Each has a result that could sharpen what is known about a system.

**Second, a public data product that is already close to the scientific question.** Processed light curves, orbit catalogues, merger trees and published selection functions can make an ambitious question manageable. The first project should have a realistic route from archive to interpretable evidence.

**Third, an existing result you can reproduce.** Reproduction gives you a working benchmark, exposes conventions that papers sometimes leave implicit, and helps identify where an extension would matter. It also gives agents concrete outputs to work towards.

**Fourth, a result that remains useful across several outcomes.** A carefully scoped comparison can be valuable if it detects an effect, constrains its magnitude, or establishes that an influential inference is highly sensitive to an assumption. That usefulness depends on choosing a question the astronomical community already has reason to care about.

One encouraging detail from this search is that there are different kinds of opening:

| Kind of opening | Strong example here |
|---|---|
| Explicitly documented unfinished analysis | Jupiter feature measurements |
| Newly available treatment of detection | Gaia cluster selection function |
| Long records suitable for a new physical comparison | Dwarf novae and Miras |
| A well-characterised survey that enables forward inference | OSSOS |
| Independent observations that can test predictions | Transit forecasts and asteroid occultations |
| Existing simulation histories that can be queried differently | IllustrisTNG |

# How I would use Codex and Claude agents

Agents are particularly useful here because much of the initial burden consists of learning archive conventions, assembling reproducible data pipelines, reproducing analyses and building simulations.

I would divide the work into independently checkable tasks:

1. **Archive and provenance:** Retrieve a small sample, document units, flags, filters, time standards and selection rules, and produce diagnostic plots.
2. **Reproduction:** Implement the nearest published analysis and compare its outputs with the paper.
3. **Simulation:** Generate data under competing physical or statistical explanations and pass them through the actual observation process.
4. **Independent checking:** Reimplement a key calculation or inspect whether the proposed model can recover known simulated parameters.

You would retain responsibility for the scientific question, the assumptions that connect measurements to physical processes, and the interpretation. A second agent agreeing with the first is weak evidence; an independently specified calculation, a recovered simulation parameter or a successful prediction is much stronger.

I would also bring in a domain astronomer once there is a compact, concrete pilot: one question, a few diagnostic figures, the closest papers and a clear description of the proposed extension. At that stage, their knowledge can rapidly resolve whether an apparent effect is a familiar instrumental issue, an established physical distinction or something worth pursuing. A substantive contribution to framing or interpretation could naturally lead to collaboration.

The physics learning can remain focused. For a light-curve project, you would first need fluency in magnitudes and fluxes, passbands, time conventions and the particular source class. For OSSOS, the initial investment would be orbital distributions and survey geometry. For Gaia clusters, it would be stellar ages, mass estimates and cluster dissolution. Each is a manageable domain to learn in the course of doing a specific analysis.

## What I would choose in your position

**For the first completed project, I would choose dwarf novae, with meteor streams a close alternative.** Both support a small initial sample, substantial statistical modelling and a credible route to an interpretable result.

**For the project most likely to hold your attention over several years, I would choose Gaia cluster populations.** The relationship between formation, survival, environment and the reconstruction of history is exceptionally close to your existing scientific interests.

**For the project most likely to remain enjoyable as a hobby, I would choose Jupiter’s storms.** It combines visual engagement with a concrete scientific question and a community already producing observations of lasting value.

My first practical move would be to run **two small feasibility studies: dwarf novae and Gaia clusters**. For each, obtain a small sample, reproduce one published result, and test recovery of known effects in simulated observations. That would tell you which subject has both a tractable scientific opening and the kind of intellectual pull that makes you want to return to it in your own time.

# Barry
These are frankly twenty wonderful ideas, all of which sound very interesting to me, and I agree that dwarf Novae one would be an excellent candidate as a selection. So, thinking about how I would take this forward, I'll soon create a repository and connect a Claude and Codex agent to it and start the work. But I thought perhaps you could help develop the initial framework and structure of the repository and dig a little deeper into the context, perhaps sharpen the question or maybe there is a central question and some ancillary questions or hypotheses that come out of it. Think more about the underlying modelling. Do a initial literature review. I'll get my agents to revisit this. But essentially it's to seed a repository with the right sort of background and framework with enough detail that once I do plug the agents in, they're not starting just with an idea, but they're actually starting with a sufficient body of preliminary research that they're primed to take the project forward. And you seem well positioned to provide that initial package, ideally in a, in the form of a Git repository as a zip file that I could then unpack, point the agents towards and then push it to remote and get it started that way. How does that sound? If good, then proceed!

# GPT-6 Pro
**I’ve built the repository seed, Barry.**

It contains an **initialized Git repository**, including its `.git` directory, a `main` branch, an initial commit and the tag `seed-v0.1.0`. You can unpack it, point Claude and Codex at it, and add your remote.

The package includes twelve research and implementation notes, a **30-reference bibliography with an evidence register**, a provisional target catalogue, shared agent instructions, separate kickoff prompts, a manuscript outline, and a small runnable Python prototype.

**No real astronomical light curves have been imported.** The executable examples are explicitly synthetic; their purpose is to make the proposed reasoning testable and give the agents a checked starting point. The archive-access notes distinguish documented availability from access and data quality that still need to be established.

## 1. The literature changes the emphasis

The most consequential finding is that **“do dwarf novae have memory?” already has a substantial history**. Hempelmann and Kurths explicitly discussed memory in the SS Cyg outburst sequence in 1990. Ak, Özkan and Mattei subsequently examined long-term light-curve parameters across 36 dwarf novae, including relationships with adjacent quiescent intervals and the danger of correlations created by shared components of the variables. [researchgate.net](https://www.researchgate.net/publication/234184992_Dynamics_of_the_outburst_series_of_SS_Cygni?utm_source=chatgpt.com)

That makes the original idea a useful direction, but it needs a more precise contribution than finding serial correlation or a relationship between outburst duration and recurrence.

I have therefore framed the project around this question:

> **Among well-observed ordinary dwarf novae, does information from a completed outburst improve calibrated forecasts of the next outburst beyond star-specific recurrence patterns and changing activity, once incomplete observation is accounted for?**

This gives the project a bounded empirical objective. It also preserves the physical interest: if information from an outburst improves prediction, we can ask what that reveals about the state of the system and which explanations remain compatible with it.

The distinction matters because changing activity is itself established territory. For example, Šimon’s RU Peg study examined changes in outburst morphology and recurrence, including alternative interpretations involving missed events. It is a close precedent worth reproducing before extending. [arxiv.org](https://arxiv.org/html/2112.03620v1?utm_source=chatgpt.com)

**My assessment is that the sharpened project remains promising, but its precise novelty is provisional.** The repository makes a focused citation audit an early task. It does not claim that no one has previously performed an observation-aware forecasting comparison.

### What the review provides

The review covers historical recurrence studies, the disc-instability framework, population catalogues, supercycles, changing states, observation effects and recent work through **5 November 2026**. It separates several kinds of evidence:

- Relevant full-text sections that were inspected.
- Abstracts and bibliographic records that support narrower claims.
- Important historical papers whose full methods still need to be obtained.
- Recent papers whose forecasting implications cannot be assessed from the accessible material.

Each bibliography entry has a corresponding evidence record stating what was inspected, what it supports and what remains unresolved. That should make it much easier for your agents to revisit the review without inheriting unwarranted confidence.

One useful correction is also preserved: the **Coppejans et al. catalogue of 722 dwarf novae** and the **Otulakowska-Hypka, Olech and Patterson compilation** are different resources. Their system-level summaries are useful context, but they do not supply the complete event-by-event chronology needed for this study. [academic.oup.com](https://academic.oup.com/mnras/article/456/4/4441/1033235?utm_source=chatgpt.com)

## 2. The central question and ancillary hypotheses

I have kept **incremental predictive information** as the primary question, with several related questions that can be investigated without turning the first paper into an unrestricted search.

| Question | Proposed test | Interpretation of a positive result |
|---|---|---|
| Does the completed outburst help? | Add its duration to a recurrence model and evaluate later forecasts | Duration contains information useful for prediction |
| Does activity change through time? | Compare stationary recurrence with models that adapt to past timing | Following the system’s changing activity improves prediction |
| Does duration add information beyond that adaptation? | Compare the same changing-activity model with and without the completed mark | Duration adds information beyond the specified timing-history baseline |
| How much do observations affect the apparent relationship? | Inject events and errors through realistic observing schedules | Identifies which findings survive missed events, boundary errors and sampling changes |
| Does predictive value vary among systems or epochs? | Estimate and report within-system effects and between-system variation | Establishes the extent and limits of generalisation |
| Can a physical mechanism be distinguished? | Later comparison of identifiable joint models of marks and latent state | At most model-dependent evidence for a particular explanation |

The last question is deliberately an extension. A completed outburst may predict the next event because it is a good indicator of an unobserved accretion state. That would be useful predictive information, even if the earlier outburst does not directly determine the later one.

For the first paper, **duration is the primary outburst characteristic**. A homogeneous-passband optical fluence measure is a possible secondary characteristic, provided its coverage and uncertainty can be handled defensibly. It should remain an optical proxy; converting it into bolometric energy or accreted mass requires additional assumptions. Multicolour modelling of dwarf-nova outbursts illustrates why the observed brightness is a combination of physical contributions. [Astronomy & Astrophysics (A&A)](https://doi.org/10.1051/0004-6361/202037631?utm_source=chatgpt.com)

## 3. The proposed modelling structure

The protocol uses four models with a clear relationship to one another.

| Model | Information used | Purpose |
|---|---|---|
| **M0: renewal baseline** | Each star’s waiting-time distribution | Establish ordinary recurrence predictability |
| **M1: completed-outburst model** | M0 plus the completed outburst’s duration | Test information relative to stationary recurrence |
| **M2: changing-activity model** | Timing history and an adapting activity state | Provide a credible nonstationary alternative |
| **M3: combined model** | The same activity structure as M2, plus completed duration | Test the main incremental-information question |

**M3 versus M2 is the central comparison.** M1 versus M0 is useful, but it leaves open the possibility that duration is simply tracking changes in activity that a stronger baseline could already capture.

The initial mathematical formulation is a lognormal waiting-time model. For star \(j\) and outburst \(i\), a combined version is:

\[
\log Q_{ij}
=
\alpha_j
+
\beta_j
\left(
\log D_{ij}
-
\overline{\log D}_{j,\mathrm{train}}
\right)
+
z_j(\tau_{ij})
+
\epsilon_{ij}.
\]

Here:

- \(Q_{ij}\) is the following quiescent waiting time.
- \(D_{ij}\) is completed-outburst duration.
- \(\alpha_j\) describes the star’s baseline.
- \(\beta_j\) describes the duration association.
- \(z_j(\tau_{ij})\) represents changing activity inferred from information available at forecast time.
- The centring constant comes from training data.

This provides a tractable starting point and an interpretable effect size. For example, doubling duration multiplies the model’s conditional median waiting time by \(2^{\beta_j}\).

The protocol proposes alternative waiting-time distributions as a sensitivity check. A renewal baseline can have an increasing or decreasing hazard as time passes; independent successive waits do not require an exponential distribution or constant event probability.

For changing activity, I recommend starting with an auditable past-only comparator—such as a discounted recurrence estimate or an autoregression in earlier gaps—before attempting a richer latent-state model. The documentation includes a possible continuous-time state formulation, along with its assumptions and identifiability limits.

### Two definitional traps deserve particular attention

Let an outburst begin at \(s_i\) and end at \(e_i\). Then:

\[
D_i=e_i-s_i,\qquad
Q_i=s_{i+1}-e_i,\qquad
C_i=s_{i+1}-s_i=D_i+Q_i.
\]

The full onset-to-onset cycle \(C_i\) **contains the previous duration**. A duration–cycle correlation can therefore arise partly from arithmetic. The literature already recognises this issue; it is one reason the proposed primary response is the following quiescent interval. [nek.istanbul.edu.tr](https://nek.istanbul.edu.tr/ekos/MAKALE/M7229.pdf?utm_source=chatgpt.com)

Using the quiescent interval resolves that shared-component problem, but leaves a measurement problem. If the estimated end is late by \(\delta\), then:

\[
\widehat D=D+\delta,\qquad
\widehat Q=Q-\delta.
\]

The same boundary error lengthens one variable and shortens the other. Independent end-time error alone can introduce negative covariance. The protocol therefore requires **joint treatment of event-boundary uncertainty**, rather than separate error bars that discard the shared uncertainty.

These are precisely the kinds of details that could otherwise produce an attractive but misleading finding.

### A forecast needs an observable issue time

The true end of an outburst is generally identifiable only after further observations. A historical forecast must therefore be issued when completion could actually have been confirmed.

If \(a\) days of verified quiescence have already elapsed at that point, the relevant event probability over the next \(h\) days is:

\[
P(\text{event within }h\mid Q>a)
=
1-\frac{S(a+h)}{S(a)}.
\]

The protocol addresses uncertain endpoints and the distinction between genuinely verified survival and an interval in which an entire outburst might have been missed.

It also distinguishes an **observation-time hindcast** from a faithful reconstruction of operational forecasting. If we know when observations were taken but not when they were uploaded or revised, we should describe the retrospective test accordingly.

## 4. A deliberately modest first sample

The initial feasibility queue contains six candidates:

| Candidate | Proposed role |
|---|---|
| **SS Cyg** | Reference system for extraction and historical comparisons |
| **U Gem** | A second benchmark for testing whether the procedure generalises |
| **SS Aur** | Another ordinary-system candidate for variation among targets |
| **RU Peg** | A useful test of sensitivity to changing outburst morphology |
| **BV Cen** | A southern candidate that broadens observing geography |
| **UU Aql** | An additional candidate for a modest multi-system pilot |

Their nomination is supported by historical monitoring resources and object-specific literature. The AAVSO Legacy CV programme identifies long-monitored candidates, while the Sion et al. study supplies relevant U Gem-type context for UU Aql, BV Cen and CH UMa. Those sources support candidacy; they do not establish present-day suitability for this analysis. [aavso](https://archive.aavso.org/index.php/aavso-legacy-cv-program?utm_source=chatgpt.com)

The registry also contains:

- **Three ordinary-system reserves:** CH UMa, AR And and DX And.
- **Five separate challenge cases:** Z Cam, RX And, VW Hyi, SU UMa and WZ Sge.

The challenge cases are kept separate because standstills, supercycles and rare superoutbursts change the event-definition and waiting-time problem. They may become useful extensions or tests of where the first model fails.

Every row explicitly records that **current identity checks and data eligibility remain pending**. I have not filled the catalogue with guessed coordinates, observing counts or assertions of adequate coverage.

An eventual expansion to roughly 12–20 ordinary systems is a conditional planning scale. It should follow demonstrated feasibility and simulation results.

### An important selection rule

The protocol does **not** require a star to have a specified number of completed cycles in the final evaluation period. That would preferentially select shorter waits and use future outcomes to decide inclusion.

Instead, select targets using development-period information, issue forecasts under the frozen eligibility rule, and retain those forecasts even when the next event is not observed before coverage ends. Appropriate censoring then becomes part of the analysis.

## 5. Data acquisition is the first substantive task

The source plan gives each archive a specific role.

| Source | Proposed use |
|---|---|
| **AAVSO** | Primary long-baseline observations for the initial familiar systems |
| **ASAS-SN** | Complementary survey observations and a comparison of sampling regimes |
| **CRTS / DNCVOBCAT** | Historical context, target reconnaissance and possible additional photometry |
| **ZTF** | Optional survey validation and more recent observations |
| **TESS / Kepler** | Optional dense checks of morphology and event boundaries |

AAVSO’s current documentation provides search and download routes for its photometry. A practical change is that the legacy Data Download Tool has been retired; the package directs the agents to the current applications and flags the July 2026 usage guidance. [AAVSO](https://aavso.org/blog/new-aavso-website-coming/?utm_source=chatgpt.com)

ASAS-SN has an official Python client, but the inspected repository and rendered documentation contain differing query examples. The acquisition instructions require the agents to pin and inspect the version they actually use, then record a working call and its returned schema. [GitHub](https://github.com/asas-sn/skypatrol?utm_source=chatgpt.com)

The data contract makes the consequential distinctions explicit:

- Original timestamps, time scales and heliocentric/barycentric conventions remain identifiable.
- Visual estimates, V, g, r and unfiltered measurements remain distinguishable.
- Faint limits are represented separately from exact measurements.
- Missing rows are not automatically treated as observations of quiescence.
- Duplicate provenance is checked across archives.
- Observing effort that increases after an alert is treated as a potential source of selection.

For ZTF specifically, the documentation distinguishes catalogue light curves from forced photometry and explains the latter’s difference-image/reference-flux semantics. That is a reason to inspect the product carefully before treating it as a complete brightness history. [irsa.ipac.caltech.edu](https://irsa.ipac.caltech.edu/docs/program_interface/ztf_lightcurve_api.html?utm_source=chatgpt.com)

The first acquisition deliverable is therefore a small, auditable package: authentic raw bytes, a checksum and query record, verified metadata, a development-period plot, coverage diagnostics and manually reviewed event boundaries.

## 6. The simulation programme is designed to challenge the interpretation

The planned scientific simulations go beyond generating data from the model being fitted. They include:

- Independent renewal cycles with non-exponential waits.
- Differences among stars that could create a pooled association.
- A shared slowly changing state affecting both duration and recurrence.
- A direct duration association.
- Both a shared state and a duration association.
- Abrupt changes of regime.
- Changing mixtures of event types.
- Shared endpoint errors.
- Seasonal gaps, limiting depth, duplicate observations and triggered follow-up.

The eventual pipeline should generate events and brightness, apply an observation process, give only the resulting observations to the inference procedure, and reveal the simulation truth after predictions are stored.

That sequence allows separate answers to four questions:

1. Is the calculation implemented correctly?
2. Can the estimator recover parameters under its assumptions?
3. Can the study distinguish competing explanations under realistic departures?
4. Does it predict later astronomical observations usefully?

The repository also proposes expressing power in a physically interpretable way—for example, whether a **20% change in median waiting time when duration doubles** would be distinguishable. That is a provisional design example, to be revised with the pilot and domain input.

### What the supplied prototype already does

The runnable prototype generates four synthetic scenarios: independent cycles, a duration effect, a shared state, and both mechanisms. It fits M0 and M1 using earlier complete cycles and evaluates later cycles.

It separately generates noisy toy photometry with seasonal gaps and limiting observations.

**The forecast fitting uses known simulation truth.** It does not infer the events from that sampled photometry. In simulation terminology, it is an *oracle* demonstration.

This makes a useful conceptual result visible: duration can improve forecasts in the shared-state scenario even though the generator has no direct duration effect. That is a demonstration of why useful prediction does not uniquely identify the mechanism.

The following remain explicitly unimplemented research tasks: real-data adapters, event extraction, fitted censoring and missing-event models, joint boundary integration, M2/M3 inference, hierarchical pooling and uncertainty in estimated parameters.

## 7. What is inside the repository

| Area | Contents |
|---|---|
| **Entry points** | README, shared `AGENTS.md`, and a `CLAUDE.md` pointer |
| **Research notes** | Brief, literature review, data plan, target plan, statistical design, simulation plan, decision gates, roadmap, data dictionary, domain primer, workflow and validation record |
| **References** | BibTeX bibliography, matching evidence register and search log |
| **Configuration** | Provisional study plan and 14-row candidate registry |
| **Code** | Synthetic event and observation generation, M0/M1 forecasts, probability helpers and CSV validation |
| **Tests** | Scientific and data-integrity checks |
| **Example outputs** | Labelled synthetic tables, metrics, checksums and a diagnostic figure |
| **Agent handoff** | Claude and Codex kickoff prompts, an independent-review prompt and a session-handoff template |
| **Coordination** | Task board and decision log |
| **Manuscript** | A result-neutral outline with proposed figures and tables |

The core demonstration and tests use the Python standard library. Matplotlib is optional for recreating the figure.

### Verification completed

I tested an extracted copy of the actual ZIP:

- **All 17 unit and integration tests passed.**
- The regenerated example matched **all 16 recorded CSV checksums** and the stored scenario summaries.
- Structural checks passed for local links, citation/evidence matching, configuration files and candidate identifiers.
- The Git repository was clean, and its object-integrity check passed.

The tests cover consequential risks such as unavailable training outcomes, future-data leakage, training-only scaling, probability calculations, faint limits and duplicate source identities. They verify the scaffold within its stated scope.

## 8. How I would start Claude and Codex

After unpacking, the immediate local checks are:

```bash
cd dwarf-nova-memory

python -m unittest discover -s tests -v
python scripts/validate_seed.py
python scripts/run_demo.py --output outputs/first_local_run
```

Use `python3` if that is the executable on your system. The demo requires a new, empty output directory.

To attach the repository to your remote:

```bash
git remote add origin YOUR_REMOTE_URL
git push -u origin main
git push origin seed-v0.1.0
```

For the first parallel assignment, I suggest:

**Claude:** audit the physical framing and nearest precedents, then produce a short novelty/feasibility memo and challenge the proposed event definitions.

**Codex:** audit the runnable scaffold, obtain one authentic light curve through a documented route, and produce a provenance and observation-quality report.

Then swap implementation and review responsibilities at the next milestone. The prompts are already written, and both agents are directed to the same scientific instructions and decision record.

The first meaningful checkpoint is an **audited feasibility pack**: one or two authentic acquisitions, defensible event boundaries, a historical reproduction, and a decision about the smallest viable predictive comparison. From there, the project can expand with evidence.

I think that gives you a sound starting position: a specific scientific question, a substantial account of what is already known, explicit competing explanations, and enough executable structure for the agents to begin productive work immediately.
