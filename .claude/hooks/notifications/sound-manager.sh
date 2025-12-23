#!/bin/bash

# Unified notification sound manager - cross-platform support
# Consolidates play-sound.sh and notification-sound.sh
#
# Environment variables:
#   CLAUDE_NOTIFICATION_SOUND - Custom sound file path
#   CLAUDE_SOUND_REPEAT - Number of times to play (default: 1)
#   CLAUDE_SOUND_DELAY - Delay between repeats in seconds (default: 0.1)

# Read JSON input if available (for Notification events)
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
SOUND_FILE="${CLAUDE_NOTIFICATION_SOUND:-}"
REPEAT="${CLAUDE_SOUND_REPEAT:-1}"
DELAY="${CLAUDE_SOUND_DELAY:-0.1}"

# Auto-set repeat count based on event type
if [[ "$hook_event" == "Notification" ]]; then
  REPEAT="${CLAUDE_SOUND_REPEAT:-3}"
fi

play_sound() {
  if command -v paplay &>/dev/null; then
    # PulseAudio (Linux/WSL2 with audio support)
    local sound="${SOUND_FILE:-/usr/share/sounds/freedesktop/stereo/complete.oga}"
    paplay "$sound" 2>/dev/null
  elif command -v powershell.exe &>/dev/null; then
    # WSL2 with Windows sound
    local sound="${SOUND_FILE:-/mnt/c/Windows/Media/chimes.wav}"
    # Convert WSL path to Windows path
    local win_path=$(echo "$sound" | sed 's|^/mnt/\([a-z]\)/|\U\1:/|')
    powershell.exe -c "(New-Object Media.SoundPlayer '$win_path').PlaySync()" 2>/dev/null
  elif command -v aplay &>/dev/null; then
    # ALSA (Linux)
    local sound="${SOUND_FILE:-/usr/share/sounds/alsa/Front_Center.wav}"
    aplay -q "$sound" 2>/dev/null
  elif command -v afplay &>/dev/null; then
    # macOS
    local sound="${SOUND_FILE:-/System/Library/Sounds/Glass.aiff}"
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
