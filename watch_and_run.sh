#!/bin/bash
# Watches for eval completions, updates memory, and chains the next eval automatically.
# Run this in the background: bash watch_and_run.sh &> watch_and_run.log &

set -e
COLAR_DIR="$(cd "$(dirname "$0")" && pwd)"
MEMORY_FILE="/Users/soham/.claude/projects/-Users-soham-Downloads-researchpaper/memory/project_colar_replication.md"
LOG_FILE="$COLAR_DIR/watch_and_run.log"
source "$COLAR_DIR/venv/bin/activate"

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

update_memory() {
    local section="$1"
    local content="$2"
    python3 - <<EOF
import re

with open('$MEMORY_FILE', 'r') as f:
    text = f.read()

# Replace the status section
old = r'## Current Status.*'
text = re.sub(r'## Current Status \(as of [^\n]+\)', '## Current Status (as of $(date +%Y-%m-%d\ %H:%M))', text)

with open('$MEMORY_FILE', 'w') as f:
    f.write(text)
EOF
    # Append results section
    python3 - <<EOF2
with open('$MEMORY_FILE', 'r') as f:
    text = f.read()

marker = '## Results'
new_block = """## Results

$content
"""
if marker in text:
    # Replace existing results section
    import re
    text = re.sub(r'## Results\n[\s\S]*', new_block, text)
else:
    text = text.rstrip() + '\n\n' + new_block

with open('$MEMORY_FILE', 'w') as f:
    f.write(text)
EOF2
    log "Memory updated: $section"
}

extract_acc() {
    local json="$1"
    python3 -c "
import json, statistics
with open('$json') as f:
    d = json.load(f)
accs = [v['acc'] for v in d.values() if isinstance(v, dict) and 'acc' in v]
flat = [a for sub in accs for a in (sub if isinstance(sub, list) else [sub])]
correct = sum(1 for a in flat if a == 1.0)
total = len(flat)
# average per-question (across test_times runs)
per_q = []
for v in d.values():
    if isinstance(v, dict) and 'acc' in v:
        a = v['acc']
        per_q.append(sum(a)/len(a) if isinstance(a, list) else a)
avg = sum(per_q)/len(per_q) if per_q else 0
print(f'{avg*100:.1f}')
" 2>/dev/null || echo "?"
}

extract_chain_len() {
    local json="$1"
    python3 -c "
import json
with open('$json') as f:
    d = json.load(f)
lens = []
for v in d.values():
    if isinstance(v, dict):
        if 'output_length' in v:
            l = v['output_length']
            lens.extend(l if isinstance(l, list) else [l])
        elif 'n_latent_forward' in v:
            l = v['n_latent_forward']
            lens.extend(l if isinstance(l, list) else [l])
avg = sum(lens)/len(lens) if lens else 0
print(f'{avg:.2f}')
" 2>/dev/null || echo "?"
}

# ─── Wait for CoT to finish ───────────────────────────────────────────────────
log "Waiting for CoT evaluation to complete (PID 9590)..."
COT_JSON="$COLAR_DIR/logs/cot/qsa-gsm/g-1b-cot-bs256/test.json"
while ps -p 9590 > /dev/null 2>&1; do
    sleep 30
done
log "CoT process finished."

# Give it 5s to flush files
sleep 5

if [ -f "$COT_JSON" ]; then
    COT_ACC=$(extract_acc "$COT_JSON")
    COT_LEN=$(extract_chain_len "$COT_JSON")
    log "CoT result: acc=$COT_ACC% chain_len=$COT_LEN"
else
    log "WARNING: CoT test.json not found at $COT_JSON"
    COT_ACC="not found"
    COT_LEN="?"
fi

update_memory "CoT done" "| CoT (replicated) | ${COT_ACC}% | ${COT_LEN} | ~53.6% expected |"

# ─── Run CoLaR c=5 ────────────────────────────────────────────────────────────
log "Starting CoLaR c=5 evaluation..."
cd "$COLAR_DIR"
python run.py \
    --test_ckpt_path=pretrained/logs/colar/qsa-gsm/colar-final/checkpoints/colar_best.ckpt \
    --workspace_path=workspace \
    compression_factor=5 \
    --log_suffix=colar-c5 \
    2>&1 | tee -a "$LOG_FILE"

log "CoLaR c=5 process finished."
sleep 5

COLAR5_JSON=$(find "$COLAR_DIR/logs/colar" -name "test.json" -newer "$COLAR_DIR/watch_and_run.log" 2>/dev/null | head -1)
if [ -f "$COLAR5_JSON" ]; then
    C5_ACC=$(extract_acc "$COLAR5_JSON")
    C5_LEN=$(extract_chain_len "$COLAR5_JSON")
    log "CoLaR c=5 result: acc=$C5_ACC% chain_len=$C5_LEN"
else
    log "WARNING: CoLaR c=5 test.json not found"
    C5_ACC="not found"; C5_LEN="?"
fi

update_memory "CoLaR c=5 done" "| CoT (replicated) | ${COT_ACC}% | ${COT_LEN} | ~53.6% expected |
| CoLaR-5 (replicated) | ${C5_ACC}% | ${C5_LEN} blobs | ~41.7% expected |"

# ─── Run CoLaR c=2 ────────────────────────────────────────────────────────────
log "Starting CoLaR c=2 evaluation..."
cd "$COLAR_DIR"
python run.py \
    --test_ckpt_path=pretrained/logs/colar/qsa-gsm/colar-final/checkpoints/colar_best.ckpt \
    --workspace_path=workspace \
    compression_factor=2 \
    --log_suffix=colar-c2 \
    2>&1 | tee -a "$LOG_FILE"

log "CoLaR c=2 process finished."
sleep 5

COLAR2_JSON=$(find "$COLAR_DIR/logs/colar" -name "test.json" -newer "$COLAR5_JSON" 2>/dev/null | head -1)
if [ -f "$COLAR2_JSON" ]; then
    C2_ACC=$(extract_acc "$COLAR2_JSON")
    C2_LEN=$(extract_chain_len "$COLAR2_JSON")
    log "CoLaR c=2 result: acc=$C2_ACC% chain_len=$C2_LEN"
else
    log "WARNING: CoLaR c=2 test.json not found"
    C2_ACC="not found"; C2_LEN="?"
fi

# ─── Final memory update ──────────────────────────────────────────────────────
update_memory "ALL DONE" "| CoT (replicated) | ${COT_ACC}% | ${COT_LEN} tokens | ~53.6% expected |
| CoLaR-5 (replicated) | ${C5_ACC}% | ${C5_LEN} blobs | ~41.7% expected |
| CoLaR-2 (replicated) | ${C2_ACC}% | ${C2_LEN} blobs | ~48.8% expected |"

# Also update the status checkboxes
python3 - <<EOF
with open('$MEMORY_FILE', 'r') as f:
    text = f.read()
text = text.replace('- [**RUNNING**] CoT evaluation', '- [x] CoT evaluation — DONE, acc=${COT_ACC}%')
text = text.replace('- [ ] CoLaR c=5 evaluation — not started yet', '- [x] CoLaR c=5 evaluation — DONE, acc=${C5_ACC}%')
text = text.replace('- [ ] CoLaR c=2 evaluation — not started yet', '- [x] CoLaR c=2 evaluation — DONE, acc=${C2_ACC}%')
with open('$MEMORY_FILE', 'w') as f:
    f.write(text)
EOF

log "All evaluations complete. Memory file fully updated."
log "Summary: CoT=${COT_ACC}% | CoLaR-5=${C5_ACC}% | CoLaR-2=${C2_ACC}%"
