#!/usr/bin/env python3
"""Parse a Claude Code session .jsonl log and extract skill execution metrics.

Usage:
    python3 parse_session.py <session_log.jsonl> [--skill <skill-name>]

Output: JSON with structured session data including timestamps, phases, tool calls,
and duration breakdowns for the targeted skill execution.
"""

import json
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict


def parse_timestamp(ts_str):
    """Parse ISO timestamp string to datetime."""
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def extract_text_preview(content, max_len=120):
    """Extract a short text preview from message content."""
    if isinstance(content, str):
        return content[:max_len].replace("\n", " ")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    return block.get("text", "")[:max_len].replace("\n", " ")
                if block.get("type") == "tool_use":
                    return f"[tool: {block.get('name', '?')}]"
                if block.get("type") == "tool_result":
                    return "[tool_result]"
    return ""


def extract_tool_names(content):
    """Extract all tool names from a message's content blocks."""
    tools = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                tools.append(block.get("name", "unknown"))
    return tools


def find_skill_invocation(events):
    """Find the skill invocation command in user messages."""
    for ev in events:
        msg = ev.get("message", {})
        if msg.get("role") != "user":
            continue
        content = msg.get("content", "")
        text = ""
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text += block.get("text", "")
        if "<command-name>/" in text:
            import re
            match = re.search(r"<command-name>/([^<]+)</command-name>", text)
            if match:
                return match.group(1).strip()
    return None


def parse_session(log_path, target_skill=None):
    """Parse session log and return structured metrics."""
    events = []
    with open(log_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not events:
        return {"error": "No events found in log file"}

    # Auto-detect skill if not specified
    detected_skill = find_skill_invocation(events)
    skill_name = target_skill or detected_skill

    # Extract timeline of messages
    timeline = []
    tool_call_count = defaultdict(int)
    total_tool_calls = 0

    for ev in events:
        ts = parse_timestamp(ev.get("timestamp"))
        msg = ev.get("message", {})
        role = msg.get("role")
        content = msg.get("content", "")

        if ts and role in ("user", "assistant"):
            tools = extract_tool_names(content)
            for t in tools:
                tool_call_count[t] += 1
                total_tool_calls += 1

            timeline.append({
                "timestamp": ts.isoformat(),
                "time_str": ts.strftime("%H:%M:%S"),
                "role": role,
                "preview": extract_text_preview(content),
                "tools": tools,
            })

    if not timeline:
        return {"error": "No messages found in timeline"}

    # Calculate session boundaries
    first_ts = parse_timestamp(timeline[0]["timestamp"])
    last_ts = parse_timestamp(timeline[-1]["timestamp"])
    total_duration_s = (last_ts - first_ts).total_seconds() if first_ts and last_ts else 0

    # Identify user turns (conversation turns)
    user_turns = [t for t in timeline if t["role"] == "user" and t["preview"] and not t["preview"].startswith("[tool")]
    assistant_turns = [t for t in timeline if t["role"] == "assistant"]

    # Calculate agent vs developer time
    # Developer time = gaps between last assistant message and next user message
    developer_time_s = 0
    agent_time_s = 0
    last_assistant_ts = None

    for entry in timeline:
        ts = parse_timestamp(entry["timestamp"])
        if entry["role"] == "assistant":
            if last_assistant_ts is None and first_ts:
                # First assistant response - agent processing from start
                pass
            last_assistant_ts = ts
        elif entry["role"] == "user" and last_assistant_ts and entry["preview"] and not entry["preview"].startswith("[tool"):
            # User typing time
            gap = (ts - last_assistant_ts).total_seconds()
            if gap > 2:  # Only count gaps > 2s as developer time
                developer_time_s += gap

    agent_time_s = total_duration_s - developer_time_s

    # Tool call summary
    tool_summary = dict(sorted(tool_call_count.items(), key=lambda x: -x[1]))

    # Build the result
    result = {
        "session_log": os.path.basename(log_path),
        "detected_skill": skill_name,
        "total_duration_s": round(total_duration_s, 1),
        "total_duration_human": f"{int(total_duration_s // 60)}m {int(total_duration_s % 60)}s",
        "agent_time_s": round(agent_time_s, 1),
        "developer_time_s": round(developer_time_s, 1),
        "agent_pct": round(agent_time_s / total_duration_s * 100, 1) if total_duration_s > 0 else 0,
        "developer_pct": round(developer_time_s / total_duration_s * 100, 1) if total_duration_s > 0 else 0,
        "total_events": len(events),
        "total_tool_calls": total_tool_calls,
        "user_turns": len(user_turns),
        "assistant_messages": len(assistant_turns),
        "tool_call_breakdown": tool_summary,
        "timeline": timeline,
    }

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_session.py <session_log.jsonl> [--skill <skill-name>]")
        sys.exit(1)

    log_path = sys.argv[1]
    target_skill = None

    if "--skill" in sys.argv:
        idx = sys.argv.index("--skill")
        if idx + 1 < len(sys.argv):
            target_skill = sys.argv[idx + 1]

    if not os.path.exists(log_path):
        print(f"Error: File not found: {log_path}")
        sys.exit(1)

    result = parse_session(log_path, target_skill)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
