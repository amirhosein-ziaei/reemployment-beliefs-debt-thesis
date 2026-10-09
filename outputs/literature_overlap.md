# G-P2 literature overlap (Phase 1)

**Question under review.** Among employed respondents, does perceived difficulty finding another
job (low `Q22new`) predict subjective debt-payment distress (`Q30new`) beyond perceived job-loss
risk (`Q13new`) and general pessimism?

## How this review was done, and its limits

* The full texts of Mitra (June 2026) and Hartmann & Leth-Petersen (2024) could **not** be opened
  in this session: the session's network policy blocked `anushkamitra.com`, `econstor.eu`,
  `econ.ku.dk` and `doi.org` (HTTP 403 at the egress proxy). The adjudication report says both
  full texts were inspected for that report.
* What is stated below therefore comes from (a) the October 2026 adjudication report (marked
  **[ADJ]**), (b) abstract/summary text returned by web search in this session (marked **[ABS]**),
  or (c) background knowledge of well-known published papers, not re-checked this session (marked
  **[BK]**). Nothing here is presented as a reading of full text that did not happen.
* **Phase 2 must re-read both full texts** (the June 2026 Mitra PDF and the published Labour
  Economics version) and check every row below. Use Mitra's appendix to see exactly which SCE
  items appear, including any debt or finance variables.

## 1. Mitra (June 2026), "Macroeconomic Sentiments and Job Search Behavior", FRB working paper

Source: <https://anushkamitra.com/research/macroeconomic-sentiments-job-search/macroeconomic-sentiments-job-search.pdf>

| What it establishes | Basis |
| - | - |
| Uses SCE employed-worker beliefs about **separation (job loss) and job finding**, including their **interaction**, linked to on-the-job search and later separations | [ADJ] |
| Employed workers who expect the labour market to worsen perceive higher own job-loss risk and **search more while employed** | [ABS] |
| The pessimism–search link is attributed to **fear of job loss rather than job-finding expectations** | [ABS] |
| Interprets this as precautionary on-the-job search, with a calibrated search-and-matching model separating precautionary from job-ladder search | [ABS] |
| Within-local-market associations; explicitly limits causal interpretation; includes a comparison with ECB data | [ADJ] |
| Outcome is search behaviour, not debt service; no debt-payment expectation outcome is reported | [ADJ]; to re-check in appendix |

**Implication for G-P2.** The loss/finding distinction, its interaction, and the use of SCE
employed-worker beliefs as labour-risk measures are **already established**. G-P2 cannot claim the
mechanism, the distinction, or the data as new. What remains is a **different outcome**:
subjective debt-service distress. One useful contrast is worth noting carefully. If Mitra finds
finding beliefs do little for *search* while G-P2 finds they matter for *debt-payment
expectations*, that is a difference in which belief matters for which margin. It does not show a
new mechanism, and it needs the same horizon caveats.

## 2. Hartmann & Leth-Petersen (2024), "Subjective unemployment expectations and (self-)insurance", *Labour Economics* 90, 102579

Sources: <https://doi.org/10.1016/j.labeco.2024.102579>;
working-paper version <https://www.econstor.eu/bitstream/10419/298445/1/1828134864.pdf>

| What it establishes | Basis |
| - | - |
| Danish panel survey of unemployment expectations **linked to administrative records** on income, savings and unemployment-insurance membership | [ABS], [ADJ] |
| Subjective expectations carry predictive information for later unemployment, yet respondents **overestimate** their own risk | [ABS] |
| Higher expected risk goes with **UI take-up and more liquid savings** (self-insurance) | [ABS] |
| Already connects perceived labour risk to **household financial preparation**, and validates against realised outcomes | [ADJ] |

**Implication for G-P2.** The step from labour-risk beliefs to household finance is already taken,
and with a stronger design: administrative outcome validation, which the SCE public core file
cannot provide. G-P2's remaining room is narrow:
(i) **conditional job-finding** beliefs, not only unemployment-incidence beliefs;
(ii) a **debt-service distress** outcome rather than insurance or saving;
(iii) a U.S. monthly panel.
G-P2 has **no realised financial outcome**. It cannot claim to validate beliefs against behaviour.

## 3. Other close work (to be screened properly in Phase 2)

| Paper | Overlap | Basis |
| - | - | - |
| Mueller, Spinnewijn & Topa (2021, AER), job seekers' beliefs | Job-finding beliefs predict finding but are optimistically biased and update slowly. G-P2 must not turn a 3-month conditional finding probability into an expected duration | [ADJ], [BK] |
| Kuchler & Zafar (2019, JF), personal experience and expectations | Personal experience shifts aggregate pessimism. This warns that a common sentiment factor can look like a financial mechanism | [ADJ], [BK] |
| Balleer, Duernecker, Forstner & Goensch (2026, JME) | Biased labour expectations and labour outcomes. A recent benchmark for linking beliefs to consequential outcomes | [ADJ] |
| Stephens (2004, REStat); Hendren (2017, AER) | Subjective job-loss expectations predict job loss and consumption responses. The labour-risk → household-finance link is old | [BK] (not re-checked this session) |
| NY Fed SCE releases and Liberty Street posts on delinquency expectations | Breakdowns of `Q30new` by income, age and education, reported regularly by the SCE team. Descriptive gradients in `Q30new` are not new | search results this session |

A targeted search in this session found **no paper whose main outcome is SCE `Q30new` modelled on
`Q22new` given `Q13new`**. That is a search result, not proof of absence. Searches covered general
web and abstract text only, not SSRN/NBER full-text indexes.

## 4. What narrow contribution remains for G-P2

Stated conservatively:

> Using the SCE monthly panel, measure how much **conditional reemployment difficulty** adds to
> employed respondents' **subjective probability of missing a minimum debt payment** once
> job-loss beliefs, persistent person-level pessimism and a small set of general-sentiment
> controls are held fixed. Report this as a precisely bounded association, plus an incremental
> prediction of next-month payment expectations. Make no causal claim and no claim about
> realised delinquency.

The contribution is **measurement and incremental-information**, not a mechanism. A precise small
increment, or a precise null, is still a usable master's result (see `phase1_feasibility.md`).

## 5. Claims G-P2 must not make

* That income-interruption risk is a new channel for household financial distress.
* That separating job-loss from job-finding expectations is new (Mitra already does this, with the
  interaction).
* That `Q13new × (1 − Q22new)` is the probability of an income interruption. Horizons are 12 months
  vs 3 months conditional on loss "this month", and the debt item is 3 months unconditional.
* That results predict actual delinquency, default or credit outcomes.
