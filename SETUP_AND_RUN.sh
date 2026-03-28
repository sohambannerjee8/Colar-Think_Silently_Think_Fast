#!/bin/bash
# =============================================================================
# CoLaR Paper Replication - Setup and Run Script
# "Think Silently, Think Fast: Dynamic Latent Compression of LLM Reasoning Chains"
# =============================================================================

set -e
COLAR_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$COLAR_DIR/workspace"
VENV="$COLAR_DIR/venv"

echo "============================================"
echo "CoLaR Replication Setup"
echo "Working dir: $COLAR_DIR"
echo "Workspace:   $WORKSPACE"
echo "============================================"

# ---- Step 0: Activate environment ----
if [ ! -d "$VENV" ]; then
    echo "[Step 0] Creating Python 3.10 virtual environment..."
    python3.10 -m venv "$VENV"
fi
source "$VENV/bin/activate"
echo "[Step 0] Python: $(python --version), venv active"

# ---- Step 1: Install dependencies (if needed) ----
if ! python -c "import torch; import transformers; import lightning; import peft" 2>/dev/null; then
    echo "[Step 1] Installing dependencies..."
    pip install torch torchvision torchaudio
    pip install transformers lightning peft "numpy<2.0" datasets jsonlines tensorboard omegaconf
else
    echo "[Step 1] Dependencies already installed, skipping."
fi

# ---- Step 2: Download base model (requires HF auth for Llama) ----
MODEL_DIR="$WORKSPACE/models/llms/Llama-3.2-1B-Instruct"
if [ ! -f "$MODEL_DIR/config.json" ]; then
    echo "[Step 2] Downloading Llama-3.2-1B-Instruct..."
    echo "  NOTE: This is a gated model. You must:"
    echo "  1. Accept license at https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct"
    echo "  2. Run: huggingface-cli login"
    echo ""
    python -c "
from huggingface_hub import snapshot_download
snapshot_download('meta-llama/Llama-3.2-1B-Instruct', local_dir='$MODEL_DIR')
print('Model downloaded successfully!')
"
else
    echo "[Step 2] Llama model already exists, skipping."
fi

# ---- Step 3: Prepare GSM8K dataset ----
DATA_DIR="$WORKSPACE/datasets/text_reasoning/gsm"
if [ ! -f "$DATA_DIR/train.json" ]; then
    echo "[Step 3] Downloading and preprocessing GSM8K..."
    mkdir -p "$DATA_DIR"
    cd "$COLAR_DIR"
    python -c "
import json
from datasets import load_dataset

output_dir = '$DATA_DIR'
test_ds = load_dataset('openai/gsm8k', 'main', split='test')
train_ds = load_dataset('openai/gsm8k', 'main', split='train[:90%]')
val_ds = load_dataset('openai/gsm8k', 'main', split='train[90%:]')

for split, ds in zip(['train', 'val', 'test'], [train_ds, val_ds, test_ds]):
    ds_json = []
    for d in ds:
        q = d['question']
        a = d['answer']
        [steps, answer] = a.split('\n####')
        steps = steps.split('\n')
        answer = answer.strip()
        ds_json.append({'question': q, 'steps': steps, 'answer': answer})
    with open(f'{output_dir}/{split}.json', 'w') as f:
        json.dump(ds_json, f)
    print(f'  {split}: {len(ds_json)} samples')
"
else
    echo "[Step 3] GSM8K data already exists, skipping."
fi

# ---- Step 4: Download pretrained checkpoints ----
PRETRAINED_DIR="$COLAR_DIR/pretrained"
if [ ! -d "$PRETRAINED_DIR/logs" ]; then
    echo "[Step 4] Downloading pretrained CoLaR checkpoints from HuggingFace..."
    python -c "
from huggingface_hub import snapshot_download
snapshot_download('AlbertTan/CoLaR', local_dir='$PRETRAINED_DIR')
print('Pretrained checkpoints downloaded!')
"
else
    echo "[Step 4] Pretrained checkpoints already exist, skipping."
fi

echo ""
echo "============================================"
echo "Setup complete! Available commands:"
echo "============================================"
echo ""
echo "# Activate environment first:"
echo "source $VENV/bin/activate"
echo ""
echo "# --- SANITY CHECK (tiny data, no GPU needed) ---"
echo "cd $COLAR_DIR"
echo "python run.py --model=cot --dataset=qsa --no_log --devices=0 tiny_dataset=True --workspace_path=$WORKSPACE"
echo ""
echo "# --- EVALUATE PRETRAINED CoT BASELINE ---"
echo "python run.py --test_ckpt_path=$PRETRAINED_DIR/logs/cot/qsa-gsm/llama-1b-cot/checkpoints/epoch7__step12056__monitor0.560.ckpt --workspace_path=$WORKSPACE"
echo ""
echo "# --- EVALUATE PRETRAINED CoLaR (c=5, high compression) ---"
echo "python run.py --test_ckpt_path=$PRETRAINED_DIR/logs/colar/qsa-gsm/colar-final/checkpoints/colar_best.ckpt --workspace_path=$WORKSPACE compression_factor=5"
echo ""
echo "# --- EVALUATE PRETRAINED CoLaR (c=2, lower compression) ---"
echo "python run.py --test_ckpt_path=$PRETRAINED_DIR/logs/colar/qsa-gsm/colar-final/checkpoints/colar_best.ckpt --workspace_path=$WORKSPACE compression_factor=2"
echo ""
echo "# --- TRAIN CoT FROM SCRATCH (need GPU) ---"
echo "python run.py --devices=0 --model=cot --dataset=qsa --do_test --workspace_path=$WORKSPACE dataset_name=gsm model_id=Llama-3.2-1B-Instruct batch_size=8 accumulate_grad_batches=32 max_epochs=20"
echo ""
echo "# --- TRAIN CoLaR FROM SCRATCH (need CoT checkpoint first) ---"
echo "python run.py --devices=0 --model=colar --dataset=qsa --do_test --load_ckpt_path=<COT_CKPT_PATH> --workspace_path=$WORKSPACE dataset_name=gsm model_id=Llama-3.2-1B-Instruct batch_size=8 accumulate_grad_batches=32 max_compression_factor=5 compression_factor=5 max_new_tokens=16 max_epochs=20"
echo ""
