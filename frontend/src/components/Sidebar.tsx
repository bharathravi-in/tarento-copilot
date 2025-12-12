import { FC, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { authService } from '../services/authService'
import './Sidebar.css'

interface NavItem {
  label: string
  icon: string
  path: string
  badge?: number
}

const NAV_SECTIONS = [
  {
    title: 'Main',
    items: [
      { label: 'Dashboard', icon: '📊', path: '/dashboard' },
      { label: 'Conversations', icon: '💬', path: '/conversations' },
    ],
  },
  {
    title: 'Intelligence',
    items: [
      { label: 'Documents', icon: '📄', path: '/documents' },
      { label: 'Agents', icon: '🤖', path: '/agents' },
      { label: 'Search', icon: '🔍', path: '/search' },
    ],
  },
  {
    title: 'Settings',
    items: [
      { label: 'Organization', icon: '🏢', path: '/organization' },
      { label: 'Profile', icon: '👤', path: '/profile' },
    ],
  },
]

interface SidebarProps {
  collapsed?: boolean
  onToggle?: () => void
}

export const Sidebar: FC<SidebarProps> = ({ collapsed = false, onToggle }) => {
  const navigate = useNavigate()
  const user = authService.getCurrentUser()

  const handleNavigation = (path: string) => {
    navigate(path)
  }

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Logo Section */}
      <div className="sidebar-logo">
        <div className="logo-icon">TC</div>
        {!collapsed && <span className="logo-text">Tarento</span>}
      </div>

      {/* Navigation Sections */}
      <nav className="sidebar-nav">
        {NAV_SECTIONS.map((section) => (
          <div key={section.title} className="nav-section">
            {!collapsed && <h3 className="nav-section-title">{section.title}</h3>}
            <ul className="nav-items">
              {section.items.map((item) => (
                <li key={item.path}>
                  <button
                    className="nav-item"
                    onClick={() => handleNavigation(item.path)}
                    title={item.label}
                  >
                    <span className="nav-icon">{item.icon}</span>
                    {!collapsed && (
                      <>
                        <span className="nav-label">{item.label}</span>
                        {item.badge && (
                          <span className="nav-badge">{item.badge}</span>
                        )}
                      </>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      {/* User Info Section */}
      {!collapsed && user && (
        <div className="sidebar-footer">
          <div className="user-mini">
            <div className="user-avatar">{(user.full_name || 'U').charAt(0).toUpperCase()}</div>
            <div className="user-name-mini">{user.full_name || 'User'}</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Sidebar
