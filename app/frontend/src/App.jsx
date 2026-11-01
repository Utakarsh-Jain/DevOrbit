import { useCallback, useEffect, useMemo, useState } from 'react'

async function request(path, options) {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
    ...options,
  })

  if (response.status === 204) {
    return null
  }

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
  const [statuses, setStatuses] = useState([])
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

  // Edit state for inline/modal update (CRUD - Update)
  const [editingIssue, setEditingIssue] = useState(null)
  const [editForm, setEditForm] = useState({ title: '', description: '', status: '' })

  // Status mapping derived dynamically from backend
  const statusLabels = useMemo(() => {
    const map = {}
    statuses.forEach((s) => {
      map[s.status] = s.label
    })
    return map
  }, [statuses])

  const loadDashboard = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [rootInfo, healthInfo, allIssues, backendStatuses] = await Promise.all([
        request('/').catch(() => null),
        request('/health').catch(() => ({ status: 'DOWN' })),
        request('/api/issues'),
        request('/api/issues/statuses').catch(() => []),
      ])

      if (rootInfo && typeof rootInfo === 'object') {
        setMeta(rootInfo)
      }
      setHealth(healthInfo)
      setIssues(Array.isArray(allIssues) ? allIssues : [])
      if (Array.isArray(backendStatuses) && backendStatuses.length > 0) {
        setStatuses(backendStatuses)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

  // Count issues by dynamic statuses
  const counts = useMemo(() => {
    const res = { total: issues.length }
    statuses.forEach((s) => {
      res[s.status] = 0
    })
    issues.forEach((issue) => {
      if (res[issue.status] !== undefined) {
        res[issue.status] += 1
      }
    })
    return res
  }, [issues, statuses])

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

  // CRUD - Create (POST)
  async function handleCreate(event) {
    event.preventDefault()
    if (!form.title.trim() || !form.description.trim()) return

    setSubmitting(true)
    setError('')
    setNotice('')
    try {
      const created = await request('/api/issues', {
        method: 'POST',
        body: JSON.stringify({
          title: form.title.trim(),
          description: form.description.trim(),
        }),
      })
      setForm({ title: '', description: '' })
      setNotice(`Issue #${created.id} created successfully.`)
      await loadDashboard()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  // CRUD - Quick Status Update (PATCH)
  async function handleStatusChange(issue, newStatus) {
    if (newStatus === issue.status) return
    setBusyIssueId(issue.id)
    setError('')
    setNotice('')
    try {
      await request(`/api/issues/${issue.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      })
      setNotice(`Issue #${issue.id} marked as ${statusLabels[newStatus] || newStatus}.`)
      await loadDashboard()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyIssueId('')
    }
  }

  // CRUD - Full Update (PUT)
  function startEdit(issue) {
    setEditingIssue(issue)
    setEditForm({
      title: issue.title,
      description: issue.description,
      status: issue.status,
    })
  }

  function cancelEdit() {
    setEditingIssue(null)
  }

  async function handleUpdate(event) {
    event.preventDefault()
    if (!editingIssue) return

    setSubmitting(true)
    setError('')
    setNotice('')
    try {
      await request(`/api/issues/${editingIssue.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          title: editForm.title.trim(),
          description: editForm.description.trim(),
          status: editForm.status,
        }),
      })
      setNotice(`Issue #${editingIssue.id} updated successfully.`)
      setEditingIssue(null)
      await loadDashboard()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  // CRUD - Delete (DELETE)
  async function handleDelete(issue) {
    if (!window.confirm(`Are you sure you want to delete #${issue.id}?`)) return

    setBusyIssueId(issue.id)
    setError('')
    setNotice('')
    try {
      await request(`/api/issues/${issue.id}`, {
        method: 'DELETE',
      })
      setNotice(`Issue #${issue.id} deleted.`)
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
            <h1>{meta?.application ?? 'DevOrbit'}</h1>
            <p>Campus Issue Management Lifecycle</p>
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
            {meta?.environment ?? 'local'}
          </span>
        </div>
      </header>

      {/* Dynamic Summary Cards (Clicked card filters issues) */}
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

        {statuses.map((s) => (
          <div
            key={s.status}
            className={`stat stat--${s.status.toLowerCase()} ${filter === s.status ? 'stat--selected' : ''}`}
            onClick={() => setFilter(s.status)}
            role="button"
            tabIndex={0}
          >
            <span className="stat__title">{s.label}</span>
            <span className="stat__count">{counts[s.status] ?? 0}</span>
          </div>
        ))}
      </section>

      {/* Notifications */}
      {error && <div className="banner banner--error">{error}</div>}
      {notice && <div className="banner banner--ok">{notice}</div>}

      {/* Main Content */}
      <main className="content">
        {/* Left: Create Form */}
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
                placeholder="e.g. Projector not working in Lab 3"
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
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Issue'}
            </button>
          </form>
        </section>

        {/* Right: Issues List */}
        <section className="card list-card">
          <div className="list-card__header">
            <div className="list-card__title">
              <h2>Issues Feed</h2>
              {filter !== 'ALL' && (
                <span className="filter-badge">
                  Filtered: {statusLabels[filter] || filter}
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
                title="Refresh feed"
              >
                {loading ? '...' : '↻'}
              </button>
            </div>
          </div>

          {loading && issues.length === 0 ? (
            <p className="empty">Loading issues from server...</p>
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
                      {statusLabels[issue.status] ?? issue.status}
                    </span>
                  </div>

                  <h3 className="issue-title">{issue.title}</h3>
                  <p className="issue-description">{issue.description}</p>

                  <div className="issue-item__bottom">
                    <span className="issue-date">{formatDate(issue.createdAt)}</span>

                    <div className="issue-actions-row">
                      {/* CRUD - Edit button */}
                      <button
                        type="button"
                        className="btn-action btn-action--edit"
                        disabled={busyIssueId === issue.id}
                        onClick={() => startEdit(issue)}
                        title="Edit title & description"
                      >
                        Edit
                      </button>

                      {/* CRUD - Delete button */}
                      <button
                        type="button"
                        className="btn-action btn-action--delete"
                        disabled={busyIssueId === issue.id}
                        onClick={() => handleDelete(issue)}
                        title="Delete issue"
                      >
                        Delete
                      </button>

                      {/* CRUD - Status dropdown */}
                      <label className="issue-status-select">
                        <select
                          value={issue.status}
                          disabled={busyIssueId === issue.id}
                          onChange={(e) => handleStatusChange(issue, e.target.value)}
                        >
                          {statuses.map((s) => (
                            <option key={s.status} value={s.status}>
                              {s.label}
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Edit Modal (CRUD - Full Update) */}
      {editingIssue && (
        <div className="modal-backdrop">
          <div className="modal">
            <div className="modal__header">
              <h3>Edit Issue #{editingIssue.id}</h3>
              <button type="button" className="btn-close" onClick={cancelEdit}>✕</button>
            </div>
            <form onSubmit={handleUpdate}>
              <label>
                Title
                <input
                  type="text"
                  value={editForm.title}
                  minLength={3}
                  maxLength={100}
                  required
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                />
              </label>
              <label>
                Description
                <textarea
                  value={editForm.description}
                  minLength={5}
                  maxLength={1000}
                  required
                  rows={4}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                />
              </label>
              <label>
                Status
                <select
                  value={editForm.status}
                  onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                >
                  {statuses.map((s) => (
                    <option key={s.status} value={s.status}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </label>
              <div className="modal__footer">
                <button type="button" className="btn-secondary" onClick={cancelEdit}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
