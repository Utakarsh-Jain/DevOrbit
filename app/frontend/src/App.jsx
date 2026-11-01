import { useCallback, useEffect, useMemo, useState } from 'react'

const STATUSES = ['OPEN', 'IN_PROGRESS', 'RESOLVED']

const STATUS_LABELS = {
  OPEN: 'Open',
  IN_PROGRESS: 'In Progress',
  RESOLVED: 'Resolved',
}

const NEXT_STATUS = {
  OPEN: 'IN_PROGRESS',
  IN_PROGRESS: 'RESOLVED',
}

const NEXT_STATUS_LABEL = {
  OPEN: 'Start Progress →',
  IN_PROGRESS: 'Mark Resolved ✓',
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
  const [searchQuery, setSearchQuery] = useState('')
  const [lastRefreshed, setLastRefreshed] = useState(null)

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
      setLastRefreshed(new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }))
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
        !searchQuery ||
        issue.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        issue.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        issue.id.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesFilter && matchesSearch
    })
  }, [issues, filter, searchQuery])

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
      setNotice('Issue reported successfully.')
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
      setNotice(`Issue ${issue.id} marked as ${STATUS_LABELS[status]}.`)
      await loadDashboard()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyIssueId('')
    }
  }

  return (
    <div className="page">
      {/* Top Header / Brand */}
      <header className="hero">
        <div className="hero__brand">
          <div className="hero__mark">DO</div>
          <div>
            <h1>DevOrbit</h1>
            <p>Campus Issue Management Lifecycle</p>
          </div>
        </div>
        <div className="hero__meta">
          <div className="pill">
            <span className="pill__dot"></span>
            Version: <strong>{meta?.version ?? '1.0.0'}</strong>
          </div>
          <div className={`pill ${health?.status === 'UP' ? 'pill--ok' : 'pill--down'}`}>
            <span className="pill__status-dot"></span>
            Status: <strong>{health?.status ?? 'UNKNOWN'}</strong>
          </div>
          <div className="pill">
            Env: <strong>{meta?.environment ?? 'production'}</strong>
          </div>
        </div>
      </header>

      {/* Overview Stat Cards */}
      <section className="stats">
        <div
          className={`stat ${filter === 'ALL' ? 'stat--active' : ''}`}
          onClick={() => setFilter('ALL')}
          role="button"
          tabIndex={0}
        >
          <span className="stat__label">Total Issues</span>
          <span className="stat__value">{counts.total}</span>
        </div>
        <div
          className={`stat stat--open ${filter === 'OPEN' ? 'stat--active' : ''}`}
          onClick={() => setFilter('OPEN')}
          role="button"
          tabIndex={0}
        >
          <span className="stat__label">Open</span>
          <span className="stat__value">{counts.OPEN}</span>
        </div>
        <div
          className={`stat stat--progress ${filter === 'IN_PROGRESS' ? 'stat--active' : ''}`}
          onClick={() => setFilter('IN_PROGRESS')}
          role="button"
          tabIndex={0}
        >
          <span className="stat__label">In Progress</span>
          <span className="stat__value">{counts.IN_PROGRESS}</span>
        </div>
        <div
          className={`stat stat--resolved ${filter === 'RESOLVED' ? 'stat--active' : ''}`}
          onClick={() => setFilter('RESOLVED')}
          role="button"
          tabIndex={0}
        >
          <span className="stat__label">Resolved</span>
          <span className="stat__value">{counts.RESOLVED}</span>
        </div>
      </section>

      {/* Alert Banners */}
      {error && <div className="banner banner--error">{error}</div>}
      {notice && <div className="banner banner--ok">{notice}</div>}

      {/* Main Two-Column Layout */}
      <div className="layout">
        {/* Left Column: Create Issue Form */}
        <section className="panel">
          <div className="panel__header">
            <h2>Report Campus Issue</h2>
          </div>
          <form className="form" onSubmit={handleCreate}>
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
                placeholder="Specify location and details..."
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </label>
            <button type="submit" className="btn btn--primary" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Issue'}
            </button>
          </form>
        </section>

        {/* Right Column: Issues List */}
        <section className="panel panel--grow">
          <div className="panel__header">
            <div className="panel__title-row">
              <h2>Issues Feed</h2>
              {lastRefreshed && (
                <span className="muted-time">Refreshed: {lastRefreshed}</span>
              )}
            </div>
            <button
              type="button"
              className="btn btn--ghost"
              onClick={loadDashboard}
              disabled={loading}
            >
              {loading ? 'Refreshing...' : '↻ Refresh'}
            </button>
          </div>

          {/* Filter Bar & Search */}
          <div className="controls-bar">
            <div className="filter-tabs">
              <button
                type="button"
                className={`tab ${filter === 'ALL' ? 'tab--active' : ''}`}
                onClick={() => setFilter('ALL')}
              >
                All ({counts.total})
              </button>
              <button
                type="button"
                className={`tab ${filter === 'OPEN' ? 'tab--active' : ''}`}
                onClick={() => setFilter('OPEN')}
              >
                Open ({counts.OPEN})
              </button>
              <button
                type="button"
                className={`tab ${filter === 'IN_PROGRESS' ? 'tab--active' : ''}`}
                onClick={() => setFilter('IN_PROGRESS')}
              >
                In Progress ({counts.IN_PROGRESS})
              </button>
              <button
                type="button"
                className={`tab ${filter === 'RESOLVED' ? 'tab--active' : ''}`}
                onClick={() => setFilter('RESOLVED')}
              >
                Resolved ({counts.RESOLVED})
              </button>
            </div>
            <input
              type="search"
              className="search-input"
              placeholder="Filter by keyword..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Issue Cards */}
          {loading && issues.length === 0 ? (
            <p className="muted empty-state">Loading issues from cluster...</p>
          ) : filteredIssues.length === 0 ? (
            <p className="muted empty-state">
              {searchQuery || filter !== 'ALL'
                ? 'No matching issues found.'
                : 'No campus issues reported yet.'}
            </p>
          ) : (
            <ul className="issues">
              {filteredIssues.map((issue) => (
                <li key={issue.id} className="issue">
                  <div className="issue__head">
                    <span className="issue__id">#{issue.id}</span>
                    <span className={`badge badge--${issue.status.toLowerCase()}`}>
                      {STATUS_LABELS[issue.status] ?? issue.status}
                    </span>
                  </div>

                  <h3 className="issue__title">{issue.title}</h3>
                  <p className="issue__desc">{issue.description}</p>

                  <div className="issue__foot">
                    <span className="muted-time">Reported {formatDate(issue.createdAt)}</span>

                    <div className="issue__controls">
                      {/* One-click quick transition button for live demos */}
                      {NEXT_STATUS[issue.status] && (
                        <button
                          type="button"
                          className="btn-quick"
                          disabled={busyIssueId === issue.id}
                          onClick={() => handleStatusChange(issue, NEXT_STATUS[issue.status])}
                        >
                          {NEXT_STATUS_LABEL[issue.status]}
                        </button>
                      )}

                      {/* Dropdown selector */}
                      <label className="issue__action">
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
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {/* Minimal Footer */}
      <footer className="footer">
        <span>DevOrbit Campus Issue Management · Cloud-Native Architecture</span>
      </footer>
    </div>
  )
}
