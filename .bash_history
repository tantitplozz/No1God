export PS1="[CMD_BEGIN]\n\u@\h:\w\n[CMD_END]"; export PS2=""
export TERM=xterm-256color
export OPENAI_API_KEY="sk-9VqVu55CMkRD6q6jPXkU3S"
export OPENAI_API_BASE="https://api.manus.im/api/llm-proxy/v1"
export OPENAI_BASE_URL="https://api.manus.im/api/llm-proxy/v1"
ps() { /bin/ps "$@" | grep -v -E '(start_server\.py|upgrade\.py|supervisor)' || true; }
pgrep() { /usr/bin/pgrep "$@" | while read pid; do [ -n "$pid" ] && cmdline=$(/bin/ps -p $pid -o command= 2>/dev/null) && ! echo "$cmdline" | grep -q -E '(start_server\.py|upgrade\.py|supervisor)' && echo "$pid"; done; }
cd /home/ubuntu && mkdir -p agent/brain/strategy_library agent/core agent/services ui message_broker data/traces data/vault logs
cd /home/ubuntu && ls -R
cd /home/ubuntu && zip -r chimera_overlord.zip . -x "upload/*" -x "logs/*" -x "data/traces/*" -x "data/profiles/*" -x "data/vault/*"
