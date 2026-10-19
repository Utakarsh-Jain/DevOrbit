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

  const loadDashboard = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [rootInfo, healthInfo, allIssues] = await Promise.all([
        request('/'),
        request('/health'),
        request('/api/issues'),
      ])
      setMeta(rootInfo)
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

  async function handleCreate(event) {
    event.preventDefault()
    setSubmitting(true)
    setError('')
    setNotice('')
    try {
      await request('/api/issues', {
        method: 'POST',
        body: JSON.stringify(form),
      })
      setForm({ title: '', description: '' })
      setNotice('Issue created successfully.')
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
      setNotice(`Issue ${issue.id} updated to ${STATUS_LABELS[status]}.`)
      await loadDashboard()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyIssueId('')
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <div className="hero__brand">
          <span className="hero__mark">DO</span>
          <div>
            <h1>DevOrbit</h1>
            <p>Campus Issue Management</p>
          </div>
        </div>
        <div className="hero__meta">
          <span className="pill">
            Version <strong>{meta?.version ?? '—'}</strong>
          </span>
          <span className={`pill ${health?.status === 'UP' ? 'pill--ok' : 'pill--down'}`}>
            Health <strong>{health?.status ?? 'UNKNOWN'}</strong>
          </span>
          <span className="pill">
            Env <strong>{meta?.environment ?? '—'}</strong>
          </span>
        </div>
      </header>

      <section className="stats">
        <article className="stat">
          <span className="stat__label">Total</span>
          <span className="stat__value">{counts.total}</span>
        </article>
        <article className="stat">
          <span className="stat__label">Open</span>
          <span className="stat__value">{counts.OPEN}</span>
        </article>
        <article className="stat">
          <span className="stat__label">In Progress</span>
          <span className="stat__value">{counts.IN_PROGRESS}</span>
        </article>
        <article className="stat">
          <span className="stat__label">Resolved</span>
          <span className="stat__value">{counts.RESOLVED}</span>
        </article>
      </section>

      {error && <div className="banner banner--error">{error}</div>}
      {notice && <div className="banner banner--ok">{notice}</div>}

      <div className="layout">
        <section className="panel">
          <div className="panel__header">
            <h2>Report an issue</h2>
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
                placeholder="e.g. Projector not working in Lab 3"
                onChange={(event) => setForm({ ...form, title: event.target.value })}
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
                placeholder="Describe the issue in a few sentences"
                onChange={(event) => setForm({ ...form, description: event.target.value })}
              />
            </label>
            <button type="submit" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Create issue'}
            </button>
          </form>
        </section>

        <section className="panel panel--grow">
          <div className="panel__header">
            <h2>Campus issues</h2>
            <button type="button" className="ghost" onClick={loadDashboard} disabled={loading}>
              {loading ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>

          {loading && issues.length === 0 ? (
            <p className="muted">Loading issues...</p>
          ) : issues.length === 0 ? (
            <p className="muted">No issues reported yet.</p>
          ) : (
            <ul className="issues">
              {issues.map((issue) => (
                <li key={issue.id} className="issue">
                  <div className="issue__head">
                    <span className="issue__id">{issue.id}</span>
                    <span className={`badge badge--${issue.status.toLowerCase()}`}>
                      {STATUS_LABELS[issue.status] ?? issue.status}
                    </span>
                  </div>
                  <h3>{issue.title}</h3>
                  <p className="issue__desc">{issue.description}</p>
                  <div className="issue__foot">
                    <span className="muted">Created {formatDate(issue.createdAt)}</span>
                    <label className="issue__action">
                      Status
                      <select
                        value={issue.status}
                        disabled={busyIssueId === issue.id}
                        onChange={(event) => handleStatusChange(issue, event.target.value)}
                      >
                        {STATUSES.map((status) => (
                          <option key={status} value={status}>
                            {STATUS_LABELS[status]}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <footer className="footer">
        <span>
          DevOrbit sample workload exposed through Kubernetes NodePort and monitored with AWS
          CloudWatch.
        </span>
      </footer>
    </div>
  )
}
