# Work Stories

Converted from `Work Stories.xlsx` (sheets: stories, Questions & Answers, Followup questions).

## Stories

Index:

1. Postgres & OS Zero-Downtime Upgrade
2. Secret Scanner
3. Search Infrastructure Modernization
4. Database Health Check & Resiliency
5. IRIS: Autonomous AI Incident Remediation
6. Maestro: Multi-Agent SDLC Platform Adoption
7. Homefeed vs Rankie failure
8. Kafka consumer retries
9. Embeddings on seperate cluster
10. HDFS retirement vs CosmosDB cost
11. AI suggestion of kafka offset commit change
12. FaultLine: Autonomous SRE Sidecar
13. Search Compute Capacity Conflict

### 1. Postgres & OS Zero-Downtime Upgrade

**Context**

I owned the PostgreSQL and Ubuntu upgrade across about 40 production clusters, and I led 10 to 15 engineers through it. The clusters ran legacy PostgreSQL 9.6 on Ubuntu, with critical CVEs open and Microsoft's Trust requirements unmet. PostgreSQL 9.6 has no native logical replication, so a standard upgrade meant substantial downtime and customer-refund risk. Breaking changes also affected multiple Java and infrastructure services. The work touched all 15 Viva Engage teams, about 150 engineers. The biggest challenge wasn't the database work. The 15 service teams weren't sure how to test their service after the upgrade to certify that it still worked. They had unit and integration tests, but those didn't cover everything, and end-to-end integration tests carried their own risk and cost.

**Actions**

I designed a two-phase migration to keep downtime small, and I worked on four fronts. For the database, I used pg_upgrade to move PostgreSQL from 9.6 to 18.6. To protect the services that depend on it, I introduced feature flags so the Java and infrastructure services stayed compatible across both versions without deployment locks, and I built dynamic maintenance banners to keep customers informed. For the OS, I ruled out an in-place Ubuntu upgrade because of the Ubuntu 18.04 libc index-invalidation issue. Instead, I used native logical replication to stream changes to a mirrored Ubuntu cluster, which allowed a short cutover. Throughout, I wrote a comprehensive rollback plan and aligned executives and stakeholders across organizations on it, so a VP-level audience had confidence in a plan with broad production impact.

Because the PostgreSQL upgrade averaged about one hour of downtime per cluster, I grouped the clusters into non-SLA and SLA cohorts and scheduled them in separate upgrade windows. I upgraded the non-SLA clusters first, allowed enough bake time to observe stability, and then upgraded the SLA clusters in the later window.

I tackled the testing uncertainty by narrowing the question. Instead of asking each of the 15 teams to prove every possible scenario, which was impossible, I asked them to identify their service's core SLA test scenarios and certify those after the upgrade. That gave each team a bounded, achievable definition of working that fit within the cohort windows and avoided depending on risky end-to-end suites. My decision rule after the upgrade was simple: if a core SLA scenario failed, we rolled back, and for any other issue we fixed forward, treating it as a problem to fix quickly rather than a reason to roll back.

The UI only had a generic system-outage banner, but for this upgrade customers needed a specific message with the maintenance time in it. The front-end team was busy with feature work, so instead of waiting I made the front-end change myself, using AI to help. The front-end team was happy with it, and it left them with a reusable custom template for outage banners.

When I first presented the plan to the VP and senior leaders, the feedback was that it was too technical. They needed to decide whether to do the upgrade, not follow the details, so I reframed it around status, risk and the decision needed, with the technical detail as backup.

During the Saturday production upgrade, Azure had intermittent VM provisioning issues. We had procured capacity, but Azure was doing maintenance. In the large call with senior leaders on whether to continue or abort, several tech leads were concerned and asked to abort. I proposed a third option: since weekend customer traffic is lower, continue the upgrade on the minimum number of nodes, and add capacity once the Azure SDKs were stable. We went ahead that way, and on Saturday night, when the SDKs were stable, we provisioned full capacity.

**Results**

I completed all 40 or so clusters and every deployment stamp. The PostgreSQL upgrade averaged about one hour of downtime per cluster, and the OS upgrade needed roughly a five-minute cutover. Incidents involving replication lag, kernel panics and I/O saturation fell by 40%. The upgrades also secured the Trust and security clearance needed for Microsoft 365 integrations, including Teams and Copilot. The Infrastructure team owns the Postgres tooling today.

**Learnings**

I learned that a sound migration design isn't enough for a high-risk infrastructure upgrade. Comprehensive rollback planning and early executive alignment are essential. When teams can't prove everything works, I narrow certification to the core SLA scenarios and set a clear rule: roll back if one fails, otherwise fix forward. That beat chasing exhaustive coverage. I also learned how to build VP-level confidence and align stakeholders across organizations around a plan with broad production impact, by leading with the decision and risk instead of the technical detail. And when an external dependency like Azure provisioning fails mid-upgrade, "continue or abort" is often a false binary: I look for a reduced-scope option that keeps the risk acceptable, here minimum nodes during low weekend traffic.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| L | L | L | L | L |

**Signals shown:** Ownership, Ambiguity, Perseverance, Growth, Communication, Leadership

---

### 2. Secret Scanner

**Context**

Expired certificates and secrets had caused two major Viva Engage outages that affected all customers, and Viva Engage serves 250 million daily active users across 15 services. Trust required rotation every 60 days, but teams tracked secrets in spreadsheets and local notes across different technology stacks, with no central visibility. Executive leadership set a goal of eliminating certificate- and secret-related outages, and I took ownership of the design and the cross-org rollout. I led 10 engineers to build it.

**Actions**

I attacked the problem in three parts: the platform, the standards and adoption, which was the hardest. For the platform, I automated discovery across Azure Key Vaults and live VMs and clusters, with deduplication and removal of obsolete credentials, and I built central reporting with alerts 15 days before expiration. For the standards, I established governance that is firm on compliance but respects each team's architecture and constraints, and I aligned leaders across organizations on it. For adoption, I knew teams were on very different stacks, so I wrote onboarding documentation and held weekly office hours so they could self-serve instead of depending on me.

Adoption was hard because every team tracked secrets and certificates its own way: Azure Key Vaults, HashiCorp Vault, env files and more. I aligned the leaders of each team first, identified the gaps each team had, and then wrote a thorough onboarding guideline for them.

Trust and compliance clearance of the approach was also difficult, and I worked through it with those teams.

After launch, teams reported a lot of expiry alerts for secrets their services didn't use. The scanner was reporting every certificate and secret it found on a VM, not only the ones the service actually used. I iterated on the scanner so it reported only the credentials a service actually used, which cut the noise and kept teams' trust in the alerts.

**Results**

The rollout reached 100% adoption across all 15 Viva Engage teams, about 150 engineers, and achieved the goal of zero certificate- and secret-related outages. The platform monitored thousands of credentials and issued automated 15-day pre-expiry alerts, replacing manual tracking and supporting continuous Trust and security compliance. Infrastructure owns the platform today.

**Learnings**

I learned that a shared security platform succeeds only when teams can adopt it easily. Clear standards, self-service docs and sustained support mattered as much as the scanner itself. I also learned to balance firm compliance requirements with an understanding of each team's architecture. And I learned that noisy alerts erode trust quickly, so I treat early user feedback as a signal to iterate on accuracy, not just coverage.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| XL | XL | XL | L | XL |

**Signals shown:** Ownership, Ambiguity, Perseverance, Growth, Communication, Leadership

---

### 3. Search Infrastructure Modernization

**Context**

I led the modernization of our search platform with 10 to 15 engineers, and it affected all 15 Viva Engage teams, about 150 engineers. The platform ran on legacy Elasticsearch instances with fragile manual deployment scripts. Provisioning took several days and security patching was risky. On top of that, the organization paid millions of dollars a year for commercial licensing, mostly for inter-node TLS.

**Actions**

I took on three parts: the build, the platform and the legal path. I started by looking at what the license was actually buying, and it was mostly inter-node TLS. So I forked open-source Elasticsearch and implemented native TLS transport security, which removed the commercial licensing dependency. I was explicit that this meant real engineering cost and risk. For the platform, I designed the migration to Azure Kubernetes Service and wrote Helm charts and declarative CI/CD pipelines for provisioning, autoscaling and zero-downtime rolling upgrades. For the legal path, I worked with Microsoft legal teams on licensing, IP and contribution requirements.

**Results**

Cluster provisioning and patching dropped from several days to under 15 minutes, with single-click deployments. Removing the licensing dependency saved more than $10 million a year in COGS, and reliability and inter-node security improved across search environments. The search team owns the platform today.

**Learnings**

I learned to treat legal and open-source governance as architectural inputs, not final approval steps. Engaging legal, compliance and IP stakeholders early validates the approach and avoids late-stage delays.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| L | L | L | L | L |

**Signals shown:** Ownership, Ambiguity, Perseverance, Growth, Communication, Leadership

---

### 4. Database Health Check & Resiliency

**Context**

Tier-1 services had intermittent read failures and customers were seeing brief outages, yet the primary database dashboards showed healthy clusters. The failures were sporadic and spread across microservices, so nobody could tell which component was at fault. FaultLine, the AI SRE sidecar I built, flagged the pattern and suggested a health and resiliency review of the database read path. I took on the investigation, which affected all 15 Viva Engage teams, about 150 engineers.

**Actions**

I treated FaultLine's suggestion as a lead to verify, not a conclusion, and worked layer by layer instead of guessing. I traced the full read path and tested each layer separately: the client application, the connection pooler and the read replicas. I instrumented latency and errors per node, and that isolated one replica with severe disk I/O stalls. Then I found the real root cause: the pooler's TCP health check verified connectivity but not query execution, so it kept sending traffic to the degraded replica. I replaced that shallow check with synthetic queries and added circuit breaking to take unhealthy nodes out of rotation.

**Results**

The intermittent read micro-outages stopped and read availability reached 99.999%. I also removed a silent failure mode across the database fleet. The deeper health-check and node-ejection approach became an organization-wide operational template.

**Learnings**

I learned not to equate a successful connection with a healthy service. In distributed-system investigations, I map boundaries, test hypotheses with telemetry, and check the behavior customers depend on instead of relying only on aggregate dashboards.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| L | L | L | L | M |

**Signals shown:** Ownership, Ambiguity, Perseverance, Growth, Leadership

---

### 5. IRIS: Autonomous AI Incident Remediation

**Context**

I saw infrastructure engineers spending more and more time on repetitive service requests and manual incident triage. That on-call toil pulled senior engineers away from platform work, and context switching slowed responses during critical incidents. I conceived and led IRIS, with a team of 10 to 15 engineers, and it supports all 15 Viva Engage teams, about 150 engineers.

**Actions**

IRIS is a multi-agent AI system for infrastructure triage and remediation, and I worked on three parts: the design, the safety and the governance. For the design, I built a conversational framework that coordinates specialized agents to inspect telemetry, consult runbooks, and propose or execute actions through secure APIs. For safety, I added a two-stage verification pipeline that uses retrieved ground-truth information and engineer feedback to reduce hallucination risk. For governance, I partnered with Trust and Security leadership on permission boundaries and blast-radius controls for production actions, because existing enterprise policy didn't yet cover this use case.

**Results**

IRIS autonomously resolved about 30% of infrastructure service requests. Triage latency for recurring incidents fell by 45%, which freed hundreds of engineering hours each month for higher-value platform work. The Infrastructure team owns IRIS today.

**Learnings**

I learned that production AI automation is as much a safety and governance challenge as a technical one. I earn trust through explicit permission scoping, verifiable outputs and appropriate human-in-the-loop controls.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| L | L | XL | L | L |

**Signals shown:** Ownership, Ambiguity, Growth, Communication, Leadership

---

### 6. Maestro: Multi-Agent SDLC Platform Adoption

**Context**

Maestro, a multi-agent SDLC platform, grew out of a hackathon concept. It could automate development tasks, but teams had different workflows and stacks, and many engineers were skeptical of AI automation. The adoption goal was 15 teams, roughly 150 engineers, and I led the cross-org adoption with 10 to 15 engineers.

**Actions**

I worked on three things: listening, reshaping the product and making adoption self-service. I started by partnering with team leads to understand their workflow friction, and I realized the skeptics weren't rejecting the idea, they were rejecting disruption. So I refined Maestro into modular plug-ins that fit existing CI/CD pipelines, so teams could adopt it piece by piece. To make adoption self-service, I created reference architectures, automated setup scripts and self-service documentation. I also ran office hours and biweekly feedback forums, and I worked with early adopters so peers could address concerns and show practical benefits.

**Results**

I onboarded 10 teams, more than 100 engineers, and the remaining teams entered active evaluation. Adopted services automated tasks such as code scaffolding, dependency management and release validation, and saw about a 25% reduction in cycle time. The Infrastructure team owns Maestro today. Next, I'm driving full adoption across all Viva Engage teams and pitching it up for adoption across other M365 teams, and the Teams team has already started dogfooding it.

**Learnings**

I learned that platform adoption starts with understanding developers' needs, not asking them to change for the platform's sake. Modular integration, low-friction onboarding and ongoing feedback turned skepticism into adoption. Executive sponsorship mattered, but it didn't replace hands-on developer support.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| L | L | L | M | L |

**Signals shown:** Ownership, Ambiguity, Perseverance, Growth, Communication, Leadership

---

### 7. Homefeed vs Rankie failure

**Context**

I investigated a production issue where a failure in Rankie, the ranking service, also took down the home feed, so users saw errors on the main surface. The trade-off was between ranked-feed quality and keeping a basic feed available when ranking was down.

**Actions**

I proposed a fail-open design: if Rankie is unavailable, the home feed returns a basic feed instead of failing. The service team pushed back because ranking quality directly affects the customer experience. When I dug into why, I realized the disagreement came from different assumptions: I was optimizing for availability, and they were optimizing for quality. So I explained the availability trade-off over several discussions and helped bring the product team into the decision, so that it rested on customer impact and not engineering opinion.

**Results**

The fallback-feed work went into the backlog. Rankie failures were infrequent, and building a backup feed required significant effort. My design wasn't adopted at that time. I disagreed, made my case, and then committed to the decision.

**Learnings**

I learned that a technically sound resiliency proposal isn't automatically the highest-priority investment. Now I bring failure frequency, customer impact and implementation cost to the first conversation, and I recognize when a different prioritization is reasonable.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| S | S | M | M | M |

**Signals shown:** Ownership, Ambiguity, Perseverance, Conflict Resolution, Growth, Communication

---

### 8. Kafka consumer retries

**Context**

VentSpout reads Kafka events, sends them to consumer services, and waits for a successful HTTP response. During downstream outages or network partitions, repeated delivery attempts saturated VentSpout's resources. I was reviewing the reliability fix.

**Actions**

A teammate proposed replacing constant-delay retries with exponential backoff. While reviewing his pull request, I noticed that retries could still synchronize across consumers. So I recommended adding jitter, meaning random variation in retry delays, so failed requests wouldn't all retry at once and create another burst of load. I framed it as building on his proposal.

**Results**

After jitter was added, VentSpout had fewer resource-starvation problems, because retry attempts were spread over time instead of arriving in synchronized bursts.

**Learnings**

I learned to use code reviews to examine system behavior under failure, not just whether the implementation is correct. Asking whether exponential backoff was sufficient led me to a small change that made the retry strategy more resilient.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| S | M | M | M | S |

**Signals shown:** Ownership, Ambiguity, Growth, Communication

---

### 9. Embeddings on seperate cluster

**Context**

I was helping provide infrastructure for the search team's embeddings workload on a shared platform, which had real run-cost and reliability consequences across teams. The decision was whether to use the existing search clusters or create separate ones, balancing cost and operational overhead against workload isolation.

**Actions**

I advocated for the existing clusters to control COGS and avoid maintaining more clusters. My manager preferred separate clusters to reduce noisy-neighbor risk, and I disagreed with him directly. But I took his concern seriously, because embeddings traffic could hurt search latency for everyone. I brought cost and maintenance data so the discussion stayed on facts, and I reframed the question around the real goals: cost, operational complexity and isolation.

**Results**

The final design hosts embeddings on the existing search clusters, in dedicated node pools, with an embeddings kill switch. It addresses the isolation concern without a fully separate set of clusters, and my manager and I both owned the result.

**Learnings**

I learned to look beyond the either-or framing of a disagreement. Focusing on the underlying concerns of cost, operational complexity and isolation helped me find a middle ground. In hindsight, I'd propose node pools plus a kill switch in my first pass.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| M | M | M | M | M |

**Signals shown:** Ownership, Ambiguity, Conflict Resolution, Growth, Communication

---

### 10. HDFS retirement vs CosmosDB cost

**Context**

A Hadoop-based metadata system required specialized Hadoop expertise to run. I proposed retiring it and moving the workload to Azure Cosmos DB, to cut that maintenance burden.

**Actions**

A colleague challenged my proposal, arguing that Cosmos DB would be expensive and might not scale. I took that seriously and ran a proof of concept. I presented the results on scalability and explained the operational benefits of a managed service over a system that depended on Hadoop specialists. Then I led the migration of the metadata workload to Cosmos DB and retired the Hadoop ecosystem.

**Results**

Cosmos DB met the scaling needs, but the cost outcome was bad: COGS reached nearly 10 times the previous Hadoop operating cost, because the original discounts ended and pricing changed. I won the technical argument and missed on cost.

**Learnings**

I learned that proving scalability doesn't establish long-term viability. I now model several years of costs, including growth, discount expiry and pricing-change scenarios, and I give cost objections the same rigor as technical ones. I applied this on search modernization, where I deliberately accepted the engineering cost of the Elasticsearch fork with the numbers modeled up front.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| S | M | M | M | M |

**Signals shown:** Ownership, Ambiguity, Conflict Resolution, Growth, Communication

---

### 11. AI suggestion of kafka offset commit change

**Context**

I was working on a Kafka broker saturation issue. FaultLine, the AI SRE sidecar I built, noticed that the system committed offsets after every event and suggested batching commits to reduce broker load. FaultLine is designed to recommend only and leave the decision to a human, which made me the approval gate.

**Actions**

It sounded right, so I implemented the FaultLine-recommended change and batched the offset commits instead of committing after each event. I validated the local logic, but I didn't validate the downstream assumptions. Service teams soon got alerts for high lag and elevated HTTP 5xx errors from delayed offset commits, and I reverted my pull request right away.

**Results**

I backed out the change. It was my mistake: I shipped an optimization that was right in isolation but wrong in the system.

**Learnings**

I learned to treat AI recommendations, including those from a tool I built, as hypotheses, not validated solutions. Human approval only protects production if the approver validates the downstream impact. Before applying a similar change, I validate downstream assumptions, test end to end, and define rollout and rollback criteria. I've applied this to the agentic work I lead: IRIS has a two-stage verification pipeline and permission boundaries.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| S | S | M | M | S |

**Signals shown:** Ownership, Growth

---

### 12. FaultLine: Autonomous SRE Sidecar

**Context**

Investigating incidents and performance problems across our services meant manually correlating Kusto logs, Grafana metrics and runbooks, and slow or sustained inefficiencies often went unnoticed because nothing had spiked or failed outright. I designed and built FaultLine, an autonomous SRE sidecar prototype that investigates anomalies and recommends fixes, but never applies remediation without human approval. The goal was faster, evidence-based triage that engineers could trust.

**Actions**

I worked on four parts: detection, correlation, grounded recommendations and safety.

For detection, I covered three categories of findings: functional anomalies such as failed workflows and violations of explicitly configured business rules, non-functional anomalies such as latency spikes, error-rate increases, resource saturation and SLO violations, and sustained performance opportunities such as slow queries, excessive retries and low cache hit rates. I used service-specific baselines and configurable thresholds with online rolling Z-score and EWMA calculations. FaultLine evaluates functional correctness only against supplied rules, so it doesn't invent business requirements.

For correlation, I streamed raw logs through drain3 into templates and tracked per-service template frequency in a 60-second sliding window. I correlated metric spikes of at least 3.0 sigma with log-template frequency increases of at least 300% within plus or minus 60 seconds, within a service first and then across services using trace IDs or configured dependencies. Functional-rule violations and sustained performance findings don't require a simultaneous metric and log burst. I deduplicated repeated findings and labeled each with category, severity and affected services.

For grounded recommendations, I retrieved the top two relevant local runbook snippets for each finding using vector search, then used Azure OpenAI to generate a structured incident brief: evidence, root-cause hypothesis, confidence, remediation, expected impact, validation steps, rollback steps and a proposed diff. I kept observed evidence, hypotheses and estimated improvement separate. Logs and runbooks were treated as untrusted data, not instructions, and diffs were repository-specific only when source context was supplied.

For safety and integration, I made collection read-only against the existing Kusto and Grafana sources, made annotation writes separately configurable and permission-scoped, and used least-privilege, environment-based authentication. I also built a credential-free mock mode, clearly labeled so mocked calls are never reported as real successes, and a traffic simulator for database-pool exhaustion, a functional workflow failure and sustained degradation. A failure in an integration never interrupts telemetry ingestion.

One finding was that Grouper, Mugshot and Directory were spending most of their CPU time on RSA operations for service-to-service URL signing, with significant performance issues in Grouper. FaultLine suggested HMAC-SHA256 as an alternative to evaluate. I benchmarked it against the existing RSA approach and, in my test, it was about 500 times faster. But the team was worried about the production risk of changing the signing mechanism in AFD, and I took that concern seriously.

**Results**

FaultLine is a prototype that I demonstrated end to end in mock mode, and the real Kusto and Grafana integrations depend on access to the verified endpoint, schema and datasource settings, which I couldn't assume. Its suggestions led to three outcomes, and each one taught me something different:

- **RSA signing hotspot (this story):** FaultLine surfaced the CPU cost of RSA signing in Grouper, Mugshot and Directory. The team kept RSA and introduced caching instead, which improved performance without changing the signing mechanism. The HMAC alternative wasn't deployed, so the roughly 500x improvement is a benchmark result, not a production outcome.
- **Database Health Check (story 4):** FaultLine flagged the intermittent read failures and suggested a read-path review. I verified it with per-node telemetry, found the degraded replica and the shallow pooler health check, and replaced it with synthetic queries and circuit breaking. Read availability reached 99.999%, and the approach became an org-wide operational template.
- **Kafka offset commit (story 11):** FaultLine suggested batching offset commits to reduce broker saturation. I applied it without validating downstream assumptions, service teams got lag and HTTP 5xx alerts, and I reverted the change right away. It showed that human approval only protects production if the approver validates the downstream impact.


**Learnings**

I learned that a strong benchmark alone doesn't justify a security-sensitive production change, and that an AI-assisted tool earns trust through explicit evidence, human approval and honest limits such as false positives and incomplete telemetry. Caching was a pragmatic improvement even though it differed from the option I evaluated. Next time, I'd pair performance evidence with security and compatibility validation, a staged rollout and clear rollback criteria, to help the team weigh the trade-off.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| S | S | L | L | S |

**Signals shown:** Ownership, Ambiguity, Growth, Communication

---

### 13. Search Compute Capacity Conflict

**Context**

The search team asked me to scale the Elasticsearch nodes substantially, with more GPU and memory, because they were running many experiments with the latest search models at production scale. Azure had a capacity crunch, so I had to allocate compute wisely. At the same time, the Copilot integration rollout depended on that search work, and the added compute was increasing the COGS budget.

**Actions**

I disagreed with simply provisioning more, and I drove the resolution in four steps.

1. **I pushed back and asked for efficiency and evidence.** I asked the search team's tech lead to improve the search model, which had a very large query fan-out, so it needed less compute, and to run his experiments in pre-prod to get benchmarks before rolling out to prod.
2. **I took his constraints seriously.** He replied that they had no pre-prod environment at production scale and that optimizing the models wasn't feasible in the short term. That was a legitimate limit, so I stopped pressing for it, but I also couldn't approve open-ended compute. We didn't resolve it, and he raised it to the leadership team because the Copilot integration rollout was getting delayed. With the COGS increase, it reached the VP level.
3. **I engaged the leadership team with the trade-off.** I presented the competing constraints directly: scarce Azure capacity, rising COGS and the Copilot timeline. We agreed to roll out the experiments to fewer users until the models improved enough to need less compute.
4. **I raised the option that created headroom.** I proposed moving non-SLA workloads to a different cluster to free up compute in the meantime. The tech lead agreed, and I carried it forward.

**Results**

The non-SLA workload move freed up about 30% of capacity, and the limited rollout let the experiments continue within it. My pre-prod benchmarking request wasn't adopted, because a production-scale pre-prod environment didn't exist.

The change that lasted was a regular sync between the search team and me on progress improving search model efficiency. It turned a disagreement over compute into a shared, recurring commitment to make the models need less, and it kept that commitment visible instead of letting it depend on a one-off escalation.

**Learnings**

I learned that when two legitimate priorities collide, an option that creates headroom, like moving non-SLA workloads, gives leaders and the other team something to agree on, and that a recurring sync keeps an agreement from fading. I also learned to check that my ask is feasible, since a prod-scale pre-prod environment didn't exist.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| L | M | L | M | L |

**Signals shown:** Ownership, Ambiguity, Conflict Resolution, Growth, Communication, Leadership

---

## Answer Framework

Each answer is built for what interviewers score:

- **Target the signal.** Pause, work out what the question tests (Ownership, Perseverance, Conflict Resolution, Ambiguity, Leadership, Growth), then pick the story.
- **Actions are the center.** Name specific actions: designing, aligning, communicating, implementing, iterating, analyzing. If 30 seconds pass with no action, cut context.
- **Context is about 10%.** Only the stakes and what makes the actions understandable.
- **Replace "we" with what I did.** Credit others by name, but be specific about my contribution. Avoid passive phrasing like "I was assigned."
- **Open with a roadmap for bigger stories.** "I contributed in three ways..." Then pause for questions.
- **Name the framework.** At senior levels, say how I decided: the criteria, the trade-offs, the reversibility test.
- **Be honest about imperfections.** Include what was hard, what I got wrong and what I would change.
- **Quantify beyond myself.** Baseline-to-result metrics, and the effect on other engineers, teams and customers.
- **Steer the interview.** Drop breadcrumbs in the TMAY and offer a menu of examples.
- **Close with a learning that changed my behavior,** ideally with a later example of applying it.
- **Practice out loud.** Aim for about 2 to 3 minutes per story, with no filler and no backtracking.

## Story Selection by Level

Lead with these for a Principal / Sr. Staff loop, since they have org-wide scope and measurable impact:

- **Flagship:** Secret Scanner, Search modernization (Elasticsearch fork), IRIS, Maestro, Postgres & OS upgrade.
- **Supporting (deep technical diagnosis):** Database Health Check; FaultLine for AI-assisted SRE design (a prototype, so state its status honestly).
- **Growth or failure examples only, not main answers:** Cosmos DB cost miss, Kafka offset revert, Rankie, Embeddings, VentSpout jitter. Their own scope ratings are S/M, so use each once.

## Gaps to Fill (real details only)

These are the gaps that make the answers read below Principal level. Fill each with a true detail. Don't guess. Q3, Q5, Q6, Q9, Q11, Q12, Q13, Q14, Q16 and Q19 contain DRAFT text, and Q1, Q2, Q10, Q17, Q18 and Q21 contain bracketed scale, baseline and ownership lines. Replace each [bracket] with a true detail, or revert or delete it.

- **Scale:** Viva Engage users or request volume, number of services and clusters, customers affected.
- **Baselines:** outages per year before Secret Scanner, IRIS requests per month, what the 40% incident drop was measured against, refund exposure avoided in the Postgres upgrade.
- **Leading through others:** team size on each initiative, who built what, how you grew others, who owns it after launch.
- **Org-level influence:** the roadmap or vision you set, the leaders you aligned (titles) and the orgs involved.
- **Senior-level conflict:** one real disagreement with a partner org or senior leader that ended win-win (to replace Embeddings and Rankie as the main conflict answers).
- **Mentoring seniors:** Q11 now uses a real example (coaching a staff engineer to 100% alt_pool adoption); add the supporting numbers. One more real example is still needed for Q3 and Q12.
- **Recency:** a date for each story. Prefer the last 0 to 3 years.
- **After launch:** whether each project still runs, was expanded or was handed off.

## Questions & Answers

Index:

1. Tell me about yourself (TMAY)
2. Tell me about your favorite project / most impactful project / a time you solved an ambiguous problem
3. Tell me about a time when you had to address underperformance in your team
4. Tell me about a conflict you had at work / Discuss a time when you had conflicting perspectives with teammates and how you handled it / Tell me about a time you had a conflict with a coworker. How did you resolve it?
5. How do you prioritize fixing a serious bug with complaining users when you are transitioning to a new project in a few days?
6. Describe advocating for a team mate to help them fit in at work / Describe changing a colleague's opinion from negative to positive
7. Tell me about a time you handled a disagreement that arose from differences in assumptions
8. How do you manage multiple priorities, do you like to be in a place where priorities keep changing or prefer doing the same thing repeatedly?
9. You are organizing an off-site and a final venue is decided by majority vote, but some people who voted for other options say they won't join. How would you resolve this conflict?
10. How do you accommodate new requirements that arise mid-task while still sticking to your original timelines? / Tell me about a time you had to pivot mid-project. / Tell me about a project where the requirements were not clear or kept changing
11. Tell me how you helped someone in your team to get better at some task / Describe a situation where a team member was struggling and what you learned from it
12. Describe going above and beyond to help someone
13. Tell me about a time when you had to make a trade-off between two competing priorities or options / Tell me about a time when you had to make tradeoffs between quality and cost
14. Describe one thing you have learned recently
15. What would you like to have improved about your last role? / What would you like to see in your next manager?
16. How would you handle a situation where one team member takes all the credit for a group project?
17. Tell about a time when you had to go against the norm and push for a change / Tell me about a time when you made an unpopular decision
18. Tell me about a problem you had to solve that required in-depth thought and analysis
19. What have you done to develop your leadership skills?
20. Give me an example of a tough or critical piece of feedback you received
21. Give me an example of when you had to make an important decision and had to decide between moving forward or gathering more information
22. What are you trying to improve most (professionally)

### 1. Tell me about yourself (TMAY)

**Answer**

I build the infrastructure that lets about 150 engineers across 15 teams move faster without breaking things. I'm a Senior Principal Software Engineer on the Viva Engage infrastructure team at Microsoft, with 18 years of experience in distributed systems. I set technical direction for platforms that many teams depend on, and I bring about 150 engineers along with it. When so much is high priority, I scale myself by delegating to staff and senior engineers. I focus on reliability, cost efficiency and developer productivity. Viva Engage serves 250 million daily active users across 15 services.

A few examples. I led Secret Scanner, a central credential discovery and rotation platform. It reached 100% adoption across all 15 Viva Engage teams, about 150 engineers, with zero certificate or secret-related outages. I drove our search modernization: I pushed us to fork Elasticsearch and run it on AKS, which cut provisioning and patching from days to under 15 minutes and saved more than $10M a year. I conceived IRIS, a multi-agent system that resolves about 30% of infrastructure requests on its own and cut triage latency by 45%. And I lead Maestro, an SDLC platform that more than 100 engineers across 10 teams now use. I also led the Postgres and OS upgrade across about 40 production clusters, which involved a lot of cross-org alignment.

Each one removed a systemic problem for many teams at once. I want to apply that to consumer-scale infrastructure and agentic AI for operations, where the leverage is even larger.

**Follow-up 1**

> Q: Why do you say you've spent 18 years on distributed systems, and what ties your three examples together?
> A: Each one removed a systemic problem for many teams at once: Secret Scanner for credential outages, the Elasticsearch fork for cost and toil, and IRIS for repetitive requests. The common thread is reliability, cost and developer productivity at org scale.

**Follow-up 2**

> Q: How do you bring 100+ engineers along without formal authority?
> A: I make adoption easy and let results speak. With Maestro I built plug-ins, docs and office hours, and 10 teams, more than 100 engineers, came on board.

**Follow-up 3**

> Q: Which of the three examples was hardest?
> A: IRIS, because trust in autonomous actions has to be earned. I partnered with Trust and Security leadership on permission boundaries and blast-radius controls. It now resolves about 30% of requests on its own and cut triage latency by 45%.

**Follow-up 4**

> Q: Why consumer-scale infrastructure and agentic AI for operations next?
> A: The leverage across organizations is larger there, and it extends what I built with IRIS and Maestro. I'd tailor this part to each company.

---

### 2. Tell me about your favorite project / most impactful project / a time you solved an ambiguous problem

**Answer**

My favorite project is the PostgreSQL and Ubuntu upgrade, because I owned it end to end across about 40 production clusters, and the path wasn't defined when I started.

The clusters ran legacy PostgreSQL 9.6 on Ubuntu with critical CVEs open and Microsoft's Trust requirements unmet. PostgreSQL 9.6 has no native logical replication, so a standard upgrade meant substantial downtime and customer-refund risk. Breaking changes also affected multiple Java and infrastructure services, and the work touched all 15 Viva Engage teams, about 150 engineers. Viva Engage serves 250 million daily active users across 15 services. I led 10 to 15 engineers.

The ambiguity was real. There was no proven path for this version jump at this scale, and the 15 service teams didn't know how to certify their service afterward, because their unit and integration tests didn't cover everything and end-to-end tests were risky. I contributed in three ways: the migration design, the rollout, and certification with stakeholder alignment, which was the hardest part.

On the migration design, I used a two-phase approach. I used pg_upgrade to move PostgreSQL from 9.6 to 18.6, with feature flags so the Java and infrastructure services stayed compatible across both versions without deployment locks, and dynamic maintenance banners to keep customers informed. For the OS, I ruled out an in-place Ubuntu upgrade because of the Ubuntu 18.04 libc index-invalidation issue, and used native logical replication to a mirrored Ubuntu cluster for a short cutover.

On the rollout, because the PostgreSQL upgrade averaged about one hour of downtime per cluster, I grouped the clusters into non-SLA and SLA cohorts in separate windows. I upgraded the non-SLA clusters first with enough bake time, then the SLA clusters.

On certification and alignment, I narrowed the question for the service teams. Instead of proving every scenario, they identified their core SLA test scenarios and certified those. My rule was to roll back if a core SLA scenario failed, otherwise fix forward. I also wrote a comprehensive rollback plan and aligned executives and stakeholders across organizations, so a VP-level audience had confidence in a plan with broad production impact. My first presentation to the VP and senior leaders was too technical, because they needed to decide whether to upgrade. So I reframed it around the decision and the risk.

Two other moments show ownership. The UI only had a generic outage banner, and customers needed a specific message with the maintenance time. The front-end team was busy, so I made the change myself with AI help, and they now have a reusable custom template. Then on the Saturday production upgrade, Azure had intermittent VM provisioning issues from its own maintenance. Several tech leads wanted to abort. I proposed continuing on the minimum nodes, since weekend traffic is lower, and provisioning full capacity once the Azure SDKs were stable, which happened that night.

The result: all 40 or so clusters and every deployment stamp completed, about one hour of PostgreSQL downtime per cluster and a roughly five-minute OS cutover. Incidents involving replication lag, kernel panics and I/O saturation fell by 40%, and the upgrades secured the Trust and security clearance needed for Microsoft 365 integrations, including Teams and Copilot. The Infrastructure team owns the Postgres tooling today.

What I learned is that a sound migration design isn't enough for a high-risk upgrade. Rollback planning, early executive alignment and a bounded, achievable definition of working for each team matter as much as the technology.

**Follow-up 1**

> Q: Why was certification the hardest part?
> A: The 15 service teams couldn't say how to prove their service worked after the upgrade. Their unit and integration tests had gaps and end-to-end tests were risky, so I asked each team to certify only its core SLA scenarios, with a roll-back-or-fix-forward rule.

**Follow-up 2**

> Q: Why that migration design?
> A: PostgreSQL 9.6 has no native logical replication, and an in-place Ubuntu 18.04 upgrade would have hit the libc index-invalidation issue. So I used pg_upgrade for the database, and native logical replication to a mirrored Ubuntu cluster for the OS, which kept the cutover short.

**Follow-up 3**

> Q: What would you do differently?
> A: I'd involve the service teams in defining their core SLA scenarios earlier, since certification was the hardest part. I'd also give the VP and senior leaders a decision-first summary from the start, since my first presentation was too technical.

**Follow-up 3b**

> Q: What happened on the production night?
> A: Azure had intermittent VM provisioning issues from its own maintenance, even though we had procured capacity. In the go-or-abort call with senior leaders, some tech leads asked to abort. I proposed continuing on the minimum nodes, because weekend customer traffic is lower, and provisioning full capacity once the Azure SDKs were stable. We did, and we had full capacity that Saturday night.

**Follow-up 4**

> Q: How do you know it worked?
> A: All 40 or so clusters and every deployment stamp were upgraded, with about one hour of PostgreSQL downtime per cluster and a roughly five-minute OS cutover. Incidents involving replication lag, kernel panics and I/O saturation fell by 40%.

---

### 3. Tell me about a time when you had to address underperformance in your team

**Answer**

During [the Postgres and OS upgrade], an engineer on one of the service teams owned [the Java compatibility workstream] and kept missing commitments, and [some of their work needed rework]. That put the multi-team schedule and the Trust deadline at risk, so I acted early.

I met them one-on-one before assuming a performance problem. The scope was ambiguous and they were hesitant to raise blockers, so this looked like a clarity problem, not a capability problem.

I made three changes. I broke the workstream into milestones with clear acceptance criteria. I paired with them on the first milestone. And I set weekly check-ins with specific feedback, while being direct that the expectations were non-negotiable. Clarity didn't mean lowering the bar.

Within [about two months] they were delivering independently and [owned a larger piece of the migration]. The schedule risk went away. [Imperfection: what slipped before it improved.]

I also fixed it for the wider team. When one person struggles with ambiguity, others usually do too, so I now write acceptance criteria into the design docs I set.

What I learned is to fix clarity and feedback first, and if that doesn't work, to escalate early with a documented plan instead of letting it drift. [In this case I [did or didn't] need to escalate.]

**Follow-up 1**

> Q: How did you know it was a clarity problem and not a capability problem?
> A: I met them one-on-one before assuming anything, and I asked where they were stuck instead of why things were late. The signals were that the scope was ambiguous and they were hesitant to raise blockers. Neither points to low skill. I treated it as a hypothesis and let the milestones and pairing test it. If those hadn't helped, I would have changed my read. [What you actually saw that confirmed it.]

**Follow-up 2**

> Q: How did you stay candid without demoralizing them?
> A: I kept the feedback about concrete work against agreed acceptance criteria, not about them as a person, and I gave it every week so nothing came as a surprise. Pairing on the first milestone showed them what good looked like and that I was invested in their success. I was also direct that the expectations were non-negotiable. Clarity didn't mean lowering the bar, and support plus a firm bar is what kept it from feeling like a punishment.

**Follow-up 3**

> Q: What did you change for the wider team?
> A: When one person struggles with ambiguity, others usually do too, they just hide it better. So I now write acceptance criteria into the design docs I set. That fixes the cause for everyone instead of coaching one person at a time, and the next engineer doesn't have to hit the same wall.

**Follow-up 4**

> Q: What if it hadn't improved?
> A: I'd escalate early with a documented plan instead of letting it drift: what we agreed, which milestones slipped, and what support I'd already given. That way the manager and the engineer aren't surprised, and the multi-team schedule and the Trust deadline aren't left to chance while I wait. [Your true timeline for when you would have.]

---

### 4. Tell me about a conflict you had at work / Discuss a time when you had conflicting perspectives with teammates and how you handled it / Tell me about a time you had a conflict with a coworker. How did you resolve it?

**Answer**

I have three conflict examples: one with the search team's tech lead on compute capacity, one with my manager on embeddings, and one with a service team on Homefeed and Rankie. I'll start with the search compute one.

The search team asked me to scale the Elasticsearch nodes substantially, with more GPU and memory, because they were running many experiments with the latest search models at production scale. Azure had a capacity crunch, so I had to allocate compute wisely. Meanwhile the Copilot integration rollout depended on that work, and the extra compute was increasing the COGS budget.

I disagreed with simply provisioning more, and I drove the resolution in four steps. First, I pushed back directly with the search team's tech lead: I asked him to improve the search model, which had a very large query fan-out, so it needed less compute, and to run his experiments in pre-prod to get benchmarks before rolling out to prod. Second, I took his answer seriously: they had no pre-prod environment at production scale, and optimizing the models wasn't feasible in the short term. We didn't resolve it, and he raised it to the leadership team because the Copilot rollout was getting delayed. With the COGS increase, it reached the VP level. Third, I engaged the leadership team with the trade-off directly: scarce Azure capacity, rising COGS and the Copilot timeline. We agreed to roll out the experiments to fewer users until the models improved enough to need less compute. Fourth, I raised the option that created headroom: moving non-SLA workloads to a different cluster. The tech lead agreed, and I carried it forward.

The move freed up about 30% of capacity, and the limited rollout let the experiments continue within it. My pre-prod benchmarking request wasn't adopted, since a production-scale pre-prod environment didn't exist, and I accepted that. What lasted was a regular sync between the search team and me on progress improving search model efficiency, which turned a compute dispute into a shared, recurring commitment.

What I learned is that when two legitimate priorities collide, an option that creates headroom gives leaders and the other team something to agree on, and a recurring sync keeps the agreement from fading. I also learned to check that my ask is feasible.

**Follow-up 1**

> Q: Why did you disagree with just adding compute?
> A: Azure had a capacity crunch and the added compute was increasing COGS. I wanted the model to need less compute, and benchmarks before prod rollout.

**Follow-up 2**

> Q: What was his concern, and how did you treat it?
> A: He had no prod-scale pre-prod environment and thought optimizing the models wasn't feasible, while the Copilot integration rollout was being delayed. I treated those as legitimate, which is why I stopped pressing for pre-prod benchmarks and raised an option that created capacity instead.

**Follow-up 3**

> Q: How did you reach the resolution, and who proposed what?
> A: It reached the VP level because of the Copilot delay and COGS. I engaged the leadership team with the trade-off, and we agreed to roll out the experiments to fewer users until the models need less compute. I raised moving non-SLA workloads to a different cluster, the tech lead agreed, and it freed up about 30% of capacity.

**Follow-up 4**

> Q: What changed afterward, and what would you do differently?
> A: We held a regular sync on progress improving search model efficiency, so the agreement didn't depend on one escalation. I'd also check the feasibility of my ask earlier and raise the capacity option sooner.

---

### 5. How do you prioritize fixing a serious bug with complaining users when you are transitioning to a new project in a few days?

**Answer**

The bug comes first, because customer pain doesn't wait for my transition date. I'll walk through my approach with a real example.

My approach has three parts. First, I assess severity and blast radius, tell the affected users we're on it, and mitigate fast with a rollback, feature flag or workaround. Second, I find and fix the root cause instead of patching. Third, if I can't fully close it, I hand it off explicitly: written root-cause findings, repro steps, telemetry links, remaining work, and a named owner who has agreed to take it.

The real example is the Database Health Check. [I was about to move to [next project, such as IRIS] when] tier-1 services had intermittent read failures that customers felt as brief outages, while every dashboard looked healthy. [I told my manager and the incoming project's lead right away that my transition date might move.]

[I told the affected teams we were on it and removed the suspect replica from rotation as a temporary mitigation.] Then I traced the read path, instrumented per-node latency, and found a replica with severe disk I/O stalls and a pooler health check that verified only connectivity. I replaced it with synthetic queries and circuit breaking, and [handed the runbook and ownership to [team]].

Read availability reached 99.999%, and the approach became an org-wide operational template. [My transition moved by [N] weeks.] [Imperfection: what I'd do differently.]

What I learned is that the customer's problem, not my calendar, defines when the work is done.

**Follow-up 1**

> Q: How do you decide between rollback and a workaround?
> A: I pick whichever gives users relief fastest with the least new risk. If a recent change caused it and rolling back is safe, I roll back. If I can switch off the affected path with a feature flag, I do that without a redeploy. If neither is possible, I use a workaround. Mitigation only buys time, so the root-cause fix runs on its own timeline. On the Database Health Check, [removing the suspect replica from rotation was the mitigation].

**Follow-up 2**

> Q: What if you can't finish the fix before you move?
> A: I hand it off explicitly: written root-cause findings, repro steps, telemetry links, remaining work, and a named owner who has agreed to take it. Agreed matters, because a document with an assigned owner who hasn't accepted it is an abandoned bug. I'd also walk the owner through it live instead of just sending the doc.

**Follow-up 3**

> Q: Who do you tell, and when?
> A: My manager and the incoming project's lead, early. A transition date is a plan, not a promise, and if the bug is serious the date may need to move. Telling them early lets them adjust, and telling them late forces a bad trade-off. I also tell the affected teams we're on it, and I stay reachable during the first week. [What you actually did.]

**Follow-up 4**

> Q: Have you done this for real?
> A: Yes, on the Database Health Check. I traced the read path, instrumented per-node latency, found two failure modes, and replaced the connectivity-only health check with synthetic queries and circuit breaking. [The transition detail.] I stayed until I had eliminated the failure mode, and read availability reached 99.999%.

---

### 6. Describe advocating for a team mate to help them fit in at work / Describe changing a colleague's opinion from negative to positive

**Answer**

I have two examples. The first is advocacy. [An engineer, [name or role], who joined from another team, was quiet in design reviews, and some senior people read that as lack of depth.] I knew their work on [IRIS's verification pipeline] was strong, so I had them present the design, credited their ideas by name in cross-org forums, and coached them privately on framing trade-offs. [Within a few months, other teams pulled them into their reviews.]

The second, changing opinions at scale, is Maestro, the multi-agent SDLC platform I lead. Many engineers across teams were skeptical of AI automation, and a mandate wouldn't have worked.

I took three steps. First, I listened to team leads about their workflow friction. The skeptics weren't rejecting the idea, they were rejecting disruption. Second, I rebuilt Maestro as modular plug-ins that fit into their existing CI/CD pipelines, so teams could adopt it piece by piece. Third, I tailored the message: fit with their pipelines for team leads, reference architectures, setup scripts and docs for engineers, and office hours and biweekly feedback forums with early adopters so skeptics heard from peers.

Ten teams, more than 100 engineers, adopted it, with about a 25% cycle-time reduction for adopted services.

What I learned is that skeptics change their minds when you solve their real problem and let them see results.

**Follow-up 1**

> Q: How did you advocate for the quieter engineer?
> A: The problem was perception, not skill: being quiet in design reviews was being read as lack of depth. I knew their work was strong, so I gave it a stage. I had them present the design, I credited their ideas by name in cross-org forums so the credit attached to them and not to me, and I coached them privately on framing trade-offs, because part of the issue was how to enter a debate. [What you actually did.]

**Follow-up 2**

> Q: How did you win over Maestro skeptics?
> A: I found that they weren't rejecting automation, they were rejecting disruption to their workflows. So I listened to team leads about their friction first, then rebuilt Maestro as modular plug-ins that fit their existing CI/CD pipelines. Teams could adopt it piece by piece instead of all or nothing. A mandate wouldn't have worked on this audience.

**Follow-up 3**

> Q: What made peers trust it?
> A: I tailored the message to the audience: fit with their pipelines for team leads, and reference architectures, setup scripts and docs for engineers. Then I ran office hours and biweekly feedback forums with early adopters, so skeptics heard from peers who were actually using it, not from me. 10 teams and 100+ engineers adopted it, with about a 25% cycle-time reduction for adopted services.

**Follow-up 4**

> Q: What did you learn?
> A: To find the objection under the objection before arguing the benefits. With Maestro it was disruption, not AI. Skeptics change their minds when you solve their real problem and let them see results. For advocacy, I learned to make someone's work visible instead of vouching for them in the abstract.

---

### 7. Tell me about a time you handled a disagreement that arose from differences in assumptions

**Answer**

This was a disagreement about Homefeed and Rankie. Rankie is the ranking service behind the home feed. When it failed, the home feed failed with it, so users saw errors on the main surface.

I proposed a fail-open design: if Rankie is down, return a basic feed. The service team disagreed. I dug into why, and the disagreement came down to different assumptions. They assumed ranked quality is the core experience, so a degraded feed might be worse than none. I was optimizing for availability, and they were optimizing for quality.

I took three steps. I made those assumptions explicit and walked through the availability trade-off over several conversations. I brought in the product team so the decision rested on customer impact, not engineering opinion. And I weighed failure frequency against the cost of building a backup feed.

The fallback-feed work went to the backlog, since Rankie failures were infrequent and a backup feed was costly. My design wasn't adopted at that point. I disagreed, made my case with data, and then committed fully, and I think it was a reasonable call.

What I learned is to name assumptions early and to bring failure frequency, impact and cost data to the very first conversation.

**Follow-up 1**

> Q: Why did you propose fail-open?
> A: When Rankie failed, the home feed failed with it, and users saw errors on the main surface of the product. Fail-open means degrading to a basic feed instead of returning an error, so users still get content. I was putting availability of the main surface ahead of ranking quality, and I knew the cost was a lower-quality feed during an outage.

**Follow-up 2**

> Q: What was the real difference in assumptions?
> A: The service team believed ranked quality is the core experience, so a degraded feed might be worse than none. I was optimizing for availability, and they were optimizing for quality. Neither is wrong. Until I named that, we were arguing about the solution when the disagreement was really about what the product promises.

**Follow-up 3**

> Q: How did you resolve it?
> A: Over several conversations I made the assumptions explicit and walked through the availability trade-off. I brought in the product team because the real question, whether a degraded feed is better than an error for users, is a customer-impact question, not an engineering preference. Then I weighed how often Rankie fails against what a backup feed would cost to build.

**Follow-up 4**

> Q: Do you still think you were right?
> A: My design wasn't adopted, and I think that was reasonable. Rankie failures were infrequent and a backup feed was costly, so the work went to the backlog. I disagreed, made my case with data, and then committed fully. I'd bring failure-frequency and cost data to the first conversation, which would have shortened the debate, and I'd revisit the decision if failures became more frequent, because that changes the numbers.

---

### 8. How do you manage multiple priorities, do you like to be in a place where priorities keep changing or prefer doing the same thing repeatedly?

**Answer**

I'm comfortable with changing priorities as long as there is a clear way to decide. At my level I'm driving a long initiative, like the Postgres and OS upgrades across about 40 production clusters, while production issues and cross-team asks land on top.

I handle it four ways. First, I rank by customer impact, risk and deadline, and I agree on those rules with stakeholders up front, so reprioritizing isn't a negotiation each time. Second, I protect focused time for the one or two things that matter most. Third, I decide quickly what to drop or defer, and I tell stakeholders so nobody is surprised. Fourth, and this is how I scale myself, when so much is on my plate and all of it is high priority, I delegate to staff and senior engineers. I give them clear outcomes and context, let them own the how, and stay available for the hard calls.

I like variety, but I don't accept repeating toil, and at scale I eliminate it. That's why I built IRIS. It resolves about 30% of infrastructure requests on its own and cut triage latency by 45%, which freed engineers for the more interesting problems.

What I learned is that agreed decision rules, and automating the repetitive work, are what make constantly changing priorities sustainable.

**Follow-up 1**

> Q: How do you rank when everything is urgent?
> A: I use three criteria: customer impact, risk and deadline, and I agree on them with stakeholders up front. When two things collide we apply the rule instead of renegotiating each time. If everything still ranks as high priority, I delegate pieces to staff and senior engineers with a clear outcome and context, let them own the how, and stay available for the hard calls. Otherwise I become the bottleneck.

**Follow-up 2**

> Q: How do you protect focus?
> A: I pick the one or two things that matter most and protect time for them. I decide quickly what to drop, delegate or defer, instead of letting everything slip a little. And I tell stakeholders at that moment, so nobody is surprised later. Quietly slipping everything is the failure mode I'm avoiding.

**Follow-up 3**

> Q: What do you do about repetitive work?
> A: I like variety, but I don't accept repeating toil, and at scale I eliminate it. IRIS came from that: infrastructure engineers were spending more and more time on repetitive requests and manual triage. It now resolves about 30% of requests on its own and cut triage latency by 45%, which freed engineers for the more interesting problems.

**Follow-up 4**

> Q: Example of this on the Postgres/OS upgrade?
> A: With about 40 clusters in flight, production issues and cross-team asks landed on top. I applied the same rules: rank by impact, risk and deadline, delegate pieces across the 10 to 15 engineers I led, and tell stakeholders what moved so nobody found out late.

---

### 9. You are organizing an off-site and a final venue is decided by majority vote, but some people who voted for other options say they won't join. How would you resolve this conflict?

**Answer**

I'd treat this as a buy-in problem, not a voting problem. I'll walk through my approach, then a real example of the same principle.

First, I'd talk to the objectors directly and one-on-one to find out what's behind it: cost, distance, accessibility, dietary needs, or feeling unheard. Often the reason is specific and fixable. Second, I'd be transparent about how the decision was made and the criteria used. Ideally I would have published those before the vote. Third, I'd adjust for real concerns without reopening the decision, and be honest about what I can't solve. The goal is that people feel heard even if they didn't get their first choice.

The real example is Secret Scanner. Every team tracked secrets and certificates its own way, with Azure Key Vaults, HashiCorp Vault, env files and more, so I didn't start with a mandate. I aligned each team's leaders first, identified the gaps each team had, and wrote a thorough onboarding guideline with regular office hours. Then teams told me they were getting a lot of expiry alerts for secrets their services didn't use, because the scanner reported every certificate it found on the VM. I treated that as a legitimate concern, not resistance, and iterated the scanner to report only what a service actually used, without reopening the 60-day standard.

What I learned is to understand the underlying concern first, then design for it. On the embeddings disagreement, that meant dedicated node pools plus a kill switch.

**Follow-up 1**

> Q: What do you listen for in the one-on-ones?
> A: The specific reason: cost, distance, accessibility, dietary needs, or feeling unheard. The last one matters most, because if people feel the vote ignored them, no venue fix helps. A specific constraint is usually fixable and cheap to fix. I listen first and don't pitch the venue.

**Follow-up 2**

> Q: Why not just reopen the vote?
> A: Reopening teaches everyone that the loudest objection overrides the process, and it punishes the people who accepted the result. I'd explain the criteria, ideally published before the vote, and adjust for real concerns without reopening the decision. The exception is new information: if someone shows the venue is actually unworkable, for example inaccessible for a colleague, that is a fact, not displeasure, and I'd revisit it.

**Follow-up 3**

> Q: What if someone still won't come?
> A: I'd be honest about what I can't solve and respect their choice. I'd also make sure they aren't shut out of the outcomes, for example by sharing notes or offering a remote way to take part. The goal is that people feel heard even if they didn't get their first choice.

**Follow-up 4**

> Q: Where have you done this?
> A: On Secret Scanner, teams complained about expiry alerts for secrets their services didn't use. I treated it as a real concern and changed the scanner to report only credentials a service actually used, without reopening the 60-day standard. On the embeddings disagreement, I understood the underlying concern and designed for it with node pools and a kill switch.

---

### 10. How do you accommodate new requirements that arise mid-task while still sticking to your original timelines? / Tell me about a time you had to pivot mid-project. / Tell me about a project where the requirements were not clear or kept changing

**Answer**

Maestro is my best example. It started as a hackathon idea, and I took it on with a goal of adoption across 15 teams, about 150 engineers. Teams had different workflows and stacks, many were skeptical of AI automation, and requirements kept shifting as feedback came in.

I did three things. First, I decided not to defend the original design. I listened to team leads and reshaped it with them into modular plug-ins that fit their existing CI/CD pipelines. Second, I triaged every new ask: needed for adoption, or nice-to-have. Nice-to-haves went into a visible backlog, so people could see their ask was recorded and why it wasn't first. Third, I made it scale without me, with reference architectures, setup scripts, self-service docs, office hours and biweekly forums.

Ten of the 15 teams and more than 100 engineers have adopted it, and the rest are in active evaluation. Adopted services saw about a 25% cycle-time reduction. I led 10 to 15 engineers building the plug-ins. The Infrastructure team owns it day to day. Next, I'm driving full adoption across all Viva Engage teams, and I'm pitching Maestro up to get adoption across other M365 teams. The Teams team has already started dogfooding it.

What I learned is that when requirements move, I hold the outcome, stay flexible on scope, and make the trade-offs visible.

A shorter example is the Saturday production Postgres upgrade. Azure had intermittent VM provisioning issues, even though we had procured capacity, because Azure was doing maintenance. Some tech leads asked to abort. I pivoted the plan instead of abandoning it: since weekend traffic is lower, we continued the upgrade on the minimum nodes and provisioned full capacity once the Azure SDKs were stable, which happened that night. Same principle: hold the outcome, change the scope.

**Follow-up 1**

> Q: How did you triage changing asks?
> A: For every new ask I asked one question: is it needed for adoption? If yes, it was in scope now. If it was a nice-to-have, it went into a visible backlog, so the requester could see it was recorded and why it wasn't first. Visibility matters, because people stop re-escalating once they can see their ask is tracked. That let me hold the outcome, adoption, and flex the scope.

**Follow-up 2**

> Q: What did you change in the original design?
> A: The hackathon design didn't fit how teams actually worked, and I chose not to defend it. I listened to team leads and reshaped it with them into modular plug-ins that fit their existing CI/CD pipelines, so a team could adopt it without changing its pipeline. Designing it with the leads also made them co-owners instead of recipients.

**Follow-up 3**

> Q: How did you scale without becoming the bottleneck?
> A: Reference architectures, setup scripts and self-service docs let a team adopt without me. Office hours and biweekly forums were the feedback loop, and they surfaced new requirements early. I led 10 to 15 engineers building the plug-ins, and the Infrastructure team owns it day to day.

**Follow-up 4**

> Q: What was the outcome?
> A: 10 of the 15 teams and more than 100 of about 150 engineers have adopted it, with about a 25% cycle-time reduction in adopted services. It isn't finished: the rest are in active evaluation. I'm driving full adoption across Viva Engage and pitching it to other M365 teams, and the Teams team has already started dogfooding it.

---

### 11. Tell me how you helped someone in your team to get better at some task / Describe a situation where a team member was struggling and what you learned from it

**Answer**

A fellow staff engineer on my team built alt_pool, a dedicated connection pool for migration-related workflows, to stop migration traffic from creating a noisy-neighbor problem in our data store. The implementation was correct. He then sent a mass communication to all 150 engineers asking them to move their migration workflows to alt_pool, and adoption was low. He was struggling, not because of the engineering, but because a broadcast ask wasn't enough to change what 15 teams do.

I looked into the situation instead of taking over, and I coached him in three steps. First, align the tech lead of each team before asking their engineers to change, so the request came through people they trusted. Second, make adoption easy: write short, step-by-step instructions with documentation, so a team could adopt it without needing him. Third, run office hours to help engineers set it up. It's the same pattern that worked for Secret Scanner and Maestro, and I coached him through it rather than doing it for him.

Once he followed those steps, adoption of alt_pool reached 100%, with all 15 teams on it. [Any reduction in noisy-neighbor incidents.] [Imperfection: what was slow or didn't work at first.]

What I learned is that a correct solution doesn't adopt itself, and that coaching a senior engineer is mostly about shifting their attention from building to adoption: align the leaders, remove friction and offer hands-on help. It also scaled my impact. When so much is on my plate and all of it is high priority, I delegate to staff and senior engineers like him, give them clear outcomes and coach them, and he now knows how to drive cross-team change without me.

**Follow-up 1**

> Q: How did you avoid just doing it yourself?
> A: If I had done the outreach, the 15 teams would have learned that adoption depends on me, and he would have learned nothing. So I coached him on the sequence, tech leads first, then easy documented steps, then office hours, and he ran each step himself. I stayed in the role of coach. [Where, if anywhere, you stepped in.]

**Follow-up 2**

> Q: What did the coaching cover?
> A: First the diagnosis: a correct solution isn't the same as adoption, and a broadcast to 150 engineers doesn't change what 15 teams do. Then three steps. Align each team's tech lead first, so the ask comes through someone they trust. Write short, step-by-step docs so a team can adopt alt_pool without needing him. And run office hours for hands-on setup. It's the same pattern that worked for Secret Scanner and Maestro.

**Follow-up 3**

> Q: How did you know it worked?
> A: Adoption of alt_pool reached 100% once he followed those steps, with all 15 teams on it. The other outcome is that he now knows how to drive cross-team change without me. [Add any reduction in noisy-neighbor incidents.]

**Follow-up 4**

> Q: What did you learn?
> A: A correct solution doesn't adopt itself. When a strong senior engineer is struggling, it's often about shifting their attention from building to adoption, and the fix is to align leaders, make the change easy and provide hands-on help. As a coach, I also learned to diagnose what the problem actually is before offering help. His engineering was fine, and the issue was how he was asking.

---

### 12. Describe going above and beyond to help someone

**Answer**

During [a Postgres cluster cutover], [an engineer] on [another team] owned [their service's] migration and was anxious because the window was [outside normal hours].

I wasn't required to be there, but they were carrying a risk they had never carried. I joined, walked through the rollback plan with them beforehand, stayed on the bridge during the cutover, and helped them validate afterward.

Then I turned the cutover checklist into a runbook for the other deployment stamps, our independent production environments, so the help wasn't one-off. [[Number] teams used it across [number] stamps.]

It cost me [a few evenings]. [They] went on to run [later cutovers] themselves, and the runbook helped other teams. [Imperfection: what I'd do differently.]

What I learned is to show up when someone carries a risk they've never carried, and to turn one-off help into something reusable.

A second example is the Postgres upgrade outage banner. The UI only had a generic system-outage banner, but this upgrade needed a specific message with the time in it. The front-end team was busy with feature work, so I made the change myself with AI help, instead of leaving the gap or adding to their queue. They now have a custom outage-banner template they can reuse.

**Follow-up 1**

> Q: Why did you join when you weren't required?
> A: They were carrying a risk they'd never carried, [an out-of-hours cutover], and a first high-stakes cutover is exactly when having someone who has seen one matters most. My being there lowered the risk for them and for their service, and I believe in showing up for that.

**Follow-up 2**

> Q: What exactly did you do?
> A: Before the cutover I walked through the rollback plan with them, so they knew the trigger and the steps before the pressure started. During it I stayed on the bridge. Afterward I helped them validate. Rollback decisions get made under stress, so rehearsing them in advance is the most useful thing I can give someone doing this for the first time.

**Follow-up 3**

> Q: What did it cost you?
> A: [A few evenings], and it was worth it: [they] ran later cutovers themselves. It also taught me that this kind of help doesn't scale if I do it one team at a time, which is why I turned it into a runbook.

**Follow-up 4**

> Q: How did you make it last?
> A: I turned the cutover checklist into a runbook for the other deployment stamps, so the next team didn't need me on the bridge. [How many teams used it.] The outage banner is the same idea: I built the custom template once, and the front-end team can reuse it for future outages.

---

### 13. Tell me about a time when you had to make a trade-off between two competing priorities or options / Tell me about a time when you had to make tradeoffs between quality and cost

**Answer**

I have two trade-off examples: one on IRIS, balancing automation coverage against safety, and one where I got the cost model wrong on a Hadoop to Cosmos DB migration. I'll start with IRIS.

IRIS is the multi-agent system I conceived to cut on-call toil, and I led 10 to 15 engineers building it. It supports all 15 Viva Engage teams, about 150 engineers. Infrastructure engineers were spending more and more time on repetitive requests and manual triage. The trade-off was how much to let the agents do on their own. More autonomy would resolve more requests and free more engineering time. But a wrong action in production could be costly, and enterprise policy didn't yet cover autonomous actions.

I weighed the value of each action against its blast radius and chose to earn trust in stages. I took three steps. First, I added a two-stage verification pipeline that uses retrieved ground-truth information and engineer feedback to reduce hallucination risk. Second, I partnered with Trust and Security leadership on permission boundaries and blast-radius controls for production actions, and I accepted that this would limit what IRIS could do at first, [for example, higher-risk actions stayed human-approved]. Third, I [widened autonomy as the data showed it was reliable, using criteria such as an error-rate threshold].

IRIS now resolves about 30% of infrastructure requests on its own, and triage latency for recurring incidents fell by 45%, freeing hundreds of engineering hours a month. The Infrastructure team owns IRIS today. The cost of the trade-off was [the coverage I deferred, such as X% of requests that still need human approval].

What I learned is that production AI automation is as much a safety and governance challenge as a technical one. [I'd rather ship a smaller share safely and grow it than ship more and lose trust.]

**Follow-up 1**

> Q: How did you decide how much autonomy to give IRIS?
> A: I weighed the value of each action against its blast radius, and started with [lower-risk actions]. Alongside that, I added a two-stage verification pipeline that uses retrieved ground-truth information and engineer feedback, to reduce hallucination risk. Then I widened autonomy as the data showed it was reliable. [Your true criteria, such as an error-rate threshold.]

**Follow-up 2**

> Q: How did you get Trust and Security leadership to agree?
> A: Enterprise policy didn't yet cover autonomous actions, so I didn't ask for an exception. I partnered with them on permission boundaries and blast-radius controls for production actions, which made them co-designers of the limits and gave them something concrete to approve. [The specific compromise you reached.]

**Follow-up 3**

> Q: What did the trade-off cost you?
> A: Slower coverage at first: [for example, higher-risk actions stayed human-approved]. [Quantify it.] I accepted that on purpose, because trust lost on one bad production action is hard to win back. IRIS now resolves about 30% of requests on its own, and that share grew as the evidence came in.

**Follow-up 4**

> Q: Have you made a trade-off that went wrong?
> A: Yes. I moved a Hadoop-based metadata system to Cosmos DB. I ran a proof of concept, proved scalability and led the migration, but I didn't model the multi-year cost. Discounts ended and pricing changed, and run cost reached nearly ten times the previous Hadoop cost. Now I model multi-year costs before recommending anything, including growth, discount expiry and pricing changes.

---

### 14. Describe one thing you have learned recently

**Answer**

Recently I learned to treat AI recommendations as hypotheses, and to build verification into agentic systems at the org level.

It started with a personal mistake. FaultLine, the AI SRE sidecar I built, noted that the Kafka consumers committed offsets after every event, and suggested batching commits to reduce broker saturation. It sounded right, so I implemented it, even though FaultLine is designed to leave the approval decision to a human. Service teams soon got alerts for high lag and elevated HTTP 5xx errors, and I reverted my pull request right away. An optimization can be right in isolation and wrong in the system. I had validated the local logic but not the downstream assumptions.

The bigger step was turning that into a standard for the agentic work I lead. I contributed in three ways. First, I now validate downstream assumptions, test end to end, and define rollout and rollback criteria before applying any AI-suggested change. Second, I built that into IRIS: a two-stage verification pipeline and permission boundaries, so AI actions earn trust. Third, I [shared it as a review checklist that [number] teams now use for AI-assisted changes, and presented it at [forum]].

[Result: for example, since then, no AI-suggested change has caused a production incident on the teams using it.] The speed from AI only pays off when verification is built in.

**Follow-up 1**

> Q: Why did you implement the AI suggestion?
> A: It sounded right. Committing offsets after every event can saturate brokers, so batching looked like a reasonable fix. But I applied it without enough end-to-end validation. FaultLine is designed to leave the approval decision to a human, and I was that human, so the gap was my review, not the tool.

**Follow-up 2**

> Q: How did you find out it was wrong?
> A: Service teams got alerts for high lag and elevated HTTP 5xx errors, and I reverted my pull request right away. I reverted first and diagnosed second, because the priority was stopping the customer-visible impact. What I'd missed was that an optimization can be right in isolation and wrong in the system. I'd validated the local logic but not the downstream assumptions.

**Follow-up 3**

> Q: What's your rule now?
> A: I treat an AI recommendation as a hypothesis. Before applying any AI-suggested change I validate the downstream assumptions, test end to end, and define rollout and rollback criteria. The more irreversible and widespread the impact, the more evidence I want first.

**Follow-up 4**

> Q: How did you spread that beyond your own work?
> A: I built it into IRIS: a two-stage verification pipeline and permission boundaries, so AI actions earn trust instead of being assumed. [I also shared a review checklist adopted by N teams.] The point was to move verification from one person's habit to something built into the system.

---

### 15. What would you like to have improved about your last role? / What would you like to see in your next manager?

**Answer**

About my current role, I'd like more protected time for long-term technical bets, because operational load often crowds them out. That's partly why I built automation like IRIS and Secret Scanner. But a clearer split between planned and reactive work would have helped, and I'd negotiate that earlier next time.

For my next manager, I'd want four things. Clear outcomes and context, with autonomy on how. Candid, regular feedback. Advocacy for the team's work with senior leadership, and help clearing cross-org blockers. And someone who encourages calculated risks and treats failures as learning, not blame. My Cosmos DB cost miss is the kind of learning I mean.

That combination lets me spend my time where I add the most leverage.

**Follow-up 1**

> Q: Why did operational load crowd out long-term bets?
> A: Reactive work wins by default because it comes with visible urgency, and long-term bets have no deadline pressure, so they lose every tie. My response was to attack the load itself: I built automation like IRIS and Secret Scanner to remove reactive work instead of just absorbing it.

**Follow-up 2**

> Q: What would you negotiate next time?
> A: A clearer split between planned and reactive work, earlier. I'd propose an explicit split, so long-term work is protected by default and reactive load has a defined boundary. I'd raise it at planning time, not after the bets had already slipped.

**Follow-up 3**

> Q: What do you need from a manager?
> A: Clear outcomes and context with autonomy on how, so I spend my time where I add leverage. Candid, regular feedback: the "too technical" feedback on my Postgres updates made me better. Advocacy with senior leadership and help clearing cross-org blockers, because my work crosses orgs. And encouragement for calculated risks.

**Follow-up 4**

> Q: How do you want failure handled?
> A: As learning, not blame, like my Cosmos DB cost miss. I got the cost model wrong, and what came out of it is that I now model multi-year costs. A manager who treats a miss as blame teaches people to hide the next one. A manager who treats it as learning gets the lesson out early.

---

### 16. How would you handle a situation where one team member takes all the credit for a group project?

**Answer**

I'll walk through how I'd handle it, then a real example of the same principle.

I'd start with a private, direct conversation, assuming thoughtlessness rather than malice, and describe the specific behavior and its impact. Then I'd make contribution visible going forward: shared design docs with named owners, credits in status updates, and letting each person present their own part. If it became a pattern, I'd bring in the manager with concrete examples.

I do this on Maestro, where adoption across teams depends on the engineers who build with it. I run biweekly feedback forums with early adopters, and [I credit the team leads and engineers who built plug-ins or shaped the design by name, in the forums and in my updates to leadership]. [For example, [name] built the [plug-in], and I had them present it to [audience].] That also makes the next team more willing to contribute.

On a smaller scale, in a design review of VentSpout's Kafka retry logic, a teammate proposed exponential backoff. I suggested jitter and framed it as building on his proposal. Retries stopped synchronizing and resource starvation eased, and he got the credit for the starting idea.

**Follow-up 1**

> Q: Why assume thoughtlessness rather than malice?
> A: It's usually true, and it keeps the conversation on the specific behavior and its impact. Assuming malice makes the person defensive, and the conversation ends before anything changes. If I'm wrong, the pattern shows up in the steps that follow.

**Follow-up 2**

> Q: How do you make contribution visible?
> A: Through structure, not confrontation: shared design docs with named owners, credits in status updates, and letting each person present their own part. That makes taking credit harder and giving credit the default, without singling anyone out.

**Follow-up 3**

> Q: When do you involve the manager?
> A: If it becomes a pattern after the direct conversation, and I bring concrete examples, such as specific docs or updates, not impressions. The aim is to fix the behavior, not to punish the person.

**Follow-up 4**

> Q: How do you model it yourself?
> A: On Maestro, [I credit the engineers who build plug-ins by name in forums and leadership updates, and have them present their work]. In the VentSpout Kafka retry review, a teammate proposed exponential backoff. I suggested jitter and framed it as building on his proposal. Retries stopped synchronizing and resource starvation eased, and he got the credit for the starting idea.

---

### 17. Tell about a time when you had to go against the norm and push for a change / Tell me about a time when you made an unpopular decision

**Answer**

The norm was paying for commercial Elasticsearch licensing, mainly for inter-node TLS, and I pushed against it.

Provisioning took days, patching was risky, and licensing cost millions annually. The search platform affected all 15 Viva Engage teams, about 150 engineers.

I did it in three parts: the business case, the legal path, and the build.

For the business case, I looked at what we were really paying for. The license was mostly buying inter-node TLS, which could be built on open source. So I proposed forking open-source Elasticsearch and building native TLS transport security. It meant real engineering cost and risk, and I said so up front, backed by numbers.

For the legal path, I worked with Microsoft legal teams on licensing, IP and contribution requirements, treating them as architectural inputs.

For the build, I led the design and implementation. I migrated the platform to AKS and wrote Helm charts and declarative CI/CD for provisioning, autoscaling and zero-downtime rolling upgrades.

Provisioning and patching dropped from days to under 15 minutes, saving more than $10M a year in run cost. I led 10 to 15 engineers on the build. The search team owns the platform today.

What I learned is that going against the norm works when you take the risks explicitly, treat legal as a design input, and back the choice with numbers. I'd bring legal in even earlier next time, with a written risk plan.

**Follow-up 1**

> Q: Why was forking Elasticsearch worth the risk?
> A: Licensing cost millions annually, and the license was mostly buying inter-node TLS, which could be built on open source. On top of that, provisioning took days and patching was risky. I weighed that against real engineering cost and risk, said so up front, and backed the decision with numbers instead of conviction.

**Follow-up 2**

> Q: How did you handle legal risk?
> A: I worked with Microsoft legal on licensing, IP and contribution requirements, and treated them as architectural inputs, because they constrain what we can build and contribute. They weren't a sign-off at the end. Looking back, I'd bring them in even earlier, with a written risk plan.

**Follow-up 3**

> Q: What did you build beyond TLS?
> A: I migrated the platform to AKS and wrote Helm charts and declarative CI/CD for provisioning, autoscaling and zero-downtime rolling upgrades. That is what took provisioning and patching from days to under 15 minutes. The fork removed the license cost, and the automation removed the toil.

**Follow-up 4**

> Q: What would you do differently?
> A: I'd bring legal in even earlier with a written risk plan. The result was provisioning and patching in under 15 minutes instead of days, and more than $10M a year saved. I led 10 to 15 engineers on the build, and the search team owns the platform today.

---

### 18. Tell me about a problem you had to solve that required in-depth thought and analysis

**Answer**

The deepest analysis I've done was the Database Health Check. Tier-1 services had intermittent read failures while every dashboard looked healthy. It affected all 15 Viva Engage teams, about 150 engineers.

FaultLine flagged the pattern and suggested a review of the read path, and I verified it rather than trusting it. I started by mapping the read path end to end: client, connection pooler and replicas. Then I instrumented per-node latency and tested each layer with telemetry-driven hypotheses. That isolated two failure modes. One replica had severe disk I/O stalls. And the pooler's TCP health check verified only connectivity, so it kept routing traffic to the sick node.

The health checks measured what had been chosen to measure, not what users depend on. So I replaced them with synthetic queries that test real read behavior, and added circuit breaking.

Read availability reached 99.999%, and the approach became an org-wide operational template. [The failures affected all Viva Engage customers, and [team] now owns the template.]

What I learned is that a green dashboard is only as good as what it measures, so health checks should test what users depend on.

**Follow-up 1**

> Q: Why did every dashboard look healthy?
> A: A dashboard only measures what you chose to measure. The pooler's TCP health check verified connectivity only, so a replica with severe disk I/O stalls still passed and kept receiving traffic. Users felt brief outages while every dashboard stayed green.

**Follow-up 2**

> Q: How did you find the root cause?
> A: FaultLine flagged the pattern and suggested a review of the read path, but I verified it instead of trusting it. I mapped the path end to end: client, pooler and replicas. Then I instrumented per-node latency and tested each layer with telemetry-driven hypotheses, which narrowed intermittent failures down to specific nodes.

**Follow-up 3**

> Q: What were the two failure modes?
> A: A replica with severe disk I/O stalls, which was the trigger, and a pooler that kept routing to the sick node, which is why users felt it. Fixing only the replica would have left the next sick node undetected, so I fixed both.

**Follow-up 4**

> Q: What was the fix and result?
> A: I replaced the connectivity checks with synthetic queries that test real read behavior, and added circuit breaking so a sick node comes out of rotation. Read availability reached 99.999%, and the approach became an org-wide operational template.

---

### 19. What have you done to develop your leadership skills?

**Answer**

I've grown most by taking on work that crosses organizational boundaries, and each project taught me something different.

On the Postgres upgrade across about 40 clusters, I learned to build VP-level confidence and align stakeholders around a high-risk plan, including rollback planning, and to present it as a decision, not a technical walkthrough. I also learned to make certification achievable: the 15 service teams couldn't prove everything worked, so I had them certify only their core SLA scenarios, with a clear rule: roll back if a core scenario fails, otherwise fix forward. On the production night, when Azure provisioning issues pushed leaders toward aborting, I proposed continuing on minimum nodes and adding capacity later. With Secret Scanner and Maestro, I learned that adoption comes from understanding teams and giving them docs and office hours, not mandates, and from iterating on feedback, like the unused-secret alerts I removed from Secret Scanner. Secret Scanner reached 100% adoption across all 15 Viva Engage teams, and Maestro now serves more than 100 engineers. With IRIS, I partnered with Trust and Security leadership on permission boundaries and blast-radius controls, so autonomous actions could earn trust.

I also learn from my own misses, like the reverted Kafka change, which taught me to validate end to end. [DRAFT: I also invest in other senior engineers, for example coaching [name or role] to own [initiative] across teams.] I also set the roadmap for Maestro beyond Viva Engage: full adoption across all Viva Engage teams, and I'm pitching it up for adoption across other M365 teams, with the Teams team already dogfooding it.

The shift for me has been from solving the problem myself to creating the conditions for other teams to succeed. When so much is on my plate and all of it is high priority, I delegate to staff and senior engineers, which is how I scale myself.

**Follow-up 1**

> Q: What was hardest about the Postgres upgrade?
> A: The 15 service teams couldn't say how to certify their service after the upgrade, since their unit and integration tests didn't cover everything and end-to-end tests were risky. I asked each team to certify its core SLA scenarios instead of every scenario, and set a clear rule: roll back if a core scenario fails, otherwise fix forward. Building VP-level confidence in a high-risk plan, including rollback planning, was the other hard part.

**Follow-up 2**

> Q: What did you learn from Secret Scanner and Maestro?
> A: Adoption comes from understanding teams and giving them docs and office hours, not mandates: 100% adoption across Viva Engage teams and 100+ engineers on Maestro.

**Follow-up 3**

> Q: What did IRIS teach you?
> A: Trust in autonomous actions has to be earned. Enterprise policy didn't yet cover autonomous actions, so instead of asking for exceptions I partnered with Trust and Security leadership on permission boundaries and blast-radius controls, and added a two-stage verification pipeline. The leadership lesson is to bring the risk owners in as co-designers of the limits.

**Follow-up 4**

> Q: How have setbacks shaped you?
> A: The reverted Kafka change taught me to validate end to end. I applied an AI suggestion without checking downstream assumptions, service teams got lag and 5xx alerts, and I reverted right away. Now I define rollout and rollback criteria first. More broadly, I've moved from solving problems myself to creating conditions for others: delegating to staff and senior engineers, coaching instead of doing, as with alt_pool, and writing the docs and running the office hours that let teams adopt without me.

---

### 20. Give me an example of a tough or critical piece of feedback you received

**Answer**

A senior leader told me my Postgres upgrade updates were too technical, and he couldn't tell what decisions he needed to make. The VP and senior leaders needed to decide whether to do the upgrade, and my first presentation walked them through the technical plan instead. It stung, but he was right.

I looked at my updates from his side. He needed to act, and I was giving him detail. So I changed the format: lead with status and risk in business terms, state the decision needed, and keep technical detail in an appendix.

Executive alignment became much easier, which helped a high-risk upgrade move forward.

What I learned is that communication is judged by whether the audience can act on it.

**Follow-up 1**

> Q: What exactly was the feedback? 
> A: My Postgres updates were too technical, and a senior leader couldn't tell what decisions he needed to make. The VP and senior leaders needed to decide whether to go ahead with the upgrade, and I was walking them through the technical plan the way I'd brief engineers.

**Follow-up 2**

> Q: How did you react? 
> A: It stung, but he was right. I didn't defend the format. I looked at my updates from his side: he needed to act, and I was giving him detail he couldn't act on.

**Follow-up 3**

> Q: What did you change? 
> A: I lead with status and risk in business terms, then state the decision needed, and keep technical detail in an appendix. The detail is still there for anyone who wants to check it, but it no longer sits between the leader and the decision.

**Follow-up 4**

> Q: What was the impact? 
> A: Executive alignment became easier, which helped a high-risk upgrade move forward. The lesson is that communication is judged by whether the audience can act on it, so I now start any senior update by asking what decision the reader needs to make.

---

### 21. Give me an example of when you had to make an important decision and had to decide between moving forward or gathering more information

**Answer**

The Postgres and OS upgrades covered about 40 production clusters and affected all 15 Viva Engage teams, about 150 engineers. The risk was high, but the CVE and Trust requirements were pressing, so I couldn't wait for perfect information.

My framework was reversibility. For reversible parts, like feature flags for cross-version compatibility, I moved forward fast. For irreversible parts, I went deeper before committing. For the OS, I chose native logical replication to a mirrored Ubuntu cluster. That avoided an Ubuntu 18.04 issue where a C library change invalidates database indexes, and it kept the cutover short.

Because the PostgreSQL upgrade averaged about one hour of downtime per cluster, I split the rollout into non-SLA and SLA cohorts with separate upgrade windows. I upgraded non-SLA clusters first and allowed enough bake time to observe stability before proceeding with the SLA clusters in the later window.

I aligned executives on a clear plan, including rollback, and led execution across all clusters and deployment stamps.

The same trade-off came up live during the Saturday production upgrade. Azure had intermittent VM provisioning issues, so leaders had to choose between continuing and aborting, and several tech leads wanted to abort. I didn't have complete information on when the Azure SDKs would stabilize, so I proposed the reversible middle path: continue on the minimum nodes, since weekend traffic is lower, and add the remaining capacity once the SDKs were stable. We did exactly that and provisioned full capacity that night.

The hardest part was that the 15 service teams couldn't say how to certify their service after the upgrade. Their unit and integration tests didn't cover everything, and end-to-end tests were risky. I couldn't wait for exhaustive coverage, so I asked each team to identify its core SLA test scenarios and certify only those, and I set a clear rule for after the upgrade: roll back if a core SLA scenario failed, otherwise fix forward.

The Postgres upgrade averaged roughly one hour of downtime per cluster, the OS cutover took about five minutes, and related incidents fell 40%. The Infrastructure team owns the Postgres tooling today. I led 10 to 15 engineers, and the upgrade affected all 15 teams.

The Kafka offset change is the opposite case. I moved on a FaultLine suggestion without enough validation and had to revert.

What I learned is that the more irreversible and widespread the impact, the more evidence I want. For reversible changes, I move fast with clear rollback criteria.

**Follow-up 1**

> Q: Which parts were reversible?
> A: Feature flags for cross-version compatibility. I moved forward fast on those and went deeper on the irreversible parts. For service certification, I asked teams to certify only their core SLA scenarios: roll back if one failed, otherwise fix forward.

**Follow-up 2**

> Q: Why logical replication for the OS?
> A: Native logical replication to a mirrored Ubuntu cluster avoided the Ubuntu 18.04 index-invalidation issue and kept the cutover short.

**Follow-up 3**

> Q: What were the results?
> A: About 40 clusters, roughly one hour of downtime per cluster for Postgres, about five minutes for the OS cutover, and related incidents down 40%.

**Follow-up 4**

> Q: When do you gather more evidence?
> A: The more irreversible and widespread the impact, the more evidence I want. For the PostgreSQL rollout, I upgraded non-SLA clusters first and allowed enough bake time before upgrading SLA clusters in a separate window. For reversible changes I move fast with clear rollback criteria, unlike the Kafka change I had to revert.

### 22. What are you trying to improve most (professionally)

**Answer**

I'm working on two connected things. First, translating technical trade-offs into simpler decision frameworks, so teams can move without needing me in every discussion. Second, scaling standards across many engineers without creating too much process or becoming a central approver.

Both come from the same lesson: my impact is limited if every important call has to go through me. I've seen the alternative work. On the Postgres upgrade, the 15 service teams couldn't prove everything worked, so I gave them a simple frame: certify your core SLA scenarios, roll back if one fails, otherwise fix forward. They could decide without me. On Secret Scanner, the standard was firm on compliance, 60-day rotation, but flexible on how each team met it, so teams didn't need approval for their own architecture. With the alt_pool coaching, I helped a staff engineer drive adoption through tech leads, easy documented steps and office hours, instead of me or him approving each team.

I'm still improving at this. The skill is deciding which constraints are firm, which are flexible and which decisions teams can own, then writing that down clearly and briefly. I stay involved for novel or irreversible decisions and delegate the rest to staff and senior engineers, which is how I scale myself.

**Follow-up 1**

> Q: What does a simpler decision framework look like?
> A: A short rule a team can apply alone: what's firm, what's flexible, and what to do if it goes wrong. For the Postgres upgrade it was: certify your core SLA scenarios, roll back if one fails, otherwise fix forward.

**Follow-up 2**

> Q: How do you avoid becoming a central approver?
> A: I keep standards firm on the outcome and flexible on how, delegate decisions to staff and senior engineers, and stay involved only for novel or irreversible calls.

**Follow-up 3**

> Q: How do you avoid too much process?
> A: I prefer a few clear principles and easy self-service paths, like onboarding docs and office hours, over approval gates and long checklists.

**Follow-up 4**

> Q: Why does this matter at your level?
> A: Scope grows faster than my time. If decisions depend on me, teams slow down, so the leverage comes from making good decisions easy for other people to make.

---

## Questions I Ask the Interviewer

1. What does success look like in the first 90 days?
2. What's the most important problem you're hoping this hire will solve?
3. What's the biggest challenge the team is facing right now?
