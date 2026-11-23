# Cross-Functional (XFN) Interview Prep

> **Format:** 45 minutes, story-driven. The opening is usually *"Walk me through a project or initiative you led that required collaboration across multiple functions. How did you ensure the effectiveness of the overall project team? How did you keep everyone informed and aligned?"*
> **What they score:** whether you can work across the company, handle different approaches and agendas, build positive partnerships, manage difficult ones, and show **self-awareness**: what went well, what you got wrong, and what you changed afterward.
>
> **Evidence rule:** everything here comes from your story bank, Connect notes and the May 2025 PostgreSQL thread. **[confirm]** marks a gap. Don't fill it in the room with something that didn't happen.

---

## 0. How to Use the 45 Minutes

| Time | What happens | Your move |
|---|---|---|
| 0–2 min | Intro | One line: "I'm the infrastructure engineer whose projects only succeed if 15 other teams, plus legal, security and leadership, move with me." |
| 2–15 min | **Primary story** (§2: PostgreSQL upgrade) | Spend 2–3 minutes on the overview, then let them dig in. Have both "went well" and "could have gone better" ready. |
| 15–35 min | Follow-ups and second stories | A different function (§3: Legal), a difficult partnership (§4), a conflict you couldn't resolve (§5), a relationship you hurt (§6) |
| 35–40 min | Self-awareness probes | §8: the honest list |
| 40–45 min | Your questions | §11 |

**Rules for every answer**
- Name the **function** and its **agenda**, not just "another team". The point is that different functions want different things.
- Say what **you** did: you wrote it, you ran the review, you made the call.
- Include **one thing that went badly** in every story, without being asked. That's the self-awareness signal they want.
- Use **roles, not names**, for colleagues.

---

## 1. My Cross-Functional Operating Model

Have these ready to name, because every story below shows one or more of them:

| # | Principle | Where it shows up |
|---|---|---|
| 1 | **Align leaders first, then make adoption easy.** Get each team's lead on board, then give engineers docs, office hours and clear steps. | Secret Scanner, Maestro, alt_pool, PostgreSQL |
| 2 | **Write the options down and invite people to break them.** A written trade-off beats a meeting full of opinions. | PostgreSQL no-outage test (§2.5), Search compute (§4) |
| 3 | **Treat another function's constraints as design inputs, not approval gates.** | Legal on the Elasticsearch fork (§3), Trust and Security on IRIS |
| 4 | **Decision-driven communication for leaders, detail-driven for engineers.** | PostgreSQL VP feedback (§2.6) |
| 5 | **Agree the decision rules before the high-pressure moment.** | Core-SLA rollback rule; ranking criteria for priorities |
| 6 | **Separate ownership layers with evidence, then help the other team fix their layer.** | Telemetry loss, VENT lag (§7) |
| 7 | **Make agreements durable:** recurring syncs, written decisions, named reviewers. | Search compute sync (§4), PostgreSQL reviewer list |

---

## 2. Primary Story: PostgreSQL & Ubuntu Upgrade Across ~40 Clusters

### 2.1 The 2–3 minute version (say it out loud)

"I led the upgrade of Viva Engage's data tier: about 40 production PostgreSQL clusters, from 9.6 to a supported version, plus an Ubuntu upgrade underneath. The trigger was open critical CVEs and unmet Microsoft Trust requirements, and that was blocking Viva Engage from integrating with Microsoft Teams and Microsoft 365 Copilot, which both have strict security requirements.

Technically it was hard, but the harder part was the people. Every one of the 15 Viva Engage service teams, about 150 engineers, ran on these clusters. It also needed leadership up to the executive sponsor, principal engineers who cared about data integrity, product managers for customer messaging, the front-end team for the outage banner, Trust and Security, the Azure compute capacity team for extra compute, and a partner team for the lab environment. Each had a different agenda. Leadership wanted confidence and minimal customer impact. Service teams wanted to know exactly what to test and when. Senior leaders wanted zero risk of corruption.

I made it work with three things. First, **one shared definition of done**: each team certified only its core end-user scenarios, with a rollback rule agreed in advance. Second, **written options and open review**: when the executive sponsor asked to test production without a write outage, I wrote up the options, put them in front of the principal engineers, accepted their critique of my own proposal, and closed with a documented decision and named reviewers. Third, **a communication cadence for each audience**: org-wide status posts, a scenario tracker with deadlines owned by an engineer I coached, and decision-driven updates for executives.

We upgraded every cluster without production issues on the PostgreSQL upgrade. The CVEs were cleared, which opened the path to the Teams and Copilot integrations, and once those shipped, **Viva Engage's daily active users grew 30%**. Related incidents also dropped 40%. It didn't all go well. My first plan review with the VP was too technical, service teams were confused about roles early on."

### 2.2 The cast: who was involved and what each wanted

| Function | Their agenda | The tension with my goals |
|---|---|---|
| Engage leadership team and executive sponsor | Confidence, minimal customer impact, a clear go/no-go | Wanted production testing without any write outage (§2.5) |
| Infrastructure team (mine) | A safe, repeatable execution | Capacity: 10–15 engineers, with operations work on top |
| 15 backend service teams | Know exactly what to test and when, and don't break their service | Unit and integration tests had gaps; end-to-end tests were risky; roles were unclear at first |
| Principal engineers (service side) | Data integrity: no split brain, no corrupted IDs | Challenged my first option publicly, and rightly |
| Product managers | Accurate customer messaging | The banner text |
| Front-end team | Their own feature roadmap | No capacity for the banner |
| Trust and Security | CVEs cleared, Trust requirements met | A deadline I didn't control |
| Azure compute capacity team (external partner) | Fair use of scarce capacity across all their customers, plus their own maintenance | I needed extra compute for every window, because we kept the old nodes running as the rollback path while the new ones came up. Later, VM provisioning failed mid-upgrade |
| YES team | The LAB environment | Shared ownership of LAB |

### 2.3 How I made the overall team effective

- **One definition of done.** The 15 teams couldn't say how to sign off, so I narrowed it: each team certified its **core end-user scenarios**, and the rule was fixed in advance. If a core scenario fails, we roll back. Otherwise we fix forward. That removed debate from the high-pressure moment.
- **Clear ownership.** I coached an engineer on my team to own the cross-team testing effort: the scenario spreadsheet, deadlines and tracking. That meant coordination didn't run through me.
- **Work made easy for partners.** Each team got a concrete pre-upgrade checklist:
  1. Review the end-user scenarios, including async writes.
  2. For scenarios expected to fail, mark whether the data is recoverable, for example through Vent retries.
  3. Document mitigations: longer TTLs, more retries, pausing async jobs.
  4. Flag anything the read-only banner didn't cover.
  It had dates on it: scenario sheet by May 14, 2025, staging test on May 16.
- **Unblocking instead of waiting.** The front-end team was busy, so I built the specific outage-banner template myself with AI help. They kept it as a reusable template.
- **Capacity secured ahead of time.** Keeping the old nodes as a rollback path meant running old and new nodes side by side, so each window needed far more compute than normal. I worked with the Azure compute capacity team to get that extra compute ahead of each window and release it once we no longer needed a rollback. **[confirm: how much extra (cores or VMs), how far ahead you asked, how you sized it, and when the old nodes were released.]**
- **Reversible calls under pressure.** When Azure VM provisioning failed on the production Saturday and several tech leads wanted to abort, I proposed a middle path: continue on the minimum nodes during low weekend traffic, and add full capacity once Azure was stable.

### 2.4 How I kept everyone informed and aligned

| Audience | Channel | Cadence | What they got |
|---|---|---|---|
| Whole org | Status and plan posts in the org community (the May 7, 2025 post was seen by 173 people) | At each milestone | Environment status, the production runbook, options under consideration, links to the runbook and tracker |
| Service teams | Shared scenario spreadsheet + runbook | Deadline-driven | What to test, by when, and what mitigations to put in place |
| Principal engineers | RFC review meeting | For key decisions | The options with trade-offs, for them to challenge |
| Executives | Decision-driven updates | At go/no-go points | Status, risk in business terms, the decision needed; technical detail in an appendix |
| Azure compute capacity team | Capacity requests and follow-ups **[confirm: tickets, meetings or a named contact]** | Before each window, and live when provisioning failed | How much compute, for which regions, for how long, and why: old nodes stay up as the rollback path |
| Customers | Maintenance banner with the specific time | Each window | "Read-only until X" |
| Incident calls | Live bridge with senior leaders | During windows | Options and a recommendation, not just status |

**[confirm: any recurring sync, such as a weekly cross-team standup, and what you used for live updates during windows.]**

### 2.5 The hardest partnership moment: the executive's no-outage test request

- **The ask:** before production, the executive sponsor asked to test Microsoft's own tenant (MSIT) on the new PostgreSQL version **without** a write outage for other tenants. Another leader named the real goal: give service teams more time to test than a ~1-hour window allows. That goal was legitimate.
- **What I did:** I wrote up three options in the org post: route only Cell 0 to new-version nodes, a dry run under a full write outage followed by a revert, or dedicated clusters for MSIT. I asked the principal engineers by name whether they had concerns.
- **What went wrong:** my first option didn't hold up. Principal engineers pointed out that the clusters are stamp-wide with one writable primary, so routing Cell 0 to a new-version node means **two primaries: a split brain**. IDs generated in Postgres propagate into other stores such as Cosmos DB, so the corruption would spread. On top of that, cell affinity isn't guaranteed, and Cell 0 also carries other customers' traffic.
- **How I handled it:** I didn't defend the option. I took it to an RFC review with infra and service principal engineers, agreed with the critique, and posted the conclusion: no safe dry run exists without a write outage, so we'd upgrade under a write outage and validate in-window with MSIT as the canary, with a rollback rule. When the sponsor asked who had reviewed it, I named the infra and service reviewers. I also asked every service team for an estimated certification time, so leadership could size the window.
- **Outcome:** the decision held. A later dry run in Cell 0 was ruled out again because real customer traffic ran through that cell.
- **What I learned:** **pre-wire risky options with the domain experts before putting them in front of an executive.** I put a routing option in a 173-person post before checking cell affinity and the single-primary constraint with the people who knew those constraints best. Now I run that check privately first.

### 2.6 What could have gone better (volunteer at least two)

| What happened | What I should have done | What I do now |
|---|---|---|
| My first plan review with the VP and senior leaders was **too technical**. They needed to make a go/no-go decision, and I walked them through the design. | Ask first what decision the audience has to make | Decision-driven format: status, risk in business terms, the ask; detail in an appendix |
| Service teams were **confused about their roles** early on | Publish a RACI before the first window | A written RACI for each window, plus a named coordinator |
| A non-SLA upgrade **failed on Azure API issues**, and my updates to leadership gave status but not enough on **mitigation steps and timelines** | Give mitigation steps and a timeline with every update | Incident updates always include what we're doing, what's next and when |
| A **last-minute Azure core shortage** | Track capacity with Azure proactively | Quota and capacity are a pre-flight checklist item |
| I posted the Cell 0 routing option **before pre-wiring it with experts** | Check the constraints privately first | Pre-wire risky options (§2.5) |
| **Rollback testing took longer than expected** | Plan rollback rehearsal as its own milestone | A dedicated rollback milestone, with a working STAGE environment |
| **Ubuntu upgrade: missed early signals.** A sequence problem appeared after the OS cutover. My manager said my reflection was too high-level. | Turn lessons into mechanisms | Pre-flight checklists, stage gates with pass/fail criteria, early-signal alerts **[confirm the customer impact]** |

The manager feedback in the last row is a strong self-awareness point. You can say: *"My manager told me my reflection was too high-level and didn't turn into repeatable changes. He was right, so now I write lessons as mechanisms: checklists, gates and alerts."*

### 2.7 Likely follow-ups

> **Q: How did you get 15 teams to actually do the work?**
> I made the ask small and concrete: core end-user scenarios only, a short checklist and a dated deadline. An engineer I coached owned the tracking. And everyone knew the rollback rule in advance, which gave teams a reason to pick scenarios carefully.

> **Q: What did you do when the executive asked for something you thought was unsafe?**
> I treated the goal as real: more test time. I wrote down the options, invited the experts to break them, changed my position when they did, and closed with a documented recommendation and named reviewers (§2.5).

> **Q: Who was hardest to work with, and why?**
> Not a person, a dependency: Azure during the production Saturday. I'd worked with the Azure compute capacity team to secure extra compute, because we kept the old nodes running for rollback. But Azure's maintenance made provisioning unreliable. I couldn't change Azure, so I changed the plan: minimum nodes now, full capacity later. Internally, the hardest moment was being challenged publicly on the Cell 0 option, and the right response was to agree.

> **Q: Why did you need extra capacity at all?**
> Because the safe rollback path was the old nodes themselves. Until the new version was validated, I kept the old 9.6 nodes running next to the new ones, so a rollback meant switching back, not rebuilding 10 TB clusters. That roughly doubled the compute for each cluster during its window **[confirm]**, across up to 50 replicas. So I worked with the Azure compute capacity team ahead of time on how much we needed, where, and for how long, and released it once rollback was no longer needed.

> **Q: How did you make sure leadership wasn't surprised?**
> Decision-driven updates at each go/no-go point, the org-wide status posts, and live options on incident calls. I'll own that my updates during the Azure API failure lacked mitigation steps and timelines, and I fixed that afterward.

---

## 3. A Different Function: Legal on the Elasticsearch Fork

**Use when asked:** working with a non-engineering function, influencing without authority, going against the norm.

- **Situation:** the organization paid millions a year in commercial Elasticsearch licensing, mostly for inter-node TLS. Provisioning took days and patching was risky. The platform affected all 15 teams.
- **The partnership:** forking open source raised licensing, IP and contribution questions only **Microsoft legal** could answer. Legal's agenda is risk avoidance. Mine was cost and velocity.
- **What I did:** I worked with legal on licensing, IP and contribution requirements, and treated their constraints as **architectural inputs**, not a final sign-off. I was explicit up front that the fork carried real engineering cost and risk, and I backed the case with numbers.
- **Outcome:** native TLS on the fork, AKS with Helm and declarative CI/CD, provisioning and patching from days to under 15 minutes, and more than $10M a year saved. The search team owns the platform today.
- **Could have gone better:** I'd bring legal in **even earlier, with a written risk plan**. Engaging late risks late-stage delays.
- **Lesson:** a non-engineering partner's constraints belong in the design, not at the end of it.

---

## 4. A Difficult Partnership: Search Compute Capacity Conflict

**Use when asked:** conflicting agendas, a difficult partner, an escalation.

- **Situation:** the search team's tech lead asked me to substantially scale Elasticsearch nodes (more GPU and memory) for production-scale experiments with new search models. Azure had a capacity crunch, the extra compute was raising COGS, and the Copilot integration rollout depended on the work.
- **Agendas:** the search team wanted speed for experiments and the Copilot timeline. I was responsible for scarce capacity and COGS. Both were legitimate.
- **What I did:** I proposed three options that needed less compute, instead of just adding more.
  1. **Pushed back with a way to cut load.** I proposed lowering the search model's query fan-out, so each search sends fewer requests to the servers. I also asked him to benchmark in pre-prod before rolling out to prod.
  2. **Took his constraints seriously.** They had no production-scale pre-prod environment, and optimizing the models wasn't feasible in the short term. We didn't resolve it, and he escalated to leadership. With the COGS impact, it reached the VP level.
  3. **Gave leadership the trade-off and a smaller rollout:** scarce capacity, rising COGS, the Copilot timeline. I proposed indexing data only for the users eligible for the A/B experiments, instead of the whole user base, so the feature could roll out to them without more compute. We agreed to roll out to those users until the models needed less compute.
  4. **Created headroom:** I proposed moving non-SLA traffic to the DR region. The tech lead agreed, it freed about 30% of capacity, and I carried it out.
- **Outcome:** experiments rolled out to the A/B users within the freed capacity. What lasted was a **regular sync** between the search team and me on model-efficiency progress, which turned a dispute into a shared commitment.
- **Could have gone better:** my pre-prod benchmarking ask **wasn't feasible**, because the environment didn't exist. I should have checked that before pushing it, and raised the capacity option sooner, before it went to the VP.
- **Lesson:** when two legitimate priorities collide, options that shrink the need or create headroom (fewer users to index, non-SLA traffic moved to DR) give everyone something to agree on, and a recurring sync keeps the agreement from fading.
- **Likely probe:** "Didn't moving traffic to the DR region weaken disaster recovery?" **[confirm: how much DR headroom stayed free, whether non-SLA traffic would be shed during a real failover, and who signed off.]**

---

## 5. A Conflict I Couldn't Resolve: Homefeed and Rankie Fail-Open

**Use when asked:** a disagreement you lost, disagree and commit, differing assumptions.

- **Situation:** when Rankie (the ranking service) failed, the home feed failed with it, so users saw errors on the main surface.
- **My position:** fail open, returning a basic feed when Rankie is down. **The service team's position:** ranked quality *is* the experience, so a degraded feed might be worse than none.
- **What I did:** over several conversations I made the different assumptions explicit (availability versus quality), and I **brought in the product team** so the decision rested on customer impact, not engineering preference.
- **Outcome:** my design **wasn't adopted**. Rankie failures were infrequent and a backup feed was costly, so it went to the backlog. I disagreed, made my case, then committed fully, and I think the call was reasonable.
- **What I'd change:** bring **failure frequency, customer impact and cost data to the first conversation**, not the third. I lost time arguing principles when the decision was really about numbers.

---

## 6. A Relationship I Hurt: The Kafka Offset Change

**Use when asked:** "Tell me about a time you screwed up with another team."

- **What happened:** FaultLine, the AI SRE sidecar I built, suggested batching Kafka offset commits to reduce broker saturation. I implemented it after validating only the local logic. **Service teams then got paged** for high lag and elevated HTTP 5xx errors. I'd created an incident for partner teams with a change they hadn't asked for.
- **What I did:** reverted my pull request right away, and owned it as my mistake: the change was right in isolation and wrong in the system. **[confirm: how you communicated with the affected teams, whether you held a post-incident review, and whether you apologized directly.]**
- **What changed:** for any change that affects partner systems, I now validate downstream assumptions, test end to end, and define rollout and rollback criteria **before** shipping. I built the same discipline into IRIS (a two-stage verification pipeline and permission boundaries), so AI-suggested changes earn trust instead of spending it.
- **Lesson:** trust with partner teams is spent quickly by surprising them. The approver, which was me, is accountable for the downstream impact.

---

## 7. Ownership Boundaries: When the Fix Belongs to the Other Team

**Use when asked:** handling different agendas, pushing back on a partner, influencing without authority.

### 7.1 Outlook email telemetry loss
- **Situation:** two legacy events from YAMS went missing on the way to Analytics, so Engage daily active users were under-reported by 15–20%, across several thousand customer networks. The investigation focused on the Host Log Collector (HLC).
- **The tension:** the natural ask of the infra team was "fix the HLC bug". But we designed HLC to **drop logs when host buffers are full**, to keep the host alive.
- **What I did:** reframed the problem in the open: logs are best-effort by design, so customer-facing metrics shouldn't depend on them. I recommended that the service team collect these metrics through another mechanism.
- **The partnership skill:** telling a partner that the fix is on their side, and backing it with the design rationale rather than leaving it as "not our problem". **[confirm: how the service team responded, and what mechanism they adopted.]**

### 7.2 VENT lag (from Connect)
- I resolved ambiguity about VENT lag by building alignment that the root cause was **service-side event consumption, not infrastructure**, and I proactively educated partner teams so the fix landed at the right layer. My manager called out my *"ability to separate infrastructure vs. service ownership concerns and influence partner teams."* **[confirm the specifics before using this as a full story.]**

**Lesson for both:** a boundary dispute goes well when you bring evidence, explain your own layer's design honestly, and help the other team with theirs. It goes badly when it sounds defensive.

---

## 8. Short Supporting Examples (one or two sentences each)

| Story | Function or partner | The XFN point |
|---|---|---|
| **Secret Scanner** | 15 teams with different secret stores (AKV, HashiCorp Vault, env files); Trust and compliance | Aligned each team's leaders first, identified their gaps, wrote onboarding guides, ran office hours. Got through a difficult Trust and compliance clearance. When teams complained about alerts for secrets they didn't use, I treated it as legitimate feedback and fixed the scanner. 100% adoption. |
| **IRIS** | Trust and Security leadership | Enterprise policy didn't cover autonomous AI actions, so I didn't ask for exceptions. I co-designed permission boundaries and blast-radius controls with them. |
| **Maestro** | Skeptical team leads across 15 teams | Skeptics were rejecting disruption, not AI. I rebuilt it as plug-ins that fit their pipelines, and peers convinced peers through forums. 10 teams, 100+ engineers. |
| **alt_pool coaching** | A staff engineer's broadcast ask that wasn't landing | Coached him to align tech leads first, write easy steps and run office hours. 100% adoption across 15 teams. |
| **Embeddings clusters** | My manager | Disagreed directly, brought cost data, and found node pools plus a kill switch, so we both owned the result. |

---

## 9. Self-Awareness Bank

Be ready to say any of these without being asked:

1. **I over-explain to executives.** My first VP plan review was too technical. Now: decision first.
2. **I've put a risky option in front of leadership before pre-wiring it with experts** (the Cell 0 split brain). Now: private expert check first.
3. **I've pushed an ask that wasn't feasible** (pre-prod benchmarking with no pre-prod environment). Now: check feasibility before asking.
4. **I've surprised partner teams with a change** (Kafka offsets). Now: validate downstream assumptions and set rollback criteria first.
5. **I've argued principles when the decision was about numbers** (Rankie). Now: bring the data to the first conversation.
6. **My reflections were too high-level** (manager feedback on the Ubuntu setbacks). Now: lessons become checklists, gates and alerts.
7. **I've won a technical argument and lost on cost** (Cosmos DB, nearly 10x the Hadoop cost). Now: I give cost objections from partners the same rigor as technical ones.

---

## 10. Question Bank → Which Story

| Question | Lead with | Backup |
|---|---|---|
| Walk me through a cross-functional project you led | §2 PostgreSQL | §8 Secret Scanner |
| How did you keep the team informed and aligned? | §2.4 communication table | §4 recurring sync |
| How did you ensure the project team was effective? | §2.3 definition of done, ownership, unblocking | §8 alt_pool |
| A difficult partnership | §4 Search compute | §2.5 executive ask |
| Conflicting agendas between teams | §4 Search compute | §5 Rankie |
| A conflict you couldn't resolve | §5 Rankie | §4 (pre-prod ask not adopted) |
| A working relationship you screwed up | §6 Kafka offsets | §2.5 Cell 0 option |
| Working with a non-engineering function | §3 Legal | §8 IRIS with Trust and Security |
| Influencing without authority | §8 Maestro / Secret Scanner | §7 telemetry |
| Pushing back on a senior leader | §2.5 executive ask | §8 Embeddings with your manager |
| Communicating with executives | §2.6 VP feedback | §2.4 |
| When another team says no | §5 Rankie | §8 Secret Scanner false positives |
| When do you escalate? | §4: escalate with a trade-off and a headroom option, not a complaint | §2.5 |
| How has your approach to collaboration changed? | §9 self-awareness bank | §1 operating model |

**My escalation rule:** escalate when two legitimate priorities collide and the people involved can't trade them off, never as a first move. Bring the trade-off, the options and a recommendation. After the decision, set up a recurring check-in so it holds.

---

## 11. Questions to Ask the Interviewer

1. Which functions does this team depend on most, and where does that partnership create the most friction today?
2. How are cross-team priorities resolved here when two teams' goals collide, and who makes the call?
3. Can you tell me about a cross-functional project that went sideways, and what the team changed afterward?

---

## 12. Facts to Confirm Before the Interview

| # | Item | Where |
|---|---|---|
| 1 | Any recurring cross-team sync during the PostgreSQL project, and the live channel used during windows | §2.4 |
| 2 | Ubuntu sequence problem: customer impact | §2.6 |
| 3 | Kafka offsets: how you communicated with affected teams, whether there was a postmortem or a direct apology | §6 |
| 4 | Telemetry: how the service team responded, and what mechanism they adopted | §7.1 |
| 5 | VENT lag: specifics (teams, evidence, outcome) | §7.2 |
| 6 | Secret Scanner: what made the Trust and compliance clearance difficult | §8 |
| 7 | PostgreSQL target version: say it consistently (the May 2025 thread says 16; other docs say 18.6) | §2.1 |
| 8 | Azure capacity: how much extra compute, how far ahead you asked, how you worked with the capacity team, and when old nodes were released | §2.2, §2.3, §2.7 |
