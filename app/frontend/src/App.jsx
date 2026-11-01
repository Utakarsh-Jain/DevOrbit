import { useCallback, useEffect, useMemo, useState } from 'react'

async function request(path, options) {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) }, ...options })
  const text = await response.text()
  let data = null
  if (text) { try { data = JSON.parse(text) } catch { data = text } }
  if (!response.ok) {
    const details = Array.isArray(data?.details) ? ` ${data.details.join(' ')}` : ''
    throw new Error((data && (data.error || data.message)) ? `${data.error || data.message}${details}` : `Request failed with status ${response.status}`)
  }
  return data
}

function formatDate(value) {
  if (!value || Number.isNaN(Date.parse(value))) return '—'
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

export default function App() {
  const [meta, setMeta] = useState(null)
  const [issues, setIssues] = useState([])
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [busyIssueId, setBusyIssueId] = useState('')
  const [form, setForm] = useState({ title: '', description: '' })
  const [filter, setFilter] = useState('ALL')
  const [search, setSearch] = useState('')

  const loadDashboard = useCallback(async () => {
    setLoading(true); setError('')
    try {
      // The root response is the UI contract; this client carries no deployment defaults.
      const rootInfo = await request('/')
      if (!rootInfo?.ui?.endpoints?.issues || !rootInfo?.ui?.endpoints?.health || !Array.isArray(rootInfo.ui.statuses)) throw new Error('The server returned an incomplete UI configuration.')
      const [healthInfo, allIssues] = await Promise.all([request(rootInfo.ui.endpoints.health), request(rootInfo.ui.endpoints.issues)])
      setMeta(rootInfo); setHealth(healthInfo); setIssues(Array.isArray(allIssues) ? allIssues : [])
    } catch (err) { setError(err.message || 'Unable to load the dashboard.') } finally { setLoading(false) }
  }, [])

  useEffect(() => { loadDashboard() }, [loadDashboard])
  const statuses = meta?.ui?.statuses ?? []
  const statusLabels = useMemo(() => Object.fromEntries(statuses.map(({ value, label }) => [value, label])), [statuses])
  const counts = useMemo(() => issues.reduce((acc, issue) => {
    acc.total += 1
    if (Object.hasOwn(acc, issue.status)) acc[issue.status] += 1
    return acc
  }, { total: 0, ...Object.fromEntries(statuses.map(({ value }) => [value, 0])) }), [issues, statuses])
  const filteredIssues = useMemo(() => issues.filter((issue) => {
    const fields = [issue.title || '', issue.description || '', issue.id || '']
    return (filter === 'ALL' || issue.status === filter) && (!search || fields.some((value) => value.toLowerCase().includes(search.toLowerCase())))
  }), [issues, filter, search])

  async function handleCreate(event) {
    event.preventDefault()
    if (!meta || !form.title.trim() || !form.description.trim()) return
    setSubmitting(true); setError(''); setNotice('')
    try {
      await request(meta.ui.endpoints.issues, { method: 'POST', body: JSON.stringify({ title: form.title.trim(), description: form.description.trim() }) })
      setForm({ title: '', description: '' }); setNotice('Issue submitted successfully.'); await loadDashboard()
    } catch (err) { setError(err.message) } finally { setSubmitting(false) }
  }

  async function handleStatusChange(issue, status) {
    if (!meta || status === issue.status) return
    setBusyIssueId(issue.id); setError(''); setNotice('')
    try {
      await request(`${meta.ui.endpoints.issues}/${encodeURIComponent(issue.id)}`, { method: 'PATCH', body: JSON.stringify({ status }) })
      setNotice(`Issue #${issue.id} moved to ${statusLabels[status] || status}.`); await loadDashboard()
    } catch (err) { setError(err.message) } finally { setBusyIssueId('') }
  }

  const config = meta?.ui?.form
  return <div className="page">
    <header className="header"><div className="header__brand"><div className="header__logo">DO</div><div><h1>{meta?.ui?.title || 'Loading…'}</h1><p>{meta?.ui?.subtitle || ''}</p></div></div><div className="header__status">{meta && <><span className="pill">v<strong>{meta.version}</strong></span><span className={`pill ${health?.status === 'UP' ? 'pill--up' : 'pill--down'}`}><span className="status-dot" />{health?.status || 'Unavailable'}</span><span className="pill">{meta.environment}</span></>}</div></header>
    {meta && <section className="stats"><button type="button" className={`stat ${filter === 'ALL' ? 'stat--selected' : ''}`} onClick={() => setFilter('ALL')}><span className="stat__title">All Issues</span><span className="stat__count">{counts.total}</span></button>{statuses.map(({ value, label }) => <button key={value} type="button" className={`stat stat--${value.toLowerCase()} ${filter === value ? 'stat--selected' : ''}`} onClick={() => setFilter(value)}><span className="stat__title">{label}</span><span className="stat__count">{counts[value]}</span></button>)}</section>}
    {error && <div className="banner banner--error" role="alert">{error}</div>}{notice && <div className="banner banner--ok" role="status">{notice}</div>}
    {meta && config && <main className="content"><section className="card form-card"><h2>Report Issue</h2><form onSubmit={handleCreate}><label>Title<input type="text" value={form.title} minLength={config.titleMinLength} maxLength={config.titleMaxLength} required onChange={(e) => setForm({ ...form, title: e.target.value })} /></label><label>Description<textarea value={form.description} minLength={config.descriptionMinLength} maxLength={config.descriptionMaxLength} required rows={4} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label><button type="submit" className="btn-primary" disabled={submitting}>{submitting ? 'Submitting…' : 'Submit Issue'}</button></form></section>
      <section className="card list-card"><div className="list-card__header"><div className="list-card__title"><h2>Issues</h2>{filter !== 'ALL' && <span className="filter-badge">Filtered by: {statusLabels[filter]}<button type="button" aria-label="Clear filter" onClick={() => setFilter('ALL')}>✕</button></span>}</div><div className="list-card__actions"><input type="search" className="search-box" placeholder="Search issues…" value={search} onChange={(e) => setSearch(e.target.value)} /><button type="button" className="btn-refresh" aria-label="Refresh issues" onClick={loadDashboard} disabled={loading}>{loading ? '…' : '↻'}</button></div></div>
        {loading && issues.length === 0 ? <p className="empty">Loading issues…</p> : filteredIssues.length === 0 ? <p className="empty">{search || filter !== 'ALL' ? 'No matching issues found.' : 'No issues reported yet.'}</p> : <div className="issue-list">{filteredIssues.map((issue) => <article key={issue.id} className="issue-item"><div className="issue-item__top"><span className="issue-id">#{issue.id}</span><span className={`badge badge--${String(issue.status).toLowerCase()}`}>{statusLabels[issue.status] || issue.status}</span></div><h3 className="issue-title">{issue.title}</h3><p className="issue-description">{issue.description}</p><div className="issue-item__bottom"><span className="issue-date">{formatDate(issue.createdAt)}</span><label className="issue-status-select"><span>Status:</span><select value={issue.status} disabled={busyIssueId === issue.id} onChange={(e) => handleStatusChange(issue, e.target.value)}>{statuses.map(({ value, label }) => <option key={value} value={value}>{label}</option>)}</select></label></div></article>)}</div>}</section></main>}
  </div>
}
