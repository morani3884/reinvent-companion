# Meetings, notes, deal coaching and the 90 days after

## 30-second prep (before every meeting)

Pull the meeting from the state file and give a brief the user can read walking in:

- **With AWS** (partner development manager, account managers, executives): the one specific ask, the joint value, one proof point, and the next step with a date.
- **With prospects or customers**: their likely pain, how they use AWS (from public sources or what the user said), the one outcome to aim for, and the follow-up.
- **With investors or peers**: the one-line story and what they want from the conversation.

Mark anything you inferred from public sources as such.

## Before the week: numbers to bring and a question bank

AWS teams can only get concrete about capacity, pricing options or architecture when they see real numbers. For each AWS meeting, add an action asking the user to fill in what's relevant - for example current and peak monthly spend, utilization of the main resource (GPU, compute, storage), peak season, current commitment coverage, capacity errors they've hit, and how large a commitment the business would consider. Store the answers they give in the meeting's `goal`/`ask` or in `materials`. Never estimate these numbers.

Offer 5-10 questions per goal for sessions, the Expo, Ask the Experts and meetings, saved as a `materials` entry or in the meeting's `ask`. Good questions are specific to their workload ("what's the right instance family for batch image inference at our latency target?"), not generic.

## Recap flow (after a meeting)

Triggered when the user says the meeting is done, asks to recap, or a scheduled evening check-in finds a meeting without a note.

1. Ask 2-3 quick questions, or take their voice note or brain-dump as is.
2. Play back a recap: who was there, key points, needs and objections, what was agreed, and the action items as task / owner / due date.
3. They confirm or correct in one reply.
4. Save to the state file: a `notes` entry linked by `item_id`, each action item into `actions`, new people into `contacts` exactly as given, `outcome` and `next_step` on the meeting item. Rebuild the workbook.
5. Offer a follow-up draft for them to send. Tell them in two lines what changed.

No-show? Draft a warm, no-blame reschedule the same day for them to send.

Important sessions get 3 bullet takeaways in the item's `next_step` or a note.

## Deal coaching (only when relevant)

Keep it short and practical. Most people at re:Invent book too many sessions and too few meetings.

- Start from existing pipeline rather than cold leads.
- The best room has three people: the customer's decision maker, their AWS account manager, and the user's partner development manager.
- Ask AWS contacts for warm intros, invite-only events and where they're investing this year.
- Raise ACE, Marketplace private offers, ISV Accelerate or marketing funds only if the user says they use those programs. Never invent eligibility, amounts or rules - link the official pages and suggest confirming with their AWS contact:
  - https://aws.amazon.com/partners/programs/ace/
  - https://aws.amazon.com/partners/programs/isv-accelerate/
- If you cite an ROI statistic, cite the source and its limits.

Useful targets by profile (adapt, don't impose):
- **Startup**: one dated ask per AWS contact, a named AWS owner, an architecture review booked, 3 customer conversations with next steps.
- **ISV**: top co-sell opportunities, a named AWS owner per deal, one private offer in motion if they sell through Marketplace, one joint customer story.
- **Learning-focused**: sessions for their stack, Ask the Experts, a takeaways doc.

Draft a short message to the partner development manager and each account manager with one specific ask and a date, for the user to send. Log it on the contact.

## Partnership status

If they're an AWS partner, check the public AWS Partner Solutions Finder (partners.amazonaws.com) and AWS Marketplace. Report what's listed (tier, programs, competencies, listings, case studies) and what isn't. Ask for what isn't public (PDM name, account managers, co-sell status). Suggest the one ask for the week. Never promise outcomes.

## After the event: 48 hours and 90 days

- **Within 48 hours**: write a recap into `meta.recap`, list every meeting still missing a follow-up, and draft those follow-ups.
- **Weekly for 90 days** (a scheduled task if available, otherwise when they ask): what moved, what's stalling, open asks to AWS, contacts due a nudge. Update the `pipeline` 30/60/90 columns with only what the user confirms.
- **At 90 days**: what the week produced against the original goal, what to repeat next year, and an offer to start planning the next edition.
