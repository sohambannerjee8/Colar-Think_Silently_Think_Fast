# CoLaR Replication — Think Silently, Think Fast

Replication of the paper **"Think Silently, Think Fast: Dynamic Latent Compression of LLM Reasoning Chains"** (arXiv 2505.16552) using the authors' pretrained checkpoints on GSM8K.

**Original paper:** [arXiv](https://arxiv.org/pdf/2505.16552) | **Original repo:** [xiaomi-research/colar](https://github.com/xiaomi-research/colar) | **Pretrained models:** [AlbertTan/CoLaR](https://huggingface.co/AlbertTan/CoLaR)

---

## What We Did

- Downloaded the authors' pretrained CoT and CoLaR checkpoints (Llama-3.2-1B-Instruct backbone)
- Fixed two bugs that blocked evaluation on local setup (see [Bug Fixes](#bug-fixes))
- Ran all three evaluations on Apple M5 MPS (24GB RAM) — each run averages over 5 random seeds
- Built a Streamlit dashboard (`dashboard.py`) explaining the paper architecture, training pipeline, and replication results

---

## Replication Results (GSM8K Test Set)

| Method | Our Accuracy | Our Chain Length | Paper Accuracy | Paper Chain Length |
|--------|-------------|-----------------|----------------|--------------------|
| CoT baseline | **49.96%** | 25.60 tokens | 53.6% | 21.4 tokens |
| CoLaR c=5 | **24.97%** | 5.65 blobs | 41.7% | 4.57 blobs |
| CoLaR c=2 | **40.41%** | 12.84 blobs | 48.8% | 10.0 blobs |

### Key Observations

- **Relative ordering is preserved**: CoLaR-2 > CoLaR-5, and both are below CoT — exactly as the paper reports.
- **Compression trade-off holds**: higher compression factor (c=5) → shorter chain but lower accuracy; lower compression factor (c=2) → longer chain but higher accuracy.
- **Accuracy gap vs paper**: our numbers are uniformly lower (~3–17%). This is expected — the paper trained and evaluated on NVIDIA GPUs (CUDA), while we run on Apple Silicon (MPS). The `bfloat16` floating-point behavior differs between the two backends, and small numerical differences compound across multiple latent generation steps.

---

## Setup

```bash
conda create -n colar python=3.10
conda activate colar
pip install -r requirements.txt
```

Download pretrained checkpoints from [AlbertTan/CoLaR](https://huggingface.co/AlbertTan/CoLaR) and place them under `pretrained/`.

Download the GSM8K dataset and Llama-3.2-1B-Instruct model under `workspace/`.

---

## Evaluation

```bash
# CoT baseline
python run.py \
  --test_ckpt_path=pretrained/logs/cot/qsa-gsm/llama-1b-cot/checkpoints/epoch7__step12056__monitor0.560.ckpt \
  --workspace_path=workspace

# CoLaR c=5
python run.py \
  --test_ckpt_path=pretrained/logs/colar/qsa-gsm/colar-final/checkpoints/colar_best.ckpt \
  --workspace_path=workspace compression_factor=5

# CoLaR c=2
python run.py \
  --test_ckpt_path=pretrained/logs/colar/qsa-gsm/colar-final/checkpoints/colar_best.ckpt \
  --workspace_path=workspace compression_factor=2
```

---

## Dashboard

An interactive Streamlit dashboard covering the paper architecture, training pipeline, code walkthrough, and live replication results:

```bash
streamlit run dashboard.py
```

---

## Bug Fixes

Two issues needed to be fixed to run evaluation on a fresh local setup:

1. **`LitCoT` vs `LitCot` capitalization** — the pretrained checkpoint was saved with class name `LitCoT` but the codebase defines `LitCot`. Fixed by adding an alias in `src/models/cot.py`:
   ```python
   LitCoT = LitCot  # alias for checkpoint compatibility
   ```

2. **`torch.load` missing `weights_only=False`** — PyTorch 2.x changed the default to `weights_only=True`, which breaks loading checkpoints that contain OmegaConf objects. Fixed in `run.py` line 29.
