import { useState } from 'react'
import Employees from './pages/Employees'
import Login from './pages/Login'
import { getAccessToken } from './lib/api'
import './App.css'
const navigation = [
  { section: 'MAIN MENU', items: [{ icon: '▦', en: 'Dashboard', ur: 'ڈیش بورڈ' }] },
  {
    section: 'PEOPLE MANAGEMENT',
    items: [
      { icon: '♙', en: 'Employees', ur: 'ملازمین' },
      { icon: '▤', en: 'Organization', ur: 'تنظیم' },
      { icon: '◷', en: 'Attendance', ur: 'حاضری' },
      { icon: '▣', en: 'Leave Management', ur: 'چھٹیوں کا انتظام' },
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
  { title: 'Leave Applications', detail: 'Awaiting HR review', count: 12, icon: '▣' },
  { title: 'Attendance Corrections', detail: 'Pending verification', count: 8, icon: '◷' },
  { title: 'Employee Changes', detail: 'Awaiting approval', count: 5, icon: '♙' },
]

function App() {
  const [activePage, setActivePage] = useState('Dashboard')
  const [darkMode, setDarkMode] = useState(false)
  const [urdu, setUrdu] = useState(false)
  const [search, setSearch] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(
  Boolean(getAccessToken()),
  ) 

  const pageTitle = urdu
    ? navigation.flatMap((group) => group.items).find((item) => item.en === activePage)?.ur ?? activePage
    : activePage

  

  if (!isAuthenticated) {
  return <Login onLoginSuccess={() => setIsAuthenticated(true)} />
  }
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

        <nav className="sidebar-nav">
          {navigation.map((group) => (
            <div className="nav-group" key={group.section}>
              <p className="nav-heading">{group.section}</p>
              {group.items.map((item) => (
                <button
                  className={`nav-item ${activePage === item.en ? 'active' : ''}`}
                  key={item.en}
                  onClick={() => setActivePage(item.en)}
                  type="button"
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span>{urdu ? item.ur : item.en}</span>
                  {item.en === 'Employees' && <span className="nav-count">248</span>}
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">?</div>
            <strong>Need assistance?</strong>
            <p>Contact your system administrator.</p>
            <button type="button" onClick={() => setActivePage('Help & Support')}>Get Support ↗</button>
          </div>
          <div className="user-profile">
            <div className="user-avatar">SA</div>
            <div className="user-info">
              <strong>System Admin</strong>
              <small>Super Administrator</small>
            </div>
            <button className="more-button" type="button" aria-label="User menu">•••</button>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            <span>Workspace</span><span className="crumb-divider">/</span><strong>{pageTitle}</strong>
          </div>
          <div className="topbar-actions">
            <label className="search-box">
              <span>⌕</span>
              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder={urdu ? 'تلاش کریں...' : 'Search anything...'}
              />
              <kbd>⌘ K</kbd>
            </label>
            <button className="top-icon" type="button" onClick={() => setUrdu(!urdu)} title="Change language">
              {urdu ? 'EN' : 'اردو'}
            </button>
            <button className="top-icon theme-button" type="button" onClick={() => setDarkMode(!darkMode)} title="Toggle theme">
              {darkMode ? '☀' : '☾'}
            </button>
            <button className="top-icon notification-button" type="button" title="Notifications">
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
                  <p className="eyebrow">WEDNESDAY, NOVEMBER 04, 2026</p>
                  <h1>{urdu ? 'خوش آمدید، ایڈمن!' : 'Good afternoon, Admin!'} <span>✦</span></h1>
                  <p className="welcome-subtitle">Here&apos;s what&apos;s happening across your organization today.</p>
                </div>
                <button className="primary-button" type="button" onClick={() => setActivePage('Employees')}>
                  <span>＋</span> Add New Employee
                </button>
              </section>

              <section className="stats-grid">
                <div className="stat-card">
                  <div className="stat-top"><span>Total Employees</span><span className="stat-icon violet">♙</span></div>
                  <strong className="stat-value">248</strong>
                  <div className="stat-bottom"><span className="trend positive">↗ 8.2%</span><span>vs last month</span></div>
                </div>
                <div className="stat-card">
                  <div className="stat-top"><span>Present Today</span><span className="stat-icon green">✓</span></div>
                  <strong className="stat-value">216</strong>
                  <div className="stat-bottom"><span className="trend positive">87.1%</span><span>of total workforce</span></div>
                </div>
                <div className="stat-card">
                  <div className="stat-top"><span>On Leave</span><span className="stat-icon orange">◷</span></div>
                  <strong className="stat-value">18</strong>
                  <div className="stat-bottom"><span className="trend neutral">Today</span><span>across departments</span></div>
                </div>
                <div className="stat-card">
                  <div className="stat-top"><span>Pending Approvals</span><span className="stat-icon blue">▤</span></div>
                  <strong className="stat-value">25</strong>
                  <div className="stat-bottom"><span className="trend warning">Needs attention</span><span>across 3 categories</span></div>
                </div>
              </section>

              <section className="dashboard-grid">
                <div className="panel attendance-panel">
                  <div className="panel-header">
                    <div><h2>Attendance Overview</h2><p>Workforce attendance for today</p></div>
                    <button className="select-button" type="button">Today⌄</button>
                  </div>
                  <div className="attendance-content">
                    <div className="donut-wrap">
                      <div className="donut"><div className="donut-center"><strong>87.1%</strong><small>Present</small></div></div>
                    </div>
                    <div className="attendance-legend">
                      <div><i className="legend-dot present-dot" /><span>Present</span><strong>216</strong></div>
                      <div><i className="legend-dot leave-dot" /><span>On Leave</span><strong>18</strong></div>
                      <div><i className="legend-dot absent-dot" /><span>Absent</span><strong>10</strong></div>
                      <div><i className="legend-dot off-dot" /><span>Week Off</span><strong>4</strong></div>
                    </div>
                  </div>
                  <div className="panel-footer"><span>Last updated: 09:45 AM</span><button type="button" onClick={() => setActivePage('Attendance')}>View attendance →</button></div>
                </div>

                <div className="panel approvals-panel">
                  <div className="panel-header">
                    <div><h2>Pending Approvals</h2><p>Items that need your attention</p></div>
                    <span className="pending-total">25 pending</span>
                  </div>
                  <div className="approval-list">
                    {approvals.map((item) => (
                      <button className="approval-item" key={item.title} type="button" onClick={() => setActivePage(item.title)}>
                        <span className="approval-icon">{item.icon}</span>
                        <span className="approval-copy"><strong>{item.title}</strong><small>{item.detail}</small></span>
                        <strong className="approval-count">{item.count}</strong>
                        <span className="approval-arrow">›</span>
                      </button>
                    ))}
                  </div>
                  <div className="panel-footer"><span>Across all departments</span><button type="button" onClick={() => setActivePage('Approvals')}>View all →</button></div>
                </div>
              </section>

              <section className="panel activity-panel">
                <div className="panel-header">
                  <div><h2>Recent Activity</h2><p>Latest updates from your organization</p></div>
                  <button className="text-button" type="button" onClick={() => setActivePage('Activity Log')}>View activity log →</button>
                </div>
                <div className="activity-table">
                  <div className="activity-table-head"><span>USER</span><span>ACTIVITY</span><span>TIME</span><span>STATUS</span></div>
                  {activities.filter((activity) => `${activity.name} ${activity.action}`.toLowerCase().includes(search.toLowerCase())).map((activity) => (
                    <div className="activity-row" key={activity.name}>
                      <div className="activity-user"><span className={`activity-avatar ${activity.color}`}>{activity.initials}</span><strong>{activity.name}</strong></div>
                      <span className="activity-description">{activity.action}</span>
                      <span className="activity-time">{activity.time}</span>
                      <span className="status-badge">Completed</span>
                    </div>
                  ))}
                </div>
              </section>
              <p className="demo-note">Dashboard preview · Sample data for interface demonstration</p>
            </>
          ) : activePage === 'Employees' ? (
            <Employees />
          ) : (
            <section className="module-placeholder">
              <div className="placeholder-icon">▦</div>
              <p className="eyebrow">UDL HRMS WORKSPACE</p>
              <h1>{pageTitle}</h1>
              <p>This module is part of the planned HRMS interface. Its functionality will be developed in the next stages.</p>
              <button
                className="primary-button"
                type="button"
                onClick={() => setActivePage('Dashboard')}
              >
                ← Back to Dashboard
              </button>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}

export default App