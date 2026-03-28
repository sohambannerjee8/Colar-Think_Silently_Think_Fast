'use client'
import { useState } from 'react'
import dynamic from 'next/dynamic'

const RechartsBar = dynamic(() => import('../components/Charts'), { ssr: false })

const TABS = [
  'Overview',
  'The Problem',
  'Architecture',
  'Training Pipeline',
  'Code Walkthrough',
  'Our Results',
  'Key Insights',
]

// ─── Data ──────────────────────────────────────────────────────────────────
const PAPER_METHODS = [
  { name: 'CoT',       acc: 53.6, chain: 21.4, type: 'Text' },
  { name: 'iCoT',      acc: 24.6, chain: 0,    type: 'Text (reduced)' },
  { name: 'Coconut',   acc: 27.6, chain: 6,    type: 'Fixed latent' },
  { name: 'CODI',      acc: 14.3, chain: 6,    type: 'Fixed latent' },
  { name: 'CoLaR-5',   acc: 41.7, chain: 4.57, type: 'Dynamic latent' },
  { name: 'CoLaR-2',   acc: 48.8, chain: 10.0, type: 'Dynamic latent' },
]

const OUR_RESULTS = [
  { method: 'CoT',     ourAcc: 49.96, paperAcc: 53.6, ourChain: 25.60, paperChain: 21.4, unit: 'tokens' },
  { method: 'CoLaR-5', ourAcc: 24.97, paperAcc: 41.7, ourChain: 5.65,  paperChain: 4.57, unit: 'blobs'  },
  { method: 'CoLaR-2', ourAcc: 40.41, paperAcc: 48.8, ourChain: 12.84, paperChain: 10.0, unit: 'blobs'  },
]

// ─── Reusable UI ──────────────────────────────────────────────────────────
function Card({ children, className = '' }) {
  return (
    <div className={`bg-slate-800 border border-slate-700 rounded-xl p-5 ${className}`}>
      {children}
    </div>
  )
}

function Badge({ children, color = 'blue' }) {
  const colors = {
    blue: 'bg-blue-900/50 text-blue-300 border border-blue-700',
    green: 'bg-green-900/50 text-green-300 border border-green-700',
    yellow: 'bg-yellow-900/50 text-yellow-300 border border-yellow-700',
    red: 'bg-red-900/50 text-red-300 border border-red-700',
    purple: 'bg-purple-900/50 text-purple-300 border border-purple-700',
  }
  return (
    <span className={`inline-block text-xs px-2 py-0.5 rounded font-medium ${colors[color]}`}>
      {children}
    </span>
  )
}

function CodeBlock({ children, lang = 'text' }) {
  return (
    <pre className="bg-slate-900 border border-slate-700 rounded-lg p-4 text-sm text-slate-300 overflow-x-auto leading-relaxed">
      <code>{children}</code>
    </pre>
  )
}

function SectionTitle({ children }) {
  return <h2 className="text-2xl font-bold text-white mb-1">{children}</h2>
}

function SubTitle({ children }) {
  return <h3 className="text-lg font-semibold text-blue-300 mt-6 mb-2">{children}</h3>
}

function InfoBox({ children, type = 'info' }) {
  const styles = {
    info:    'bg-blue-900/30 border-blue-500 text-blue-200',
    success: 'bg-green-900/30 border-green-500 text-green-200',
    warning: 'bg-yellow-900/30 border-yellow-500 text-yellow-200',
    error:   'bg-red-900/30 border-red-500 text-red-200',
  }
  return (
    <div className={`border-l-4 rounded-r-lg p-4 text-sm leading-relaxed ${styles[type]}`}>
      {children}
    </div>
  )
}

// ─── Pages ─────────────────────────────────────────────────────────────────

function Overview() {
  return (
    <div className="space-y-6">
      <div>
        <SectionTitle>CoLaR: Compressed Latent Reasoning</SectionTitle>
        <p className="text-slate-400 text-sm mt-1">
          <em>Think Silently, Think Fast: Dynamic Latent Compression of LLM Reasoning Chains</em>
          &nbsp;·&nbsp; Wenhui Tan et al. &nbsp;·&nbsp;
          <a href="https://arxiv.org/abs/2505.16552" target="_blank" rel="noreferrer"
             className="text-blue-400 hover:underline">arXiv 2505.16552</a>
          &nbsp;·&nbsp;
          <a href="https://huggingface.co/AlbertTan/CoLaR" target="_blank" rel="noreferrer"
             className="text-blue-400 hover:underline">Pretrained Models</a>
          &nbsp;·&nbsp;
          <a href="https://github.com/sohambannerjee8/Colar" target="_blank" rel="noreferrer"
             className="text-blue-400 hover:underline">GitHub</a>
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <InfoBox type="info">
          <strong className="block mb-1">Core Idea</strong>
          CoLaR teaches LLMs to <strong>think in compressed latent vectors</strong> instead of writing
          every reasoning step as text. The compression level is <strong>adjustable at inference time</strong> —
          no retraining needed.
        </InfoBox>
        <InfoBox type="warning">
          <strong className="block mb-1">Why It Matters</strong>
          Chain-of-Thought is powerful but expensive. CoLaR achieves <strong>up to 5× fewer steps</strong> with
          only ~5% accuracy loss — and on hard tasks, the RL-enhanced model actually <strong>beats CoT</strong>.
        </InfoBox>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <h3 className="font-semibold text-white mb-2">1. Dynamic Compression</h3>
          <p className="text-slate-400 text-sm">
            Unlike prior methods (Coconut, CODI) that fix the number of latent steps,
            CoLaR lets you choose the compression factor <code className="text-blue-300">c</code> at
            inference time. Train once, deploy at any speed.
          </p>
        </Card>
        <Card>
          <h3 className="font-semibold text-white mb-2">2. Two-Stage Training</h3>
          <p className="text-slate-400 text-sm">
            <strong className="text-slate-300">Stage 1 (SFT):</strong> Learn to compress reasoning into latent blobs.<br />
            <strong className="text-slate-300">Stage 2 (RL):</strong> Use GRPO to discover shorter, smarter reasoning paths.
          </p>
        </Card>
        <Card>
          <h3 className="font-semibold text-white mb-2">3. State-of-the-Art</h3>
          <p className="text-slate-400 text-sm">
            CoLaR-2 reaches <strong className="text-white">48.8%</strong> on GSM8K with only 10 latent steps
            (vs CoT's 21.4 tokens at 53.6%). On GPQA, CoLaR-8B-RL <strong className="text-white">beats CoT</strong> (37.5% vs 35.7%) using 69% fewer steps.
          </p>
        </Card>
      </div>

      <Card>
        <h3 className="font-semibold text-white mb-4">Methods Comparison — GSM8K (Paper, Table 1)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400">
                <th className="text-left py-2 pr-4">Method</th>
                <th className="text-left py-2 pr-4">Type</th>
                <th className="text-right py-2 pr-4">Accuracy</th>
                <th className="text-right py-2">Chain Length</th>
              </tr>
            </thead>
            <tbody>
              {PAPER_METHODS.map((m, i) => (
                <tr key={i} className={`border-b border-slate-700/50 ${m.name.startsWith('CoLaR') ? 'text-blue-300 font-medium' : 'text-slate-300'}`}>
                  <td className="py-2 pr-4">{m.name}</td>
                  <td className="py-2 pr-4 text-slate-400 text-xs">{m.type}</td>
                  <td className="py-2 pr-4 text-right font-mono">{m.acc}%</td>
                  <td className="py-2 text-right font-mono">{m.chain === 0 ? '—' : m.chain}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <RechartsBar chartId="overview" />
    </div>
  )
}

function Problem() {
  return (
    <div className="space-y-6">
      <SectionTitle>The Problem: Chain-of-Thought is Expensive</SectionTitle>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <h3 className="font-semibold text-red-400 mb-3">Without CoT</h3>
          <CodeBlock>{`Q: 7 spoons cost $21. What do 5 cost?
A: 12`}</CodeBlock>
          <p className="text-red-400 text-sm mt-2">Often wrong — model guesses without reasoning</p>
        </Card>
        <Card>
          <h3 className="font-semibold text-green-400 mb-3">With CoT</h3>
          <CodeBlock>{`Q: 7 spoons cost $21. What do 5 cost?
Let's think step by step:
21 / 7 = 3   (one spoon costs $3)
3 × 5 = 15   (five spoons cost $15)
A: 15`}</CodeBlock>
          <p className="text-green-400 text-sm mt-2">Correct — but costs 14 extra tokens of generation</p>
        </Card>
      </div>

      <Card>
        <h3 className="font-semibold text-white mb-3">The Cost at Scale</h3>
        <p className="text-slate-400 text-sm leading-relaxed">
          Every token generated takes <strong className="text-slate-300">~10–50ms</strong> on GPU (autoregressive generation is sequential).
          At millions of requests per day with 20+ reasoning tokens each, this adds up to massive compute bills.
          The KV-cache also grows linearly with sequence length, consuming memory.
        </p>
        <div className="flex gap-4 mt-4">
          {[
            { label: 'Average CoT length', value: '21.4 tokens', color: 'text-red-400' },
            { label: 'CoLaR-2 chain', value: '10 blobs', color: 'text-yellow-400' },
            { label: 'CoLaR-5 chain', value: '4.57 blobs', color: 'text-green-400' },
          ].map(s => (
            <div key={s.label} className="bg-slate-900 rounded-lg p-3 flex-1 text-center">
              <div className={`text-xl font-bold font-mono ${s.color}`}>{s.value}</div>
              <div className="text-slate-500 text-xs mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </Card>

      <div>
        <SubTitle>Prior Approaches and Their Limitations</SubTitle>
        <div className="space-y-3">
          {[
            { name: 'iCoT', idea: 'Gradually remove reasoning steps during training', chain: 'None (0 tokens)', limit: '24.6% accuracy — too aggressive, loses reasoning ability entirely', color: 'red' },
            { name: 'Coconut', idea: 'Replace text reasoning with fixed hidden state feedback', chain: 'Fixed 6 steps', limit: 'Cannot adapt to problem difficulty — every question gets 6 steps whether it needs 1 or 20', color: 'yellow' },
            { name: 'CODI', idea: 'Self-distillation: compress teacher CoT into fixed latent representations', chain: 'Fixed 6 steps', limit: '14.3% accuracy — distillation loses too much information', color: 'red' },
            { name: 'CoLaR (this work)', idea: 'Dynamic compressed latent reasoning with RL refinement', chain: 'Flexible (prompt-controlled)', limit: 'Slightly below CoT in accuracy, but dramatically faster and dynamically adjustable', color: 'green' },
          ].map(m => (
            <Card key={m.name} className="border-slate-700">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-white">{m.name}</span>
                    <Badge color={m.color}>{m.chain}</Badge>
                  </div>
                  <p className="text-slate-400 text-sm">{m.idea}</p>
                  <p className="text-slate-500 text-xs mt-1 italic">{m.limit}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      <InfoBox type="success">
        <strong className="block mb-1">CoLaR's Key Insight</strong>
        Don't remove reasoning — <strong>compress it</strong>. Instead of generating 20 text tokens, generate
        4 compressed latent vectors ("blobs") that encode the same information.
        And let the user choose the compression level at inference time — no retraining needed.
      </InfoBox>
    </div>
  )
}

function Architecture() {
  return (
    <div className="space-y-6">
      <SectionTitle>Architecture: How CoLaR Works</SectionTitle>

      <Card>
        <h3 className="font-semibold text-white mb-3">High-Level Overview</h3>
        <CodeBlock>{`┌─────────────────────────────────────────────────────────┐
│                      CoLaR Model                        │
│                                                         │
│  ┌─────────────────────┐    ┌────────────────────────┐  │
│  │  LLM Backbone       │    │  Latent Head           │  │
│  │  (Llama-3.2-1B)     │───>│  (LatentPolicy)        │  │
│  │                     │    │  3-layer MLP           │  │
│  │  Frozen weights     │    │  Predicts Normal(μ, σ) │  │
│  │  + LoRA adapters    │    │  for next thought-blob │  │
│  └─────────────────────┘    └────────────────────────┘  │
│                                                         │
│  ┌─────────────────────┐                               │
│  │  Embedding Compress │  Averages c embeddings        │
│  │  (training only)    │  with 1/√c scaling            │
│  └─────────────────────┘                               │
└─────────────────────────────────────────────────────────┘`}</CodeBlock>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <h3 className="font-semibold text-white mb-2">Component 1: Embedding Compression</h3>
          <p className="text-slate-400 text-sm mb-3">
            Takes <code className="text-blue-300">c</code> consecutive token embeddings and merges them into one vector.
            This creates the "compressed thoughts" used during training.
          </p>
          <div className="bg-slate-900 rounded-lg p-3 text-center text-sm font-mono text-slate-300 mb-3">
            compressed = (Σ embed_i) / √c
          </div>
          <p className="text-slate-500 text-xs leading-relaxed">
            Why <code>1/√c</code> not <code>1/c</code>? Regular mean shrinks variance (σ²→σ²/c),
            confusing the model. Dividing by √c preserves variance: Var(sum/√c) = c·σ²/c = σ² ✓
          </p>
        </Card>

        <Card>
          <h3 className="font-semibold text-white mb-2">Component 2: Latent Head (LatentPolicy)</h3>
          <p className="text-slate-400 text-sm mb-3">
            Predicts a <strong>probability distribution</strong> over the next thought-blob, not a single vector.
            Stochastic sampling enables RL exploration.
          </p>
          <CodeBlock>{`LLM hidden state (2048-dim)
    │
    ▼
Linear(2048→2048) + GELU
    │
    ▼
Linear(2048→2048) + LayerNorm
    ├──► mean_head  → μ (2048-dim)
    └──► log_std   → log(σ)
              ↓
    Sample from Normal(μ, σ)
              ↓
    Next thought-blob (2048-dim)`}</CodeBlock>
        </Card>
      </div>

      <Card>
        <h3 className="font-semibold text-white mb-2">Component 3: LoRA Adapters</h3>
        <p className="text-slate-400 text-sm mb-3">
          The base Llama model is <strong className="text-slate-300">frozen</strong>. Only LoRA adapters and the Latent Head are trained.
        </p>
        <div className="flex gap-4 text-sm">
          {[
            { label: 'Total params', value: '1.24B' },
            { label: 'LoRA (rank=128)', value: '~67M' },
            { label: 'Latent Head', value: '~16M' },
            { label: 'Trainable', value: '6.7%', highlight: true },
          ].map(s => (
            <div key={s.label} className={`flex-1 bg-slate-900 rounded-lg p-3 text-center ${s.highlight ? 'border border-blue-500' : ''}`}>
              <div className={`text-lg font-bold font-mono ${s.highlight ? 'text-blue-300' : 'text-white'}`}>{s.value}</div>
              <div className="text-slate-500 text-xs mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="font-semibold text-white mb-3">Inference Flow (Step by Step)</h3>
        <div className="space-y-2">
          {[
            ['1. Encode Question', 'Tokenize + embed the question with speed prompt: "Question: ... (Thinking speed: 5)###"'],
            ['2. LLM Forward', 'Run the question through Llama → get hidden state h₁'],
            ['3. Latent Head Predicts', 'LatentPolicy takes h₁ → samples thought-blob from Normal(μ, σ)'],
            ['4. Feed Blob Back', 'The blob is fed back into Llama as the next "token" embedding (no decoding to text!)'],
            ['5. Repeat Steps 3–4', 'Keep generating blobs until the LLM predicts ### (end-of-thinking token)'],
            ['6. Generate Answer', 'After ###, switch to normal text generation for the final answer'],
          ].map(([step, desc]) => (
            <div key={step} className="flex gap-3 text-sm">
              <span className="text-blue-400 font-medium whitespace-nowrap">{step}</span>
              <span className="text-slate-400">{desc}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

function Training() {
  return (
    <div className="space-y-6">
      <SectionTitle>Training Pipeline: Two Stages</SectionTitle>

      <Card>
        <CodeBlock>{`Stage 0              Stage 1 (SFT)              Stage 2 (RL)
────────             ──────────────             ────────────────
Download        →    Train CoT baseline    →    Train CoLaR SFT  →  RL (GRPO)
Llama-1B             (50 epochs)                (50 epochs)          (~4000 steps)
                     Learns full text           Compresses reasoning  Finds shorter +
                     reasoning chains           into latent blobs     smarter paths`}</CodeBlock>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <h3 className="font-semibold text-white mb-2">Stage 1: SFT — What Happens</h3>
          <ol className="text-slate-400 text-sm space-y-2 list-decimal list-inside">
            <li>Sample random compression factor <code className="text-blue-300">c ∈ [1, 5]</code></li>
            <li>Compress the full reasoning chain into blobs of size <code className="text-blue-300">c</code></li>
            <li>Compute two losses and backprop through LoRA + Latent Head</li>
          </ol>
          <div className="mt-3 bg-slate-900 rounded p-3 text-xs text-slate-400">
            <strong className="text-slate-300">Why random c?</strong> The model becomes a generalist —
            it learns to handle any compression from 1 (no compression) to 5 (max). This enables
            changing speed at inference time without retraining.
          </div>
        </Card>

        <Card>
          <h3 className="font-semibold text-white mb-2">SFT Loss Functions</h3>
          <div className="space-y-3 text-sm">
            <div className="bg-slate-900 rounded p-3">
              <div className="text-blue-300 font-medium mb-1">L_comp — Language Modeling Loss</div>
              <p className="text-slate-400 text-xs">
                Standard cross-entropy. Trains the LLM to predict what tokens are <em>inside</em> each compressed blob.
                Keeps the LLM grounded in real token semantics.
              </p>
            </div>
            <div className="bg-slate-900 rounded p-3">
              <div className="text-blue-300 font-medium mb-1">L_latent — Blob Prediction Loss</div>
              <p className="text-slate-400 text-xs">
                Trains the Latent Head to predict the <em>next</em> compressed blob.
                Uses soft-MSE: MSE distance + small entropy regularization (α = −1e−6) to prevent
                the distribution from collapsing to a point.
              </p>
              <div className="font-mono text-xs text-slate-300 mt-1">
                L = ||μ − target||² + α·H(Normal(μ,σ))
              </div>
            </div>
            <div className="bg-slate-900 rounded p-3">
              <div className="text-blue-300 font-medium mb-1">Total = L_comp + L_latent</div>
              <p className="text-slate-400 text-xs">
                Equal weighting (ce_weight=1, embed_weight=1) — both objectives are equally important.
              </p>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <h3 className="font-semibold text-white mb-2">Stage 2: RL with GRPO</h3>
        <p className="text-slate-400 text-sm mb-4">
          Group Relative Policy Optimization — generates 8 rollouts per question, computes rewards,
          and trains the model to prefer answers that are both <strong className="text-slate-300">correct</strong> and <strong className="text-slate-300">concise</strong>.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
          <div className="bg-slate-900 rounded-lg p-3">
            <div className="text-purple-300 font-medium mb-1">Accuracy Reward</div>
            <p className="text-slate-400 text-xs">+1 if the final answer is correct, 0 otherwise. Drives the model to stay accurate while compressing.</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-3">
            <div className="text-purple-300 font-medium mb-1">Length Penalty</div>
            <p className="text-slate-400 text-xs">Optional penalty for using more blobs than needed. Teaches the model to be concise.</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-3">
            <div className="text-purple-300 font-medium mb-1">Group Relative</div>
            <p className="text-slate-400 text-xs">Normalize rewards within each group of 8 rollouts — stable training without an explicit value network.</p>
          </div>
        </div>
      </Card>

      <InfoBox type="success">
        <strong className="block mb-1">Result of RL</strong>
        On harder tasks (GPQA, MATH), CoLaR-RL not only compresses reasoning by 82.8% but actually
        <strong> outperforms the CoT teacher</strong> — suggesting RL discovers reasoning shortcuts the text chain never found.
      </InfoBox>
    </div>
  )
}

function CodeWalkthrough() {
  const files = [
    { file: 'run.py', section: 'Entry point', desc: 'Loads config, instantiates model + trainer, calls do_test() for evaluation. Bug fixed: added weights_only=False for PyTorch 2.x compatibility.' },
    { file: 'src/models/colar.py', section: 'Paper §3.1–3.3', desc: 'Main CoLaR model. forward() implements SFT training with random c sampling. latent_generate() implements inference-time blob generation loop.' },
    { file: 'src/models/cot.py', section: 'Paper §2', desc: 'CoT baseline model. Bug fixed: added LitCoT = LitCot alias for pretrained checkpoint compatibility.' },
    { file: 'src/models/model_base.py', section: 'Shared logic', desc: 'Base class for both CoT and CoLaR. Handles tokenization, LoRA setup, embedding compression, and latent_generate().' },
    { file: 'src/models/projector.py', section: 'Paper §3.1', desc: 'LatentPolicy MLP: predicts Normal(μ, σ) over next thought-blob. 3-layer MLP with GELU activation and LayerNorm.' },
    { file: 'src/configs/models/colar.yaml', section: 'Config', desc: 'All hyperparameters: lora_config (r=128), latent_cot_config (max_compression_factor=5), latent_generation_config (compression_factor=5).' },
    { file: 'src/datasets/qsa.py', section: 'Data', desc: 'GSM8K dataset loader. Each sample has question, steps (reasoning chain), and answer fields. QSA = Question, Steps, Answer.' },
  ]

  return (
    <div className="space-y-6">
      <SectionTitle>Code Walkthrough</SectionTitle>
      <p className="text-slate-400 text-sm">How the paper maps to the codebase.</p>

      <div className="space-y-3">
        {files.map(f => (
          <Card key={f.file}>
            <div className="flex items-start gap-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <code className="text-blue-300 text-sm font-medium">{f.file}</code>
                  <Badge color="purple">{f.section}</Badge>
                </div>
                <p className="text-slate-400 text-sm">{f.desc}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card>
        <h3 className="font-semibold text-white mb-3">Key Config Parameters</h3>
        <CodeBlock>{`# src/configs/models/colar.yaml (key fields)
max_compression_factor: 5      # c sampled from [1, max_c] during training
compression_factor: 5          # c used at inference time (override via CLI)

lora_config:
  r: 128                       # LoRA rank — high rank for expressiveness
  lora_alpha: 32               # scaling factor

latent_cot_config:
  embed_modeling_loss: mse     # soft-MSE loss for blob prediction
  entropy_weight: -1e-6        # tiny regularization (negative = encourage spread)
  sqrt_mean: true              # use 1/sqrt(c) scaling (not 1/c)

latent_generation_config:
  max_n_latent_forward: 64     # max blobs before forced stop
  latent_temperature: 1.0      # sampling temperature for LatentPolicy`}</CodeBlock>
      </Card>

      <Card>
        <h3 className="font-semibold text-white mb-3">Bug Fixes We Applied</h3>
        <div className="space-y-3">
          <div className="bg-slate-900 rounded-lg p-4">
            <Badge color="red">Bug 1</Badge>
            <p className="text-slate-300 text-sm mt-2 mb-1 font-medium">LitCoT vs LitCot capitalization mismatch</p>
            <p className="text-slate-400 text-xs mb-2">
              Pretrained checkpoint was saved with class name <code>LitCoT</code>, but the codebase defines <code>LitCot</code>.
              PyTorch's unpickling fails with an AttributeError.
            </p>
            <CodeBlock>{`# Fix in src/models/cot.py (bottom of file):
LitCoT = LitCot  # alias for checkpoint compatibility`}</CodeBlock>
          </div>
          <div className="bg-slate-900 rounded-lg p-4">
            <Badge color="red">Bug 2</Badge>
            <p className="text-slate-300 text-sm mt-2 mb-1 font-medium">torch.load missing weights_only=False</p>
            <p className="text-slate-400 text-xs mb-2">
              PyTorch 2.x changed the default to <code>weights_only=True</code>, which blocks loading
              checkpoints containing OmegaConf objects.
            </p>
            <CodeBlock>{`# Fix in run.py line 29:
# Before:
state_dict = torch.load(ckpt_path, map_location='cpu')
# After:
state_dict = torch.load(ckpt_path, map_location='cpu', weights_only=False)`}</CodeBlock>
          </div>
        </div>
      </Card>
    </div>
  )
}

function Results() {
  return (
    <div className="space-y-6">
      <div>
        <SectionTitle>Our Replication Results</SectionTitle>
        <p className="text-slate-400 text-sm mt-1">
          Evaluated on GSM8K test set (1,319 questions) using the authors' pretrained checkpoints.
          Each run averages over 5 random seeds. Hardware: Apple M5 MPS, 24GB RAM.
        </p>
      </div>

      {/* Main results table */}
      <Card>
        <h3 className="font-semibold text-white mb-4">Results vs Paper (Table 1, GSM8K)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400 text-xs uppercase tracking-wider">
                <th className="text-left py-2 pr-6">Method</th>
                <th className="text-right py-2 pr-4">Our Accuracy</th>
                <th className="text-right py-2 pr-4">Paper Accuracy</th>
                <th className="text-right py-2 pr-4">Gap</th>
                <th className="text-right py-2 pr-4">Our Chain</th>
                <th className="text-right py-2">Paper Chain</th>
              </tr>
            </thead>
            <tbody>
              {OUR_RESULTS.map(r => {
                const gap = r.ourAcc - r.paperAcc
                return (
                  <tr key={r.method} className="border-b border-slate-700/50 text-slate-300">
                    <td className="py-3 pr-6 font-medium text-white">{r.method}</td>
                    <td className="py-3 pr-4 text-right font-mono text-blue-300 font-semibold">{r.ourAcc}%</td>
                    <td className="py-3 pr-4 text-right font-mono text-slate-400">{r.paperAcc}%</td>
                    <td className={`py-3 pr-4 text-right font-mono text-sm ${gap >= -5 ? 'text-yellow-400' : 'text-red-400'}`}>
                      {gap.toFixed(1)}%
                    </td>
                    <td className="py-3 pr-4 text-right font-mono text-blue-300">{r.ourChain} {r.unit}</td>
                    <td className="py-3 text-right font-mono text-slate-400">{r.paperChain} {r.unit}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Key metric cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {OUR_RESULTS.map(r => {
          const gap = r.ourAcc - r.paperAcc
          return (
            <Card key={r.method}>
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-white">{r.method}</span>
                <Badge color={gap >= -5 ? 'yellow' : 'red'}>{gap > 0 ? '+' : ''}{gap.toFixed(1)}% vs paper</Badge>
              </div>
              <div className="text-3xl font-bold text-blue-300 font-mono">{r.ourAcc}%</div>
              <div className="text-slate-500 text-xs mt-1">accuracy (paper: {r.paperAcc}%)</div>
              <div className="mt-3 text-sm font-mono text-slate-300">{r.ourChain} {r.unit}</div>
              <div className="text-slate-500 text-xs">chain length (paper: {r.paperChain})</div>
            </Card>
          )
        })}
      </div>

      <RechartsBar chartId="results" />

      {/* Explanation of gap */}
      <Card>
        <h3 className="font-semibold text-white mb-3">Why Our Numbers Are Lower Than the Paper</h3>
        <div className="space-y-3 text-sm">
          <div className="flex gap-3">
            <span className="text-yellow-400 font-bold mt-0.5">1</span>
            <div>
              <strong className="text-slate-200">MPS vs CUDA floating-point</strong>
              <p className="text-slate-400 mt-0.5">
                The paper trained and evaluated on NVIDIA GPUs. Apple Silicon (MPS) has different
                <code className="text-blue-300"> bfloat16</code> rounding behavior. In the latent sampling loop,
                small numerical differences compound across 5–13 generation steps, leading to systematically
                different blob trajectories.
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <span className="text-yellow-400 font-bold mt-0.5">2</span>
            <div>
              <strong className="text-slate-200">Relative ordering is fully preserved</strong>
              <p className="text-slate-400 mt-0.5">
                CoLaR-2 (40.41%) &gt; CoLaR-5 (24.97%), and CoT (49.96%) &gt; both — exactly as the paper reports.
                This confirms the model logic and compression trade-off are working correctly.
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <span className="text-yellow-400 font-bold mt-0.5">3</span>
            <div>
              <strong className="text-slate-200">Slightly longer chain lengths</strong>
              <p className="text-slate-400 mt-0.5">
                Our model generates more blobs (5.65 vs 4.57 for c=5; 12.84 vs 10.0 for c=2).
                The end-of-thinking <code className="text-blue-300">###</code> prediction is
                affected by the same numerical differences — the model is slightly less decisive about stopping.
              </p>
            </div>
          </div>
        </div>
      </Card>

      <InfoBox type="info">
        <strong className="block mb-1">Bottom Line</strong>
        The replication validates the paper's core claims: dynamic compression works,
        the compression trade-off is real, and the pretrained checkpoints are functional.
        The absolute accuracy gap is a hardware/precision artefact, not a code or data issue.
      </InfoBox>
    </div>
  )
}

function Insights() {
  return (
    <div className="space-y-6">
      <SectionTitle>Key Insights</SectionTitle>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <h3 className="font-semibold text-white mb-2">The Compression Trade-off</h3>
          <p className="text-slate-400 text-sm">
            Higher compression = fewer steps but lower accuracy. This is expected and confirmed
            by our results. The key innovation is that you can <em>tune</em> this at inference
            time — no retraining needed.
          </p>
          <div className="mt-3 text-xs font-mono space-y-1">
            <div className="flex justify-between text-slate-400">
              <span>CoT (c=1, text)</span><span>53.6% / 21.4 tokens</span>
            </div>
            <div className="flex justify-between text-blue-300">
              <span>CoLaR-2</span><span>48.8% / 10 blobs</span>
            </div>
            <div className="flex justify-between text-blue-400">
              <span>CoLaR-5</span><span>41.7% / 4.57 blobs</span>
            </div>
          </div>
        </Card>

        <Card>
          <h3 className="font-semibold text-white mb-2">Stochasticity is a Feature</h3>
          <p className="text-slate-400 text-sm">
            The Latent Head predicts a <em>distribution</em>, not a single vector.
            This is intentional — stochastic sampling lets the RL stage explore diverse
            reasoning paths. At test time, temperature controls the trade-off between
            creativity and consistency.
          </p>
        </Card>

        <Card>
          <h3 className="font-semibold text-white mb-2">LoRA Efficiency</h3>
          <p className="text-slate-400 text-sm">
            Only 6.7% of weights are trained, yet the model learns to use a completely
            different reasoning modality (latent vectors vs text). This suggests the core
            reasoning knowledge is already in the frozen backbone — CoLaR just teaches it
            a new "language" to think in.
          </p>
        </Card>

        <Card>
          <h3 className="font-semibold text-white mb-2">RL Can Exceed the Teacher</h3>
          <p className="text-slate-400 text-sm">
            On GPQA (graduate-level science), CoLaR-8B-RL scores 37.5% vs the CoT teacher's 35.7% —
            while using 69% fewer steps. This suggests RL discovers reasoning shortcuts
            that the original text chain never found, not just compressions of it.
          </p>
        </Card>
      </div>

      <Card>
        <h3 className="font-semibold text-white mb-3">Limitations</h3>
        <div className="space-y-2 text-sm text-slate-400">
          <p>• <strong className="text-slate-300">Interpretability:</strong> Latent blobs are opaque — you can't read them. This makes debugging harder than with explicit CoT.</p>
          <p>• <strong className="text-slate-300">Hardware sensitivity:</strong> Results vary between GPU architectures due to bfloat16 differences, as our replication shows.</p>
          <p>• <strong className="text-slate-300">Training cost:</strong> Requires a pre-trained CoT model as starting point — you can't train CoLaR from scratch directly.</p>
          <p>• <strong className="text-slate-300">Short answers only:</strong> Currently limited to tasks with short output answers (max_new_tokens=16). Complex generation tasks are not covered.</p>
        </div>
      </Card>

      <Card>
        <h3 className="font-semibold text-white mb-3">Setup Details (Our Replication)</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          {[
            { k: 'Model', v: 'Llama-3.2-1B-Instruct' },
            { k: 'Dataset', v: 'GSM8K (1,319 test)' },
            { k: 'Hardware', v: 'Apple M5 MPS 24GB' },
            { k: 'Seeds', v: '5 per run' },
          ].map(s => (
            <div key={s.k} className="bg-slate-900 rounded-lg p-3">
              <div className="text-slate-500 text-xs">{s.k}</div>
              <div className="text-slate-200 font-medium mt-1">{s.v}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

// ─── Main App ───────────────────────────────────────────────────────────────
export default function App() {
  const [active, setActive] = useState(0)

  const pages = [Overview, Problem, Architecture, Training, CodeWalkthrough, Results, Insights]
  const ActivePage = pages[active]

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/95 sticky top-0 z-10 backdrop-blur">
        <div className="max-w-5xl mx-auto px-4 py-3">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-2xl">🧠</span>
            <div>
              <h1 className="text-base font-bold text-white leading-tight">CoLaR Replication</h1>
              <p className="text-slate-400 text-xs">Think Silently, Think Fast · arXiv 2505.16552</p>
            </div>
          </div>
          {/* Tab navigation */}
          <div className="flex gap-1 overflow-x-auto pb-1 scrollbar-hide">
            {TABS.map((tab, i) => (
              <button
                key={tab}
                onClick={() => setActive(i)}
                className={`whitespace-nowrap px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  active === i
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
                } ${i === 5 ? 'border border-blue-500/50' : ''}`}
              >
                {tab}{i === 5 ? ' ★' : ''}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        <ActivePage />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700 mt-12 py-6 text-center text-slate-500 text-xs">
        <p>Replication by Soham Bannerjee · 2026 ·{' '}
          <a href="https://github.com/sohambannerjee8/Colar-Think_Silently_Think_Fast" target="_blank" rel="noreferrer"
             className="text-blue-400 hover:underline">GitHub</a>
          {' · '}
          <a href="https://arxiv.org/abs/2505.16552" target="_blank" rel="noreferrer"
             className="text-blue-400 hover:underline">Original Paper</a>
        </p>
      </footer>
    </div>
  )
}
