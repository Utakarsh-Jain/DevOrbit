import { useCallback, useEffect, useMemo, useState } from 'react'

const STATUSES = ['OPEN', 'IN_PROGRESS', 'RESOLVED']

const STATUS_LABELS = {
  OPEN: 'Open',
  IN_PROGRESS: 'In Progress',
  RESOLVED: 'Resolved',
}

async function request(path, options) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
    ...options,
  })

  const text = await response.text()
  let data = null
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = text
    }
  }

  if (!response.ok) {
    const message =
      (data && (data.error || data.message)) ||
      `Request failed with status ${response.status}`
    throw new Error(message)
  }

  return data
}

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

export default function App() {
  const [issues, setIssues] = useState([])
  const [meta, setMeta] = useState(null)
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
    setLoading(true)
    setError('')
    try {
      const [rootInfo, healthInfo, allIssues] = await Promise.all([
        request('/').catch(() => null),
        request('/health').catch(() => ({ status: 'DOWN' })),
        request('/api/issues'),
      ])
      if (rootInfo && typeof rootInfo === 'object') {
        setMeta(rootInfo)
      }
      setHealth(healthInfo)
      setIssues(Array.isArray(allIssues) ? allIssues : [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

  const counts = useMemo(() => {
    return issues.reduce(
      (acc, issue) => {
        acc.total += 1
        if (acc[issue.status] !== undefined) acc[issue.status] += 1
        return acc
      },
      { total: 0, OPEN: 0, IN_PROGRESS: 0, RESOLVED: 0 },
    )
  }, [issues])

  const filteredIssues = useMemo(() => {
    return issues.filter((issue) => {
      const matchesFilter = filter === 'ALL' || issue.status === filter
      const matchesSearch =
        !search ||
        issue.title.toLowerCase().includes(search.toLowerCase()) ||
        issue.description.toLowerCase().includes(search.toLowerCase()) ||
        issue.id.toLowerCase().includes(search.toLowerCase())
      return matchesFilter && matchesSearch
    })
  }, [issues, filter, search])

  async function handleCreate(event) {
    event.preventDefault()
    if (!form.title.trim() || !form.description.trim()) return

    setSubmitting(true)
    setError('')
    setNotice('')
    try {
      await request('/api/issues', {
        method: 'POST',
        body: JSON.stringify({
          title: form.title.trim(),
          description: form.description.trim(),
        }),
      })
      setForm({ title: '', description: '' })
      setNotice('Issue submitted successfully.')
      await loadDashboard()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  async function handleStatusChange(issue, status) {
    if (status === issue.status) return
    setBusyIssueId(issue.id)
    setError('')
    setNotice('')
    try {
      await request(`/api/issues/${issue.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      })
      setNotice(`Issue #${issue.id} moved to ${STATUS_LABELS[status]}.`)
      await loadDashboard()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyIssueId('')
    }
  }

  return (
    <div className="page">
      {/* Header */}
      <header className="header">
        <div className="header__brand">
          <div className="header__logo">DO</div>
          <div>
            <h1>DevOrbit</h1>
            <p>Campus Issue Management</p>
          </div>
        </div>

        <div className="header__status">
          <span className="pill">
            v<strong>{meta?.version ?? '1.0.0'}</strong>
          </span>
          <span className={`pill ${health?.status === 'UP' ? 'pill--up' : 'pill--down'}`}>
            <span className="status-dot"></span>
            {health?.status ?? 'DOWN'}
          </span>
          <span className="pill">
            {meta?.environment ?? 'production'}
          </span>
        </div>
      </header>

      {/* Summary Filter Cards (Click card to filter - No duplicate tabs needed) */}
      <section className="stats">
        <div
          className={`stat ${filter === 'ALL' ? 'stat--selected' : ''}`}
          onClick={() => setFilter('ALL')}
          role="button"
          tabIndex={0}
        >
          <span className="stat__title">All Issues</span>
          <span className="stat__count">{counts.total}</span>
        </div>
        <div
          className={`stat stat--open ${filter === 'OPEN' ? 'stat--selected' : ''}`}
          onClick={() => setFilter('OPEN')}
          role="button"
          tabIndex={0}
        >
          <span className="stat__title">Open</span>
          <span className="stat__count">{counts.OPEN}</span>
        </div>
        <div
          className={`stat stat--progress ${filter === 'IN_PROGRESS' ? 'stat--selected' : ''}`}
          onClick={() => setFilter('IN_PROGRESS')}
          role="button"
          tabIndex={0}
        >
          <span className="stat__title">In Progress</span>
          <span className="stat__count">{counts.IN_PROGRESS}</span>
        </div>
        <div
          className={`stat stat--resolved ${filter === 'RESOLVED' ? 'stat--selected' : ''}`}
          onClick={() => setFilter('RESOLVED')}
          role="button"
          tabIndex={0}
        >
          <span className="stat__title">Resolved</span>
          <span className="stat__count">{counts.RESOLVED}</span>
        </div>
      </section>

      {/* Notifications */}
      {error && <div className="banner banner--error">{error}</div>}
      {notice && <div className="banner banner--ok">{notice}</div>}

      {/* Main Content Layout */}
      <main className="content">
        {/* Left: New Issue Form */}
        <section className="card form-card">
          <h2>Report Issue</h2>
          <form onSubmit={handleCreate}>
            <label>
              Title
              <input
                type="text"
                value={form.title}
                minLength={3}
                maxLength={100}
                required
                placeholder="e.g. Wi-Fi down in Lab 4"
                onChange={(e) => setForm({ ...form, title: e.target.value })}
              />
            </label>
            <label>
              Description
              <textarea
                value={form.description}
                minLength={5}
                maxLength={1000}
                required
                rows={4}
                placeholder="Provide location and specific details..."
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </label>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Issue'}
            </button>
          </form>
        </section>

        {/* Right: Issues List */}
        <section className="card list-card">
          <div className="list-card__header">
            <div className="list-card__title">
              <h2>Issues</h2>
              {filter !== 'ALL' && (
                <span className="filter-badge">
                  Filtered by: {STATUS_LABELS[filter]}
                  <button type="button" onClick={() => setFilter('ALL')}>✕</button>
                </span>
              )}
            </div>
            <div className="list-card__actions">
              <input
                type="search"
                className="search-box"
                placeholder="Search issues..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <button
                type="button"
                className="btn-refresh"
                onClick={loadDashboard}
                disabled={loading}
              >
                {loading ? '...' : '↻'}
              </button>
            </div>
          </div>

          {loading && issues.length === 0 ? (
            <p className="empty">Loading issues...</p>
          ) : filteredIssues.length === 0 ? (
            <p className="empty">
              {search || filter !== 'ALL'
                ? 'No matching issues found.'
                : 'No issues reported yet.'}
            </p>
          ) : (
            <div className="issue-list">
              {filteredIssues.map((issue) => (
                <article key={issue.id} className="issue-item">
                  <div className="issue-item__top">
                    <span className="issue-id">#{issue.id}</span>
                    <span className={`badge badge--${issue.status.toLowerCase()}`}>
                      {STATUS_LABELS[issue.status] ?? issue.status}
                    </span>
                  </div>

                  <h3 className="issue-title">{issue.title}</h3>
                  <p className="issue-description">{issue.description}</p>

                  <div className="issue-item__bottom">
                    <span className="issue-date">{formatDate(issue.createdAt)}</span>
                    <label className="issue-status-select">
                      <span>Status:</span>
                      <select
                        value={issue.status}
                        disabled={busyIssueId === issue.id}
                        onChange={(e) => handleStatusChange(issue, e.target.value)}
                      >
                        {STATUSES.map((status) => (
                          <option key={status} value={status}>
                            {STATUS_LABELS[status]}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
