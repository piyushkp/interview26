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
12. FaultLine

### 1. Postgres & OS Zero-Downtime Upgrade

**Context**

I owned the PostgreSQL and Ubuntu upgrade across about 40 production clusters, and I led 10 to 15 engineers through it. The clusters ran legacy PostgreSQL 9.6 on Ubuntu, with critical CVEs open and Microsoft's Trust requirements unmet. PostgreSQL 9.6 has no native logical replication, so a standard upgrade meant substantial downtime and customer-refund risk. Breaking changes also affected multiple Java and infrastructure services. The work touched all 15 Viva Engage teams, about 150 engineers.

**Actions**

I designed a two-phase migration to keep downtime small, and I worked on four fronts. For the database, I used pg_upgrade to move PostgreSQL from 9.6 to 18.6. To protect the services that depend on it, I introduced feature flags so the Java and infrastructure services stayed compatible across both versions without deployment locks, and I built dynamic maintenance banners to keep customers informed. For the OS, I ruled out an in-place Ubuntu upgrade because of the Ubuntu 18.04 libc index-invalidation issue. Instead, I used native logical replication to stream changes to a mirrored Ubuntu cluster, which allowed a short cutover. Throughout, I wrote a comprehensive rollback plan and aligned executives and stakeholders across organizations on it, so a VP-level audience had confidence in a plan with broad production impact.

**Results**

I completed all 40 or so clusters and every deployment stamp. The PostgreSQL upgrade averaged about one hour of downtime per cluster, and the OS upgrade needed roughly a five-minute cutover. Incidents involving replication lag, kernel panics and I/O saturation fell by 40%. The upgrades also secured the Trust and security clearance needed for Microsoft 365 integrations, including Teams and Copilot. The Infrastructure team owns the Postgres tooling today.

**Learnings**

I learned that a sound migration design isn't enough for a high-risk infrastructure upgrade. Comprehensive rollback planning and early executive alignment are essential. I also learned how to build VP-level confidence and align stakeholders across organizations around a plan with broad production impact.

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

**Results**

The rollout reached 100% adoption across all 15 Viva Engage teams, about 150 engineers, and achieved the goal of zero certificate- and secret-related outages. The platform monitored thousands of credentials and issued automated 15-day pre-expiry alerts, replacing manual tracking and supporting continuous Trust and security compliance. Infrastructure owns the platform today.

**Learnings**

I learned that a shared security platform succeeds only when teams can adopt it easily. Clear standards, self-service docs and sustained support mattered as much as the scanner itself. I also learned to balance firm compliance requirements with an understanding of each team's architecture.

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

Tier-1 services had intermittent read failures and customers were seeing brief outages, yet the primary database dashboards showed healthy clusters. The failures were sporadic and spread across microservices, so nobody could tell which component was at fault. I took on the investigation, which affected all 15 Viva Engage teams, about 150 engineers.

**Actions**

I worked layer by layer instead of guessing. I traced the full read path and tested each layer separately: the client application, the connection pooler and the read replicas. I instrumented latency and errors per node, and that isolated one replica with severe disk I/O stalls. Then I found the real root cause: the pooler's TCP health check verified connectivity but not query execution, so it kept sending traffic to the degraded replica. I replaced that shallow check with synthetic queries and added circuit breaking to take unhealthy nodes out of rotation.

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

I was working on a Kafka broker saturation issue. An AI model noticed that the system committed offsets after every event and suggested batching commits to reduce broker load.

**Actions**

It sounded right, so I implemented the AI-recommended change and batched the offset commits instead of committing after each event. I validated the local logic, but I didn't validate the downstream assumptions. Service teams soon got alerts for high lag and elevated HTTP 5xx errors from delayed offset commits, and I reverted my pull request right away.

**Results**

I backed out the change. It was my mistake: I shipped an optimization that was right in isolation but wrong in the system.

**Learnings**

I learned to treat AI recommendations as hypotheses, not validated solutions. Before applying a similar change, I validate downstream assumptions, test end to end, and define rollout and rollback criteria. I've applied this to the agentic work I lead: IRIS has a two-stage verification pipeline and permission boundaries.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| S | S | M | M | S |

**Signals shown:** Ownership, Growth

---

### 12. FaultLine

**Context**

I reviewed FaultLine findings showing that Grouper, Mugshot and Directory were spending most of their CPU time on RSA operations for service-to-service URL signing, and that Grouper had significant performance issues. FaultLine suggested HMAC-SHA256 as an alternative to evaluate.

**Actions**

I benchmarked HMAC-SHA256 against the existing RSA approach, and in my test it was about 500 times faster. That gave me evidence for considering a change to the signing mechanism. But the team was worried about the production risk of changing it in AFD, and I took that concern seriously.

**Results**

The team kept RSA and introduced caching instead, which improved performance without changing the signing mechanism. The HMAC alternative I benchmarked wasn't deployed, so the roughly 500x improvement is a benchmark result, not a production outcome.

**Learnings**

I learned that a strong benchmark alone doesn't justify a security-sensitive production change. I also recognized that caching was a pragmatic improvement even though it differed from the option I evaluated. Next time, I'd pair performance evidence with security and compatibility validation, a staged rollout and clear rollback criteria, to help the team weigh the trade-off.

| Impact | Scope | Personal Contribution | Tech Complexity | Organizational Complexity |
|---|---|---|---|---|
| S | S | M | M | S |

**Signals shown:** Ambiguity, Growth, Communication

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
- **Supporting (deep technical diagnosis):** Database Health Check.
- **Growth or failure examples only, not main answers:** Cosmos DB cost miss, Kafka offset revert, Rankie, Embeddings, VentSpout jitter, FaultLine. Their own scope ratings are S/M, so use each once.

## Gaps to Fill (real details only)

These are the gaps that make the answers read below Principal level. Fill each with a true detail. Don't guess. Q3, Q4, Q5, Q6, Q9, Q11, Q12, Q13, Q14, Q16 and Q19 contain DRAFT text, and Q1, Q2, Q10, Q17, Q18 and Q21 contain bracketed scale, baseline and ownership lines. Replace each [bracket] with a true detail, or revert or delete it.

- **Scale:** Viva Engage users or request volume, number of services and clusters, customers affected.
- **Baselines:** outages per year before Secret Scanner, IRIS requests per month, what the 40% incident drop was measured against, refund exposure avoided in the Postgres upgrade.
- **Leading through others:** team size on each initiative, who built what, how you grew others, who owns it after launch.
- **Org-level influence:** the roadmap or vision you set, the leaders you aligned (titles) and the orgs involved.
- **Senior-level conflict:** one real disagreement with a partner org or senior leader that ended win-win (to replace Embeddings and Rankie as the main conflict answers).
- **Mentoring seniors:** one real example of growing a senior or staff engineer (to replace Q3, Q11 and Q12).
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

### 1. Tell me about yourself (TMAY)

**Answer**

I build the infrastructure that lets about 150 engineers across 15 teams move faster without breaking things. I'm a Senior Principal Software Engineer on the Viva Engage infrastructure team at Microsoft, with 18 years of experience in distributed systems. I set technical direction for platforms that many teams depend on, and I bring about 150 engineers along with it. I focus on reliability, cost efficiency and developer productivity. Viva Engage serves 250 million daily active users across 15 services.

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

My favorite project is Secret Scanner, because I owned it end to end and set the direction for how the entire Viva Engage org manages credentials.

Expired certificates and secrets caused two major Viva Engage outages, and Microsoft's Trust requirements called for rotation every 60 days. Teams tracked secrets in spreadsheets across very different stacks, with no central view. Leadership set a goal of zero certificate and secret outages. Viva Engage serves 250 million daily active users across 15 services. Both outages affected all Viva Engage customers.

I contributed in three ways: the platform, the standards, and adoption, which was the hardest part.

On the platform, I designed automated discovery across Azure Key Vaults, VMs and clusters, plus deduplication, removal of obsolete credentials, central reporting, and alerts 15 days before expiry. I chose discovery over migration so teams didn't have to change their architecture.

On standards, I defined governance that is firm on compliance, meaning 60-day rotation, but flexible on how teams get there. I aligned leaders across organizations on it before rollout, framing it as the zero-outage goal for executives and as flexibility for team leads. [The standard became [the rotation policy other orgs adopted].]

On adoption, the stacks were so different that one-size onboarding would have failed. I wrote onboarding docs and ran weekly office hours so teams could self-serve instead of depending on me.

The result: 100% adoption across all 15 Viva Engage teams, about 150 engineers, thousands of credentials monitored, and the zero-outage goal achieved. Teams now handle rotation themselves, so the platform runs without me. I led 10 engineers to build it, and Infrastructure owns it today.

What I learned is that a platform spanning organizations only works when adoption is easy. Standards, docs and sustained support matter as much as the code.

**Follow-up 1**

> Q: Why was adoption the hardest part of Secret Scanner?
> A: Teams were on very different stacks and tracked secrets in spreadsheets. I built onboarding docs and ran weekly office hours so they could self-serve instead of depending on me.

**Follow-up 2**

> Q: How did you keep standards firm without forcing one architecture on every team?
> A: I defined governance that is firm on compliance, meaning 60-day rotation, but flexible on architecture, and I aligned leaders across orgs on it before rollout.

**Follow-up 3**

> Q: What would you do differently?
> A: I'd bring pilot teams in earlier to shape the reporting before the wider rollout.

**Follow-up 4**

> Q: How do you know it worked?
> A: 100% adoption across all 15 Viva Engage teams, about 150 engineers, thousands of credentials monitored, alerts 15 days before expiry, and zero certificate or secret outages, after two major expiry outages that affected all Viva Engage customers.

---

### 3. Tell me about a time when you had to address underperformance in your team

**Answer**

During [the Postgres and OS upgrade], a senior engineer, [name or role], owned [the Java compatibility workstream] and kept missing commitments, and [some of their work needed rework]. That put the multi-team schedule and the Trust deadline at risk, so I acted early.

I met them one-on-one before assuming a performance problem. [The scope was ambiguous and they were hesitant to raise blockers, or another true cause], so this looked like a clarity problem, not a capability problem.

I made three changes. I broke the workstream into milestones with clear acceptance criteria. I paired with them on the first milestone. And I set weekly check-ins with specific feedback, while being direct that the expectations were non-negotiable. Clarity didn't mean lowering the bar.

Within [about two months] they were delivering independently and [owned a larger piece of the migration]. The schedule risk went away. [Imperfection: what slipped before it improved.]

I also fixed it for the wider team. When one person struggles with ambiguity, others usually do too, so I now write acceptance criteria into the design docs I set.

What I learned is to fix clarity and feedback first, and if that doesn't work, to escalate early with a documented plan instead of letting it drift. [In this case I [did or didn't] need to escalate.]

**Follow-up 1**

> Q: How did you know it was a clarity problem and not a capability problem?
> A: I met them one-on-one before assuming anything. [The true cause you found.]

**Follow-up 2**

> Q: How did you stay candid without demoralizing them?
> A: I gave specific feedback every week, paired with them on the first milestone, and was direct that the expectations were non-negotiable.

**Follow-up 3**

> Q: What did you change for the wider team?
> A: I now write acceptance criteria into the design docs I set, because when one person struggles with ambiguity, others usually do too.

**Follow-up 4**

> Q: What if it hadn't improved?
> A: I'd escalate early with a documented plan instead of letting it drift. [Your true timeline for when you would have.]

---

### 4. Tell me about a conflict you had at work / Discuss a time when you had conflicting perspectives with teammates and how you handled it / Tell me about a time you had a conflict with a coworker. How did you resolve it?

**Answer**

I have three conflict examples: one with a partner service's senior lead on the Postgres upgrade, one with my manager on embeddings, and one with a service team on Homefeed and Rankie. I'll start with the Postgres one.

During the Postgres and OS upgrade across about 40 production clusters, the owner of a partner Java service, [director or senior lead], objected to my cutover schedule. Their service had [release freeze or customer commitment], and the breaking changes in the new PostgreSQL version put it at risk. If the upgrade slipped, the CVE and Trust deadline for [number] clusters would slip with it.

I disagreed with delaying, and I raised it directly in a one-on-one before it escalated. I took three steps. First, I asked what was driving the freeze and learned their real concern was [specific risk], not the date. Second, I brought data on the CVE exposure and the Trust deadline, so the discussion stayed on risk, not preference. Third, I proposed the feature flags I was already building, so their service could stay compatible across both PostgreSQL versions with no deployment lock, and I committed [my team or myself] to [specific support, such as joint compatibility testing].

They agreed to the original window. Their service shipped on its own schedule, and the cutover for their clusters finished [outcome, such as on time with X downtime]. [Optional follow-on: they later adopted the flag pattern for their own migrations.] [Imperfection: what was still hard, or what I'd do differently.]

What I learned is to separate a person's stated position from their real constraint, and to design a plan that removes the constraint instead of winning the argument. [Optional: how the relationship was afterward.]

**Follow-up 1**

> Q: Why did you disagree with delaying the upgrade?
> A: The CVE and Trust deadline covered [number] clusters, and delaying one service's window would have pushed the others back too. [Your true reason, in your words.]

**Follow-up 2**

> Q: What was their concern, and how did you treat it?
> A: [Specific risk, such as breaking changes landing during a release freeze.] I treated it as legitimate and asked what was driving it before I pushed.

**Follow-up 3**

> Q: How did you reach the resolution?
> A: I proposed feature flags so their service stayed compatible across both versions with no deployment lock, and I committed [specific support]. [How and when they agreed.]

**Follow-up 4**

> Q: What would you do differently?
> A: [For example: bring the partner team in before the schedule was set.] Replace this with a true lesson.

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
> A: I pick whichever gives users relief fastest and safest: rollback, feature flag or workaround first, then the root-cause fix on its own timeline.

**Follow-up 2**

> Q: What if you can't finish the fix before you move?
> A: I hand it off explicitly: written root-cause findings, repro steps, telemetry links, remaining work, and a named owner who has agreed to take it.

**Follow-up 3**

> Q: Who do you tell, and when?
> A: My manager and the incoming project's lead, early, so the transition date can move if needed. I also stay reachable during the first week. [What you actually did.]

**Follow-up 4**

> Q: Have you done this for real?
> A: Yes, on the Database Health Check. [The transition detail.] I stayed until I eliminated the failure mode, and read availability reached 99.999%.

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
> A: I had them present the design, credited their ideas by name in cross-org forums, and coached them privately on framing trade-offs. [What you actually did.]

**Follow-up 2**

> Q: How did you win over Maestro skeptics?
> A: I listened to team leads about workflow friction and rebuilt Maestro as modular plug-ins that fit their existing CI/CD pipelines, instead of mandating it.

**Follow-up 3**

> Q: What made peers trust it?
> A: I ran office hours and biweekly feedback forums with early adopters, so peers heard from peers. 10 teams and 100+ engineers adopted it, with about a 25% cycle-time reduction.

**Follow-up 4**

> Q: What did you learn?
> A: Skeptics change their minds when you solve their real problem and let them see results.

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
> A: When Rankie failed, the home feed failed with it and users saw errors on the main surface. A basic feed would have kept the feed available.

**Follow-up 2**

> Q: What was the real difference in assumptions?
> A: The service team believed ranked quality is the core experience, so a degraded feed might be worse than none. I was optimizing for availability, and they were optimizing for quality.

**Follow-up 3**

> Q: How did you resolve it?
> A: I made the assumptions explicit over several conversations and brought in the product team, so the decision rested on customer impact.

**Follow-up 4**

> Q: Do you still think you were right?
> A: My design wasn't adopted, and I think that was reasonable, since Rankie failures were infrequent and a backup feed was costly. I'd bring failure-frequency and cost data to the first conversation.

---

### 8. How do you manage multiple priorities, do you like to be in a place where priorities keep changing or prefer doing the same thing repeatedly?

**Answer**

I'm comfortable with changing priorities as long as there is a clear way to decide. At my level I'm driving a long initiative, like the Postgres and OS upgrades across about 40 production clusters, while production issues and cross-team asks land on top.

I handle it three ways. First, I rank by customer impact, risk and deadline, and I agree on those rules with stakeholders up front, so reprioritizing isn't a negotiation each time. Second, I protect focused time for the one or two things that matter most. Third, I decide quickly what to drop, delegate or defer, and I tell stakeholders so nobody is surprised.

I like variety, but I don't accept repeating toil, and at scale I eliminate it. That's why I built IRIS. It resolves about 30% of infrastructure requests on its own and cut triage latency by 45%, which freed engineers for the more interesting problems.

What I learned is that agreed decision rules, and automating the repetitive work, are what make constantly changing priorities sustainable.

**Follow-up 1**

> Q: How do you rank when everything is urgent?
> A: Customer impact, risk and deadline, with the rules agreed with stakeholders up front.

**Follow-up 2**

> Q: How do you protect focus?
> A: I protect time for the one or two things that matter most, decide quickly what to drop, delegate or defer, and tell stakeholders so nobody is surprised.

**Follow-up 3**

> Q: What do you do about repetitive work?
> A: I eliminate it. That's why I built IRIS, which resolves about 30% of requests on its own and cut triage latency by 45%.

**Follow-up 4**

> Q: Example of this on the Postgres/OS upgrade?
> A: With about 40 clusters in flight, production issues landed on top. I applied the same ranking rules and told stakeholders what moved.

---

### 9. You are organizing an off-site and a final venue is decided by majority vote, but some people who voted for other options say they won't join. How would you resolve this conflict?

**Answer**

I'd treat this as a buy-in problem, not a voting problem. I'll walk through my approach, then a real example of the same principle.

First, I'd talk to the objectors directly and one-on-one to find out what's behind it: cost, distance, accessibility, dietary needs, or feeling unheard. Often the reason is specific and fixable. Second, I'd be transparent about how the decision was made and the criteria used. Ideally I would have published those before the vote. Third, I'd adjust for real concerns without reopening the decision, and be honest about what I can't solve. The goal is that people feel heard even if they didn't get their first choice.

The real example is Secret Scanner. After I aligned leaders across organizations on the 60-day rotation standard, [team or lead] said they wouldn't onboard because [reason, such as a legacy stack the scanner couldn't cover]. I talked to them one-on-one and learned [the specific constraint]. I [extended discovery to cover their stack, or agreed a phased timeline], without reopening the standard. [They onboarded by [date].] [Imperfection: what I'd do differently.]

What I learned is to understand the underlying concern first, then design for it. On the embeddings disagreement, that meant dedicated node pools plus a kill switch.

**Follow-up 1**

> Q: What do you listen for in the one-on-ones?
> A: The specific reason: cost, distance, accessibility, dietary needs or feeling unheard. Often it's fixable.

**Follow-up 2**

> Q: Why not just reopen the vote?
> A: It would undermine the process. I'd explain the criteria, ideally published before the vote, and adjust for real concerns without reopening the decision.

**Follow-up 3**

> Q: What if someone still won't come?
> A: I'd be honest about what I can't solve and respect their choice. The goal is that people feel heard even if they didn't get their first choice.

**Follow-up 4**

> Q: Where have you done this?
> A: On Secret Scanner, [with [team] after the rotation standard was set]. [What you did.] On the embeddings disagreement, I understood the underlying concern and designed for it with node pools and a kill switch.

---

### 10. How do you accommodate new requirements that arise mid-task while still sticking to your original timelines? / Tell me about a time you had to pivot mid-project. / Tell me about a project where the requirements were not clear or kept changing

**Answer**

Maestro is my best example. It started as a hackathon idea, and I took it on with a goal of adoption across 15 teams, about 150 engineers. Teams had different workflows and stacks, many were skeptical of AI automation, and requirements kept shifting as feedback came in.

I did three things. First, I decided not to defend the original design. I listened to team leads and reshaped it with them into modular plug-ins that fit their existing CI/CD pipelines. Second, I triaged every new ask: needed for adoption, or nice-to-have. Nice-to-haves went into a visible backlog, so people could see their ask was recorded and why it wasn't first. Third, I made it scale without me, with reference architectures, setup scripts, self-service docs, office hours and biweekly forums.

Ten of the 15 teams and more than 100 engineers have adopted it, and the rest are in active evaluation. Adopted services saw about a 25% cycle-time reduction. I led 10 to 15 engineers building the plug-ins. The Infrastructure team owns it day to day. Next, I'm driving full adoption across all Viva Engage teams, and I'm pitching Maestro up to get adoption across other M365 teams. The Teams team has already started dogfooding it.

What I learned is that when requirements move, I hold the outcome, stay flexible on scope, and make the trade-offs visible.

**Follow-up 1**

> Q: How did you triage changing asks?
> A: I classified each ask as needed for adoption or nice-to-have, and put nice-to-haves in a visible backlog.

**Follow-up 2**

> Q: What did you change in the original design?
> A: I reshaped it with team leads into modular plug-ins that fit their CI/CD pipelines, instead of defending the hackathon design.

**Follow-up 3**

> Q: How did you scale without becoming the bottleneck?
> A: I built reference architectures, setup scripts and self-service docs, and ran office hours and biweekly forums.

**Follow-up 4**

> Q: What was the outcome?
> A: 10 of the 15 teams and 100+ of about 150 engineers are onboarded, the rest are in active evaluation, and adopted services saw about a 25% cycle-time reduction.

---

### 11. Tell me how you helped someone in your team to get better at some task / Describe a situation where a team member was struggling and what you learned from it

**Answer**

A senior engineer on my team, [name or role], was technically excellent but struggled to influence other teams. Their proposals for [area] stalled in review. I needed them to own [initiative, such as a plug-in surface for Maestro or an agent in IRIS], because I couldn't stay the only person other teams trusted.

I coached them in three steps. First, I diagnosed it: I reviewed how their proposals landed and saw they led with the design instead of the problem the other team felt. Second, I had them rehearse. They presented the proposal to me, I played the skeptical team lead, and we rewrote it around the other team's workflow friction, the same approach that worked for Maestro adoption. Third, I handed over: I stepped back and let them run the next review and the follow-up forum, and I stepped in once, to [specific moment].

They got [initiative] adopted by [number] teams and now run the [office hours or forum] without me. [Optional: promotion or larger scope.] [Imperfection: what was slow or didn't work at first.]

What I learned is that the most effective way to scale my impact is to build senior people who can earn trust across teams. It was slower in the short term, but it removed me as a bottleneck.

**Follow-up 1**

> Q: How did you avoid just doing it yourself?
> A: I let them run the next review and the follow-up forum, and I stepped in once, to [specific moment].

**Follow-up 2**

> Q: What did the coaching cover?
> A: I reviewed how their proposals landed, rehearsed with me as the skeptical team lead, and rewrote the proposals around the other team's workflow friction.

**Follow-up 3**

> Q: How did you know they improved?
> A: [Evidence, such as the initiative adopted by N teams, and them running the forum without me.]

**Follow-up 4**

> Q: What did you learn?
> A: Scaling my impact means building senior people who earn trust across teams. [Replace with a true lesson.]

---

### 12. Describe going above and beyond to help someone

**Answer**

During [a Postgres cluster cutover], [an engineer] on [another team] owned [their service's] migration and was anxious because the window was [outside normal hours].

I wasn't required to be there, but they were carrying a risk they had never carried. I joined, walked through the rollback plan with them beforehand, stayed on the bridge during the cutover, and helped them validate afterward.

Then I turned the cutover checklist into a runbook for the other deployment stamps, our independent production environments, so the help wasn't one-off. [[Number] teams used it across [number] stamps.]

It cost me [a few evenings]. [They] went on to run [later cutovers] themselves, and the runbook helped other teams. [Imperfection: what I'd do differently.]

What I learned is to show up when someone carries a risk they've never carried, and to turn one-off help into something reusable.

**Follow-up 1**

> Q: Why did you join when you weren't required?
> A: They were carrying a risk they'd never carried, [an out-of-hours cutover], and I believe in showing up for that.

**Follow-up 2**

> Q: What exactly did you do?
> A: I walked through the rollback plan with them beforehand, stayed on the bridge, and helped them validate afterward.

**Follow-up 3**

> Q: What did it cost you?
> A: [A few evenings], and it was worth it: [they] ran later cutovers themselves.

**Follow-up 4**

> Q: How did you make it last?
> A: I turned the cutover checklist into a runbook for the other deployment stamps, so it helped other teams. [How many teams used it.]

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
> A: I weighed the value of each action against its blast radius, and started with [lower-risk actions]. [Your true criteria.]

**Follow-up 2**

> Q: How did you get Trust and Security leadership to agree?
> A: I partnered with them on permission boundaries and blast-radius controls instead of asking for exceptions. [The specific compromise you reached.]

**Follow-up 3**

> Q: What did the trade-off cost you?
> A: Slower coverage at first: [for example, higher-risk actions stayed human-approved]. [Quantify it.]

**Follow-up 4**

> Q: Have you made a trade-off that went wrong?
> A: Yes. I moved a Hadoop-based metadata system to Cosmos DB. I ran a proof of concept, proved scalability and led the migration, but run cost reached nearly ten times the previous Hadoop cost, because discounts ended and pricing changed. I now model multi-year costs, including growth, discount expiry and pricing changes.

---

### 14. Describe one thing you have learned recently

**Answer**

Recently I learned to treat AI recommendations as hypotheses, and to build verification into agentic systems at the org level.

It started with a personal mistake. An AI model noted that the Kafka consumers committed offsets after every event, and suggested batching commits to reduce broker saturation. It sounded right, so I implemented it. Service teams soon got alerts for high lag and elevated HTTP 5xx errors, and I reverted my pull request right away. An optimization can be right in isolation and wrong in the system. I had validated the local logic but not the downstream assumptions.

The bigger step was turning that into a standard for the agentic work I lead. I contributed in three ways. First, I now validate downstream assumptions, test end to end, and define rollout and rollback criteria before applying any AI-suggested change. Second, I built that into IRIS: a two-stage verification pipeline and permission boundaries, so AI actions earn trust. Third, I [shared it as a review checklist that [number] teams now use for AI-assisted changes, and presented it at [forum]].

[Result: for example, since then, no AI-suggested change has caused a production incident on the teams using it.] The speed from AI only pays off when verification is built in.

**Follow-up 1**

> Q: Why did you implement the AI suggestion?
> A: It sounded right, and I applied it without enough end-to-end validation.

**Follow-up 2**

> Q: How did you find out it was wrong?
> A: Service teams got alerts for high lag and elevated HTTP 5xx errors, and I reverted my pull request right away.

**Follow-up 3**

> Q: What's your rule now?
> A: I validate downstream assumptions, test end to end, and define rollout and rollback criteria before any AI-suggested change.

**Follow-up 4**

> Q: How did you spread that beyond your own work?
> A: IRIS has a two-stage verification pipeline and permission boundaries, so AI actions earn trust. [I also shared a review checklist adopted by N teams.]

---

### 15. What would you like to have improved about your last role? / What would you like to see in your next manager?

**Answer**

About my current role, I'd like more protected time for long-term technical bets, because operational load often crowds them out. That's partly why I built automation like IRIS and Secret Scanner. But a clearer split between planned and reactive work would have helped, and I'd negotiate that earlier next time.

For my next manager, I'd want four things. Clear outcomes and context, with autonomy on how. Candid, regular feedback. Advocacy for the team's work with senior leadership, and help clearing cross-org blockers. And someone who encourages calculated risks and treats failures as learning, not blame. My Cosmos DB cost miss is the kind of learning I mean.

That combination lets me spend my time where I add the most leverage.

**Follow-up 1**

> Q: Why did operational load crowd out long-term bets?
> A: Reactive work took priority by default. That's partly why I built automation like IRIS and Secret Scanner.

**Follow-up 2**

> Q: What would you negotiate next time?
> A: A clearer split between planned and reactive work, earlier.

**Follow-up 3**

> Q: What do you need from a manager?
> A: Clear outcomes and context with autonomy on how, candid regular feedback, advocacy with senior leadership, and help clearing cross-org blockers.

**Follow-up 4**

> Q: How do you want failure handled?
> A: As learning, not blame, like my Cosmos DB cost miss.

---

### 16. How would you handle a situation where one team member takes all the credit for a group project?

**Answer**

I'll walk through how I'd handle it, then a real example of the same principle.

I'd start with a private, direct conversation, assuming thoughtlessness rather than malice, and describe the specific behavior and its impact. Then I'd make contribution visible going forward: shared design docs with named owners, credits in status updates, and letting each person present their own part. If it became a pattern, I'd bring in the manager with concrete examples.

I do this on Maestro, where adoption across teams depends on the engineers who build with it. I run biweekly feedback forums with early adopters, and [I credit the team leads and engineers who built plug-ins or shaped the design by name, in the forums and in my updates to leadership]. [For example, [name] built the [plug-in], and I had them present it to [audience].] That also makes the next team more willing to contribute.

On a smaller scale, in a design review of VentSpout's Kafka retry logic, a teammate proposed exponential backoff. I suggested jitter and framed it as building on his proposal. Retries stopped synchronizing and resource starvation eased, and he got the credit for the starting idea.

**Follow-up 1**

> Q: Why assume thoughtlessness rather than malice?
> A: It's usually true, and it keeps the conversation on specific behavior and its impact.

**Follow-up 2**

> Q: How do you make contribution visible?
> A: Shared design docs with named owners, credits in status updates, and letting each person present their own part.

**Follow-up 3**

> Q: When do you involve the manager?
> A: If it becomes a pattern, with concrete examples.

**Follow-up 4**

> Q: How do you model it yourself?
> A: On Maestro, [I credit the engineers who build plug-ins by name in forums and leadership updates, and have them present their work]. On the VentSpout retry review, I framed jitter as building on a teammate's proposal.

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
> A: Licensing cost millions annually and provisioning took days. I accepted real engineering cost and risk, and backed the decision with numbers.

**Follow-up 2**

> Q: How did you handle legal risk?
> A: I worked with Microsoft legal on licensing, IP and contribution requirements, and treated them as architectural inputs.

**Follow-up 3**

> Q: What did you build beyond TLS?
> A: I migrated the platform to AKS and wrote Helm charts and declarative CI/CD for provisioning, autoscaling and zero-downtime rolling upgrades.

**Follow-up 4**

> Q: What would you do differently?
> A: I'd bring legal in even earlier with a written risk plan. The result was provisioning and patching in under 15 minutes instead of days, and more than $10M a year saved.

---

### 18. Tell me about a problem you had to solve that required in-depth thought and analysis

**Answer**

The deepest analysis I've done was the Database Health Check. Tier-1 services had intermittent read failures while every dashboard looked healthy. It affected all 15 Viva Engage teams, about 150 engineers.

I took it on, starting by mapping the read path end to end: client, connection pooler and replicas. Then I instrumented per-node latency and tested each layer with telemetry-driven hypotheses. That isolated two failure modes. One replica had severe disk I/O stalls. And the pooler's TCP health check verified only connectivity, so it kept routing traffic to the sick node.

The health checks measured what had been chosen to measure, not what users depend on. So I replaced them with synthetic queries that test real read behavior, and added circuit breaking.

Read availability reached 99.999%, and the approach became an org-wide operational template. [Baseline: [N] tier-1 services and about [N] customers were affected by the failures, and [team] now owns the template.]

What I learned is that a green dashboard is only as good as what it measures, so health checks should test what users depend on.

**Follow-up 1**

> Q: Why did every dashboard look healthy?
> A: A dashboard only measures what you chose to measure. The pooler's TCP health check verified connectivity only.

**Follow-up 2**

> Q: How did you find the root cause?
> A: I mapped the read path (client, pooler, replicas), instrumented per-node latency, and tested each layer with telemetry-driven hypotheses.

**Follow-up 3**

> Q: What were the two failure modes?
> A: A replica with severe disk I/O stalls, and a pooler that kept routing to the sick node.

**Follow-up 4**

> Q: What was the fix and result?
> A: I replaced the checks with synthetic queries that test real read behavior and added circuit breaking. Read availability reached 99.999%, and the approach became an org-wide operational template.

---

### 19. What have you done to develop your leadership skills?

**Answer**

I've grown most by taking on work that crosses organizational boundaries, and each project taught me something different.

On the Postgres upgrade across about 40 clusters, I learned to build VP-level confidence and align stakeholders around a high-risk plan, including rollback planning. With Secret Scanner and Maestro, I learned that adoption comes from understanding teams and giving them docs and office hours, not mandates. Secret Scanner reached 100% adoption across all 15 Viva Engage teams, and Maestro now serves more than 100 engineers. With IRIS, I partnered with Trust and Security leadership on permission boundaries and blast-radius controls, so autonomous actions could earn trust.

I also learn from my own misses, like the reverted Kafka change, which taught me to validate end to end. [DRAFT: I also invest in other senior engineers, for example coaching [name or role] to own [initiative] across teams.] I also set the roadmap for Maestro beyond Viva Engage: full adoption across all Viva Engage teams, and I'm pitching it up for adoption across other M365 teams, with the Teams team already dogfooding it.

The shift for me has been from solving the problem myself to creating the conditions for other teams to succeed.

**Follow-up 1**

> Q: What was hardest about the Postgres upgrade?
> A: Building VP-level confidence in a high-risk plan, including rollback planning.

**Follow-up 2**

> Q: What did you learn from Secret Scanner and Maestro?
> A: Adoption comes from understanding teams and giving them docs and office hours, not mandates: 100% adoption across Viva Engage teams and 100+ engineers on Maestro.

**Follow-up 3**

> Q: What did IRIS teach you?
> A: I partnered with Trust and Security leadership on permission boundaries and blast-radius controls.

**Follow-up 4**

> Q: How have setbacks shaped you?
> A: The reverted Kafka change taught me to validate end to end. I've moved from solving problems myself to creating conditions for others.

---

### 20. Give me an example of a tough or critical piece of feedback you received

**Answer**

A senior leader told me my Postgres upgrade updates were too technical, and he couldn't tell what decisions he needed to make. It stung, but he was right.

I looked at my updates from his side. He needed to act, and I was giving him detail. So I changed the format: lead with status and risk in business terms, state the decision needed, and keep technical detail in an appendix.

Executive alignment became much easier, which helped a high-risk upgrade move forward.

What I learned is that communication is judged by whether the audience can act on it.

**Follow-up 1**

> Q: What exactly was the feedback? 
> A: My Postgres updates were too technical, and he couldn't tell what decisions he needed to make.

**Follow-up 2**

> Q: How did you react? 
> A: It stung, but he was right, so I changed the format.

**Follow-up 3**

> Q: What did you change? 
> A: I lead with status and risk in business terms, state the decision needed, and keep technical detail in an appendix.

**Follow-up 4**

> Q: What was the impact? 
> A: Executive alignment became easier, which helped the upgrade move forward. Communication is judged by whether the audience can act on it.

---

### 21. Give me an example of when you had to make an important decision and had to decide between moving forward or gathering more information

**Answer**

The Postgres and OS upgrades covered about 40 production clusters and affected all 15 Viva Engage teams, about 150 engineers. The risk was high, but the CVE and Trust requirements were pressing, so I couldn't wait for perfect information.

My framework was reversibility. For reversible parts, like feature flags for cross-version compatibility, I moved forward fast. For irreversible parts, I went deeper before committing. For the OS, I chose native logical replication to a mirrored Ubuntu cluster. That avoided an Ubuntu 18.04 issue where a C library change invalidates database indexes, and it kept the cutover short.

I aligned executives on a clear plan, including rollback, and led execution across all clusters and deployment stamps.

The Postgres upgrade averaged roughly one hour of downtime per cluster, the OS cutover took about five minutes, and related incidents fell 40%. The Infrastructure team owns the Postgres tooling today. I led 10 to 15 engineers, and the upgrade affected all 15 teams. [Baseline: [N] customers and about [amount] in refund exposure were at risk.]

The Kafka offset change is the opposite case. I moved on an AI suggestion without enough validation and had to revert.

What I learned is that the more irreversible and widespread the impact, the more evidence I want. For reversible changes, I move fast with clear rollback criteria.

**Follow-up 1**

> Q: Which parts were reversible?
> A: Feature flags for cross-version compatibility. I moved forward fast on those and went deeper on the irreversible parts.

**Follow-up 2**

> Q: Why logical replication for the OS?
> A: Native logical replication to a mirrored Ubuntu cluster avoided the Ubuntu 18.04 index-invalidation issue and kept the cutover short.

**Follow-up 3**

> Q: What were the results?
> A: About 40 clusters, roughly one hour of downtime per cluster for Postgres, about five minutes for the OS cutover, and related incidents down 40%.

**Follow-up 4**

> Q: When do you gather more evidence?
> A: The more irreversible and widespread the impact, the more evidence I want. For reversible changes I move fast with clear rollback criteria, unlike the Kafka change I had to revert.

---

## Questions I Ask the Interviewer

1. What does success look like in the first 90 days?
2. What's the most important problem you're hoping this hire will solve?
3. What's the biggest challenge the team is facing right now?
