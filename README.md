# reinvent-companion

**Version:** 1.2.0 (2026-11-18) · works with any AI agent

A re:Invent sidekick for anyone attending: founders, sales, partnerships, engineers.

- **Before:** researches your company, picks sessions and side events from the official catalog (Picked for you + More that may fit, rated High/Medium/Low), and lays out a draft day-by-day week.
- **During:** answers "what's next / where do I go / I have 20 free minutes", preps you 30 seconds before meetings, recaps them into action items, drafts follow-ups.
- **After:** 48-hour follow-ups and a 90-day check-in plan.
- **One source of truth:** a JSON state file, rendered into a clickable Excel workbook by a script, plus a calendar file (.ics) for kept items.
- **Safe by design:** verifies times and places on official pages, never invents sessions, contacts or AWS credit amounts, and never sends anything without your OK.

## Use it with your agent

The instructions are plain markdown. Pick your tool:

| Your tool | What to do |
|---|---|
| **Claude (app)** | Zip this folder (or use the `.skill` file) and upload it in your Skills settings. |
| **Claude Code** | Copy the folder to `~/.claude/skills/reinvent-companion/` |
| **Codex, Cursor, Copilot, Gemini CLI and other coding agents** | Put the folder in your project. They read `AGENTS.md` automatically; otherwise tell the agent: "Follow reinvent-companion/AGENTS.md". |
| **ChatGPT (custom GPT or Project), Gemini (Gem), other chat apps** | Paste `STARTER-PROMPT.md` into the instructions field, and upload `AGENTS.md` plus everything in `references/` as knowledge files. Scripts only work if the app can run Python; if not, it keeps your plan as a table in chat. |
| **Anything else** | Paste `AGENTS.md` at the start of a chat, then say: "I'm going to re:Invent, plan my week". |

Try: "I'm going to re:Invent, plan my week" · "last shuttle to MGM tonight?" · "recap my meeting with Globex".

## What your agent needs

Required: read these files and chat. Strongly recommended: web search (all times and rooms are verified live). Optional: run Python, file access, calendar/email/Drive tools, scheduling. Missing pieces degrade gracefully; the instructions say how.

## Run the scripts yourself

```
pip install openpyxl
python scripts/build_workbook.py examples/sample-state.json my-plan.xlsx
python scripts/make_ics.py examples/sample-state.json my-plan.ics
```

`examples/sample-state.json` uses clearly marked EXAMPLE rows. The schema is in `references/workbook.md`.

## Structure

- `AGENTS.md` - core behavior (same text as `SKILL.md`, without the Claude frontmatter).
- `SKILL.md` - the same, in Agent Skills format for Claude.
- `STARTER-PROMPT.md` - short prompt for chat apps with a knowledge-file feature.
- `references/` - workbook schema, logistics, meetings and deals, checklists.
- `scripts/` - `build_workbook.py`, `make_ics.py`.
- `examples/` - sample state file.

## Changelog

**1.2.0 - 2026-11-18** - Agent-agnostic packaging: `AGENTS.md`, `STARTER-PROMPT.md`, per-tool setup, capabilities section, sample state file.

**1.1.0 - 2026-11-17** - Draft items on Agenda/Today, draft day-by-day plan, cross-check of official hours, "numbers to bring" and question bank for AWS meetings.

**1.0.0 - 2026-11-17** - First version, rebuilt from the original "re:Invent AWS GTM System".

## Credits

Created by Moran Ben Baruch (original "re:Invent AWS GTM System" concept), restructured as a vendor-neutral, agent-agnostic kit. Unofficial: not affiliated with or endorsed by AWS. Always confirm event details on the official site and in the AWS Events app.

## License

MIT, see `LICENSE`.
