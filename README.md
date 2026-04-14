# cc-session-analyzer

A Claude Code plugin that analyzes any session from `.jsonl` logs and generates a comprehensive markdown report with mermaid visualizations. Works with skill-driven workflows, general coding sessions, debugging, or any multi-step task.

## Installation

```shell
/plugin marketplace add carterTsai95/cc-session-analyzer
/plugin install cc-session-analyzer@cc-session-analyzer
```

## Usage

Invoke the skill:

```shell
/cc-session-analyzer
```

Or ask naturally: "analyze this session", "generate a session report", "what happened in this session".

### 3-Checkpoint Workflow

The analyzer walks you through 3 checkpoints before generating the report:

**Checkpoint 1 — Session Discovery**
Identifies the session log, detects if a skill was used, and presents basic metrics (duration, agent/developer time split, tool call counts). You confirm the correct session before proceeding.

**Checkpoint 2 — Phase Segmentation**
Segments the session timeline into phases (exploration, implementation, validation, etc.) using heuristic analysis. You review and can adjust phase boundaries, merge, split, or rename phases.

**Checkpoint 3 — Report Preview**
Shows the planned report structure and output path. Uses a unified template for all session types — skill sessions include additional context (workflow flowchart, trigger phrases, file structure) while general sessions focus on task overview, approach, and files changed. You confirm before generation begins.

### Output

A markdown document with:
- Mermaid sequence diagram of the conversation flow
- Phase-by-phase execution breakdown
- Gantt chart of the session timeline
- Pie charts (agent vs developer time, phase breakdowns)
- Bar chart of duration by phase
- Metrics summary table
- Key observations and takeaway

All mermaid charts are GitHub-compatible.

## Session Types

| Type | Auto-detected by | Report focus |
|------|------------------|--------------|
| Skill session | `<command-name>/` in logs | Skill workflow, checkpoints, domain mapping |
| General session | No skill detected | Task summary, approach, files changed |

## Example Output

Below is a condensed example from a real session where a UI component skill generated a SwiftUI screen from a ticket. The full report includes all sections shown here.


<summary><strong>Session Analysis — Build SwiftUI Screen from Ticket</strong></summary>

### Task Overview

A skill session that converted a ticket into a production-ready SwiftUI screen using a design system component library. The skill automated requirements gathering, component analysis, plan creation with developer checkpoints, code generation, and build verification — completing in 13 minutes with 3 developer checkpoints.

**Input:** Ticket URL + design tool URL  
**Output:** A compilable SwiftUI screen using 5 design system components with proper tokens, accessibility, and state management.

### Workflow Overview

```mermaid
flowchart TD
    A["Skill invoked<br/>+ Ticket URL + Design URL"] --> B["Phase 1:<br/>Gather Requirements"]
    B --> B1[Fetch ticket via MCP]
    B1 --> B2{Design tool MCP<br/>available?}
    B2 -->|No| B3["Fallback to ticket<br/>acceptance criteria"]
    B2 -->|Yes| B4[Analyze design]
    B3 --> C["Phase 2:<br/>Analyze Components"]
    B4 --> C
    C --> C1["Dispatch Explore subagent<br/>for component inventory"]
    C1 --> C2["Read 12+ component<br/>source files to verify APIs"]
    C2 --> D["Phase 3:<br/>Create Component Plan"]
    D --> D1{Developer<br/>approves plan?}
    D1 -->|Yes| E["Phase 4:<br/>Component Usage Plan"]
    D1 -->|No| D
    E --> E1{Developer<br/>approves usage?}
    E1 -->|Feedback| E2[Incorporate corrections]
    E2 --> E1
    E1 -->|Yes| F["Phase 5:<br/>Generate SwiftUI Code"]
    F --> F1[Write .swift file]
    F1 --> G[Build Validation]
    G --> G1{Build succeeds?}
    G1 -->|No| G2["Try alternative<br/>build method"]
    G2 --> G1
    G1 -->|Yes| H[Summary]

    style D1 fill:#f9f,stroke:#333
    style E1 fill:#f9f,stroke:#333
    style B2 fill:#ff9,stroke:#333
    style G1 fill:#ff9,stroke:#333
```

### Project Context

#### Files Changed

| File | Action | Summary |
|------|--------|---------|
| `Sources/.../GeneratedScreen.swift` | Created | SwiftUI screen with page header, dropdown, 3 buttons, warning icon, legal text, category selection sheet, inline validation |

#### Ticket-to-Component Mapping

```mermaid
flowchart LR
    subgraph Ticket["Ticket Requirements"]
        J1[Page Header]
        J2[Warning Image]
        J3[Warning Content]
        J4[Reason Dropdown]
        J5[Continue CTA]
        J6[Cancel CTA]
        J7[Speak to Advisor CTA]
        J8[Legal Text]
        J9[Inline Error]
    end

    subgraph DS["Design System Components"]
        R1[PageHeader]
        R2[Icon.warningTritone]
        R3["Text + heading / paragraph tokens"]
        R4["DropDown + SheetView"]
        R5["Button .primary"]
        R6["Button .secondary"]
        R7["Button .tertiary"]
        R8["Text + small tokens"]
        R9["Validation via DropDown"]
    end

    J1 --> R1
    J2 --> R2
    J3 --> R3
    J4 --> R4
    J5 --> R5
    J6 --> R6
    J7 --> R7
    J8 --> R8
    J9 --> R9
```

### Session Walkthrough

#### Execution Breakdown

```mermaid
sequenceDiagram
    participant U as Developer
    participant C as Claude Code
    participant MCP as MCP Servers
    participant FS as Filesystem
    participant Sub as Subagent

    Note over U,Sub: Phase 1 - Setup and Requirements
    U->>C: Invoke skill + Ticket URL + Design URL
    C->>C: TaskCreate x5
    par Ticket + Design fetch
        C->>MCP: Fetch ticket details
        MCP-->>C: Ticket with acceptance criteria
        C->>C: Search for design tool MCP
        C-->>C: Not available - fallback
    end

    Note over U,Sub: Phase 2 - Component Analysis
    C->>Sub: Explore agent - inventory all components
    Sub-->>C: 30+ components cataloged
    par Read component source files
        C->>FS: Read DropDown, Button, CTAText, Validation
    end
    par Read more components
        C->>FS: Read BannerNotice, SheetView, PageHeader
    end
    par Token and API verification
        C->>FS: Read Icons, Actions, Navigation, FieldLabel
    end

    Note over U,Sub: Phase 3 - Plan Presentation
    C->>U: Component plan with layout, tokens, state

    Note over U,Sub: Phase 4 - Developer Review
    U->>C: Looks correct

    Note over U,Sub: Phase 5 - Usage Plan and Feedback
    C->>U: Component usage plan with verified APIs
    U->>C: Cancel buttons should use Button with different styles

    Note over U,Sub: Phase 6 - Revised Plan
    C->>U: Updated plan with .secondary and .tertiary
    U->>C: Yes

    Note over U,Sub: Phase 7 - Code Generation
    par Pre-write verification
        C->>FS: Verify directory, check helper patterns
    end
    C->>FS: Write GeneratedScreen.swift

    Note over U,Sub: Phase 8 - Build Validation
    C->>FS: CLI build (fails)
    U->>C: Try with the Xcode MCP
    C->>MCP: BuildProject
    MCP-->>C: Build succeeded

    Note over U,Sub: Phase 9 - Summary
    C->>U: Final summary
```

#### Key Observations

1. **Design tool fallback was seamless.** The design tool MCP wasn't available, but the ticket's detailed acceptance criteria provided sufficient requirements. The skill adapted without blocking.

2. **Subagent delegation was the right call.** The Explore subagent spent 67s cataloging 30+ components in parallel while the main agent retained context for synthesis.

3. **Component file reading was thorough.** 16 Read calls across 13 component files ensured API verification before code generation.

4. **Developer checkpoints caught a real issue.** The developer corrected the CTA approach from text links to styled buttons — a design decision that couldn't be automated.

5. **Build validation was the biggest bottleneck.** Phase 8 consumed 198s (24% of total) due to two failed CLI build approaches before the user directed to the Xcode MCP.

6. **The Xcode MCP build took 47s but worked first try.** Once directed to the right tool, validation completed with zero errors.

7. **Agent time dominated at 74%.** Only 3 user messages contained substantive input. The rest was automated tool orchestration.

#### Duration and Metrics

```mermaid
gantt
    title Session Timeline
    dateFormat YYYY-MM-DD HH:mm:ss
    axisFormat %M:%S

    section Requirements
    Setup and Requirements (42s)       :p1, 2024-01-01 00:00:00, 42s

    section Analysis
    Component Analysis (148s)          :p2, after p1, 148s

    section Planning
    Plan Presentation (22s)            :p3, after p2, 22s
    Plan Review (73s)                  :crit, p4, after p3, 73s
    Usage Plan and Feedback (75s)      :p5, after p4, 75s
    Revised Plan Confirmation (27s)    :crit, p6, after p5, 27s

    section Implementation
    Code Generation (166s)             :p7, after p6, 166s

    section Validation
    Build Validation (198s)            :p8, after p7, 198s
    Summary (11s)                      :p9, after p8, 11s
```

```mermaid
pie title "Agent vs Developer Time"
    "Agent" : 604
    "Developer" : 209
```

```mermaid
xychart-beta
    title "Duration by Phase (seconds)"
    x-axis ["Setup", "Analysis", "PlanPres", "PlanRevw", "UsagePln", "RevisedCf", "CodeGen", "BuildVal", "Summary"]
    y-axis "Seconds" 0 --> 210
    bar [42, 148, 22, 73, 75, 27, 166, 198, 11]
```

> **Legend:** Setup = Setup & Requirements, Analysis = Component Analysis, PlanPres = Plan Presentation, PlanRevw = Plan Review, UsagePln = Usage Plan & Feedback, RevisedCf = Revised Plan Confirmation, CodeGen = Code Generation, BuildVal = Build Validation

| Metric | Value |
|--------|-------|
| Total duration | 13m 32s |
| Agent time | 604s (74.2%) |
| Developer time | 209s (25.8%) |
| Total tool calls | 57 |
| Files created | 1 |
| Components used | 5 |
| Components evaluated | 13 |
| User turns | 11 |
| Subagents dispatched | 1 (Explore) |
| MCP servers used | 2 |
| Developer checkpoints | 3 |
| Developer corrections | 1 |
| Build attempts | 3 (2 failed, 1 succeeded) |

#### Takeaway

The skill converted a ticket into a compilable, 230-line SwiftUI screen in 13.5 minutes, with 74% of the time fully automated. The agent handled requirements extraction, component library analysis (reading 13 source files), plan synthesis, and code generation without intervention. Developer time was concentrated in three checkpoints that validated design decisions — one of which caught a meaningful style correction that improved the button hierarchy. The main inefficiency was build validation (198s, 24% of total), where two CLI-based build approaches failed before the developer redirected to the Xcode MCP, which succeeded on the first attempt.


## License

MIT
