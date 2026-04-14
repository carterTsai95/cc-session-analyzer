---
name: cc-session-analyzer
description: Analyze any Claude Code session from .jsonl logs. Parses timestamps, tool calls, and conversation flow, then generates a markdown analysis with mermaid charts (Gantt, sequence, pie, bar). Works with skill-driven workflows, general coding, debugging, or multi-step tasks. Use when asked to "analyze session", "session report", "what happened in this session", "generate session metrics", "how did the session go", "profile skill execution", or after completing work when documenting performance.
---

# CC Session Analyzer

Generate a session execution analysis from Claude Code `.jsonl` logs with mermaid visualizations.

Supports two session types:
- **Skill sessions** — sessions where a skill was invoked (auto-detected via `<command-name>/` in logs)
- **General sessions** — any other coding, debugging, or multi-step session

Follow all 3 checkpoints strictly in order. **Do NOT proceed to the next checkpoint until the current one is confirmed by the user.**

---

## Checkpoint 1: Session Discovery + Basic Metrics

1. Ask the user for:
   - **Which session log** to analyze — default: current session. Logs at `~/.claude/projects/<project-dir>/*.jsonl`. Find current by most recent modification time.
   - **Output path** for the analysis markdown file

2. Run the parse script:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/cc-session-analyzer/scripts/parse_session.py <session_log.jsonl>
   ```

3. Determine **session type**:
   - If `detected_skill` in parse output is non-null → **skill session**. Read that skill's `SKILL.md` to understand its workflow, description, and trigger phrases.
   - Otherwise → **general session**. Infer the task from the first user message and assistant responses.

4. Present the discovery summary:

   | Field | Value |
   |-------|-------|
   | Session log | `<filename>` |
   | Session type | Skill: `<name>` / General |
   | Total duration | Xm Ys |
   | Agent time | Xs (X%) |
   | Developer time | Xs (X%) |
   | Total tool calls | N |
   | User turns | N |
   | Top tools | Tool1 (N), Tool2 (N), ... |

**Do NOT proceed until the user confirms the correct session.**

---

## Checkpoint 2: Phase Segmentation + Timeline

Walk the parsed timeline and segment into phases.

### Phase Detection Heuristics

**For skill sessions:**

| Signal | Phase Type |
|--------|-----------|
| User message with `<command-name>/` | Skill invocation |
| User message with substantive text (>20 chars, not a tool result) | Developer input / confirmation |
| Assistant message with tool calls | Agent processing |
| Assistant message with long text (tables, lists) | Checkpoint presentation |
| Gap >5s between last assistant and next user message | Developer review time |
| MCP tool calls (`mcp__*`) | External service fetch |
| `Agent` tool call | Subagent dispatch |
| `Edit` tool calls | Implementation |
| `Bash` tool calls after all edits | Validation |

**For general sessions:**

| Signal | Phase Type |
|--------|-----------|
| Cluster of `Glob`, `Grep`, `Read` calls | Exploration / research |
| Cluster of `Edit`, `Write` calls | Implementation |
| `Bash` calls running tests or builds | Validation / testing |
| `Agent` tool calls | Subagent delegation |
| User message after long gap (>30s) | New task or direction change |
| Shift in target files/directories | Context switch |
| `EnterPlanMode` / `ExitPlanMode` | Planning phase |

For each phase, record: name, start timestamp, end timestamp, duration, tool calls, agent/developer classification.

Present the phase segmentation:

| # | Phase | Start | Duration | Agent/Dev | Tool Calls | Key Activity |
|---|-------|-------|----------|-----------|------------|--------------|
| 1 | ... | HH:MM:SS | Ns | Agent | N | ... |

**Do NOT proceed until the user confirms the phase boundaries.** The user may request merging, splitting, or renaming phases.

---

## Checkpoint 3: Report Structure Preview

Compose the planned report sections based on session type.

**Skill session sections:**
1. Title + description (from skill's SKILL.md)
2. Table of Contents
3. How It Works — mermaid flowchart of skill workflow
4. Domain-specific mapping diagram (name based on what the skill does)
5. Trigger Phrases
6. Skill File Structure — directory tree
7. Real-World Demo (sequence diagram, phase table, observations, duration charts, metrics, takeaway)

**General session sections:**
1. Title + task description (inferred from session)
2. Table of Contents
3. Task Overview — what was accomplished
4. Approach — mermaid flowchart of the steps taken
5. Files Changed — list of modified/created files with change summary
6. Session Breakdown (sequence diagram, phase table, observations, duration charts, metrics, takeaway)

**Common charts (both types):**
- Sequence diagram with participants (Developer, Claude Code, MCP Servers if used, Filesystem, Subagent if used)
- Gantt chart (phase timeline)
- Pie charts (agent vs dev time, agent breakdown, dev breakdown)
- Bar chart (duration by phase)
- Metrics summary table

Present the planned structure:

```
Planned Report for: <session description>
Output: <path>

Sections:
1. <section name> — <brief description>
2. ...

Charts: sequence diagram (N participants), Gantt (N phases),
        3 pie charts, bar chart, metrics table
```

**Do NOT proceed until the user confirms the report plan.**

---

## Implementation

After all 3 checkpoints are confirmed, generate the analysis document.

Read [references/output-template.md](references/output-template.md) for document structure and mermaid chart format examples.

### Section Generation

For each section, use real data from the parsed session and confirmed phases. Key guidelines:

- **Sequence diagram**: Show actual conversation flow. Group parallel tool calls in `par` blocks. Include all participants detected in the session.
- **Phase table**: Use confirmed phase names and boundaries from CP2.
- **Key observations**: 5-8 numbered insights. Focus on efficiency patterns, bottlenecks, what required human input, and what was automated.
- **Gantt chart**: Use `after` syntax for GitHub compatibility. Mark developer time with `:crit` (renders red).
- **Pie chart values**: Must be numbers, not percentages.
- **Bar chart x-axis**: Max 10 chars per label. Add legend below if abbreviated.
- **Metrics table**: Include total duration, agent/dev time and percentages, tool calls, files modified, and session-specific metrics.
- **Takeaway**: Single paragraph summarizing effectiveness — what was automated, what required judgment, total time, key efficiency gains.

### Mermaid Compatibility Rules

These rules prevent rendering failures on GitHub:
- Gantt: use `after` dependencies, NOT absolute timestamps. `dateFormat YYYY-MM-DD`, start from `2024-01-01 00:00:00`
- Bar chart x-axis: max 10 chars per label. Use abbreviations + legend
- No special characters in Gantt task IDs (no colons, parentheses)
- Pie chart values must be numbers, not percentages
- All charts must render on github.com

## Resources

- [scripts/parse_session.py](scripts/parse_session.py) — Session log parser (run via Bash)
- [references/output-template.md](references/output-template.md) — Document structure templates and mermaid chart examples
