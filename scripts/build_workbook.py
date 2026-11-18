#!/usr/bin/env python3
"""Build the re:Invent workbook (.xlsx) from the JSON state file.

Usage:
    python build_workbook.py state.json out.xlsx [--today YYYY-MM-DD]

The JSON file is the master copy; this script only renders it. See
references/workbook.md for the schema. Requires openpyxl.
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from urllib.parse import quote

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:
    sys.exit("openpyxl is required: pip install openpyxl")

YELLOW = PatternFill("solid", fgColor="FFF200")
HEADER_FILL = PatternFill("solid", fgColor="232F3E")
HEADER_FONT = Font(bold=True, color="FFFFFF")
LINK_FONT = Font(color="0563C1", underline="single")
EXAMPLE_FONT = Font(italic=True, color="888888")

DECISIONS = '"Keep,Skip,Maybe"'
STATUSES = '"Interested,Registered,Reserved,Confirmed,Attended"'
BOOL = '"TRUE,FALSE"'

TAB_ORDER = ["Today", "Overview", "Agenda", "Picks", "Sessions", "Side Events",
             "Meetings", "Meeting Notes", "Action Items", "Contacts",
             "Pipeline", "Logistics", "Materials"]

KIND_LABEL = {"session": "Session", "side_event": "Side event",
              "prospect_meeting": "Prospect meeting", "aws_meeting": "AWS meeting",
              "meal": "Meal", "other": "Other"}

DATE_IN_TEXT = re.compile(
    r"\d{4}-\d{2}-\d{2}|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b",
    re.I)


# ---------- helpers ----------

def sort_key(it):
    return (it.get("date") or "9999", it.get("start") or "99:99", it.get("title") or "")


def kept(it):
    return (it.get("decision") or "").lower() == "keep"


def draft(it):
    """Picked but not yet decided - shown on Agenda/Today as a draft so the
    first workbook isn't empty before the user has kept anything."""
    return bool(it.get("picked")) and (it.get("decision") or "") in ("", "Maybe")


def on_agenda(it):
    if it.get("decision") == "Skip":
        return False
    return kept(it) or draft(it) or is_meeting(it) or it.get("kind") == "meal"


def is_meeting(it):
    return it.get("kind") in ("prospect_meeting", "aws_meeting")


def gcal_link(it):
    """Google Calendar 'add event' link, or None if date/start missing."""
    d, s = it.get("date"), it.get("start")
    if not d or not s:
        return None
    try:
        start = datetime.strptime(f"{d} {s}", "%Y-%m-%d %H:%M")
        end = (datetime.strptime(f"{d} {it['end']}", "%Y-%m-%d %H:%M")
               if it.get("end") else start + timedelta(hours=1))
    except ValueError:
        return None
    fmt = "%Y%m%dT%H%M%S"
    loc = ", ".join(x for x in [it.get("venue"), it.get("room")] if x)
    details = "\n".join(x for x in [it.get("why"), it.get("route") and f"Route: {it['route']}",
                                    it.get("leave_by") and f"Leave by {it['leave_by']}",
                                    it.get("url")] if x)
    # ctz keeps the times in Las Vegas local time regardless of the viewer's zone
    return ("https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={quote('[re:Invent] ' + (it.get('title') or ''))}"
            f"&dates={start.strftime(fmt)}/{end.strftime(fmt)}"
            f"&ctz=America/Los_Angeles"
            f"&location={quote(loc)}&details={quote(details)}")


def maps_link(it):
    if it.get("map_url"):
        return it["map_url"]
    if it.get("venue"):
        return "https://www.google.com/maps/search/?api=1&query=" + quote(it["venue"] + " Las Vegas")
    return None


def directions_link(it):
    if it.get("venue"):
        return ("https://www.google.com/maps/dir/?api=1&travelmode=walking&destination="
                + quote(it["venue"] + " Las Vegas"))
    return None


class Sheet:
    """Small wrapper: header on row 2, back-link in A1, typed cell writers."""

    def __init__(self, wb, title, headers, widths=None, home=True):
        self.ws = wb.create_sheet(title)
        self.headers = headers
        self.row = 3
        if home:
            c = self.ws.cell(row=1, column=1, value="⬅ Today")
            c.hyperlink = "#'Today'!A1"
            c.font = LINK_FONT
        for i, h in enumerate(headers, 1):
            c = self.ws.cell(row=2, column=i, value=h)
            c.fill, c.font = HEADER_FILL, HEADER_FONT
            c.alignment = Alignment(vertical="center", wrap_text=True)
            self.ws.column_dimensions[get_column_letter(i)].width = (widths or {}).get(h, 16)
        self.ws.freeze_panes = "A3"

    def col(self, name):
        return self.headers.index(name) + 1

    def add(self, values, links=None, highlight=False, example=False):
        """values: dict header->value. links: dict header->(url,label)."""
        r = self.row
        for h, v in values.items():
            if h in self.headers and v not in (None, ""):
                self.ws.cell(row=r, column=self.col(h), value=v)
        for h, link in (links or {}).items():
            if h in self.headers and link and link[0]:
                c = self.ws.cell(row=r, column=self.col(h), value=link[1])
                c.hyperlink = link[0]
                c.font = LINK_FONT
        for i in range(1, len(self.headers) + 1):
            c = self.ws.cell(row=r, column=i)
            c.alignment = Alignment(vertical="top", wrap_text=True)
            if highlight:
                c.fill = YELLOW
            if example and not c.hyperlink:
                c.font = EXAMPLE_FONT
        self.row += 1
        return r

    def blank_rows(self, n, label="Add your own"):
        for _ in range(n):
            self.ws.cell(row=self.row, column=1, value=label).font = EXAMPLE_FONT
            self.row += 1

    def validate(self, header, formula):
        if header not in self.headers:
            return
        last = max(self.row + 20, 200)
        dv = DataValidation(type="list", formula1=formula, allow_blank=True)
        letter = get_column_letter(self.col(header))
        dv.add(f"{letter}3:{letter}{last}")
        self.ws.add_data_validation(dv)

    def finish(self):
        last_col = get_column_letter(len(self.headers))
        self.ws.auto_filter.ref = f"A2:{last_col}{max(self.row - 1, 2)}"


def title_of(it):
    t = it.get("title") or ""
    return f"EXAMPLE - {t}" if it.get("example") else t


def item_links(it, page_label="Page 🔗"):
    return {
        "Page": (it.get("url"), page_label),
        "Map": (maps_link(it), "Map 📍"),
        "Directions": (directions_link(it), "Directions 🚶"),
        "Add to calendar": (gcal_link(it), "Add to calendar 📅"),
        "LinkedIn": (it.get("linkedin"), "LinkedIn 👤"),
    }


def yesno(v):
    return "TRUE" if v else "FALSE"


# ---------- score ----------

def week_score(state):
    items = state.get("items", [])
    notes = state.get("notes", [])
    noted = {n.get("item_id") for n in notes}
    noted_sent = {n.get("item_id") for n in notes if n.get("followup_sent")}
    score = 0
    for it in items:
        if it.get("kind") == "session" and kept(it) and (it.get("status") or "").lower() == "attended":
            score += 1
        if is_meeting(it):
            if it.get("id") in noted:
                score += 2
            if it.get("followup_sent") or it.get("id") in noted_sent:
                score += 2
            if it.get("next_step") and DATE_IN_TEXT.search(it["next_step"]):
                score += 3
    return score


# ---------- tabs ----------

AGENDA_HEADERS = ["Date", "Start", "End", "Type", "Title", "Venue", "Room", "Who",
                  "Route", "Leave by", "Status", "Page", "Map", "Directions", "Add to calendar"]
W = {"Title": 40, "Why": 40, "Summary": 50, "Decisions": 35, "Task": 40, "Detail": 50,
     "Goal": 30, "Ask": 30, "Next step": 30, "Route": 26, "Venue": 22, "Date": 12,
     "Start": 8, "End": 8, "Leave by": 9, "Match": 9, "Keep/Skip": 11}


def agenda_row(it):
    return {"Date": it.get("date") or "TBD - check catalog", "Start": it.get("start"), "End": it.get("end"),
            "Type": KIND_LABEL.get(it.get("kind"), it.get("kind")), "Title": title_of(it),
            "Venue": it.get("venue"), "Room": it.get("room"), "Who": it.get("who"),
            "Route": it.get("route"), "Leave by": it.get("leave_by"),
            "Status": it.get("status") or ("Draft - keep or skip?" if draft(it) else None)}


def build(state, today):
    wb = Workbook()
    wb.remove(wb.active)
    items = sorted(state.get("items", []), key=sort_key)
    meta = state.get("meta", {})
    tabs_present = []

    # Today (built first so it opens first; filled below)
    today_ws = Sheet(wb, "Today", AGENDA_HEADERS + ["Keep/Skip", "Match", "Why"], W, home=False)
    today_ws.ws.cell(row=1, column=1,
                     value=f"re:Invent {meta.get('year', '')} - {meta.get('company', '')} - {today.isoformat()}").font = Font(bold=True, size=13)

    # Overview
    ov = Sheet(wb, "Overview", ["Field", "Value"], {"Field": 22, "Value": 70})
    for k in ["company", "role", "goal", "event_dates", "days_on_site", "hotel", "icp",
              "partner_status", "recap", "results_90_day"]:
        if meta.get(k):
            ov.add({"Field": k.replace("_", " ").capitalize(), "Value": meta[k]})
    if meta.get("daily_goals"):
        ov.add({"Field": "Daily goals", "Value": "\n".join(meta["daily_goals"])})
    ov.add({"Field": "Week score", "Value": week_score(state)})
    ov.add({"Field": "Kept items", "Value": sum(1 for i in items if kept(i))})
    ov.add({"Field": "Meetings", "Value": sum(1 for i in items if is_meeting(i))})
    ov.add({"Field": "Open action items",
            "Value": sum(1 for a in state.get("actions", []) if not a.get("done"))})
    ov.finish()

    # Agenda
    ag = Sheet(wb, "Agenda", AGENDA_HEADERS, W)
    for it in items:
        if on_agenda(it):
            ag.add(agenda_row(it), item_links(it), example=it.get("example"),
                   highlight=draft(it) and it.get("match") == "High")
    ag.validate("Status", STATUSES)
    ag.finish()

    # Picks
    pk_headers = ["Group", "Keep/Skip", "Match", "Type", "Title", "Date", "Start", "Venue",
                  "Why", "Page", "Add to calendar"]
    pk = Sheet(wb, "Picks", pk_headers, W)
    pk.ws.cell(row=1, column=3, value="How to add: choose Keep in the dropdown, tell me \"add [name]\" in chat, "
               "or paste any event/session link and I'll add it with its links.").font = Font(italic=True)
    undecided = [i for i in items if (i.get("decision") or "") in ("", "Maybe")
                 and i.get("kind") in ("session", "side_event")]
    for grp, sel in (("🟨 Picked for you", [i for i in undecided if i.get("picked")]),
                     ("➕ More that may fit", [i for i in undecided if not i.get("picked")])):
        for it in sel:
            pk.add({"Group": grp, "Keep/Skip": it.get("decision"), "Match": it.get("match"),
                    "Type": KIND_LABEL.get(it.get("kind")), "Title": title_of(it),
                    "Date": it.get("date"), "Start": it.get("start"), "Venue": it.get("venue"),
                    "Why": it.get("why")}, item_links(it),
                   highlight=bool(it.get("picked")) and it.get("match") == "High",
                   example=it.get("example"))
    pk.validate("Keep/Skip", DECISIONS)
    pk.finish()

    # Sessions & Side Events
    def kind_tab(name, kind, extra):
        headers = ["Keep/Skip", "Status", "Match"] + extra + ["Title", "Date", "Start", "End",
                   "Venue", "Room", "Why", "Next step", "Page", "Map", "Add to calendar"]
        sh = Sheet(wb, name, headers, W)
        sh.ws.cell(row=1, column=3, value="How to add: Keep in the dropdown, \"add [name]\" in chat, "
                   "or paste a link.").font = Font(italic=True)
        sel = [i for i in items if i.get("kind") == kind]
        sel.sort(key=lambda i: (not i.get("picked"), sort_key(i)))
        for it in sel:
            sh.add({"Keep/Skip": it.get("decision"), "Status": it.get("status"),
                    "Match": it.get("match"), "Code": it.get("code"), "Host": it.get("host"),
                    "Title": title_of(it), "Date": it.get("date"), "Start": it.get("start"),
                    "End": it.get("end"), "Venue": it.get("venue"), "Room": it.get("room"),
                    "Why": it.get("why"), "Next step": it.get("next_step")}, item_links(it),
                   highlight=bool(it.get("picked")) and it.get("match") == "High",
                   example=it.get("example"))
        sh.blank_rows(5)
        sh.validate("Keep/Skip", DECISIONS)
        sh.validate("Status", STATUSES)
        sh.finish()

    kind_tab("Sessions", "session", ["Code"])
    kind_tab("Side Events", "side_event", ["Host"])

    # Meetings
    mt_headers = ["Date", "Start", "Type", "Company", "Title", "Who", "AWS people", "Goal", "Ask",
                  "Venue", "Next step", "Outcome", "Follow-up sent", "Recap", "Map", "Add to calendar", "LinkedIn"]
    mt = Sheet(wb, "Meetings", mt_headers, W)
    meeting_rows = {}
    for it in [i for i in items if is_meeting(i)]:
        r = mt.add({"Date": it.get("date"), "Start": it.get("start"),
                    "Type": KIND_LABEL.get(it.get("kind")), "Company": it.get("company"),
                    "Title": title_of(it), "Who": it.get("who"), "AWS people": it.get("aws_people"),
                    "Goal": it.get("goal"), "Ask": it.get("ask"), "Venue": it.get("venue"),
                    "Next step": it.get("next_step"), "Outcome": it.get("outcome"),
                    "Follow-up sent": yesno(it.get("followup_sent"))}, item_links(it),
                   example=it.get("example"))
        meeting_rows[it.get("id")] = r
    mt.blank_rows(5)
    mt.validate("Follow-up sent", BOOL)
    mt.finish()

    # Meeting Notes
    nt = Sheet(wb, "Meeting Notes", ["Date", "Meeting", "Who", "Summary", "Decisions", "Follow-up sent"], W)
    by_id = {i.get("id"): i for i in items}
    for n in state.get("notes", []):
        it = by_id.get(n.get("item_id"), {})
        r = nt.add({"Date": n.get("date"), "Who": n.get("who"), "Summary": n.get("summary"),
                    "Decisions": n.get("decisions"), "Follow-up sent": yesno(n.get("followup_sent"))})
        mrow = meeting_rows.get(n.get("item_id"))
        c = nt.ws.cell(row=r, column=nt.col("Meeting"), value=it.get("title") or n.get("item_id"))
        if mrow:
            c.hyperlink = f"#'Meetings'!A{mrow}"
            c.font = LINK_FONT
            back = mt.ws.cell(row=mrow, column=mt.col("Recap"), value="Recap 📝")
            back.hyperlink = f"#'Meeting Notes'!A{r}"
            back.font = LINK_FONT
    nt.validate("Follow-up sent", BOOL)
    nt.finish()

    # Action Items
    ac = Sheet(wb, "Action Items", ["Done", "Task", "Owner", "Due", "Source"], W)
    for a in sorted(state.get("actions", []), key=lambda a: (bool(a.get("done")), a.get("due") or "9999")):
        ac.add({"Done": yesno(a.get("done")), "Task": a.get("task"), "Owner": a.get("owner"),
                "Due": a.get("due"), "Source": a.get("source")})
    ac.validate("Done", BOOL)
    ac.finish()

    # Contacts
    ct = Sheet(wb, "Contacts", ["Type", "Name", "Company", "Role", "Where met", "Follow-up",
                                "Notes", "LinkedIn", "Email"], W)
    for p in sorted(state.get("contacts", []), key=lambda p: (p.get("type") != "aws", p.get("name") or "")):
        ct.add({"Type": "AWS" if p.get("type") == "aws" else "Other", "Name": p.get("name"),
                "Company": p.get("company"), "Role": p.get("role"), "Where met": p.get("where_met"),
                "Follow-up": p.get("followup"), "Notes": p.get("notes")},
               {"LinkedIn": (p.get("linkedin"), "LinkedIn 👤"),
                "Email": (p.get("email") and "mailto:" + p["email"], "Email ✉️")})
    ct.finish()

    # Pipeline (optional)
    if state.get("pipeline"):
        cols = ["opportunity", "account", "stage", "value", "ace", "marketplace", "aws_owner",
                "next_step", "due", "day_30", "day_60", "day_90"]
        pl = Sheet(wb, "Pipeline", [c.replace("_", " ").capitalize() for c in cols], W)
        for p in state["pipeline"]:
            pl.add({c.replace("_", " ").capitalize(): p.get(c) for c in cols})
        pl.finish()

    # Logistics
    lg = Sheet(wb, "Logistics", ["Label", "Detail", "Source"], W)
    for l in state.get("logistics", []):
        lg.add({"Label": l.get("label"), "Detail": l.get("detail")},
               {"Source": (l.get("url"), "Official source 🔗")})
    lg.finish()

    # Materials (optional)
    if state.get("materials"):
        ma = Sheet(wb, "Materials", ["Name", "Link", "Audience", "Owner", "Updated"], W)
        for m in state["materials"]:
            ma.add({"Name": m.get("name"), "Audience": m.get("audience"), "Owner": m.get("owner"),
                    "Updated": m.get("updated")}, {"Link": (m.get("url"), "Open 🔗")})
        ma.finish()

    # ----- fill Today -----
    tabs_present = [t for t in TAB_ORDER if t in wb.sheetnames and t != "Today"]
    ws = today_ws.ws
    # index on row 1 to the right of the title
    for i, t in enumerate(tabs_present):
        c = ws.cell(row=1, column=6 + i, value=t)
        c.hyperlink = f"#'{t}'!A1"
        c.font = LINK_FONT

    iso = today.isoformat()
    todays = [i for i in items if i.get("date") == iso and on_agenda(i)
              and not (i.get("kind") == "side_event" and not kept(i))]
    for it in todays:
        today_ws.add({**agenda_row(it), "Keep/Skip": it.get("decision"), "Match": it.get("match"),
                      "Why": it.get("why")}, item_links(it), example=it.get("example"))
    if not todays:
        today_ws.add({"Title": "Nothing kept for today yet"})

    tonight = [i for i in items if i.get("date") == iso and i.get("kind") == "side_event"
               and (i.get("decision") or "") in ("", "Maybe")]
    tonight.sort(key=lambda i: (not i.get("picked"), sort_key(i)))
    if tonight:
        r = today_ws.row + 1
        ws.cell(row=r, column=1, value="Tonight - 🟨 Picked for you, then ➕ More that may fit").font = Font(bold=True)
        today_ws.row = r + 1
        for it in tonight:
            today_ws.add({**agenda_row(it), "Keep/Skip": it.get("decision"), "Match": it.get("match"),
                          "Why": ("🟨 " if it.get("picked") else "➕ ") + (it.get("why") or "")},
                         item_links(it),
                         highlight=bool(it.get("picked")) and it.get("match") == "High",
                         example=it.get("example"))
    today_ws.validate("Keep/Skip", DECISIONS)
    today_ws.validate("Status", STATUSES)
    today_ws.finish()

    wb.active = 0
    return wb


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("state")
    ap.add_argument("out")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today's date)")
    a = ap.parse_args()
    with open(a.state, encoding="utf-8") as f:
        state = json.load(f)
    today = date.fromisoformat(a.today) if a.today else date.today()
    wb = build(state, today)
    wb.save(a.out)
    print(f"Wrote {a.out}: tabs = {', '.join(wb.sheetnames)}; week score = {week_score(state)}")


if __name__ == "__main__":
    main()
