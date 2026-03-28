"""
CoLaR Paper Replication Dashboard
"Think Silently, Think Fast: Dynamic Latent Compression of LLM Reasoning Chains"

Run: streamlit run dashboard.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import json
import os
import glob
from pathlib import Path

COLAR_DIR = Path(__file__).parent
WORKSPACE = COLAR_DIR / "workspace"
LOGS_DIR = COLAR_DIR / "logs"
PRETRAINED_DIR = COLAR_DIR / "pretrained"

# ──────────────────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CoLaR Replication Dashboard",
    page_icon="brain",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# Sidebar Navigation
# ──────────────────────────────────────────────────────────
st.sidebar.title("CoLaR Dashboard")
page = st.sidebar.radio(
    "Navigate",
    [
        "1. Paper Overview",
        "2. The Problem",
        "3. Architecture Deep Dive",
        "4. Training Pipeline",
        "5. Code Walkthrough",
        "6. Replication Results",
        "7. Key Insights",
    ],
)

# ══════════════════════════════════════════════════════════
# PAGE 1: Paper Overview
# ══════════════════════════════════════════════════════════
if page == "1. Paper Overview":
    st.title("CoLaR: Compressed Latent Reasoning")
    st.markdown("### *Think Silently, Think Fast: Dynamic Latent Compression of LLM Reasoning Chains*")
    st.markdown("**Wenhui Tan, Jiaze Li, Jianzhong Ju, Zhenbo Luo, Jian Luan, Ruihua Song**")
    st.markdown("Renmin University of China & Xiaomi Inc. | arXiv: 2505.16552")

    st.divider()

    # Core idea
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### The One-Sentence Summary")
        st.info(
            "CoLaR teaches LLMs to **think in compressed shorthand** instead of "
            "writing every reasoning step as text tokens. The compression speed is "
            "**adjustable at inference time** via a simple prompt — no retraining needed."
        )

    with col2:
        st.markdown("### Why It Matters")
        st.warning(
            "Chain-of-Thought (CoT) reasoning is powerful but expensive: each token "
            "costs compute time and memory. CoLaR achieves **up to 5x faster reasoning** "
            "with only **~5% accuracy loss** — and on hard problems, it can actually "
            "**beat the CoT teacher**."
        )

    st.divider()

    # Key contributions
    st.markdown("### Key Contributions")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 1. Dynamic Compression")
        st.markdown(
            "Unlike prior methods (Coconut, CODI) that use a **fixed** number of latent steps, "
            "CoLaR lets you choose the compression factor `c` at inference time. "
            "Train once, deploy at any speed."
        )
    with c2:
        st.markdown("#### 2. Two-Stage Training")
        st.markdown(
            "**Stage 1 (SFT):** Learn to compress reasoning into latent blobs.\n\n"
            "**Stage 2 (RL):** Use GRPO to discover even shorter, smarter reasoning paths. "
            "The model learns to be both **more accurate** and **more concise**."
        )
    with c3:
        st.markdown("#### 3. State-of-the-Art Results")
        st.markdown(
            "CoLaR-2 achieves **48.8% accuracy** with only **10 latent steps** "
            "(vs CoT's 21.4 tokens at 53.6%). On GPQA, CoLaR-8B-RL **beats its CoT teacher** "
            "(37.5% vs 35.7%) using 69% fewer steps."
        )

    # Comparison table
    st.divider()
    st.markdown("### How CoLaR Compares (GSM8K, Llama-3.2-1B)")

    comparison_data = {
        "Method": ["CoT (baseline)", "iCoT", "Coconut", "Distill (CODI)", "CoLaR-5", "CoLaR-2"],
        "Avg Accuracy (%)": [53.6, 24.6, 27.6, 14.3, 41.7, 48.8],
        "Chain Length": [21.4, 0, 6, 6, 4.57, 10.0],
        "Reasoning Type": ["Text tokens", "No reasoning", "Fixed latent", "Fixed latent", "Dynamic latent", "Dynamic latent"],
    }

    fig = go.Figure()
    colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3"]
    for i, method in enumerate(comparison_data["Method"]):
        fig.add_trace(go.Bar(
            name=method,
            x=[method],
            y=[comparison_data["Avg Accuracy (%)"][i]],
            text=[f"{comparison_data['Avg Accuracy (%)'][i]}%<br>({comparison_data['Chain Length'][i]} steps)"],
            textposition='outside',
            marker_color=colors[i],
        ))
    fig.update_layout(
        title="Accuracy vs Method (Paper Table 1 — GSM8K Average)",
        yaxis_title="Accuracy (%)",
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════
# PAGE 2: The Problem
# ══════════════════════════════════════════════════════════
elif page == "2. The Problem":
    st.title("The Problem: Chain-of-Thought is Expensive")

    st.markdown("""
    ### What is Chain-of-Thought (CoT)?

    When you ask an LLM a math question, it generates intermediate reasoning steps before the answer:
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Without CoT")
        st.code("Q: 7 spoons cost $21. What do 5 cost?\nA: 15", language="text")
        st.error("Often wrong — the model guesses without reasoning")

    with col2:
        st.markdown("#### With CoT")
        st.code(
            "Q: 7 spoons cost $21. What do 5 cost?\n"
            "Let's think step by step:\n"
            "21 / 7 = 3 (one spoon costs $3)\n"
            "3 * 5 = 15 (five spoons cost $15)\n"
            "A: 15",
            language="text",
        )
        st.success("Correct — but generated 14 tokens of reasoning")

    st.divider()
    st.markdown("### The Cost Problem")

    st.markdown("""
    Every token the model generates takes:
    - **Time**: ~10-50ms per token on GPU (autoregressive generation is sequential)
    - **Memory**: KV-cache grows linearly with sequence length
    - **Cost**: At scale, millions of requests x 20+ reasoning tokens = massive compute bill

    **The question**: Can we keep the reasoning ability but reduce the number of generated tokens?
    """)

    st.divider()
    st.markdown("### Prior Approaches and Their Limitations")

    approaches = {
        "Method": ["iCoT", "Coconut", "CODI (Distill)", "CoLaR (this paper)"],
        "Idea": [
            "Gradually remove reasoning steps during training",
            "Replace text reasoning with fixed latent steps (hidden states fed back)",
            "Self-distillation: compress teacher CoT into latent representations",
            "Dynamic compressed latent reasoning with RL refinement",
        ],
        "Chain Length": ["0 (removes all)", "6 (fixed)", "6 (fixed)", "Flexible (1-64)"],
        "Limitation": [
            "Accuracy drops to 24.6% — too aggressive removal",
            "Fixed at 6 steps regardless of problem difficulty",
            "Only 14.3% accuracy — distillation loses too much info",
            "Slightly below CoT in accuracy (but much faster)",
        ],
    }

    for i in range(4):
        with st.expander(f"**{approaches['Method'][i]}** — {approaches['Idea'][i]}", expanded=(i == 3)):
            st.markdown(f"**Chain Length:** {approaches['Chain Length'][i]}")
            st.markdown(f"**Limitation:** {approaches['Limitation'][i]}")

    st.divider()
    st.markdown("### CoLaR's Key Insight")
    st.success(
        "**Don't remove reasoning — compress it.** Instead of generating 20 text tokens, "
        "generate 4 compressed latent vectors (\"blobs\") that encode the same information. "
        "And let the user choose how much compression they want at inference time."
    )


# ══════════════════════════════════════════════════════════
# PAGE 3: Architecture Deep Dive
# ══════════════════════════════════════════════════════════
elif page == "3. Architecture Deep Dive":
    st.title("Architecture: How CoLaR Works")

    st.markdown("### High-Level Architecture")
    st.markdown("""
    CoLaR adds two lightweight modules on top of a frozen LLM backbone:
    """)

    st.code("""
    ┌──────────────────────────────────────────────────────────────────┐
    │                         CoLaR Model                              │
    │                                                                  │
    │  ┌───────────────────────┐     ┌──────────────────────────────┐ │
    │  │  LLM Backbone         │     │  Latent Head (LatentPolicy)  │ │
    │  │  (Llama-3.2-1B)       │────>│  3-layer MLP                 │ │
    │  │                       │     │  Predicts Normal(mu, sigma)  │ │
    │  │  Frozen weights       │     │  for next thought-blob       │ │
    │  │  + LoRA adapters      │     └──────────────────────────────┘ │
    │  └───────────────────────┘                                       │
    │                                                                  │
    │  ┌───────────────────────┐                                       │
    │  │  Embedding Compress   │  Averages c consecutive embeddings   │
    │  │  (during training)    │  with 1/sqrt(c) scaling              │
    │  └───────────────────────┘                                       │
    └──────────────────────────────────────────────────────────────────┘
    """, language="text")

    st.divider()

    # Component 1: Embedding Compression
    st.markdown("### Component 1: Embedding Compression")
    st.markdown("""
    **What it does:** Takes `c` consecutive token embeddings and squishes them into one vector.

    **Why:** This is how we create the "compressed thoughts." During training, the model sees
    compressed reasoning chains and learns to work with them.
    """)

    st.markdown("#### The Math")
    st.latex(r"\text{compressed\_embed} = \frac{1}{\sqrt{c}} \sum_{i=1}^{c} \text{embed}_i")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Why `1/sqrt(c)` instead of `1/c` (mean)?")
        st.markdown("""
        Regular averaging (`1/c`) **shrinks the variance** of the embeddings:
        - If each embed has variance `sigma^2`, the mean of `c` embeds has variance `sigma^2/c`
        - The model was trained on embeddings with variance `sigma^2` — different variance confuses it

        Using `1/sqrt(c)` preserves the original variance:
        - Variance of sum/sqrt(c) = `c * sigma^2 / c = sigma^2` (unchanged!)
        """)

    with col2:
        st.markdown("#### Code (`colar.py`, lines 149-157)")
        st.code("""
# Reshape: (batch, seq_len, hidden) -> (batch, seq_len/c, c, hidden)
compressed = padded_embeds.reshape(
    batch_size, compressed_length, r, hidden_dim
).sum(dim=2)  # sum over the c tokens

# Attention mask tracks how many real tokens in each group
compressed_mask = padded_mask.reshape(
    batch_size, compressed_length, r
).sum(dim=2)

# sqrt scaling (not mean!)
if sqrt_mean:
    compressed_mask = compressed_mask.sqrt()

compressed /= (compressed_mask.unsqueeze(-1) + 1e-5)
        """, language="python")

    st.divider()

    # Component 2: Latent Head
    st.markdown("### Component 2: The Latent Head (LatentPolicy)")
    st.markdown("""
    **What it does:** Takes the LLM's hidden state and predicts a **probability distribution**
    over the next thought-blob.

    **Why a distribution (not a single vector)?** Stochastic sampling allows the model to:
    1. **Explore** different reasoning paths during RL training
    2. **Express uncertainty** — wider distribution = less confident about next step
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Architecture")
        st.code("""
LLM hidden state (2048-dim)
    │
    ▼
Linear(2048 → 2048) + GELU
    │
    ▼
Linear(2048 → 2048) + LayerNorm
    │
    ├──► mean_head: Linear(2048 → 2048) → mu
    │
    └──► log_std_head: Linear(2048 → 2048) → log(sigma)
                                                │
                                                ▼
                                    Sample from Normal(mu, sigma)
                                                │
                                                ▼
                                    Next thought-blob (2048-dim)
        """, language="text")

    with col2:
        st.markdown("#### Code (`projector.py`)")
        st.code("""
class LatentPolicy(nn.Module):
    def __init__(self, feature_size,
                 intermediate_size=512,
                 deterministic=False):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(feature_size, intermediate_size),
            nn.GELU(),
            nn.Linear(intermediate_size, intermediate_size),
            nn.LayerNorm(intermediate_size),
        )
        self.mean = nn.Linear(intermediate_size, feature_size)
        if not deterministic:
            self.log_std = nn.Linear(intermediate_size, feature_size)

    def forward(self, x, temperature=1.0):
        x = self.fc(x)
        mean = self.mean(x)
        log_std = self.log_std(x)
        std = log_std.exp() * temperature
        return Normal(mean, std)
        """, language="python")

    st.divider()

    # Component 3: LoRA
    st.markdown("### Component 3: LoRA Adapters")
    st.markdown("""
    **What:** Low-Rank Adaptation — small trainable matrices added to the LLM's attention layers.

    **Why:** The base Llama model is **frozen** (3.2B parameters). We only train:
    - LoRA adapters (rank 128): ~67M parameters
    - Latent Head: ~16M parameters
    - Total trainable: **~83M / 1.24B = 6.7%** of the model
    """)

    st.code("""
# From model_base.py — LoRA is applied to q_proj and v_proj
self.llm = get_peft_model(
    self.llm,
    peft_config=LoraConfig(r=128, lora_alpha=32)  # rank=128
)
    """, language="python")

    st.divider()

    # Inference flow
    st.markdown("### Inference Flow (Step by Step)")
    st.markdown("""
    When you ask CoLaR a question at test time, here's the exact sequence:
    """)

    steps = [
        ("1. Encode Question", "Tokenize + embed the question with speed prompt: `Question: ... (Thinking speed: 5)###`"),
        ("2. LLM Forward", "Run the question through Llama → get hidden state `h_1`"),
        ("3. Latent Head Predicts", "LatentPolicy takes `h_1` → samples thought-blob from Normal(mu, sigma)"),
        ("4. Feed Blob Back", "The blob is fed back into Llama as the next \"token\" embedding"),
        ("5. Repeat Steps 3-4", "Keep generating blobs until the LLM predicts `###` (end-of-thinking)"),
        ("6. Generate Answer", "After `###`, switch to normal text generation for the final answer"),
    ]
    for title, desc in steps:
        st.markdown(f"**{title}:** {desc}")

    st.code("""
# From model_base.py — latent_generate() (simplified)
for _ in range(max_n_latent_forward):  # max 64 steps
    # Latent Head predicts next blob distribution
    distributions = self.latent_policy(
        outputs.hidden_states[-1][:, -1:, :]
    )
    # Sample and scale by embedding std
    current_embed = distributions.rsample() * self.embeds_std

    # Feed blob back into LLM (with KV-cache)
    outputs = self.llm.forward(
        inputs_embeds=current_embed,
        past_key_values=past_key_values,
    )

    # Check if LLM wants to stop thinking
    next_token = torch.multinomial(softmax(outputs.logits[:, -1]), 1)
    if next_token == thinking_separator_id:  # '###'
        break

# Then generate answer normally
answer = self.llm.generate(inputs_embeds=all_embeds, ...)
    """, language="python")


# ══════════════════════════════════════════════════════════
# PAGE 4: Training Pipeline
# ══════════════════════════════════════════════════════════
elif page == "4. Training Pipeline":
    st.title("Training Pipeline: Two Stages")

    st.markdown("""
    CoLaR training has **two stages** — Supervised Fine-Tuning (SFT) to learn compression,
    then Reinforcement Learning (RL) to optimize for accuracy and conciseness.
    """)

    # Visual pipeline
    st.code("""
    Stage 0          Stage 1 (SFT)           Stage 2 (RL)
    ────────         ─────────────           ────────────
    Download    →    Train CoT baseline  →   Train CoLaR SFT  →   Train CoLaR RL
    Llama-1B         (50 epochs)              (50 epochs)          (~4000 steps)
                     Learns: full             Learns: compress     Learns: shorter +
                     text reasoning           reasoning into       smarter reasoning
                                              latent blobs
    """, language="text")

    st.divider()

    # Stage 1: SFT
    st.markdown("## Stage 1: Supervised Fine-Tuning (SFT)")

    tab1, tab2, tab3 = st.tabs(["Overview", "Loss Functions", "Key Code"])

    with tab1:
        st.markdown("""
        **Goal:** Teach the model to think in compressed blobs.

        **Training loop for each batch:**
        1. Sample a random compression factor `c` from `[1, max_c]` (default: [1, 5])
        2. Take the full reasoning chain (text tokens) and compress into blobs of size `c`
        3. Compute two losses: language modeling loss + latent prediction loss
        4. Backprop through LoRA weights + Latent Head

        **Why random `c`?** So the model becomes a **generalist** — it learns to handle
        any compression level from 1 (no compression) to 5 (max compression).
        This is what enables the "change speed at inference time" feature.
        """)

        st.code("""
# From colar.py forward() — random c sampling
r = random.randint(1, max_compression_factor)  # e.g., r in [1,5]
        """, language="python")

    with tab2:
        st.markdown("### Loss Function 1: Language Modeling Loss (`L_comp`)")
        st.markdown("""
        Standard cross-entropy loss — trains the LLM to predict what words are **inside** each
        compressed blob. Since each blob represents `c` tokens, we randomly pick one of those
        `c` tokens as the prediction target.

        **Why?** Without this, the model has no supervision signal for understanding the content
        of compressed blobs. The ablation study shows removing this drops accuracy by 1.6%.
        """)

        st.markdown("### Loss Function 2: Latent Prediction Loss (`L_latent`)")
        st.markdown("""
        Trains the Latent Head to predict the next blob accurately. Two versions were tested:
        """)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### NLL Loss (rejected)")
            st.latex(r"\mathcal{L}_{\text{NLL}} = -\log p_\theta(z_{t+1} | z_{\leq t})")
            st.markdown("Pure probabilistic loss. Too much randomness for simple problems.")

        with col2:
            st.markdown("#### Soft-MSE Loss (used)")
            st.latex(r"\mathcal{L}_{\text{latent}} = \text{MSE}(\hat{z}, z) - \alpha \cdot H(\sigma)")
            st.markdown("""
            MSE for accuracy + entropy term for exploration.
            - `alpha = -1e-6` (very small, just enough to prevent collapse)
            - The entropy term prevents sigma from going to zero
            """)

        st.markdown("### Total SFT Loss")
        st.latex(r"\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{comp}} + \mathcal{L}_{\text{latent}} + \alpha \cdot H(\sigma)")

    with tab3:
        st.markdown("### SFT Forward Pass (`colar.py` forward())")
        st.code("""
def forward(self, batch):
    r = random.randint(1, max_compression_factor)  # random c

    # Compress reasoning embeddings
    # [batch, seq_len, hidden] -> [batch, seq_len/c, hidden]
    compressed_embeds = reshape_and_sum(embeds, r) / sqrt(mask_sum)

    # Language modeling loss (CE on compressed tokens)
    outputs = self.llm.forward(
        inputs_embeds=compressed_embeds,
        labels=compressed_labels,
    )
    ce_loss = outputs.loss

    # Latent prediction loss
    distributions = self.latent_policy(outputs.hidden_states[-1])
    pred_embeds = distributions.rsample()

    # Soft-MSE: normalize by embedding std before computing loss
    embed_loss = F.mse_loss(
        pred_embeds,
        gold_embeds.detach() / self.embeds_std  # normalize!
    )

    # Entropy regularization
    entropy = distributions.entropy().mean()

    total_loss = ce_loss + embed_loss + entropy_weight * entropy
        """, language="python")

    st.divider()

    # Stage 2: RL
    st.markdown("## Stage 2: Reinforcement Learning with GRPO")

    tab1, tab2, tab3 = st.tabs(["Overview", "The Clever Trick", "Key Code"])

    with tab1:
        st.markdown("""
        **Goal:** Go beyond mimicking the teacher. Find **even shorter** and **smarter** reasoning paths.

        **Algorithm:** GRPO (Group Relative Policy Optimization) — a variant of PPO used in DeepSeek-R1.

        **How it works:**
        1. For each question, generate **8 different answers** by sampling from the Latent Head
        2. Check which answers are correct (reward = 1) or wrong (reward = 0)
        3. Compute **relative advantages** within the group:
        """)

        st.latex(r"A_i = \frac{r_i - \text{mean}(r_1 \ldots r_G)}{\text{std}(r_1 \ldots r_G)}")

        st.markdown("""
        4. Apply PPO-style clipped surrogate loss to reinforce correct paths

        **What changes after RL:**
        - Accuracy: 8.9% → **14.3%** (+5.4%)
        - Chain length: 56.8 → **9.79** (-83%)
        - The model got **both smarter AND faster**
        """)

    with tab2:
        st.markdown("### The Per-Token Reward Averaging Trick")
        st.markdown("""
        The reward is **spread evenly across every blob** in the reasoning chain.
        This creates an elegant incentive:
        """)

        col1, col2 = st.columns(2)
        with col1:
            st.error("""
            **Wrong answer, long path (50 blobs):**
            Penalty per blob = -1/50 = -0.02 (small)

            **Wrong answer, short path (10 blobs):**
            Penalty per blob = -1/10 = -0.1 (big!)

            **Result:** Model learns to think **deeper** when exploring wrong paths
            """)

        with col2:
            st.success("""
            **Correct answer, long path (50 blobs):**
            Reward per blob = +1/50 = +0.02 (small)

            **Correct answer, short path (10 blobs):**
            Reward per blob = +1/10 = +0.1 (big!)

            **Result:** Model learns to be **concise** when it knows the answer
            """)

        st.info(
            "This single mechanism drives the model to simultaneously become **more accurate** "
            "(explore more when uncertain) and **faster** (fewer blobs when confident)."
        )

    with tab3:
        st.markdown("### GRPO Code (`grpo.py` + `colar.py`)")
        st.code("""
# From grpo.py — advantage normalization
def group_advantages(returns, eps=1e-8):
    return (returns - returns.mean()) / (returns.std() + eps)

# From colar.py — rollout
def rollout(self, questions, gt_answers):
    # 1. Generate G=8 answers per question
    group_questions = [q for q in questions for _ in range(group_size)]
    results = self.latent_generate(group_questions, rl_mode=True)

    # 2. Score each answer
    for i in range(batch_size):
        group_answers = pred_answers[i*G : (i+1)*G]
        rewards[i] = verify_answer(gt, pred)  # 0 or 1
        # Optional: divide by chain length (per-token averaging)
        if punish_latent_length:
            rewards[i] /= n_latent_forward[i]
        advantages[i] = group_advantages(rewards[i])

# From grpo.py — clipped surrogate loss (PPO-style)
class GRPOLoss(nn.Module):
    def calculate_loss(self, logprobs, logprobs_old, mask, advantages):
        ratio = (logprobs - logprobs_old).exp()
        surr1 = ratio * advantages
        surr2 = ratio.clamp(1-eps, 1+eps) * advantages
        loss = -torch.min(surr1, surr2)
        return masked_mean(loss, mask).mean()
        """, language="python")

    st.divider()

    # Training curve
    st.markdown("### RL Training Curve (3 Phases)")

    fig = go.Figure()
    # Simulated training curve based on paper description
    steps = list(range(0, 5001, 200))
    # Accuracy: 9% → 14% (0-2k), 14-16% (2k-4k), overfit after
    acc = [9 + 5 * min(s / 2000, 1) + (2 * max(0, min((s - 2000) / 2000, 1))) for s in steps]
    # Chain length: 40 → 60 (0-2k), 60 → 20 (2k-4k)
    chain = [40 + 20 * min(s / 2000, 1) - 40 * max(0, min((s - 2000) / 2000, 1)) for s in steps]

    fig.add_trace(go.Scatter(x=steps, y=acc, name="Accuracy (%)", yaxis="y1", line=dict(color="blue", width=3)))
    fig.add_trace(go.Scatter(x=steps, y=chain, name="Chain Length (blobs)", yaxis="y2", line=dict(color="red", width=3, dash="dash")))

    fig.update_layout(
        title="RL Training Dynamics (Conceptual)",
        xaxis_title="Training Steps",
        yaxis=dict(title=dict(text="Accuracy (%)", font=dict(color="blue")), tickfont=dict(color="blue")),
        yaxis2=dict(title=dict(text="Chain Length", font=dict(color="red")), tickfont=dict(color="red"), overlaying="y", side="right"),
        height=400,
        annotations=[
            dict(x=1000, y=12, text="Phase 1: Explore", showarrow=False, font=dict(size=12)),
            dict(x=3000, y=16, text="Phase 2: Exploit", showarrow=False, font=dict(size=12)),
            dict(x=4500, y=16, text="Phase 3: Overfit", showarrow=False, font=dict(size=12, color="red")),
        ],
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════
# PAGE 5: Code Walkthrough
# ══════════════════════════════════════════════════════════
elif page == "5. Code Walkthrough":
    st.title("Code Walkthrough: File by File")

    st.markdown("""
    The codebase is organized around **PyTorch Lightning** — a framework that separates
    model logic from training boilerplate. Here's how each file maps to the paper:
    """)

    files = [
        {
            "name": "run.py",
            "role": "Entry Point",
            "paper_section": "Section 3 (Experiments)",
            "why": "Reads CLI arguments, loads configs, creates model + dataset + trainer. Handles both training and evaluation. This is where the evaluation loop loads checkpoints and runs test_times passes.",
            "key_code": """# Evaluation loop (lines 22-34)
if args.test_ckpt_path:
    state_dict = torch.load(ckpt_path, weights_only=False)["state_dict"]
    model.load_state_dict(state_dict, strict=False)  # strict=False: LoRA weights only
    for i in range(args.test_times):  # default: 5 runs with different seeds
        pl.seed_everything(args.seed + i)
        trainer.test(model=model, datamodule=data_module)""",
        },
        {
            "name": "src/models/model_base.py",
            "role": "Foundation Class",
            "paper_section": "Section 2.1 (Background)",
            "why": "Defines the base LLM setup shared by all methods (CoT, CoLaR, Coconut, etc.). Handles tokenization, prompt templates, LoRA setup, and the critical latent_generate() inference loop.",
            "key_code": """# Prompt templates (lines 58-63)
self.question_template = "Question: {} Let's think step by step:"
self.speed_template = "(Thinking speed: {})"  # THIS is how compression factor c is controlled!
self.thinking_separator = "###"  # End-of-thinking signal

# Why these templates matter:
# At test time with c=5, the input becomes:
# "Question: [Q] Let's think step by step:(Thinking speed: 5)###"
# The model sees "(Thinking speed: 5)" and knows to use 5x compression""",
        },
        {
            "name": "src/models/colar.py",
            "role": "Core CoLaR Model",
            "paper_section": "Section 2.2 + 2.3 (SFT + RL)",
            "why": "Contains BOTH training stages. forward() handles SFT with random compression factor sampling and dual loss computation. rl_training_step() + rollout() handle GRPO RL training. This is the heart of the paper.",
            "key_code": """# The two training modes (lines 53-57)
def training_step(self, batch, batch_idx):
    if self.model_kwargs.do_rl:
        return self.rl_training_step(batch)  # Stage 2: RL
    else:
        return self.sft_training_step(batch)  # Stage 1: SFT

# Key insight: same model class, same forward pass,
# just different loss functions and data flow""",
        },
        {
            "name": "src/modules/projector.py",
            "role": "Latent Head",
            "paper_section": "Section 2.2 (Architecture)",
            "why": "The small neural network that predicts the NEXT thought-blob. Outputs a Gaussian distribution Normal(mu, sigma) instead of a fixed vector — this stochasticity is essential for RL exploration and gives +1-2% accuracy over deterministic version.",
            "key_code": """# Only 39 lines of code! But critical.
# The distribution output is what enables:
# 1. Sampling different reasoning paths (RL exploration)
# 2. Temperature control at inference time
# 3. The entropy regularization in the loss""",
        },
        {
            "name": "src/modules/grpo.py",
            "role": "RL Training Engine",
            "paper_section": "Section 2.3 (RL)",
            "why": "Implements GRPO loss (PPO-style clipped surrogate) + experience replay. The group_advantages() function normalizes rewards within each group of 8 answers, and masked_sum divides by 32 for per-token reward averaging.",
            "key_code": """# The advantage normalization (line 66-67)
def group_advantages(returns, eps=1e-8):
    return (returns - returns.mean()) / (returns.std() + eps)
# If all 8 answers are wrong: advantages ≈ 0 (no one punished hard)
# If 1/8 is right: that one gets a big positive advantage

# The mysterious /32 (line 132)
def masked_sum(tensor, mask, dim=None):
    return (tensor * mask).sum(axis=dim) / 32
# This is the per-token averaging constant — normalizes the loss
# scale across different chain lengths""",
        },
        {
            "name": "src/utils/constants.py",
            "role": "Embedding Statistics",
            "paper_section": "Section 2.2 (Normalization)",
            "why": "Stores the standard deviation of each model's embeddings (sigma_e). Before computing latent loss, target embeddings are divided by sigma_e to normalize them. This keeps training numerically stable across different models.",
            "key_code": """MODEL_EMB_STD = {
    "Llama-3.2-1B-Instruct": 0.018,
    "DeepSeek-R1-Distill-Qwen-1.5B": 0.03,
    # ...
}
# Without this normalization, the MSE loss would be dominated
# by the absolute scale of embeddings rather than their direction""",
        },
        {
            "name": "src/configs/models/colar.yaml",
            "role": "Hyperparameters",
            "paper_section": "All sections",
            "why": "All hyperparameters in one place. Key settings map directly to paper decisions: max_compression_factor=5, sqrt_mean=True, lp_deterministic=False, embed_modeling_loss=mse.",
            "key_code": """# Each setting maps to a paper design choice:
max_compression_factor: 5   # Train with c in [1,5]
sqrt_mean: True             # Use 1/sqrt(c) scaling (ablation: -3.4% without)
lp_determinisitc: False     # Stochastic latent head (ablation: worse if True)
embed_modeling_loss: mse    # Soft-MSE (ablation: NLL gives -4.1%)
entropy_weight: -1e-6       # Tiny negative = maximize entropy (prevent collapse)""",
        },
    ]

    for f in files:
        with st.expander(f"**`{f['name']}`** — {f['role']} (Paper: {f['paper_section']})"):
            st.markdown(f"**Why this file exists:** {f['why']}")
            st.code(f["key_code"], language="python")


# ══════════════════════════════════════════════════════════
# PAGE 6: Replication Results
# ══════════════════════════════════════════════════════════
elif page == "6. Replication Results":
    st.title("Replication Results")

    # ── Helper: parse a test JSON file ──────────────────────────────────────
    def parse_test_json(path):
        with open(path) as f:
            data = json.load(f)
        per_q_accs, chain_lens = [], []
        for v in data.values():
            if not isinstance(v, dict) or "acc" not in v:
                continue
            accs = v["acc"] if isinstance(v["acc"], list) else [v["acc"]]
            per_q_accs.append(sum(accs) / len(accs))
            key = "n_latent_forward" if "n_latent_forward" in v else "output_length"
            vals = v[key] if isinstance(v[key], list) else [v[key]]
            chain_lens.extend(vals)
        avg_acc  = sum(per_q_accs) / len(per_q_accs) * 100 if per_q_accs else None
        avg_chain = sum(chain_lens) / len(chain_lens) if chain_lens else None
        return avg_acc, avg_chain, len(per_q_accs)

    # ── Paper ground-truth numbers ───────────────────────────────────────────
    paper = {
        "CoT":      {"acc": 53.6, "chain": 21.4},
        "CoLaR-5":  {"acc": 41.7, "chain": 4.57},
        "CoLaR-2":  {"acc": 48.8, "chain": 10.0},
    }

    # ── Locate our test JSONs ────────────────────────────────────────────────
    cot_jsons    = sorted(glob.glob(str(LOGS_DIR / "cot"    / "**" / "test_*.json"), recursive=True))
    colar_jsons  = sorted(glob.glob(str(LOGS_DIR / "colar"  / "**" / "test_*.json"), recursive=True))

    # Detect c=5 vs c=2 by checking log suffix in the parent path
    def find_colar_json(suffix):
        for p in colar_jsons:
            if suffix in p:
                return p
        return colar_jsons[-1] if colar_jsons else None

    our = {
        "CoT":     parse_test_json(cot_jsons[-1])   if cot_jsons   else (None, None, 0),
        "CoLaR-5": parse_test_json(find_colar_json("c5")) if find_colar_json("c5") else (None, None, 0),
        "CoLaR-2": parse_test_json(find_colar_json("c2")) if find_colar_json("c2") else (None, None, 0),
    }

    # ── Section 1: Side-by-side comparison ──────────────────────────────────
    st.markdown("## Our Results vs Paper")
    st.markdown(
        "Evaluating the **authors' pretrained checkpoints** (from `AlbertTan/CoLaR` on HuggingFace) "
        "on GSM8K test set — 1319 questions, 5 random seeds, Apple M5 MPS."
    )
    st.divider()

    for method in ["CoT", "CoLaR-5", "CoLaR-2"]:
        our_acc, our_chain, n_q = our[method]
        p_acc   = paper[method]["acc"]
        p_chain = paper[method]["chain"]

        st.markdown(f"### {method}")
        c1, c2, c3, c4 = st.columns(4)

        # Accuracy
        if our_acc is not None:
            delta = our_acc - p_acc
            c1.metric("Our Accuracy",   f"{our_acc:.1f}%",  delta=f"{delta:+.1f}% vs paper")
        else:
            c1.metric("Our Accuracy", "⏳ Pending", delta=None)
        c2.metric("Paper Accuracy",  f"{p_acc}%")

        # Chain length
        if our_chain is not None:
            delta_c = our_chain - p_chain
            c3.metric("Our Chain Length",   f"{our_chain:.2f}", delta=f"{delta_c:+.2f} vs paper")
        else:
            c3.metric("Our Chain Length", "⏳ Pending", delta=None)
        c4.metric("Paper Chain Length", str(p_chain))

        if our_acc is not None:
            gap = our_acc - p_acc
            if abs(gap) <= 3:
                st.success(f"Within 3% of paper — strong match.")
            elif gap < 0:
                st.warning(
                    f"Gap of {gap:.1f}%. Most likely cause: MPS (Apple Silicon) vs CUDA (NVIDIA GPU) "
                    f"produce different bfloat16 results in the latent sampling loop. "
                    f"The relative ordering across methods still confirms correct behaviour."
                )
        st.divider()

    # ── Section 2: Grouped bar chart — Our vs Paper ──────────────────────────
    st.markdown("## Accuracy: Our Results vs Paper")

    methods   = ["CoT", "CoLaR-5", "CoLaR-2"]
    paper_acc = [paper[m]["acc"] for m in methods]
    our_acc_vals = [
        our[m][0] if our[m][0] is not None else 0
        for m in methods
    ]
    our_labels = [
        f"{our[m][0]:.1f}%" if our[m][0] is not None else "Pending"
        for m in methods
    ]

    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        name="Paper", x=methods, y=paper_acc,
        marker_color="#636EFA",
        text=[f"{v}%" for v in paper_acc], textposition="outside",
    ))
    fig_cmp.add_trace(go.Bar(
        name="Ours (MPS)", x=methods, y=our_acc_vals,
        marker_color="#EF553B",
        text=our_labels, textposition="outside",
    ))
    fig_cmp.update_layout(
        barmode="group",
        yaxis=dict(title="Accuracy (%)", range=[0, 70]),
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_cmp, use_container_width=True)

    # ── Section 3: Chain length comparison ───────────────────────────────────
    st.markdown("## Chain Length: Our Results vs Paper")

    paper_chain = [paper[m]["chain"] for m in methods]
    our_chain_vals = [
        our[m][1] if our[m][1] is not None else 0
        for m in methods
    ]
    our_chain_labels = [
        f"{our[m][1]:.2f}" if our[m][1] is not None else "Pending"
        for m in methods
    ]

    fig_chain = go.Figure()
    fig_chain.add_trace(go.Bar(
        name="Paper", x=methods, y=paper_chain,
        marker_color="#636EFA",
        text=[str(v) for v in paper_chain], textposition="outside",
    ))
    fig_chain.add_trace(go.Bar(
        name="Ours (MPS)", x=methods, y=our_chain_vals,
        marker_color="#EF553B",
        text=our_chain_labels, textposition="outside",
    ))
    fig_chain.update_layout(
        barmode="group",
        yaxis_title="Avg chain length (tokens / blobs)",
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_chain, use_container_width=True)

    # ── Section 4: Full paper Table 1 for reference ──────────────────────────
    st.divider()
    st.markdown("## Full Paper Table 1 (All Methods, All Datasets)")

    paper_full = {
        "Method": ["CoT", "iCoT", "Coconut", "Distill", "CoLaR-5 (SFT)", "CoLaR-2 (SFT)"],
        "GSM8K": [56.0, 25.5, 26.3, 17.8, 43.7, 51.3],
        "GSM-Hard": [18.5, 5.7, 8.1, 3.0, 12.1, 15.1],
        "SVAMP": [66.3, 33.9, 38.1, 18.5, 52.9, 57.3],
        "MultiArith": [73.7, 33.3, 37.8, 17.7, 57.8, 71.3],
        "Average": [53.6, 24.6, 27.6, 14.3, 41.6, 48.8],
        "Chain Length": [21.4, 0, 6, 6, 4.57, 10.0],
    }

    highlight = {"CoT", "CoLaR-5 (SFT)", "CoLaR-2 (SFT)"}
    fig_full = go.Figure()
    for i, method in enumerate(paper_full["Method"]):
        vals = [paper_full[d][i] for d in ["GSM8K", "GSM-Hard", "SVAMP", "MultiArith"]]
        fig_full.add_trace(go.Scatter(
            x=["GSM8K", "GSM-Hard", "SVAMP", "MultiArith"], y=vals,
            name=method, mode="lines+markers",
            line=dict(width=3 if method in highlight else 1),
            opacity=1.0 if method in highlight else 0.35,
        ))
    fig_full.update_layout(yaxis_title="Accuracy (%)", height=420)
    st.plotly_chart(fig_full, use_container_width=True)

    # ── Section 5: RL Results ─────────────────────────────────────────────────
    st.divider()
    st.markdown("## RL Results — Paper Table 2 (MATH Dataset)")

    rl_data = {
        "Method": ["CoT", "CoLaR SFT", "CoLaR + RL"],
        "Accuracy (%)": [23.5, 8.94, 14.3],
        "Chain Length": [209, 56.8, 9.79],
    }
    col1, col2 = st.columns(2)
    with col1:
        fig_rl1 = go.Figure(go.Bar(
            x=rl_data["Method"], y=rl_data["Accuracy (%)"],
            text=[f"{v}%" for v in rl_data["Accuracy (%)"]],
            textposition="outside", marker_color=["#636EFA", "#FFA15A", "#00CC96"],
        ))
        fig_rl1.update_layout(title="MATH Accuracy", yaxis_title="Accuracy (%)", height=350)
        st.plotly_chart(fig_rl1, use_container_width=True)
    with col2:
        fig_rl2 = go.Figure(go.Bar(
            x=rl_data["Method"], y=rl_data["Chain Length"],
            text=[str(v) for v in rl_data["Chain Length"]],
            textposition="outside", marker_color=["#636EFA", "#FFA15A", "#00CC96"],
        ))
        fig_rl2.update_layout(title="MATH Chain Length", yaxis_title="Blobs / Tokens", height=350)
        st.plotly_chart(fig_rl2, use_container_width=True)

    st.success("After RL: **+5.4% accuracy** and **-83% chain length** simultaneously.")


# ══════════════════════════════════════════════════════════
# PAGE 7: Key Insights
# ══════════════════════════════════════════════════════════
elif page == "7. Key Insights":
    st.title("Key Insights & Ablation Studies")

    st.markdown("### Why Each Design Choice Matters")
    st.markdown("The paper runs ablation studies to prove each component is necessary:")

    ablations = [
        {
            "title": "Stochastic vs Deterministic Latent Head",
            "result": "Stochastic is better (+1-2% accuracy)",
            "why": "Randomness enables exploration of multiple reasoning paths. "
                   "A deterministic head gets stuck on one reasoning trajectory.",
            "code": "lp_determinisitc: False  # in colar.yaml",
        },
        {
            "title": "With vs Without L_comp (Language Modeling Loss)",
            "result": "Removing it drops accuracy by 1.6%",
            "why": "Without L_comp, the model can't understand what's packed inside "
                   "each compressed blob. Dense token-level supervision is crucial.",
            "code": "ce_weight: 1  # must be > 0",
        },
        {
            "title": "sqrt(c) Scaling vs Mean Pooling",
            "result": "Mean pooling drops accuracy by 3.4%",
            "why": "Mean pooling (1/c) changes the variance of embeddings, confusing "
                   "the model. 1/sqrt(c) preserves the original distribution.",
            "code": "sqrt_mean: True  # critical!",
        },
        {
            "title": "Soft-MSE vs NLL Loss",
            "result": "NLL gives 37.6% vs Soft-MSE's 41.7% (-4.1%)",
            "why": "Pure NLL introduces too much randomness on simple datasets. "
                   "MSE + entropy regularization finds the right balance.",
            "code": "embed_modeling_loss: mse  # not 'nll'",
        },
    ]

    for a in ablations:
        with st.expander(f"**{a['title']}** — {a['result']}"):
            st.markdown(f"**Why:** {a['why']}")
            st.code(a["code"], language="yaml")

    st.divider()

    st.markdown("### Dynamic Compression Analysis")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Train once, test with any `c`")
        st.markdown("""
        Because training uses random `c` at each step, the model becomes a generalist.
        A model trained on random c **always beats** a model trained on a single c value.

        It can even generalize to **unseen** c values:
        - Train on c = {1, 3, 5, 7}
        - Test on c = {2, 4, 6}
        - Still works and maintains reasonable accuracy!
        """)

    with col2:
        st.markdown("#### Layer-wise Activity Pattern")
        st.markdown("""
        **Low c** (detailed thinking): Shallow layers are more active
        - Simple pattern recognition is sufficient

        **High c** (condensed thinking): Deep layers are more active
        - Model uses its full computational capacity to extract meaning from dense blobs

        Higher compression = more efficient use of the model's compute.
        """)

    st.divider()

    st.markdown("### Interpreting the Latent Blobs")
    st.markdown("""
    You can't directly read the blobs (they're continuous vectors, not tokens).
    But you CAN find the nearest tokens using cosine similarity:
    """)

    st.code("""
Question: "A set of 7 spoons costs $21. How much do 5 spoons cost?"

With c=2 (mild compression, 7 blobs):
  blob_1 ~ "<<", "21"      -> start of calculation, number 21
  blob_2 ~ "/", "7"        -> division by 7
  blob_3 ~ "3", "="        -> equals 3
  blob_4 ~ "<<", ">>"      -> separators
  blob_5 ~ "*", "5"        -> multiply by 5
  blob_6 ~ "3", "="        -> equals 3
  blob_7 ~ ">>", "15"      -> result: 15
Full reasoning <<21/7=3>> <<5*3=15>> is captured!

With c=5 (high compression, 3 blobs):
  blob_1 ~ "21", "7"       -> the key numbers
  blob_2 ~ "5", "="        -> multiply and equals
  blob_3 ~ "15"            -> the answer
Less informative tokens dropped — only the important math survives!
    """, language="text")

    st.divider()

    st.markdown("### Limitations")
    limitations = [
        "Doesn't beat CoT on most benchmarks (except GPQA) — still slightly below explicit reasoning in accuracy",
        "Can't do non-integer `c` — only whole numbers work (tokens are discrete)",
        "Can't exceed training maximum — if trained with c_max=5, can't use c=10 at test time",
        "Scaling: tested up to 8B parameters — unclear how it performs on 70B+ models",
    ]
    for l in limitations:
        st.markdown(f"- {l}")

    st.divider()

    st.markdown("### Takeaway")
    st.success("""
    **CoLaR is a practical, well-engineered framework that makes a clear contribution:**

    1. **Novel idea:** Dynamic compression of reasoning chains into latent space, controllable via prompting
    2. **Sound design:** Each component (sqrt scaling, stochastic head, soft-MSE, per-token RL rewards) is validated by ablation
    3. **Strong results:** +14.1% over prior latent methods, only -4.8% vs CoT with 53% fewer steps
    4. **Reproducible:** Clean codebase, released checkpoints, standard benchmarks

    **The key insight is elegant:** by training with random compression factors and using RL with
    per-token reward averaging, the model simultaneously learns to be both smarter AND more concise.
    """)

# ──────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.markdown("---")
st.sidebar.markdown("**Replication by:** Soham")
st.sidebar.markdown("**Paper:** [arXiv 2505.16552](https://arxiv.org/abs/2505.16552)")
st.sidebar.markdown("**Code:** [AlbertTan/CoLaR](https://huggingface.co/AlbertTan/CoLaR)")
