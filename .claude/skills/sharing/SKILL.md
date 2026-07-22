---
type: skill
name: sharing
description: How to share a pipeline artifact with stakeholders over Slack - which tool to use, what to post vs. attach, and the confirm-before-sending rule
version: 1.0.0
tags: [ai-pm-os, sharing, slack, stakeholders]
---

# Sharing artifacts with stakeholders (Slack)

## Purpose

Getting an artifact out of `artifacts/` and in front of the people who need
to act on it - without turning that into a copy-paste chore, and without
posting the wrong thing to the wrong channel because nobody double-checked
first.

## Before posting anything

Sharing is a write action to a real, shared space - unlike the read-mostly
`ado`/`sql`/`kusto` tools, a Slack post can't be quietly undone once
someone's seen it. Always confirm with the user before sending:
1. Which artifact (`artifacts/<stage>.md`)
2. Which channel
3. A one-line preview of what the message will say

Only send after the user confirms. This applies even if the user's request
sounded like a direct instruction ("share the PRD with #eng") - confirm the
channel and content once, then send; don't ask twice if they already
answered both.

## What to post

Don't paste the raw markdown file into a Slack message - it reads badly and
buries the point. Instead:

1. **A short message** (3-5 sentences) summarizing what the artifact is,
   the headline decision or finding, and why the recipient should care -
   written for someone who won't open the full doc.
2. **The full artifact as a Slack Canvas** (via the `slack` MCP tool's
   canvas-management tools) when the content is more than a few paragraphs
   - PRDs, strategy docs, and validation results usually warrant a canvas
   rather than a wall of chat text. Link the canvas from the summary
   message.
3. For a quick status ping (e.g. "vision stage passed, moving to
   discovery") a plain message without a canvas is enough - use judgment
   on when the full document is actually needed versus a status update.

## Recording that it happened

After a successful share, log it so there's an audit trail matching the
rest of the pipeline's history-keeping:

```bash
python -m pipeline.runner record-share --artifact artifacts/prd.md --channel "#product-updates" --note "Shared for eng review ahead of sprint planning"
```

This writes to `context.json`'s `share_log` - it does not itself post to
Slack (that's the MCP tool's job); it just keeps a record of what was
shared, where, and when.

## Setup

See `docs/mcp-setup.md` for connecting the `slack` MCP tool - it's OAuth-based
(no token to manage) but does require workspace admin approval before first
use.
