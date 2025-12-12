import { useState } from 'react'
import type { FC, ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { Header } from './Header'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
  title?: string
  showHeader?: boolean
  showSidebar?: boolean
}

export const Layout: FC<LayoutProps> = ({
  children,
  title = 'Dashboard',
  showHeader = true,
  showSidebar = true,
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleSidebarToggle = () => {
    if (window.innerWidth <= 768) {
      setSidebarOpen(!sidebarOpen)
    } else {
      setSidebarCollapsed(!sidebarCollapsed)
    }
  }

  return (
    <div className="layout">
      {showSidebar && (
        <Sidebar collapsed={sidebarCollapsed} />
      )}

      <div
        className={`layout-main ${
          sidebarCollapsed ? 'sidebar-collapsed' : ''
        }`}
      >
        {showHeader && (
          <Header
            title={title}
            showSidebar={showSidebar}
            onSidebarToggle={handleSidebarToggle}
          />
        )}

        <main className="layout-content">{children}</main>
      </div>
    </div>
  )
}

export default Layout
