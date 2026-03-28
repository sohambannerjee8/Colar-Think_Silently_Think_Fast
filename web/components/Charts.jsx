'use client'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts'

const PAPER_DATA = [
  { name: 'CoT',     acc: 53.6, chain: 21.4 },
  { name: 'iCoT',    acc: 24.6, chain: 0    },
  { name: 'Coconut', acc: 27.6, chain: 6    },
  { name: 'CODI',    acc: 14.3, chain: 6    },
  { name: 'CoLaR-5', acc: 41.7, chain: 4.57 },
  { name: 'CoLaR-2', acc: 48.8, chain: 10.0 },
]

const COMPARE_DATA = [
  { name: 'CoT',     paper: 53.6, ours: 49.96 },
  { name: 'CoLaR-5', paper: 41.7, ours: 24.97 },
  { name: 'CoLaR-2', paper: 48.8, ours: 40.41 },
]

const CHAIN_DATA = [
  { name: 'CoT',     paper: 21.4,  ours: 25.60, unit: 'tokens' },
  { name: 'CoLaR-5', paper: 4.57,  ours: 5.65,  unit: 'blobs'  },
  { name: 'CoLaR-2', paper: 10.0,  ours: 12.84, unit: 'blobs'  },
]

const tooltipStyle = {
  backgroundColor: '#1e293b',
  border: '1px solid #334155',
  borderRadius: '8px',
  color: '#e2e8f0',
  fontSize: '12px',
}

export default function Charts({ chartId }) {
  if (chartId === 'overview') {
    return (
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
        <h3 className="font-semibold text-white mb-4 text-sm">Accuracy Comparison — All Methods (Paper Numbers)</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={PAPER_DATA} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} unit="%" domain={[0, 65]} />
            <Tooltip contentStyle={tooltipStyle} formatter={(v) => [`${v}%`, 'Accuracy']} />
            <Bar dataKey="acc" name="Accuracy"
              fill="#3b82f6"
              radius={[4, 4, 0, 0]}
              label={{ position: 'top', fill: '#94a3b8', fontSize: 11, formatter: (v) => `${v}%` }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }

  if (chartId === 'results') {
    return (
      <div className="space-y-4">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
          <h3 className="font-semibold text-white mb-4 text-sm">Accuracy: Our Results vs Paper</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={COMPARE_DATA} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} unit="%" domain={[0, 65]} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v, n) => [`${v}%`, n]} />
              <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
              <Bar dataKey="paper" name="Paper (CUDA)" fill="#64748b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="ours"  name="Ours (MPS)"   fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
          <h3 className="font-semibold text-white mb-4 text-sm">Chain Length: Our Results vs Paper</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={CHAIN_DATA} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
              <Bar dataKey="paper" name="Paper (CUDA)" fill="#64748b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="ours"  name="Ours (MPS)"   fill="#60a5fa" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    )
  }

  return null
}
