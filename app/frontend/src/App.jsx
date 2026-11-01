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
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
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

  // Modal state for full issue editing (CRUD - PUT)
  const [editingIssue, setEditingIssue] = useState(null)
  const [editForm, setEditForm] = useState({ title: '', description: '', status: '' })

  // Modal state for delete confirmation (Apple HIG Dialog)
  const [deletingIssue, setDeletingIssue] = useState(null)

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

  // Auto-dismiss notices after 4s
  useEffect(() => {
    if (!notice) return
    const timer = setTimeout(() => setNotice(''), 4000)
    return () => clearTimeout(timer)
  }, [notice])

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
      setNotice(`Issue #${created.id} logged successfully`)
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
      setNotice(`Issue #${issue.id} marked as ${statusLabels[newStatus] || newStatus}`)
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
      setNotice(`Issue #${editingIssue.id} updated`)
      setEditingIssue(null)
      await loadDashboard()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  // CRUD - Delete (DELETE)
  async function confirmDelete() {
    if (!deletingIssue) return
    const id = deletingIssue.id
    setDeletingIssue(null)
    setBusyIssueId(id)
    setError('')
    setNotice('')
    try {
      await request(`/api/issues/${id}`, {
        method: 'DELETE',
      })
      setNotice(`Issue #${id} deleted`)
      await loadDashboard()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusyIssueId('')
    }
  }

  return (
    <div className="apple-canvas">
      <div className="apple-container">
        {/* Navigation Bar */}
        <header className="apple-nav">
          <div className="apple-nav__brand">
            <div className="apple-mark" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <circle cx="12" cy="12" r="4"></circle>
                <line x1="4.93" y1="4.93" x2="9.17" y2="9.17"></line>
                <line x1="14.83" y1="14.83" x2="19.07" y2="19.07"></line>
                <line x1="14.83" y1="9.17" x2="19.07" y2="4.93"></line>
                <line x1="4.93" y1="19.07" x2="9.17" y2="14.83"></line>
              </svg>
            </div>
            <div className="apple-nav__title-group">
              <h1 className="apple-title">{meta?.application ?? 'DevOrbit Campus Issue Management'}</h1>
              <p className="apple-subtitle">Cloud-Native DevOps & Campus Operations Lifecycle</p>
            </div>
          </div>

          <div className="apple-nav__capsules">
            <div className="apple-capsule">
              <span className="apple-capsule__label">v</span>
              <span className="apple-capsule__val">{meta?.version ?? '1.0.0'}</span>
            </div>
            <div className={`apple-capsule ${health?.status === 'UP' ? 'apple-capsule--ok' : 'apple-capsule--err'}`}>
              <span className="apple-capsule__dot"></span>
              <span className="apple-capsule__val">{health?.status === 'UP' ? 'Healthy' : (health?.status ?? 'Offline')}</span>
            </div>
            <div className="apple-capsule">
              <span className="apple-capsule__val">{meta?.environment ?? 'local'}</span>
            </div>
          </div>
        </header>

        {/* Dynamic Metric Cards (Interactive Apple Widgets) */}
        <section className="apple-widgets" aria-label="Issue Summary Widgets">
          <button
            type="button"
            className={`apple-widget ${filter === 'ALL' ? 'apple-widget--active' : ''}`}
            onClick={() => setFilter('ALL')}
          >
            <span className="apple-widget__label">Total Issues</span>
            <span className="apple-widget__value">{counts.total}</span>
          </button>

          {statuses.map((s) => (
            <button
              type="button"
              key={s.status}
              className={`apple-widget apple-widget--${s.status.toLowerCase()} ${filter === s.status ? 'apple-widget--active' : ''}`}
              onClick={() => setFilter(s.status)}
            >
              <span className="apple-widget__label">{s.label}</span>
              <span className="apple-widget__value">{counts[s.status] ?? 0}</span>
            </button>
          ))}
        </section>

        {/* Floating Notification Banners */}
        {error && (
          <div className="apple-alert apple-alert--error" role="alert">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span className="apple-alert__text">{error}</span>
            <button type="button" className="apple-alert__dismiss" onClick={() => setError('')} aria-label="Dismiss error">✕</button>
          </div>
        )}
        {notice && (
          <div className="apple-alert apple-alert--success" role="status">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <span className="apple-alert__text">{notice}</span>
            <button type="button" className="apple-alert__dismiss" onClick={() => setNotice('')} aria-label="Dismiss notice">✕</button>
          </div>
        )}

        {/* Workspace Layout */}
        <div className="apple-grid">
          {/* Create Issue Panel */}
          <section className="apple-card apple-card--form">
            <div className="apple-card__header">
              <h2 className="apple-card__title">Report Issue</h2>
              <span className="apple-card__badge">New</span>
            </div>

            <form className="apple-form" onSubmit={handleCreate}>
              <div className="apple-field">
                <label htmlFor="issue-title">Title</label>
                <input
                  id="issue-title"
                  type="text"
                  value={form.title}
                  minLength={3}
                  maxLength={100}
                  required
                  placeholder="e.g. Lab 3 Projector Lamp Fault"
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                />
              </div>

              <div className="apple-field">
                <label htmlFor="issue-desc">Description</label>
                <textarea
                  id="issue-desc"
                  value={form.description}
                  minLength={5}
                  maxLength={1000}
                  required
                  rows={4}
                  placeholder="Describe location, room number, and behavior..."
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>

              <button type="submit" className="apple-btn-primary" disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit Issue'}
              </button>
            </form>
          </section>

          {/* Issues Feed Panel */}
          <section className="apple-card apple-card--feed">
            <div className="apple-feed-header">
              <div className="apple-feed-title">
                <h2 className="apple-card__title" style={{ margin: 0 }}>Issues Feed</h2>
                {filter !== 'ALL' && (
                  <span className="apple-tag">
                    {statusLabels[filter] || filter}
                    <button type="button" onClick={() => setFilter('ALL')} title="Clear status filter" aria-label="Clear filter">✕</button>
                  </span>
                )}
              </div>

              <div className="apple-feed-toolbar">
                <div className="apple-search">
                  <svg className="apple-search__icon" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  </svg>
                  <input
                    type="search"
                    placeholder="Search issues..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                  {search && (
                    <button type="button" className="apple-search__clear" onClick={() => setSearch('')}>✕</button>
                  )}
                </div>

                <button
                  type="button"
                  className="apple-btn-icon"
                  onClick={loadDashboard}
                  disabled={loading}
                  title="Refresh feed"
                  aria-label="Refresh feed"
                >
                  <svg className={`apple-spin ${loading ? 'is-spinning' : ''}`} width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                  </svg>
                </button>
              </div>
            </div>

            {loading && issues.length === 0 ? (
              <div className="apple-empty">
                <div className="apple-spinner"></div>
                <p>Loading issues from backend...</p>
              </div>
            ) : filteredIssues.length === 0 ? (
              <div className="apple-empty">
                <p className="apple-empty__title">
                  {search || filter !== 'ALL'
                    ? 'No matching campus issues'
                    : 'No campus issues reported yet'}
                </p>
                <p className="apple-empty__subtitle">
                  {search || filter !== 'ALL'
                    ? 'Try adjusting your search query or status filter.'
                    : 'Use the form on the left to report your first campus issue.'}
                </p>
              </div>
            ) : (
              <div className="apple-issue-list">
                {filteredIssues.map((issue) => (
                  <article key={issue.id} className="apple-issue-item">
                    <div className="apple-issue-item__header">
                      <span className="apple-issue-id">#{issue.id}</span>
                      <span className={`apple-badge apple-badge--${issue.status.toLowerCase()}`}>
                        <span className="apple-badge__dot"></span>
                        {statusLabels[issue.status] ?? issue.status}
                      </span>
                    </div>

                    <h3 className="apple-issue-title">{issue.title}</h3>
                    <p className="apple-issue-desc">{issue.description}</p>

                    <div className="apple-issue-item__footer">
                      <span className="apple-issue-time">{formatDate(issue.createdAt)}</span>

                      <div className="apple-issue-actions">
                        {/* Edit Button */}
                        <button
                          type="button"
                          className="apple-action-btn"
                          disabled={busyIssueId === issue.id}
                          onClick={() => startEdit(issue)}
                          title="Edit issue details"
                        >
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                          </svg>
                          <span>Edit</span>
                        </button>

                        {/* Delete Button */}
                        <button
                          type="button"
                          className="apple-action-btn apple-action-btn--delete"
                          disabled={busyIssueId === issue.id}
                          onClick={() => setDeletingIssue(issue)}
                          title="Delete issue"
                        >
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                          </svg>
                          <span>Delete</span>
                        </button>

                        {/* Inline Status Select Dropdown */}
                        <div className="apple-select-wrapper">
                          <select
                            value={issue.status}
                            disabled={busyIssueId === issue.id}
                            onChange={(e) => handleStatusChange(issue, e.target.value)}
                            aria-label={`Change status for issue #${issue.id}`}
                          >
                            {statuses.map((s) => (
                              <option key={s.status} value={s.status}>
                                {s.label}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>

      {/* Edit Sheet Modal (Apple Blur Sheet) */}
      {editingIssue && (
        <div className="apple-backdrop" onClick={cancelEdit}>
          <div className="apple-modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
            <div className="apple-modal__header">
              <div>
                <h3 className="apple-modal__title">Edit Issue #{editingIssue.id}</h3>
                <p className="apple-modal__subtitle">Update campus issue title, details or status</p>
              </div>
              <button type="button" className="apple-modal__close" onClick={cancelEdit} aria-label="Close dialog">✕</button>
            </div>

            <form onSubmit={handleUpdate} className="apple-form">
              <div className="apple-field">
                <label htmlFor="edit-title">Title</label>
                <input
                  id="edit-title"
                  type="text"
                  value={editForm.title}
                  minLength={3}
                  maxLength={100}
                  required
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                />
              </div>

              <div className="apple-field">
                <label htmlFor="edit-desc">Description</label>
                <textarea
                  id="edit-desc"
                  value={editForm.description}
                  minLength={5}
                  maxLength={1000}
                  required
                  rows={4}
                  onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                />
              </div>

              <div className="apple-field">
                <label htmlFor="edit-status">Status</label>
                <div className="apple-select-wrapper apple-select-wrapper--full">
                  <select
                    id="edit-status"
                    value={editForm.status}
                    onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                  >
                    {statuses.map((s) => (
                      <option key={s.status} value={s.status}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="apple-modal__actions">
                <button type="button" className="apple-btn-secondary" onClick={cancelEdit}>
                  Cancel
                </button>
                <button type="submit" className="apple-btn-primary" disabled={submitting}>
                  {submitting ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Sheet (Apple HIG Dialog) */}
      {deletingIssue && (
        <div className="apple-backdrop" onClick={() => setDeletingIssue(null)}>
          <div className="apple-modal apple-modal--confirm" onClick={(e) => e.stopPropagation()} role="alertdialog" aria-modal="true">
            <div className="apple-modal__icon apple-modal__icon--danger">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
            </div>
            <h3 className="apple-modal__title" style={{ textAlign: 'center', marginTop: 12 }}>
              Delete Issue #{deletingIssue.id}?
            </h3>
            <p className="apple-modal__subtitle" style={{ textAlign: 'center', margin: '6px 0 20px' }}>
              &ldquo;{deletingIssue.title}&rdquo; will be permanently removed. This action cannot be undone.
            </p>
            <div className="apple-modal__actions" style={{ justifyContent: 'center' }}>
              <button
                type="button"
                className="apple-btn-secondary"
                onClick={() => setDeletingIssue(null)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="apple-btn-danger"
                onClick={confirmDelete}
              >
                Delete Issue
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
