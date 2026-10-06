# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage roles come from `triage-labels.md`; record lifecycle state in YAML frontmatter as described below.
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Canonical tracker fields

Work Map reads YAML frontmatter as the source of truth for tracker state. Use it on every map, specification, and ticket. Plain `Status:`, `Type:`, `Assignee:`, and `Blocked by:` lines are legacy conventions; do not duplicate state in the body.

- Map: `kind: map`, `status: open|resolved|superseded`, and `resolution_scope: planning|delivery`.
- Specification: `kind: spec` and `status: draft|ready|superseded`.
- Decision ticket: `kind: decision`, `status: open|claimed|resolved|superseded`, `type: research|prototype|grilling|task`, and `parent: ../map.md`.
- Implementation ticket: `kind: implementation`, `execution: agent|human`, `parent: ../spec.md`, and a build-track status from the triage conventions, including `done` for completed work.
- `execution: agent|human` on a decision marks AFK or human-assisted work. Use it explicitly for task tickets.
- `claimed_by` names the developer or session holding a ticket claim. Include it only while the claim is held.
- `blocked_by` lists paths relative to the ticket. Every path must resolve to a ticket; dependencies must not form a cycle.
- A superseded document names its replacement with `superseded_by`.

A resolved planning map means its declared planning destination was reached. It does not mean implementation has occurred.

## Wayfinding operations

- Map: `.scratch/<effort>/map.md`. It indexes resolved decisions and records the destination, notes, remaining fog, and scope boundaries.
- Child ticket: `.scratch/<effort>/issues/NN-<slug>.md`, with canonical frontmatter and a `## Question` body. The title is the human-readable issue name.
- Blocking: use `blocked_by` paths in frontmatter. A ticket is unblocked when every listed blocker is settled.
- Frontier: scan open, unclaimed, unblocked child tickets; choose the first by number unless the user names a ticket.
- Claim: save `status: claimed` and `claimed_by: <developer-or-session>` before working the ticket.
- Resolve: append a resolution comment under `## Comments`, with the answer under `## Answer`; set `status: resolved`, remove `claimed_by`, and add a gist and link to the map's Decisions so far.
- Linked research notes and evidence are assets, not tracker documents. They do not need lifecycle frontmatter.

## Validation

From the Work Map checkout, validate this repo with:

```bash
node src/migrate.ts check /home/t3agent/workspace/shutrwise --tracker-root .scratch
```

The validator checks required fields, allowed states, paths, parent relationships, and dependency cycles. Keep the format canonical when creating or changing documents.
