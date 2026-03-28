import './globals.css'

export const metadata = {
  title: 'CoLaR Replication — Think Silently, Think Fast',
  description:
    'Replication of "Think Silently, Think Fast: Dynamic Latent Compression of LLM Reasoning Chains" (arXiv 2505.16552)',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
