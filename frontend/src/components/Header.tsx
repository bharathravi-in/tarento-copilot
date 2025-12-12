import { useState, useRef, useEffect } from 'react'
import type { FC } from 'react'
import { useNavigate } from 'react-router-dom'
import { authService } from '../services/authService'
import { logger } from '../utils/logger'
import './Header.css'

interface HeaderProps {
  title?: string
  showSidebar?: boolean
  onSidebarToggle?: () => void
}

export const Header: FC<HeaderProps> = ({
  title = 'Dashboard',
  showSidebar = true,
  onSidebarToggle,
}) => {
  const navigate = useNavigate()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const user = authService.getCurrentUser()

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = async () => {
    try {
      await authService.logout()
      navigate('/login')
      logger.info('User logged out')
    } catch (error) {
      logger.error('Logout failed', error)
    }
  }

  const handleProfileClick = () => {
    setDropdownOpen(false)
    navigate('/profile')
  }

  const handleOrgClick = () => {
    setDropdownOpen(false)
    navigate('/organization')
  }

  return (
    <header className="header">
      <div className="header-left">
        {showSidebar && (
          <button
            className="sidebar-toggle"
            onClick={onSidebarToggle}
            title="Toggle sidebar"
          >
            ☰
          </button>
        )}
        <h1 className="header-title">{title}</h1>
      </div>

      <div className="header-right">
        {/* Search Bar */}
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search documents, conversations..."
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>

        {/* User Dropdown */}
        <div className="user-dropdown-container" ref={dropdownRef}>
          <button
            className="user-button"
            onClick={() => setDropdownOpen(!dropdownOpen)}
          >
            <div className="user-avatar-header">
              {(user?.full_name || 'U').charAt(0).toUpperCase()}
            </div>
            <div className="user-info">
              <div className="user-name">{user?.full_name || 'User'}</div>
              <div className="user-email">{user?.email || 'No email'}</div>
            </div>
            <span className={`dropdown-arrow ${dropdownOpen ? 'open' : ''}`}>
              ▼
            </span>
          </button>

          {/* Dropdown Menu */}
          {dropdownOpen && (
            <div className="dropdown-menu">
              <div className="dropdown-header">
                <div className="dropdown-user-info">
                  <div className="dropdown-avatar">
                    {(user?.full_name || 'U').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="dropdown-name">{user?.full_name || 'User'}</div>
                    <div className="dropdown-role">{user?.role || 'No role'}</div>
                  </div>
                </div>
              </div>

              <div className="dropdown-divider"></div>

              <button
                className="dropdown-item"
                onClick={handleProfileClick}
              >
                <span className="dropdown-icon">👤</span>
                <span>Profile Settings</span>
              </button>

              <button
                className="dropdown-item"
                onClick={handleOrgClick}
              >
                <span className="dropdown-icon">🏢</span>
                <span>Organization</span>
              </button>

              <div className="dropdown-divider"></div>

              <button
                className="dropdown-item logout"
                onClick={handleLogout}
              >
                <span className="dropdown-icon">🚪</span>
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Header
