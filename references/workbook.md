# Workbook: state file and tabs

The JSON state file is the master copy. `scripts/build_workbook.py` turns it into the `.xlsx`. Edit the JSON (keep it valid), then rebuild. Unknown keys are ignored, missing keys are fine - fill in what you know and leave the rest out.

Never put invented data in the state file. Example rows the user didn't give you must have `"example": true` (the builder labels them "EXAMPLE").

## State schema

```json
{
  "meta": {
    "year": 2026,
    "company": "Acme",
    "role": "Founder & CEO",
    "goal": "3 AWS co-sell conversations with dated next steps",
    "event_dates": "from the official site",
    "days_on_site": "Mon-Thu",
    "hotel": "",
    "icp": "",
    "partner_status": "what's publicly listed, or what the user said",
    "daily_goals": ["Send same-day follow-ups"],
    "recap": "",
    "results_90_day": ""
  },
  "items": [
    {
      "id": "s1",
      "kind": "session | side_event | prospect_meeting | aws_meeting | meal | other",
      "title": "",
      "code": "session code, e.g. as shown in the catalog",
      "host": "side-event host",
      "date": "YYYY-MM-DD",
      "start": "HH:MM",
      "end": "HH:MM",
      "venue": "",
      "room": "",
      "match": "High | Medium | Low",
      "picked": true,
      "why": "one line",
      "decision": "Keep | Skip | Maybe | (empty)",
      "status": "Interested | Registered | Reserved | Confirmed | Attended",
      "url": "session page / event page / RSVP",
      "map_url": "",
      "route": "e.g. shuttle from Venetian, ~20 min",
      "leave_by": "HH:MM",
      "who": "attendees or speakers",
      "owner": "which colleague, for teams",
      "company": "meetings: their company",
      "goal": "meetings: what success looks like",
      "ask": "meetings: the one ask",
      "aws_people": "meetings: AWS account manager / PDM involved",
      "linkedin": "",
      "next_step": "",
      "outcome": "",
      "followup_sent": false,
      "calendar_event_id": "",
      "source": "where you verified it (URL)",
      "example": false
    }
  ],
  "notes": [
    {"item_id": "m1", "date": "YYYY-MM-DD", "who": "", "summary": "", "decisions": "", "followup_sent": false}
  ],
  "actions": [
    {"task": "", "owner": "", "due": "YYYY-MM-DD", "source": "item id or 'checklist'", "done": false}
  ],
  "contacts": [
    {"name": "", "company": "", "role": "", "type": "aws | other", "email": "only if given", "linkedin": "", "where_met": "", "followup": "", "notes": ""}
  ],
  "pipeline": [
    {"opportunity": "", "account": "", "stage": "", "value": "only if given", "ace": "", "marketplace": "", "aws_owner": "", "next_step": "", "due": "", "day_30": "", "day_60": "", "day_90": ""}
  ],
  "materials": [
    {"name": "", "url": "", "audience": "", "owner": "", "updated": ""}
  ],
  "logistics": [
    {"label": "Hotel / shuttle stop / badge pickup / last shuttle", "detail": "", "url": "official source"}
  ]
}
```

## Tabs the builder produces

| Tab | What's in it |
|---|---|
| **Today** | Index of all tabs, then today's kept items in time order, then tonight's undecided side events (Picked first). Pass `--today YYYY-MM-DD` to build it for a specific day. |
| **Overview** | `meta` plus the computed week score and counts. |
| **Agenda** | Every kept item and meeting, plus Picked items not yet decided (status "Draft - keep or skip?"), sorted by date and time, with map, directions and add-to-calendar links. Items without a date show "TBD - check catalog". |
| **Picks** | Everything not yet decided or marked Maybe - Picked first, then More. This is where the events loop lives. |
| **Sessions** | All `session` items with a Keep/Skip dropdown, status, match and session page link. |
| **Side Events** | All `side_event` items, same columns plus host. |
| **Meetings** | `prospect_meeting` and `aws_meeting` items: company, who, goal, ask, AWS people, next step, outcome, follow-up sent. |
| **Meeting Notes** | `notes`, each linked back to its meeting row. |
| **Action Items** | `actions` with Done checkboxes. |
| **Contacts** | `contacts`, AWS first, with LinkedIn and email links. |
| **Pipeline** | `pipeline`. Skipped if empty. |
| **Logistics** | `logistics` with links to the official sources. |
| **Materials** | `materials`. Skipped if empty. |

Every tab has a "back to Today" link in A1 and its header on row 2, frozen and filterable. High-match picked rows get a bright yellow fill. Each sessions and side-events tab ends with 5 blank "Add your own" rows.

## Week score

Computed by the builder from the state: +1 per kept session with status Attended, +2 per meeting with a linked note, +2 per meeting whose follow-up was sent (`followup_sent: true` on the meeting or its note), +3 per meeting whose `next_step` contains a date (YYYY-MM-DD or a month name).
