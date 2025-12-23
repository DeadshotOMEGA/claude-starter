#!/bin/bash
#
# Collaborative Mode Status Line
#
# Displays session progress when in collaborative mode.
# Falls back to default status line otherwise.
#
# Usage: Configure in .claude/settings.json:
#   {
#     "statusLine": {
#       "type": "command",
#       "command": ".claude/skills/collaborative-mode/scripts/collab-statusline.sh"
#     }
#   }

# Read JSON input from Claude Code
input=$(cat)

# Extract base info
MODEL=$(echo "$input" | jq -r '.model.display_name // "Claude"')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir // "."')
PROJECT_DIR=$(echo "$input" | jq -r '.workspace.project_dir // "."')

# Look for collaborative state file
STATE_FILE="$PROJECT_DIR/.claude/collaborative-state.json"

if [ -f "$STATE_FILE" ]; then
    ACTIVE=$(jq -r '.active // false' "$STATE_FILE" 2>/dev/null)

    if [ "$ACTIVE" = "true" ]; then
        # Extract collaborative session info
        PROJECT=$(jq -r '.project // "unknown"' "$STATE_FILE")
        PHASE=$(jq -r '.phase // "starting"' "$STATE_FILE")
        CATEGORY=$(jq -r '.category // empty' "$STATE_FILE")
        RISK=$(jq -r '.risk_level // "—"' "$STATE_FILE")
        SLUG=$(jq -r '.feature_slug // ""' "$STATE_FILE")

        # Get agents running
        AGENTS_COUNT=$(jq -r '.agents_running | length' "$STATE_FILE" 2>/dev/null || echo "0")
        FIRST_AGENT=$(jq -r '.agents_running[0] // empty' "$STATE_FILE" 2>/dev/null)

        # Calculate progress
        DONE=$(jq '[.progress[].completed] | add // 0' "$STATE_FILE" 2>/dev/null || echo "0")
        TOTAL=$(jq '[.progress[].total] | add // 32' "$STATE_FILE" 2>/dev/null || echo "32")

        # Phase emoji
        case "$PHASE" in
            "understanding") PHASE_ICON="\xf0\x9f\x8e\xaf" ;;  # Target
            "exploration")   PHASE_ICON="\xf0\x9f\x94\x8d" ;;  # Magnifying glass
            "design")        PHASE_ICON="\xe2\x9c\x8f\xef\xb8\x8f" ;;   # Pencil
            "review")        PHASE_ICON="\xf0\x9f\x94\x84" ;;  # Arrows circle
            "exit")          PHASE_ICON="\xf0\x9f\x9a\x80" ;;  # Rocket
            *)               PHASE_ICON="\xf0\x9f\x93\x8b" ;;  # Clipboard
        esac

        # Risk color (ANSI codes)
        case "$RISK" in
            "HIGH")     RISK_DISPLAY="\033[31m$RISK\033[0m" ;;  # Red
            "MODERATE") RISK_DISPLAY="\033[33m$RISK\033[0m" ;;  # Yellow
            "LOW")      RISK_DISPLAY="\033[32m$RISK\033[0m" ;;  # Green
            *)          RISK_DISPLAY="$RISK" ;;
        esac

        # Build agent indicator
        AGENT_INDICATOR=""
        if [ "$AGENTS_COUNT" -gt 0 ] && [ -n "$FIRST_AGENT" ]; then
            AGENT_INDICATOR=" \xe2\x9a\xa1$FIRST_AGENT"  # Lightning bolt
            if [ "$AGENTS_COUNT" -gt 1 ]; then
                AGENT_INDICATOR="$AGENT_INDICATOR+$((AGENTS_COUNT-1))"
            fi
        fi

        # Build category display
        CATEGORY_DISPLAY=""
        if [ -n "$CATEGORY" ]; then
            CATEGORY_DISPLAY=":$CATEGORY"
        fi

        # Output collaborative status line
        echo -e "[$MODEL] \xf0\x9f\xa4\x9d $PROJECT $PHASE_ICON $PHASE$CATEGORY_DISPLAY [$DONE/$TOTAL] $RISK_DISPLAY$AGENT_INDICATOR"
        exit 0
    fi
fi

# Default status line (not in collaborative mode)
# Show git branch if available
GIT_BRANCH=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        GIT_BRANCH=" | \xf0\x9f\x8c\xbf $BRANCH"  # Branch emoji
    fi
fi

DIR_NAME="${CURRENT_DIR##*/}"
echo -e "[$MODEL] \xf0\x9f\x93\x81 $DIR_NAME$GIT_BRANCH"
