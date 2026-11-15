# Behavioral Questions & Answers

Source: Work Stories.xlsx (Questions & Answers). Answers are narrated as a Senior Principal Engineer.

## Answer Framework

Each answer follows: context and why it mattered; what I learned by investigating; the key insight or proposal; audience-specific buy-in; what I personally led; the result (metric, then the more important outcome); and the learning.

## Index

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

---

## 1. Tell me about yourself (TMAY)

### Answer

I build the infrastructure that lets hundreds of engineers move faster without breaking things. I'm a Senior Principal Software Engineer on the Viva Engage infrastructure team at Microsoft, with 18 years of experience in distributed systems. My job is setting technical direction for platforms that many teams depend on, and bringing 100+ engineers along with it. I focus on reliability, cost efficiency and developer productivity.

Let me give you three examples. First, I led Secret Scanner, a central credential discovery and rotation platform. It reached 100% adoption across Viva Engage teams, with zero certificate or secret-related outages. Second, I drove our search modernization. I led the move to a fork of Elasticsearch running on AKS, which cut provisioning and patching from days to under 15 minutes and saved more than $10M a year. Third, I conceived IRIS, a multi-agent system that resolves about 30% of infrastructure requests on its own and cut triage latency by 45%. I also lead Maestro, an SDLC platform that more than 100 engineers across 10 teams now use.

What ties them together is that each removed a systemic problem for many teams at once. I want to apply that to consumer-scale infrastructure and agentic AI for operations, where the leverage across organizations is even larger.

**Follow-up 1**

> Q: Why do you say you've spent 18 years on distributed systems, and what ties your three examples together?
> A: Each one is about removing a systemic problem for many teams: Secret Scanner for credential outages, the search fork for cost and toil, and IRIS for repetitive requests. The common thread is reliability, cost and developer productivity at org scale.

**Follow-up 2**

> Q: How do you bring 100+ engineers along without formal authority?
> A: I make adoption easy and let results speak. With Maestro I used plug-ins, docs and office hours, and 10 teams (100+ engineers) came on board.

**Follow-up 3**

> Q: Which of the three examples was hardest?
> A: IRIS, because trust in autonomous actions has to be earned. I partnered with Trust and Security leadership on permission boundaries and blast-radius controls, and it now resolves about 30% of requests and cut triage latency 45%.

**Follow-up 4**

> Q: Why consumer-scale infrastructure and agentic AI for operations next?
> A: The leverage across organizations is larger there, and it extends what I did with IRIS and Maestro. I'd tailor this part to each company.

---

## 2. Tell me about your favorite project / most impactful project / a time you solved an ambiguous problem

### Answer

My favorite project is Secret Scanner, because I set the direction for how the entire Viva Engage org manages credentials, and I owned it end to end.

Expired certificates and secrets kept causing Viva Engage outages. Microsoft's Trust requirements called for rotation every 60 days, but teams tracked secrets in spreadsheets across very different stacks, with no central view. Executive leadership set a goal of zero certificate and secret outages.

I started by understanding how teams actually tracked and rotated credentials, and why. The stacks differed for reasonable reasons, so a single mandated approach would have failed. The key insight was that we didn't need teams to change their architecture. A platform could discover credentials where they already lived, and governance could be firm on compliance while respecting each team's design.

Getting buy-in took different conversations with different audiences. With executive leadership, I focused on the zero-outage goal and Trust compliance. With leaders across organizations, I aligned on a standard that was firm on 60-day rotation but flexible on architecture. With engineers, I showed that onboarding was self-service, with docs and weekly office hours, so they wouldn't depend on me.

I led the design and the cross-org rollout. The platform does automated discovery across Azure Key Vaults, VMs and clusters, deduplicates credentials, removes obsolete ones, and reports centrally with alerts 15 days before expiry.

We reached 100% adoption across Viva Engage teams, with thousands of credentials monitored, and achieved the zero-outage goal. More importantly, teams could self-serve without me.

The learning for me was that a platform spanning organizations succeeds only when adoption is easy. Standards, docs and sustained support matter as much as the code.

**Follow-up 1**

> Q: Why was adoption the hardest part of Secret Scanner?
> A: Teams were on very different stacks and tracked secrets in different ways. I used onboarding docs and weekly office hours so they could self-serve rather than depend on me.

**Follow-up 2**

> Q: How did you keep standards firm without forcing one architecture on every team?
> A: I defined governance that was firm on compliance (60-day rotation) but respected each team's architecture, and aligned leaders across orgs on it before rollout.

**Follow-up 3**

> Q: What would you do differently?
> A: I'd bring pilot teams in earlier to shape the reporting before the wider rollout.

**Follow-up 4**

> Q: How do you know it worked?
> A: 100% adoption across Viva Engage teams, thousands of credentials monitored, alerts 15 days before expiry, and the zero-outage goal achieved.

---

## 3. Tell me about a time when you had to address underperformance in your team

### Answer

During a large cross-team migration, an engineer I was mentoring kept missing commitments, and some of his work needed rework. That put a multi-team schedule at risk.

Before assuming a performance problem, I met him one-on-one to understand what was happening. The tasks were ambiguous and he was hesitant to ask questions. So the issue looked like clarity, not capability.

I changed how the work was framed. I broke it into milestones with clear acceptance criteria and paired with him on the first one. I set weekly check-ins with specific feedback, and I was candid that the expectations were non-negotiable, so clarity didn't come at the cost of standards.

Within about two months he was delivering independently and took ownership of a migration component, and the schedule risk went away.

At my scope, the bigger result was systemic. When one person struggles with ambiguity, others usually do too, so I now write acceptance criteria into the design docs I set for teams.

The learning for me was to fix clarity and feedback first, and to escalate early with a documented plan if that doesn't work, rather than letting it drift.

**Follow-up 1**

> Q: How did you know it was a clarity problem and not a capability problem? 
> A: I met him one-on-one before assuming anything. The tasks were ambiguous and he was hesitant to ask questions, so I fixed the clarity first.

**Follow-up 2**

> Q: How did you stay candid without demoralizing him? 
> A: I gave specific weekly feedback and paired with him on the first milestone, and I was clear the expectations were non-negotiable.

**Follow-up 3**

> Q: What did you change for the wider team? 
> A: I now write acceptance criteria into the design docs I set, because when one person struggles with ambiguity others usually do too.

**Follow-up 4**

> Q: What if it hadn't improved? 
> A: I'd escalate early with a documented plan rather than let it drift. Here he was delivering independently in about two months.

---

## 4. Tell me about a conflict you had at work / Discuss a time when you had conflicting perspectives with teammates and how you handled it / Tell me about a time you had a conflict with a coworker. How did you resolve it?

### Answer

This was a long-lived decision for the search team's embeddings workload on a shared platform, with real cost and reliability consequences across teams. The question was whether to run embeddings on the existing search clusters or build separate ones.

I favored the existing clusters to control cost of goods sold, our run cost, and to avoid operating more clusters. My manager preferred separate clusters because of noisy-neighbor risk. We disagreed openly.

Before pushing, I made sure I understood his concern, because it was legitimate: embeddings traffic could hurt search latency for everyone. I brought data on cost and operational overhead so we debated facts, not preferences. The key move was reframing the question around our real goals: cost, operational complexity and isolation. Once we framed it that way, it wasn't a choice between two clusters anymore.

The solution was to run embeddings on the existing clusters in dedicated node pools, with a kill switch for embeddings. That gave us isolation without a new set of clusters, and both of us owned the result.

The learning for me was to separate positions from underlying concerns, and to bring a proposal along with my objection. In hindsight I'd have proposed node pools plus a kill switch in my first pass.

**Follow-up 1**

> Q: Why did you favor existing clusters over separate ones?
> A: To control COGS and avoid operating more clusters. I brought cost and operational-overhead data so we debated facts, not preferences.

**Follow-up 2**

> Q: What was your manager's concern, and how did you treat it?
> A: Noisy-neighbor risk: embeddings traffic could hurt search latency for everyone. I treated it as legitimate and made sure I understood it before pushing.

**Follow-up 3**

> Q: How did you reach the resolution?
> A: We reframed around cost, complexity and isolation, and landed on dedicated node pools on existing clusters plus an embeddings kill switch.

**Follow-up 4**

> Q: What would you do differently?
> A: Propose node pools plus a kill switch in my first pass.

---

## 5. How do you prioritize fixing a serious bug with complaining users when you are transitioning to a new project in a few days?

### Answer

The bug comes first, because customer pain doesn't wait for my transition date. I haven't faced exactly this setup, so I'll describe how I'd handle it.

First, I'd understand the severity and blast radius, and tell the affected users we're working on it. Second, I'd mitigate fast, with a rollback, feature flag or workaround, so users get relief even if the root-cause fix takes longer. Third, if I can't fully close it, I'd make the handoff explicit: written root-cause findings, repro steps, telemetry links, remaining work, and a named owner who has agreed to take it.

I'd tell my manager and the incoming project's lead early so the transition date can move if needed, and I'd stay reachable during the first week.

This mirrors my Database Health Check work, where I stayed on the problem until the failure mode was eliminated, not just patched, and we reached 99.999% read availability. The learning there was that the customer's problem, not my calendar, defines when the work is done.

**Follow-up 1**

> Q: How do you decide between rollback and a workaround?
> A: Whichever gives users relief fastest and safest: rollback, feature flag or workaround first, then the root-cause fix on its own timeline.

**Follow-up 2**

> Q: What if you can't finish the fix before you move?
> A: I hand off explicitly: written root-cause findings, repro steps, telemetry links, remaining work and a named owner who has agreed to take it.

**Follow-up 3**

> Q: Who do you tell, and when?
> A: My manager and the incoming project's lead early, so the transition date can move if needed, and I stay reachable the first week.

**Follow-up 4**

> Q: Have you done this for real?
> A: Not with this exact setup, but on Database Health Check I stayed until the failure mode was eliminated and reached 99.999% read availability.

---

## 6. Describe advocating for a team mate to help them fit in at work / Describe changing a colleague's opinion from negative to positive

### Answer

I have two examples. The first is small. A newer engineer was quiet in design reviews, and some senior people read that as lack of depth. I knew his work was strong, so I had him present his design, credited his ideas by name in cross-team forums, and coached him privately on framing trade-offs. Within a few months other teams pulled him into their reviews.

The second, changing opinions, is Maestro, our multi-agent SDLC platform. Many engineers across teams were skeptical of AI automation, and a mandate wouldn't have worked.

I started by listening to team leads about their workflow friction rather than defending the platform. The key insight was that skeptics weren't rejecting the idea, they were rejecting disruption. So I rebuilt Maestro as modular plug-ins that fit into their existing CI/CD pipelines, and they could adopt it piece by piece.

Different audiences needed different messages. For team leads, it was about fit with their pipelines. For engineers, it was reference architectures, setup scripts and docs so they could get started on their own. For skeptics, it was hearing from peers, so I ran office hours and biweekly feedback forums with early adopters.

We onboarded 10 teams, more than 100 engineers, with about a 25% cycle-time reduction for adopted services.

The learning for me was that skeptics change their minds when you solve their real problem and let them see results.

**Follow-up 1**

> Q: How did you advocate for the quiet engineer? 
> A: I had him present his design, credited his ideas by name in cross-team forums, and coached him privately on framing trade-offs.

**Follow-up 2**

> Q: How did you win over Maestro skeptics?
> A: I listened to team leads about workflow friction and rebuilt Maestro as modular plug-ins fitting existing CI/CD pipelines, instead of mandating it.

**Follow-up 3**

> Q: What made peers trust it?
> A: Office hours and biweekly feedback forums with early adopters, so peers heard from peers. 10 teams and 100+ engineers adopted, with about 25% cycle-time reduction.

**Follow-up 4**

> Q: What did you learn?
> A: Skeptics change their minds when you solve their real problem and let them see results.

---

## 7. Tell me about a time you handled a disagreement that arose from differences in assumptions

### Answer

This was a disagreement about Homefeed and Rankie. Rankie is the ranking service behind the home feed, and when it failed, the home feed failed with it, so users saw errors on the main surface.

I proposed a fail-open design: if Rankie is down, return a basic feed. The service team disagreed. As I dug into why, I found we were working from different assumptions. They assumed ranked quality is the core experience, so a degraded feed might be worse than none. I was optimizing for availability, and they were optimizing for quality.

The key step was making those assumptions explicit. Over several conversations I walked through the availability trade-off, and I helped bring in the product team so the decision rested on customer impact, not engineering opinion.

The fallback-feed work went to the backlog, since Rankie failures were infrequent and a backup feed was costly. My design wasn't adopted at that point, and I think that was a reasonable call.

The learning for me was to name assumptions early and to bring failure frequency, impact and cost data to the very first conversation, so we start from facts instead of positions.

**Follow-up 1**

> Q: Why did you propose fail-open?
> A: When Rankie failed the home feed failed with it and users saw errors on the main surface; a basic feed kept availability.

**Follow-up 2**

> Q: What was the real difference in assumptions?
> A: The service team believed ranked quality is the core experience, so a degraded feed might be worse than none. We optimized for availability versus quality.

**Follow-up 3**

> Q: How did you resolve it?
> A: I made assumptions explicit over several conversations and brought in the product team so the decision rested on customer impact.

**Follow-up 4**

> Q: Do you still think you were right?
> A: My design wasn't adopted, and I think that was reasonable since Rankie failures were infrequent and a backup feed was costly. I'd bring failure-frequency and cost data to the first conversation.

---

## 8. How do you manage multiple priorities, do you like to be in a place where priorities keep changing or prefer doing the same thing repeatedly?

### Answer

I'm comfortable with changing priorities as long as there is a clear way to decide. At my level I'm usually driving a long initiative, like the Postgres and OS upgrades across about 40 clusters, while production issues and cross-team asks land on top.

My approach has three parts. First, I rank by customer impact, risk and deadline, and I agree on those rules with stakeholders up front, so reprioritizing isn't a negotiation each time. Second, I protect focused time for the one or two things that matter most. Third, I decide quickly what to drop, delegate or defer, and I tell stakeholders so nobody is surprised.

I like variety, but I don't like repeating toil, and at scale I eliminate it. That's why I built IRIS, which resolves about 30% of infrastructure requests on its own and cut triage latency by 45%. That freed engineers for the changing, more interesting problems.

The learning for me was that agreed decision rules and automating the repetitive work are what make constantly changing priorities sustainable.

**Follow-up 1**

> Q: How do you rank when everything is urgent?
> A: Customer impact, risk and deadline, with the rules agreed with stakeholders up front.

**Follow-up 2**

> Q: How do you protect focus?
> A: I protect time for the one or two things that matter most and quickly drop, delegate or defer the rest, telling stakeholders so nobody is surprised.

**Follow-up 3**

> Q: What do you do about repetitive work?
> A: I eliminate it. That's why I built IRIS, which resolves about 30% of requests and cut triage latency 45%.

**Follow-up 4**

> Q: Example of this on the Postgres/OS upgrade?
> A: With about 40 clusters in flight, production issues landed on top; I applied the same ranking rules and communicated what moved.

---

## 9. You are organizing an off-site and a final venue is decided by majority vote, but some people who voted for other options say they won't join. How would you resolve this conflict?

### Answer

I'd treat this as a buy-in problem, not a voting problem. I haven't run this exact situation, so I'll describe my approach.

First, I'd talk to the objectors one-on-one to learn what is behind it: cost, distance, accessibility, dietary needs, or feeling unheard. Often the reason is specific and fixable. Second, I'd be transparent about how the decision was made and the criteria used. Ideally I would have published those before the vote. Third, I'd make adjustments that address real concerns without reopening the decision, and be honest about what I can't solve.

The goal is that people feel heard even if they didn't get their first choice.

It's the approach I used on the embeddings cluster disagreement: understand the underlying concern, then design something that addresses it. There, the solution was dedicated node pools plus a kill switch.

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
> A: The embeddings disagreement: understand the underlying concern, then design for it with node pools and a kill switch. (Hypothetical off-site; no personal story.)

---

## 10. How do you accommodate new requirements that arise mid-task while still sticking to your original timelines? / Tell me about a time you had to pivot mid-project. / Tell me about a project where the requirements were not clear or kept changing

### Answer

Maestro is my best example. It started as a hackathon idea, and the goal grew into adoption across 15 teams, about 150 engineers. Teams had different workflows and stacks, many were skeptical of AI automation, and requirements kept shifting as feedback came in.

I started by listening to team leads. The key insight was that I shouldn't defend the original design. I reshaped it with them into modular plug-ins that fit their existing CI/CD pipelines.

To handle the stream of new asks without losing the timeline, I triaged each one by whether it was needed for adoption or was a nice-to-have. Nice-to-haves went into a visible backlog, so people could see their ask was recorded and why it wasn't first.

Then I made it scale without me. I built reference architectures, setup scripts and self-service docs, and ran office hours and biweekly forums.

We onboarded 10 teams and more than 100 engineers, the rest are in active evaluation, and adopted services saw about a 25% cycle-time reduction.

The learning for me was that when requirements move, I hold the outcome, stay flexible on scope, and make the trade-offs visible.

**Follow-up 1**

> Q: How did you triage changing asks?
> A: Each ask was classified as needed for adoption or nice-to-have, with nice-to-haves in a visible backlog.

**Follow-up 2**

> Q: What did you change in the original design?
> A: I reshaped it with team leads into modular plug-ins fitting their CI/CD pipelines rather than defending the hackathon design.

**Follow-up 3**

> Q: How did you scale without becoming the bottleneck?
> A: Reference architectures, setup scripts, self-service docs, office hours and biweekly forums.

**Follow-up 4**

> Q: What was the outcome?
> A: 10 of 15 teams and 100+ of about 150 engineers onboarded, the rest in active evaluation, with about 25% cycle-time reduction.

---

## 11. Tell me how you helped someone in your team to get better at some task / Describe a situation where a team member was struggling and what you learned from it

### Answer

An engineer on my team struggled with production debugging. He would jump to fixes without evidence, which slowed incidents.

Instead of taking over, I tried to understand what was missing. It wasn't effort, it was a mental model for investigating. So I used my Database Health Check investigation as a teaching case, walking him through mapping the read path, testing each layer, instrumenting per-node latency, and testing hypotheses with telemetry.

Then I had him lead the next incident while I coached with questions and reviewed his write-ups.

Within a couple of months his investigations were systematic and he ran incident reviews. At scale, I turned that walkthrough into onboarding material, so it helps more than one person.

The learning for me was that struggling is often a missing mental model, not lack of ability, and that coaching works best when it is hands-on and gradual.

**Follow-up 1**

> Q: How did you avoid taking over during incidents? 
> A: I used Database Health Check as a teaching case, then had him lead the next incident while I coached with questions.

**Follow-up 2**

> Q: What did the walkthrough cover? 
> A: Mapping the read path, testing each layer, instrumenting per-node latency and testing hypotheses with telemetry.

**Follow-up 3**

> Q: How did you know he improved? 
> A: Within a couple of months his investigations were systematic and he ran incident reviews.

**Follow-up 4**

> Q: What did you learn? 
> A: Struggling is often a missing mental model, not lack of ability. I turned the walkthrough into onboarding material so it helps more than one person.

---

## 12. Describe going above and beyond to help someone

### Answer

During a Postgres cluster cutover, a junior engineer on another team owned his service's migration. He was anxious because the window was outside normal hours.

I wasn't required to be there, but I understood he was carrying a risk he had never carried. I joined, walked through the rollback plan with him beforehand, stayed on the bridge during the cutover, and helped him validate afterward.

Then I turned our checklist into a runbook for the other deployment stamps, our independent production environments, so the help wasn't one-off.

It cost me a few evenings. He went on to run later cutovers himself, and the runbook helped other teams.

The learning for me was to show up when someone carries a risk they've never carried, and to turn one-off help into something reusable.

**Follow-up 1**

> Q: Why did you join when you weren't required? 
> A: He carried a risk he'd never carried, an out-of-hours cutover, and I believe in showing up for that.

**Follow-up 2**

> Q: What exactly did you do? 
> A: Walked through the rollback plan beforehand, stayed on the bridge and helped him validate afterward.

**Follow-up 3**

> Q: What did it cost you? 
> A: A few evenings, and it was worth it: he ran later cutovers himself.

**Follow-up 4**

> Q: How did you make it last? 
> A: I turned our checklist into a runbook for the other deployment stamps, so it helped other teams.

---

## 13. Tell me about a time when you had to make a trade-off between two competing priorities or options / Tell me about a time when you had to make tradeoffs between quality and cost

### Answer

My most instructive trade-off was moving a metadata system from Hadoop to Azure Cosmos DB: operational burden against cost.

Hadoop needed specialized expertise to run. A managed service would cut that burden, but it might cost more. A colleague challenged me directly, saying Cosmos DB would be expensive and might not scale.

I took the concern seriously and ran a proof of concept, then presented evidence on scalability and operational benefits. We migrated and retired Hadoop, and Cosmos DB scaled fine.

But our run cost reached nearly ten times the previous Hadoop cost, because discounts ended and pricing changed. So I won the technical argument and missed on cost.

The learning for me was that proving scalability doesn't prove long-term viability. Now I model multi-year costs, including growth, discount expiry and pricing changes, and I give cost objections the same rigor as technical ones.

By contrast, in search modernization I deliberately accepted the engineering cost of forking Elasticsearch, with the numbers modeled up front, and that saved more than $10M a year.

**Follow-up 1**

> Q: Why did you choose Cosmos DB over Hadoop?
> A: Hadoop needed specialized expertise; a managed service would cut operational burden, with the risk of higher cost.

**Follow-up 2**

> Q: How did you handle your colleague's pushback?
> A: I ran a proof of concept and presented evidence on scalability and operational benefits.

**Follow-up 3**

> Q: Why did cost reach nearly 10x?
> A: Discounts ended and pricing changed. I won the technical argument and missed on cost.

**Follow-up 4**

> Q: What do you do differently now?
> A: I model multi-year costs including growth, discount expiry and pricing changes, and treat cost objections as rigorously as technical ones. In search modernization I accepted engineering cost deliberately and saved more than $10M a year.

---

## 14. Describe one thing you have learned recently

### Answer

Recently I learned to treat AI recommendations as hypotheses.

An AI model noted that our Kafka consumers committed offsets after every event. It suggested batching commits to reduce broker saturation. It sounded right, so I implemented it. Soon service teams got alerts for high lag and elevated HTTP 5xx errors, and I reverted my pull request.

The insight was that an optimization can be right in isolation and wrong in the system. I had validated the local logic but not the downstream assumptions.

Now I validate downstream assumptions, test end-to-end, and define rollout and rollback criteria before applying any AI-suggested change.

Since I lead agentic work like IRIS and Maestro, I've made this a team standard. IRIS has a two-stage verification pipeline and permission boundaries, so AI actions earn trust.

The learning for me was that speed from AI is only valuable when verification is built in.

**Follow-up 1**

> Q: Why did you implement the AI suggestion?
> A: It sounded right, and I applied it without enough end-to-end validation.

**Follow-up 2**

> Q: How did you find out it was wrong?
> A: Service teams got alerts for high lag and elevated HTTP 5xx errors, and I reverted my pull request.

**Follow-up 3**

> Q: What's your rule now?
> A: Validate downstream assumptions, test end-to-end, and define rollout and rollback criteria before any AI-suggested change.

**Follow-up 4**

> Q: How does that apply to IRIS and Maestro?
> A: I made it a team standard; IRIS has a two-stage verification pipeline and permission boundaries so AI actions earn trust.

---

## 15. What would you like to have improved about your last role? / What would you like to see in your next manager?

### Answer

About my current role, I'd like more protected time for long-term technical bets, because operational load often crowds them out. That is partly why I built automation like IRIS and Secret Scanner. But a clearer split between planned and reactive work would have helped, and I'd negotiate it earlier next time.

For my next manager, I'd want four things. First, someone who sets clear outcomes and context and gives me autonomy on how. Second, candid, regular feedback. Third, someone who advocates for the team's work with senior leadership and clears cross-org blockers. Fourth, someone who encourages calculated risks and treats failures as learning rather than blame. My Cosmos DB cost miss is an example of the kind of learning I mean.

That combination lets me spend my time on the problems where I add the most leverage.

**Follow-up 1**

> Q: Why did operational load crowd out long-term bets?
> A: Reactive work took priority by default. That's partly why I built automation like IRIS and Secret Scanner.

**Follow-up 2**

> Q: What would you negotiate next time?
> A: A clearer split between planned and reactive work, earlier.

**Follow-up 3**

> Q: What do you need from a manager?
> A: Clear outcomes and context with autonomy on how, candid regular feedback, advocacy with senior leadership, and clearing cross-org blockers.

**Follow-up 4**

> Q: How do you want failure handled?
> A: As learning, not blame, like my Cosmos DB cost miss.

---

## 16. How would you handle a situation where one team member takes all the credit for a group project?

### Answer

I haven't had this exact situation, so I'll describe how I'd handle it.

I'd start with a private conversation, assuming thoughtlessness rather than malice, and describe the specific behavior and its impact. Then I'd make contribution visible going forward: shared design docs with named owners, credits in status updates, and letting each person present their own part. If it became a pattern, I'd bring in the manager with concrete examples.

I try to model this myself. In a design review of VentSpout's Kafka retry logic, a teammate proposed exponential backoff. I suggested adding jitter, and I framed it as building on his proposal. Retries stopped synchronizing and resource starvation eased, and it was a team result.

The learning for me is that credit habits are set by how the team works, so I make attribution part of the process.

**Follow-up 1**

> Q: Why assume thoughtlessness rather than malice?
> A: It's usually true, and it keeps the conversation about specific behavior and its impact.

**Follow-up 2**

> Q: How do you make contribution visible?
> A: Shared design docs with named owners, credits in status updates, and letting each person present their own part.

**Follow-up 3**

> Q: When do you involve the manager?
> A: If it becomes a pattern, with concrete examples.

**Follow-up 4**

> Q: How do you model it yourself?
> A: In the VentSpout Kafka retry review, a teammate proposed exponential backoff, I suggested jitter and framed it as building on his proposal. Retries stopped synchronizing and starvation eased.

---

## 17. Tell about a time when you had to go against the norm and push for a change / Tell me about a time when you made an unpopular decision

### Answer

The norm was paying for commercial Elasticsearch licensing, mainly for inter-node TLS, and I pushed against it.

Provisioning took days, patching was risky, and licensing cost millions annually. I looked at what we were really paying for. The key insight was that the license was mostly buying inter-node TLS, which we could build ourselves on open source. So I proposed forking open-source Elasticsearch and building native TLS transport security. It was real engineering cost and risk, and I said so explicitly.

Getting buy-in meant treating legal and open-source governance as architectural inputs, not afterthoughts. I worked with Microsoft legal teams on licensing, IP and contribution requirements, and I backed the proposal with numbers.

I led the design and implementation. I migrated the platform to AKS and wrote Helm charts and declarative CI/CD for provisioning, autoscaling and zero-downtime rolling upgrades.

Provisioning and patching dropped from days to under 15 minutes, and we saved more than $10M a year in run cost.

The learning for me was that going against the norm works when you take the risks explicitly, bring in legal early, and back the choice with numbers. I'd bring legal in even earlier next time, with a written risk plan.

**Follow-up 1**

> Q: Why was forking Elasticsearch worth the risk?
> A: Licensing cost millions annually and provisioning took days. I accepted real engineering cost, backed by numbers.

**Follow-up 2**

> Q: How did you handle legal risk?
> A: I worked with Microsoft legal on licensing, IP and contribution requirements, treating them as architectural inputs.

**Follow-up 3**

> Q: What did you build beyond TLS?
> A: Migration to AKS, Helm charts and declarative CI/CD for provisioning, autoscaling and zero-downtime rolling upgrades.

**Follow-up 4**

> Q: What would you do differently?
> A: Bring legal in even earlier with a written risk plan. Result: days to under 15 minutes, more than $10M a year saved.

---

## 18. Tell me about a problem you had to solve that required in-depth thought and analysis

### Answer

The deepest analysis I've done was the Database Health Check. Tier-1 services had intermittent read failures while every dashboard looked healthy.

I started by mapping the read path end to end: client, connection pooler and replicas. Then I instrumented per-node latency and tested each layer with hypotheses driven by telemetry. That isolated two failure modes. One replica had severe disk I/O stalls. And the pooler's TCP health check verified only connectivity, so it kept routing traffic to the sick node.

The key insight was that our health checks measured what we had chosen to measure, not what users depend on. So I replaced them with synthetic queries that test real read behavior, and added circuit breaking.

We reached 99.999% read availability. More importantly, the approach became an org-wide operational template.

The learning for me was that a green dashboard is only as good as what it measures, so health checks should test what users depend on.

**Follow-up 1**

> Q: Why did every dashboard look healthy?
> A: A green dashboard measures only what you chose to measure; the pooler's TCP health check verified connectivity only.

**Follow-up 2**

> Q: How did you find the root cause?
> A: I mapped the read path (client, pooler, replicas), instrumented per-node latency and tested each layer with telemetry-driven hypotheses.

**Follow-up 3**

> Q: What were the two failure modes?
> A: A replica with severe disk I/O stalls, and a pooler that kept routing to the sick node.

**Follow-up 4**

> Q: What was the fix and result?
> A: Synthetic queries testing real read behavior plus circuit breaking, reaching 99.999% read availability and an org-wide operational template.

---

## 19. What have you done to develop your leadership skills?

### Answer

I've grown most by leading work that crosses organizational boundaries, and each project taught me something different.

On the Postgres upgrade across about 40 clusters, I learned to build VP-level confidence and align stakeholders around a high-risk plan, including rollback planning. With Secret Scanner and Maestro, I learned that adoption comes from understanding teams and giving them docs and office hours rather than mandates. Secret Scanner reached 100% adoption across Viva Engage teams, and Maestro now serves more than 100 engineers. With IRIS, I partnered with Trust and Security leadership on permission boundaries and blast-radius controls, so autonomous actions could earn trust.

I also learn from setbacks, like the Cosmos DB cost outcome and the reverted Kafka change, which taught me to model costs and validate end to end.

The shift for me has been from solving the problem myself to creating the conditions for other teams to succeed.

**Follow-up 1**

> Q: What was hardest about the Postgres upgrade?
> A: Building VP-level confidence in a high-risk plan, including rollback planning.

**Follow-up 2**

> Q: What did you learn from Secret Scanner and Maestro?
> A: Adoption comes from understanding teams, docs and office hours, not mandates: 100% adoption across Viva Engage teams and 100+ engineers.

**Follow-up 3**

> Q: What did IRIS teach you?
> A: Partnering with Trust and Security leadership on permission boundaries and blast-radius controls.

**Follow-up 4**

> Q: How have setbacks shaped you?
> A: The Cosmos DB cost outcome and reverted Kafka change taught me to model costs and validate more. I've moved from solving problems myself to creating conditions for others.

---

## 20. Give me an example of a tough or critical piece of feedback you received

### Answer

A senior leader told me my Postgres upgrade updates were too technical, and he couldn't tell what decisions he needed to make. It stung, but he was right.

I looked at my updates from his side. He needed to act, and I was giving him detail. So I changed the format: lead with status and risk in business terms, state the decision needed, and keep technical detail in an appendix.

Executive alignment became much easier, which helped a high-risk upgrade move forward.

The learning for me is that communication is judged by whether the audience can act on it. I've applied the same humility to the Cosmos DB cost miss, changing how I model costs.

**Follow-up 1**

> Q: What exactly was the feedback? 
> A: My Postgres updates were too technical and he couldn't tell what decisions he needed to make.

**Follow-up 2**

> Q: How did you react? 
> A: It stung, but he was right, so I changed the format.

**Follow-up 3**

> Q: What did you change? 
> A: Lead with status and risk in business terms, state the decision needed, and put technical detail in an appendix.

**Follow-up 4**

> Q: What was the impact? 
> A: Executive alignment became easier, which helped the upgrade move forward. Communication is judged by whether the audience can act on it.

---

## 21. Give me an example of when you had to make an important decision and had to decide between moving forward or gathering more information

### Answer

On the Postgres and OS upgrades, the risk was high and I couldn't wait for perfect information, because the CVE and Trust requirements were pressing. The upgrades covered about 40 production clusters.

I started by separating the decision into parts. The key insight was that not every part carried the same risk. For reversible parts, like feature flags for cross-version compatibility, I moved forward. For irreversible parts, I went deeper. For the OS, I chose native logical replication to a mirrored Ubuntu cluster. That avoided an Ubuntu 18.04 issue where a C library change invalidates database indexes, and it kept the cutover short.

I aligned executives with a clear plan, including rollback, and led the execution across all clusters and deployment stamps.

The Postgres upgrade averaged roughly one hour of downtime per cluster, the OS cutover took about five minutes, and related incidents fell 40%.

The Kafka offset change is the opposite case. I moved on an AI suggestion without enough validation and had to revert.

The learning for me is that the more irreversible and widespread the impact, the more evidence I want. For reversible changes, I move fast with clear rollback criteria.

**Follow-up 1**

> Q: Which parts were reversible?
> A: Feature flags for cross-version compatibility; I moved forward on those and went deeper on the irreversible parts.

**Follow-up 2**

> Q: Why logical replication for the OS?
> A: Native logical replication to a mirrored Ubuntu cluster avoided the Ubuntu 18.04 libc index-invalidation issue and kept the cutover short.

**Follow-up 3**

> Q: What were the results?
> A: About 40 clusters, roughly one hour of downtime per cluster for Postgres, about five minutes for the OS cutover, and incidents down 40%.

**Follow-up 4**

> Q: When do you gather more evidence?
> A: The more irreversible and widespread the impact, the more evidence; for reversible changes I move fast with clear rollback criteria, unlike the Kafka change I reverted.

---

## Questions I Ask the Interviewer

1. What does success look like in the first 90 days?
2. What's the most important problem you're hoping this hire will solve?
3. What's the biggest challenge the team is facing right now?
