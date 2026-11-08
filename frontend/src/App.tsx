import { useMemo, useState } from 'react'
import Employees from './pages/Employees'
import Login from './pages/Login'
import { getAccessToken } from './lib/api'
import './App.css'

type NavItem = { icon: string; en: string; ur: string }
type NavGroup = { section: string; items: NavItem[] }

const navigation: NavGroup[] = [
  { section: 'MAIN MENU', items: [{ icon: '◫', en: 'Dashboard', ur: 'ڈیش بورڈ' }] },
  {
    section: 'PEOPLE MANAGEMENT',
    items: [
      { icon: '♙', en: 'Employees', ur: 'ملازمین' },
      { icon: '▦', en: 'Organization', ur: 'تنظیم' },
      { icon: '◷', en: 'Attendance', ur: 'حاضری' },
      { icon: '▤', en: 'Leave Management', ur: 'چھٹیوں کا انتظام' },
    ],
  },
  {
    section: 'FINANCE & PAYROLL',
    items: [
      { icon: '＄', en: 'Payroll', ur: 'پے رول' },
      { icon: '◈', en: 'Provident Fund', ur: 'پراویڈنٹ فنڈ' },
      { icon: '▧', en: 'EOBI & ESSI', ur: 'ای او بی آئی اور ای ایس ایس آئی' },
    ],
  },
  {
    section: 'SYSTEM',
    items: [
      { icon: '▥', en: 'Reports', ur: 'رپورٹس' },
      { icon: '⚙', en: 'Settings', ur: 'ترتیبات' },
    ],
  },
]

const activities = [
  { initials: 'AK', name: 'Ahmed Khan', action: 'New employee record created', time: '10 minutes ago', color: 'purple' },
  { initials: 'SA', name: 'Sara Ali', action: 'Leave application submitted', time: '35 minutes ago', color: 'orange' },
  { initials: 'MH', name: 'Muhammad Hassan', action: 'Attendance correction requested', time: '1 hour ago', color: 'green' },
  { initials: 'ZF', name: 'Zainab Fatima', action: 'Profile information updated', time: '2 hours ago', color: 'blue' },
]

const approvals = [
  { title: 'Leave Applications', detail: 'Awaiting HR review', count: 12, icon: '▤' },
  { title: 'Attendance Corrections', detail: 'Pending verification', count: 8, icon: '◷' },
  { title: 'Employee Changes', detail: 'Awaiting approval', count: 5, icon: '♙' },
]

function App() {
  const [activePage, setActivePage] = useState('Dashboard')
  const [darkMode, setDarkMode] = useState(false)
  const [urdu, setUrdu] = useState(false)
  const [search, setSearch] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(Boolean(getAccessToken()))

  const pageTitle = urdu
    ? navigation.flatMap((group) => group.items).find((item) => item.en === activePage)?.ur ?? activePage
    : activePage

  const filteredActivities = useMemo(
    () => activities.filter((activity) =>
      `${activity.name} ${activity.action}`.toLowerCase().includes(search.toLowerCase()),
    ),
    [search],
  )

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />
  }

  const today = new Intl.DateTimeFormat(urdu ? 'ur-PK' : 'en-PK', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: '2-digit',
  }).format(new Date())

  return (
    <div className={`app-shell ${darkMode ? 'dark' : ''}`} dir={urdu ? 'rtl' : 'ltr'}>
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">U</div>
          <div className="brand-text">
            <strong>UDL <span>HRMS</span></strong>
            <small>HUMAN RESOURCE SYSTEM</small>
          </div>
        </div>

        <div className="company-switch">
          <div className="company-icon">U</div>
          <div className="company-info">
            <strong>United Distribution</strong>
            <small>Company Workspace</small>
          </div>
          <span className="switch-arrow">⌄</span>
        </div>

        <nav className="sidebar-nav" aria-label="Main navigation">
          {navigation.map((group) => (
            <div className="nav-group" key={group.section}>
              <p className="nav-heading">{group.section}</p>
              {group.items.map((item) => (
                <button
                  className={`nav-item ${activePage === item.en ? 'active' : ''}`}
                  key={item.en}
                  onClick={() => setActivePage(item.en)}
                  type="button"
                  aria-current={activePage === item.en ? 'page' : undefined}
                >
                  <span className="nav-icon" aria-hidden="true">{item.icon}</span>
                  <span>{urdu ? item.ur : item.en}</span>
                  {item.en === 'Employees' && <span className="nav-count">—</span>}
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">?</div>
            <strong>Need assistance?</strong>
            <p>Contact your system administrator for support.</p>
            <button type="button" onClick={() => setActivePage('Help & Support')}>Get support <span>↗</span></button>
          </div>
          <div className="user-profile">
            <div className="user-avatar">SA</div>
            <div className="user-info">
              <strong>System Admin</strong>
              <small>Super Administrator</small>
            </div>
            <span className="more-button" aria-hidden="true">•••</span>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            <span>{urdu ? 'ورک اسپیس' : 'Workspace'}</span>
            <span className="crumb-divider">/</span>
            <strong>{pageTitle}</strong>
          </div>
          <div className="topbar-actions">
            <label className="search-box">
              <span aria-hidden="true">⌕</span>
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder={urdu ? 'تلاش کریں...' : 'Search activity...'}
                aria-label="Search recent activity"
              />
              <kbd>⌘ K</kbd>
            </label>
            <button className="top-icon language-button" type="button" onClick={() => setUrdu(!urdu)} title="Change language">
              {urdu ? 'EN' : 'اردو'}
            </button>
            <button className="top-icon theme-button" type="button" onClick={() => setDarkMode(!darkMode)} title="Toggle theme" aria-label="Toggle theme">
              {darkMode ? '☀' : '◐'}
            </button>
            <button className="top-icon notification-button" type="button" title="Notifications" aria-label="Notifications">
              ♧<i />
            </button>
            <div className="top-avatar">SA</div>
          </div>
        </header>

        <div className="page-content">
          {activePage === 'Dashboard' ? (
            <>
              <section className="welcome-row">
                <div>
                  <p className="eyebrow">{today.toUpperCase()}</p>
                  <h1>{urdu ? 'خوش آمدید، ایڈمن!' : 'Good day, Admin!'} <span>✦</span></h1>
                  <p className="welcome-subtitle">
                    {urdu ? 'آج آپ کی تنظیم کی صورتحال کا خلاصہ۔' : "Here's an overview of your organization's activity."}
                  </p>
                </div>
                <button className="primary-button" type="button" onClick={() => setActivePage('Employees')}>
                  <span>＋</span> {urdu ? 'نیا ملازم شامل کریں' : 'Add New Employee'}
                </button>
              </section>

              <div className="demo-banner">
                <span className="demo-banner-dot" />
                Dashboard preview · Sample figures only — live HR data is not connected yet
              </div>

              <section className="stats-grid" aria-label="Workforce summary">
                <div className="stat-card">
                  <div className="stat-top"><span>Total Employees</span><span className="stat-icon violet">♙</span></div>
                  <strong className="stat-value">—</strong>
                  <div className="stat-bottom"><span>Awaiting live data</span></div>
                </div>
                <div className="stat-card">
                  <div className="stat-top"><span>Present Today</span><span className="stat-icon green">✓</span></div>
                  <strong className="stat-value">—</strong>
                  <div className="stat-bottom"><span>Attendance integration pending</span></div>
                </div>
                <div className="stat-card">
                  <div className="stat-top"><span>On Leave</span><span className="stat-icon orange">◷</span></div>
                  <strong className="stat-value">—</strong>
                  <div className="stat-bottom"><span>Leave module integration pending</span></div>
                </div>
                <div className="stat-card">
                  <div className="stat-top"><span>Pending Approvals</span><span className="stat-icon blue">▤</span></div>
                  <strong className="stat-value">—</strong>
                  <div className="stat-bottom"><span>Approval data not connected</span></div>
                </div>
              </section>

              <section className="dashboard-grid">
                <div className="panel attendance-panel">
                  <div className="panel-header">
                    <div><h2>Attendance Overview</h2><p>Workforce attendance summary</p></div>
                    <span className="panel-tag">Coming soon</span>
                  </div>
                  <div className="empty-chart">
                    <div className="empty-chart-ring"><span>—</span></div>
                    <div><strong>Attendance data will appear here</strong><p>Connect the attendance module to view daily workforce figures.</p></div>
                  </div>
                  <div className="panel-footer"><span>Live attendance connection pending</span><button type="button" onClick={() => setActivePage('Attendance')}>Open attendance →</button></div>
                </div>

                <div className="panel approvals-panel">
                  <div className="panel-header">
                    <div><h2>Approval Categories</h2><p>Approval workflows planned for this workspace</p></div>
                    <span className="panel-tag">Preview</span>
                  </div>
                  <div className="approval-list">
                    {approvals.map((item) => (
                      <div className="approval-item" key={item.title}>
                        <span className="approval-icon">{item.icon}</span>
                        <span className="approval-copy"><strong>{item.title}</strong><small>{item.detail}</small></span>
                        <span className="approval-arrow">›</span>
                      </div>
                    ))}
                  </div>
                  <div className="panel-footer"><span>Counts will load from the backend</span><button type="button" onClick={() => setActivePage('Leave Management')}>View workflows →</button></div>
                </div>
              </section>

              <section className="panel activity-panel">
                <div className="panel-header">
                  <div><h2>Recent Activity</h2><p>Sample activity layout — not live audit records</p></div>
                  <span className="panel-tag">Sample</span>
                </div>
                <div className="activity-table">
                  <div className="activity-table-head"><span>USER</span><span>ACTIVITY</span><span>TIME</span><span>STATUS</span></div>
                  {filteredActivities.length ? filteredActivities.map((activity) => (
                    <div className="activity-row" key={activity.name}>
                      <div className="activity-user"><span className={`activity-avatar ${activity.color}`}>{activity.initials}</span><strong>{activity.name}</strong></div>
                      <span className="activity-description">{activity.action}</span>
                      <span className="activity-time">{activity.time}</span>
                      <span className="status-badge">Example</span>
                    </div>
                  )) : <p className="no-results">No sample activity matches “{search}”.</p>}
                </div>
              </section>
            </>
          ) : activePage === 'Employees' ? (
            <Employees />
          ) : (
            <section className="module-placeholder">
              <div className="placeholder-icon">{navigation.flatMap((group) => group.items).find((item) => item.en === activePage)?.icon ?? '◇'}</div>
              <p className="eyebrow">UDL HRMS WORKSPACE</p>
              <h1>{pageTitle}</h1>
              <p>This module is planned for the UDL HRMS workspace. Its screens and workflows will be developed in stages.</p>
              <button className="primary-button" type="button" onClick={() => setActivePage('Dashboard')}>← Back to Dashboard</button>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
