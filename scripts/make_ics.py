#!/usr/bin/env python3
"""Create an .ics calendar file for kept re:Invent items.

Usage:
    python make_ics.py state.json out.ics            # all kept items + meetings
    python make_ics.py state.json out.ics --ids s1 e3 # only these item ids

Times in the state file are Las Vegas local time (America/Los_Angeles).
Each event gets a 30-minute reminder that includes the leave-by time and route.
Stable UIDs mean re-importing updates events instead of duplicating them in most calendar apps.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone

TZ = "America/Los_Angeles"


def esc(s):
    return (s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    out, b = [], line.encode("utf-8")
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80:  # don't split a UTF-8 char
            cut -= 1
        out.append(b[:cut].decode("utf-8"))
        b = b[cut:]
    out.append(b.decode("utf-8"))
    return "\r\n ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("out")
    ap.add_argument("--ids", nargs="*")
    a = ap.parse_args()
    state = json.load(open(a.state, encoding="utf-8"))
    year = state.get("meta", {}).get("year", "")
    items = state.get("items", [])
    if a.ids:
        sel = [i for i in items if i.get("id") in a.ids]
    else:
        sel = [i for i in items if (i.get("decision") or "").lower() == "keep"
               or (i.get("kind") in ("prospect_meeting", "aws_meeting") and i.get("decision") != "Skip")]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//reinvent-companion//EN", "CALSCALE:GLOBAL",
             "BEGIN:VTIMEZONE", f"TZID:{TZ}",
             "BEGIN:STANDARD", "DTSTART:19701101T020000", "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU",
             "TZOFFSETFROM:-0700", "TZOFFSETTO:-0800", "TZNAME:PST", "END:STANDARD",
             "BEGIN:DAYLIGHT", "DTSTART:19700308T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU",
             "TZOFFSETFROM:-0800", "TZOFFSETTO:-0700", "TZNAME:PDT", "END:DAYLIGHT",
             "END:VTIMEZONE"]
    skipped = []
    for it in sel:
        try:
            start = datetime.strptime(f"{it['date']} {it['start']}", "%Y-%m-%d %H:%M")
        except (KeyError, ValueError):
            skipped.append(it.get("title") or it.get("id"))
            continue
        end = (datetime.strptime(f"{it['date']} {it['end']}", "%Y-%m-%d %H:%M")
               if it.get("end") else start + timedelta(hours=1))
        loc = ", ".join(x for x in [it.get("venue"), it.get("room")] if x)
        desc = "\n".join(x for x in [
            it.get("why"),
            it.get("route") and f"Route: {it['route']}",
            it.get("leave_by") and f"Leave by: {it['leave_by']}",
            it.get("ask") and f"Ask: {it['ask']}",
            it.get("url")] if x)
        alarm = "Leave by " + it["leave_by"] if it.get("leave_by") else "Starts in 30 minutes"
        if it.get("route"):
            alarm += " - " + it["route"]
        f = "%Y%m%dT%H%M%S"
        lines += ["BEGIN:VEVENT",
                  f"UID:reinvent-{year}-{it.get('id', start.strftime(f))}@reinvent-companion",
                  f"DTSTAMP:{stamp}",
                  f"DTSTART;TZID={TZ}:{start.strftime(f)}",
                  f"DTEND;TZID={TZ}:{end.strftime(f)}",
                  f"SUMMARY:{esc('[re:Invent] ' + (it.get('title') or ''))}",
                  f"LOCATION:{esc(loc)}",
                  f"DESCRIPTION:{esc(desc)}"]
        if it.get("url"):
            lines.append(f"URL:{it['url']}")
        lines += ["BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-PT30M",
                  f"DESCRIPTION:{esc(alarm)}", "END:VALARM", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    with open(a.out, "w", encoding="utf-8", newline="") as fh:
        fh.write("\r\n".join(fold(l) for l in lines) + "\r\n")
    print(f"Wrote {a.out} with {len(sel) - len(skipped)} events"
          + (f"; skipped (missing date/start): {', '.join(skipped)}" if skipped else ""))


if __name__ == "__main__":
    main()
