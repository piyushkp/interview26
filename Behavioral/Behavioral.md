# Behavioral Interview (Meta, 45 minutes)

> They want your background, what you're passionate about in tech, and the impact you want to make. Answer every question with a real story in STAR form: say "I", give numbers, and end with what you learned. Start concrete; if you drift into theory, they'll ask for an example.

---

## 0. How the 45 Minutes Go

| Time | What happens | Your move |
|---|---|---|
| 0–5 min | Intro | The 90-second intro (§1). End on the impact you want to make. |
| 5–40 min | 3–5 questions, each with follow-ups | One story each, 2–3 minutes, then let them dig in |
| 40–45 min | Your questions | Two from §8 |

**They score five focus areas:** Resolving Conflict, Growing Continuously, Embracing Ambiguity, Driving Results, and Communicating Effectively. Work out which one a question tests, then pick the story **and the principle to land** from §3.

**STAR, timed:** Situation and Task in about 20 seconds → Actions, most of the time, all "I" → Result with numbers → a one-line lesson.

---

## 1. Intro: Background, Passion, Impact

**90-second intro:**

"I'm a Senior Principal Software Engineer on the Viva Engage infrastructure team at Microsoft, with 18 years in distributed systems. I'm passionate about removing systemic problems for many teams at once, through scalability, reliability, cost and developer productivity. Lately, that means agentic AI for operations that earns trust through verification, like IRIS and FaultLine. I build the infrastructure that lets about 150 engineers across 15 teams move faster without breaking things, for a product with 250 million daily active users.

A few examples. Secret Scanner reached 100% adoption across all 15 teams and ended certificate- and secret-related outages. Forking Elasticsearch onto Kubernetes cut provisioning from days to under 15 minutes and saved more than $10M a year. The PostgreSQL upgrade across about 40 clusters unblocked our Teams and Copilot integrations, which grew daily active users 30%. And IRIS, a multi-agent AI system I conceived, resolves about 30% of infrastructure requests on its own.

Each one fixed a problem for every team at once. Next, I want to bring that leverage to consumer-scale infrastructure and agentic AI for operations, where it's even bigger."

**If they ask how you work or lead (30 seconds):** "Three habits. **I align leaders first, then make adoption easy:** that's how Secret Scanner reached 100% of teams without a mandate. **I separate the goal from the ask:** when an executive asked for a risky production test, the real goal was more test time, so I wrote down the options, let experts break them, and we landed on a safe in-window canary. **I turn every lesson into a mechanism:** after a production bug, I added checklists, gates and alerts instead of promising to be more careful."

**If they ask how you motivate or grow engineers:**
- **Give ownership, not tasks:** an engineer I coached owned certification across all 15 teams, not just the tracker, and now owns cross-team testing coordination.
- **Connect the work to why it matters:** "this upgrade is the gate to Teams and Copilot," not "patch the CVEs."
- **Coach the person, don't take over the work:** I coached a staff engineer to drive alt_pool adoption himself, and it reached 100% of teams.
- **Remove the blocker, don't just report it:** when the front-end team was busy, I built the outage-banner change myself.
- **Make wins visible, and credit them by name:** in a code review, I framed my retry fix as building on a teammate's idea, and he got the credit.

**What I like about my role and being a developer** *(make these your own)*:
- **Leverage:** one platform change fixes a problem for 15 teams at once.
- **Problems that are half technical, half people:** on the Postgres upgrade, the hardest part was getting 15 teams to agree on what "working" meant.
- **Growing people:** an engineer I coached now owns cross-team testing coordination.
- **Still building:** I still prototype and ship code myself, like FaultLine and the outage-banner change.

**The impact I want to make:** apply that leverage at consumer scale. [Tailor: the Meta team or problem you'd most want to work on, and why.]

**What I'd improve about my current role (if asked):** more protected time for long-term bets, because reactive work wins every tie. I attacked the load itself with automation like IRIS and Secret Scanner.

---

## 2. Three Projects to Know Cold

| | PostgreSQL & Ubuntu upgrade | Secret Scanner | Search modernization |
|---|---|---|---|
| **Why** | End-of-life 9.6, open critical CVEs, Trust unmet → Teams and Copilot blocked | Expired certs and secrets caused 2 outages for all customers; Trust requires 60-day rotation | Fragile manual deploys, days to provision, millions a year in licensing, mostly for TLS |
| **Scale** | ~40 clusters, ~10 TB each, 15 teams; I led 10–15 engineers | 15 teams (~150 engineers); I led 10 engineers | 15 teams; I led 10–15 engineers |
| **What I did** | Two-phase design; core-SLA certification with a pre-agreed rollback rule; parallel pipeline for 7 SLA clusters; decision-first exec updates | Automated discovery and 15-day expiry alerts; aligned each team's leaders; docs and weekly office hours; fixed noisy alerts | Forked Elasticsearch with native TLS; AKS, Helm, declarative CI/CD; worked with legal early |
| **Result** | CVEs cleared → Teams + Copilot → **+30% DAU**; **−40%** incidents; ~1 h window per cluster, ~5 min OS cutover | **100% adoption**; **zero** credential outages; thousands of credentials monitored | Provisioning **days → under 15 min**; **>$10M a year** saved |
| **Hard part** | 15 teams couldn't define "working"; Azure failed mid-upgrade; double-shifted IDs | Every team stored secrets differently; Trust clearance | The engineering and legal risk of owning a fork |

**Also ready:** **IRIS** (~30% of infra requests resolved on its own, −45% triage latency), **Maestro** (10 teams, 100+ engineers, ~25% faster cycle time), and the **database health check** (99.999% read availability).

---

## 3. Focus Area → Story → Principle

End each story with one principle that names the habit it proves. Don't recite principles; the story is the evidence.

| Focus area | What they look for | Lead story | Backup | Principles to land |
|---|---|---|---|---|
| **Resolving Conflict** | Empathy for the other side's goals; a win-win; disagree and commit | Search compute (§4.3) | Rankie (§4.8); embeddings with my manager | Separate the goal from the ask, then solve for the goal. Escalate with options, not complaints. |
| **Growing Continuously** | Owning mistakes, taking feedback, changed behavior | Kafka offset revert (§4.6) | "Too technical" feedback (§4.5); double-shifted IDs (§4.7) | Own it first, explain it second. Turn every lesson into a mechanism. |
| **Embracing Ambiguity** | Moving with incomplete information; defining success yourself | Postgres upgrade (§4.1) | Telemetry loss (§4.9); the Azure Saturday | Agree the rules before the pressure, not during it. Know your one-way doors. |
| **Driving Results** | Initiative, obstacles overcome, measurable impact | Secret Scanner (§4.4) | Search modernization; the Postgres results | Align leaders first, then make adoption easy. Remove the blocker, don't just report it. |
| **Communicating Effectively** | Adapting to the audience; clear trade-offs; listening | The exec's no-outage request (§4.2) | Decision-first updates (§4.5) | Decision-driven for leaders, detail-driven for engineers. Write the options first, then invite experts to break them. |
| **Growing others** *(not one of the five, but often asked at senior levels)* | Ownership, coaching, credit | alt_pool coaching (§4, one-liners) | The engineer who now owns testing coordination | Give ownership, not tasks. Coach the person, don't take over the work. |

Use each story once. The Postgres upgrade fits almost everything, so save it for one question and use its pieces (the Azure Saturday, the exec's request) elsewhere.

---

## 4. STAR Stories (2–3 minutes each)

### 4.1 PostgreSQL and Ubuntu upgrade (Ambiguity, Results)
- **S:** ~40 PostgreSQL 9.6 clusters were end-of-life with open critical CVEs, which blocked Teams and Copilot. There was no proven path for a seven-version jump at 10 TB per cluster, and 15 teams couldn't say how they'd prove their service still worked.
- **T:** Own it end to end, with 10–15 engineers, zero data loss and a bounded downtime budget.
- **A:**
  - I designed two phases: `pg_upgrade` on the same OS, then logical replication to Ubuntu 20.04, which avoided a silent index-corruption trap.
  - I narrowed "working" to each team's core SLA scenarios, with a rule agreed in advance: a core scenario fails → roll back; anything else → fix forward. I gave an engineer I coached ownership of certification across all 15 teams.
  - I ran the non-SLA clusters first, then the 7 SLA clusters in parallel through a pipeline I built.
  - On the production Saturday, Azure provisioning failed and leads wanted to abort. I proposed continuing on the minimum nodes, since weekend traffic is low, and we had full capacity that night.
- **R:** All ~40 clusters done; ~1 h write outage per cluster, ~5 min OS cutover; CVEs cleared → Teams and Copilot → **+30% DAU**; **−40%** related incidents.
- **Lesson:** a sound design isn't enough; rollback planning and a bounded definition of "working" matter as much.
- **Principles to land:** *Agree the rules before the pressure, not during it. Look for the reversible middle option.*

### 4.2 The exec's no-outage test request (Communication, Conflict)
- **S:** Before production, the executive sponsor asked to test Microsoft's own tenant on the new version without a write outage. The real goal was more test time for service teams.
- **T:** Meet the goal safely, or show clearly why it couldn't be done.
- **A:** I wrote up three options, posted them to the org (173 views), and asked principal engineers to break them. They showed my first option would create two writable primaries, a split brain, with corrupted IDs spreading into Cosmos DB. I agreed with the critique in an RFC review, recommended upgrading with that tenant as the in-window canary, and named the reviewers to the sponsor.
- **R:** The decision held; a later dry run was ruled out again for the same reason.
- **Lesson:** run risky options past the experts before they reach an executive.
- **Principles to land:** *Write the options first, then invite experts to break them. Change your mind fast when the facts change.*

### 4.3 Search compute capacity (Conflict)
- **S:** Our Elasticsearch cluster had 100 nodes. The search team asked for 40 more higher-GPU nodes during an Azure capacity crunch, COGS was rising, and the Copilot rollout depended on it.
- **T:** Protect capacity and cost without blocking the search team.
- **A:** I proposed lowering the model's query fan-out. The tech lead had no production-scale pre-prod and couldn't change the model quickly, and I took that seriously. It went to the VP, and there I pointed out a gap: search planned to index every tenant, but product was only launching to the dogfood tenants. So we indexed only those. I also moved non-SLA traffic to the DR region.
- **R:** **10 new nodes instead of 40**, ~30% capacity freed, the feature rolled out to the dogfood tenants, and we set up a regular sync on model efficiency.
- **Lesson:** look for the gap between what one team plans to build and what another plans to ship.
- **Principles to land:** *Shrink the need first, then add capacity. Escalate with options, not complaints.*

### 4.4 Secret Scanner (Results)
- **S:** Expired certificates and secrets had caused two major outages for all customers. Trust required 60-day rotation, and teams tracked secrets in spreadsheets.
- **T:** Eliminate certificate- and secret-related outages across 15 teams.
- **A:** I led 10 engineers to automate discovery across Key Vaults, VMs and clusters, with alerts 15 days before expiry. Every team stored secrets differently, so I aligned each team's leaders first, then gave them onboarding docs and weekly office hours. I worked through Trust and compliance clearance, and when teams complained about alerts for secrets they didn't use, I fixed the scanner.
- **R:** **100% adoption** (15 teams, ~150 engineers), **zero** certificate or secret outages, thousands of credentials monitored.
- **Lesson:** adoption is part of the product, and noisy alerts kill trust.
- **Principles to land:** *Align leaders first, then make adoption easy. Constraints are design inputs, not approval gates.*

### 4.5 "Too technical" feedback (Growth, Communication)
- **S:** At my first plan review with the VP and senior leaders, a senior leader said my update was too technical; he couldn't tell what decision he had to make.
- **A:** It stung, but he was right. I switched to decision-first: status and risk in business terms, then the decision needed, with the details in an appendix.
- **R:** Executive alignment got much easier, and a high-risk plan moved forward.
- **Lesson:** communication is judged by whether the audience can act on it.
- **Principle to land:** *Decision-driven communication for leaders, detail-driven for engineers.*

### 4.6 The Kafka offset change I reverted (Growth: a mistake)
- **S:** FaultLine, the AI SRE tool I built, suggested batching Kafka offset commits to relieve broker saturation.
- **A:** I applied it after checking only the local logic. Service teams got lag and 5xx alerts, so I reverted right away and owned it. Then I changed how I work: validate downstream assumptions, test end to end, and set rollout and rollback criteria before any AI-suggested change. I built the same into IRIS: two-stage verification and permission boundaries.
- **R:** The impact stopped quickly. The same discipline is how I evaluate AI index recommendations: one cut P95 reads from 180 to 65 ms, but cost 30–37% of write throughput and 65% more WAL.
- **Lesson:** right in isolation can be wrong in the system.
- **Principles to land:** *Own it first, explain it second. Treat AI output as a hypothesis, not an answer.*

### 4.7 Double-shifted IDs after the Ubuntu cutover (Growth)
- **S:** After the OS cutover, our sequence-sync script used the standard formula on legacy IDs that are stored shifted left 13 bits, so new IDs came out 8,192× too large. Two days later the busiest table overflowed into negative IDs, and GIF and link previews broke. About 50K rows were affected.
- **A:** I reverted the sequences to their correct values, fixed the 50K rows by hand, and checked every similar sequence. My manager said my first reflection was too high-level, and he was right, so I turned it into mechanisms: pre-flight checklists, stage gates with pass/fail criteria, and early-signal alerts.
- **R:** The bad IDs never left Postgres, so nothing needed cleaning up downstream.
- **Lesson:** our checks proved writes *worked*, not that the values were *right*.
- **Principle to land:** *Turn every lesson into a mechanism.*

### 4.8 Rankie fail-open (Conflict I didn't win)
- **S:** A failure in Rankie, the ranking service, took down the home feed. I proposed failing open to a basic feed.
- **A:** The service team pushed back: ranked quality *is* the experience. I made the different assumptions explicit, availability versus quality, and brought in product so the decision rested on customer impact.
- **R:** Not adopted: failures were rare and a backup feed was costly. I disagreed, made my case, then committed fully, and I think the call was reasonable.
- **Lesson:** bring failure frequency, customer impact and cost to the first conversation, not the third.
- **Principles to land:** *Bring data to the first conversation, not the third. Disagree openly, then commit fully.*

### 4.9 Telemetry loss (Ambiguity)
- **S:** Daily active users were under-reported by 15–20% because two legacy events intermittently vanished. The investigation was hunting for a bug in the Host Log Collector.
- **A:** The investigation traced the path end to end, and I named the hidden assumption: the collector drops logs by design when host buffers fill, to keep hosts alive. That changed the question from "fix the collector" to "why do customer-facing metrics depend on best-effort logs?", and I recommended the service team move them to a guaranteed path.
- **R:** The fix targets the whole class of problem, not one occurrence. [What the service team adopted.]
- **Lesson:** when a pipeline drops data by design, the fix belongs with the consumer, not the pipeline.
- **Principle to land:** *Prove the layer with data, then help the owner fix it.*

**More stories, one line each (principle in italics):**
- **Embeddings, with my manager (conflict):** I disagreed directly, brought cost data, and we landed on dedicated node pools plus a kill switch that we both owned. *Separate the goal from the ask.*
- **Cosmos DB cost miss (mistake):** I won the scaling argument, then cost went to ~10× when discounts ended. Now I model multi-year costs. *Give cost objections the same rigor as technical ones.*
- **Maestro (influence):** skeptics were rejecting disruption, not AI. Plug-ins, docs and office hours brought 10 teams and 100+ engineers on board, with ~25% faster cycle time. *Align leaders first, then make adoption easy.*
- **IRIS (AI with trust):** I brought Trust and Security in as co-designers of the limits; ~30% of requests resolved on its own, −45% triage latency. *Constraints are design inputs, not approval gates.*
- **alt_pool coaching (growing others):** I coached a staff engineer to align tech leads first, then make adoption easy: 100% adoption across 15 teams. *Coach the person, don't take over the work.*
- **Code-review credit (growing others):** I suggested jitter on a teammate's retry fix and framed it as building on his idea; he got the credit. *Make wins visible, and credit them by name.*
- **Outage banner (initiative):** the front-end team was busy, so I built the change myself with AI help; they reuse the template. *Remove the blocker, don't just report it.*
- **Database health check (ambiguity):** dashboards were green, reads failed sporadically. The pooler's TCP check missed a degraded replica; synthetic queries and circuit breaking got reads to 99.999%. *Prove the layer with data.*

---

## 5. Question Bank → Story

| Question | Story |
|---|---|
| Tell me about yourself | §1 |
| Your leadership style / how you work | §1, the 30-second "three habits" |
| How do you motivate or grow engineers? | §1 motivation bullets, then alt_pool coaching |
| How do you handle conflict? | Separate the goal from the ask, then §4.3 Search compute |
| How do you decide under pressure? | Look for the reversible middle option: the Azure Saturday (§4.1) |
| Your most impactful project | §4.1 Postgres |
| A conflict with a peer or another team | §4.3 Search compute |
| A disagreement with your manager | Embeddings (node pools plus a kill switch) |
| A conflict you couldn't resolve | §4.8 Rankie |
| A mistake you made | §4.6 Kafka offsets (backup: Cosmos DB cost) |
| Critical feedback you received | §4.5 "Too technical" (backup: "too high-level", §4.7) |
| Something you learned recently | AI output as a hypothesis (§4.6) |
| An ambiguous problem | §4.1 Postgres (backup: §4.9 telemetry) |
| A decision with incomplete information | The Azure Saturday: minimum nodes (§4.1) |
| Pivoting mid-project | The Azure Saturday: hold the outcome, change the scope |
| Influencing without authority | §4.4 Secret Scanner, or Maestro |
| Pushing back on a senior leader | §4.2 The exec's request |
| Going above and beyond | The outage banner, or the database health check |
| Helping someone grow | alt_pool coaching; the engineer who now owns testing coordination; code-review credit |
| Underperformance on your team | Work stories Q3 *(still a draft: fill the brackets or skip it)* |
| A project that went wrong | §4.7 Double-shifted IDs |
| What do you like about your role? | §1 |
| What would you improve about your current role? | §1 |

---

## 6. Honest Self-Awareness (volunteer one)

1. **I over-explained to executives.** Now: decision-driven for leaders, detail-driven for engineers (§4.5).
2. **I put a risky option in front of leadership before checking it with experts.** Now: write the options, and let experts break them privately first (§4.2).
3. **I pushed an ask that wasn't feasible** (pre-prod benchmarks with no pre-prod). Now: check feasibility before asking (§4.3).
4. **I surprised partner teams with a change** (Kafka offsets). Now: own it first, then validate downstream before shipping (§4.6).
5. **I argued principles when the decision was about numbers** (Rankie). Now: bring data to the first conversation, not the third (§4.8).
6. **I won a technical argument and lost on cost** (Cosmos DB, ~10×). Now: model multi-year costs and give cost objections the same rigor as technical ones.

---

## 7. Answer Checklist

- Pick the focus area first, then the story (§3).
- Situation and task in about 20 seconds. Spend the time on what *I* did.
- Numbers: before → after, plus who it affected (teams, engineers, customers).
- Name the trade-off and why you chose it.
- Include what was hard or what you got wrong.
- End with the lesson, then **one principle** from §3 that matches the focus area. Let the story prove it; never list principles.
- Stop at 2–3 minutes and let them dig in. If they redirect, give a concrete example, never theory.

---

## 8. Questions to Ask

1. What does success look like in the first 90 days?
2. What's the most important problem you're hoping this hire will solve?
3. What's the biggest challenge the team is facing right now?
4. How are cross-team priorities resolved when two teams' goals collide, and who makes the call?
5. Can you tell me about a project that went sideways, and what the team changed afterward?

---

## 9. Verify Before the Interview

1. **Dates:** when each story happened. Meta prefers the last 2–3 years.
2. **+30% DAU:** the baseline and time window, since you also quote 250M daily active users.
3. **Underperformance story** (work stories Q3): still a draft. Fill in the brackets or don't use it.
4. **Telemetry loss:** what the service team adopted, and whether DAU was corrected.
5. **Double-shifted IDs:** how long previews were broken, and how you fixed the 50K rows.
6. **AI index numbers:** where they were measured, and what you shipped.
7. **Search compute:** how much DR headroom stayed free after moving non-SLA traffic.
8. **Meta tailoring** in §1: the team or problem you'd want to work on.
