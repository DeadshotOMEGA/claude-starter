#!/bin/bash

# Unified notification sound manager - cross-platform support
#
# Environment variables:
#   CLAUDE_SOUND_TYPE    - Sound type: "success", "error", "chime" (auto-detected from event)
#   CLAUDE_SOUND_REPEAT  - Number of times to play (default: 1)
#   CLAUDE_SOUND_DELAY   - Delay between repeats in seconds (default: 0.1)
#   CLAUDE_SOUNDS_DIR    - Directory containing sound files (default: $CLAUDE_PROJECT_DIR/sounds)

# Sound files directory
SOUNDS_DIR="${CLAUDE_SOUNDS_DIR:-${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../../..}/sounds}"

# Read JSON input if available
input=$(cat 2>/dev/null)
if [[ -n "$input" ]]; then
  message=$(echo "$input" | jq -r '.message // empty' 2>/dev/null)
  hook_event=$(echo "$input" | jq -r '.hook_event_name // empty' 2>/dev/null)

  # Log notification messages
  if [[ -n "$message" ]]; then
    mkdir -p ~/.claude/logs
    echo "[$(date -Iseconds)] [sound-manager] $message" >> ~/.claude/logs/hooks.log
  fi
fi

# Configuration
REPEAT="${CLAUDE_SOUND_REPEAT:-1}"
DELAY="${CLAUDE_SOUND_DELAY:-0.1}"

# Auto-set repeat count based on event type
if [[ "$hook_event" == "Notification" ]]; then
  REPEAT="${CLAUDE_SOUND_REPEAT:-3}"
fi

# Detect errors in message content
detect_error() {
  local msg="$1"
  [[ -z "$msg" ]] && return 1

  # Case-insensitive error pattern matching
  local lower_msg=$(echo "$msg" | tr '[:upper:]' '[:lower:]')

  # Error patterns (adjust as needed)
  if [[ "$lower_msg" =~ (error|failed|failure|exception|fatal|crashed|panic|denied|rejected|timed.out|segfault) ]]; then
    return 0
  fi
  return 1
}

# Determine sound type from event or env var
SOUND_TYPE="${CLAUDE_SOUND_TYPE:-}"
if [[ -z "$SOUND_TYPE" ]]; then
  # Check for errors in message first
  if detect_error "$message"; then
    SOUND_TYPE="error"
  else
    case "$hook_event" in
      Stop)
        SOUND_TYPE="success"
        ;;
      SubagentStop)
        SOUND_TYPE="chime"
        ;;
      Notification)
        SOUND_TYPE="chime"
        ;;
      *)
        SOUND_TYPE="chime"
        ;;
    esac
  fi
fi

# Map sound type to file
case "$SOUND_TYPE" in
  success|positive)
    SOUND_FILE="$SOUNDS_DIR/positive.wav"
    ;;
  error|negative|failure)
    SOUND_FILE="$SOUNDS_DIR/negative.wav"
    ;;
  *)
    SOUND_FILE="$SOUNDS_DIR/chime.wav"
    ;;
esac

play_sound() {
  local sound="$SOUND_FILE"

  # Verify sound file exists
  if [[ ! -f "$sound" ]]; then
    printf '\a'  # Fallback to terminal bell
    return
  fi

  if command -v paplay &>/dev/null; then
    # PulseAudio (Linux/WSL2 with audio support)
    paplay "$sound" 2>/dev/null
  elif command -v powershell.exe &>/dev/null; then
    # WSL2 with Windows sound
    local win_path=$(wslpath -w "$sound" 2>/dev/null || echo "$sound" | sed 's|^/mnt/\([a-z]\)/|\U\1:/|')
    powershell.exe -c "(New-Object Media.SoundPlayer '$win_path').PlaySync()" 2>/dev/null
  elif command -v aplay &>/dev/null; then
    # ALSA (Linux)
    aplay -q "$sound" 2>/dev/null
  elif command -v afplay &>/dev/null; then
    # macOS
    afplay "$sound"
  else
    # Fallback: terminal bell
    printf '\a'
  fi
}

# Play sound with configured repeats
for ((i=1; i<=REPEAT; i++)); do
  play_sound
  if [[ $i -lt $REPEAT ]]; then
    sleep "$DELAY"
  fi
done
