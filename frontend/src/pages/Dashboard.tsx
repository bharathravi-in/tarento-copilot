import { FC, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authService } from '../services/authService'
import { logger } from '../utils/logger'
import './Dashboard.css'

interface DashboardStats {
  documents: number
  conversations: number
  agents: number
  lastActivity: string
}

export const Dashboard: FC = () => {
  const user = authService.getCurrentUser()
  const navigate = useNavigate()
  const [stats, setStats] = useState<DashboardStats>({
    documents: 0,
    conversations: 0,
    agents: 0,
    lastActivity: 'Just now',
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate loading stats from API
    const timer = setTimeout(() => {
      setStats({
        documents: 24,
        conversations: 8,
        agents: 3,
        lastActivity: 'Today at 2:30 PM',
      })
      setLoading(false)
    }, 500)

    return () => clearTimeout(timer)
  }, [])

  const handleQuickAction = (action: string) => {
    logger.info('Quick action clicked', { action })
    switch (action) {
      case 'new-conversation':
        navigate('/conversations')
        break
      case 'upload-document':
        navigate('/documents')
        break
      case 'create-agent':
        navigate('/agents')
        break
      case 'search':
        navigate('/search')
        break
      default:
        break
    }
  }

  return (
    <div className="dashboard-page">
      {/* Welcome Section */}
      <section className="welcome-section">
        <div className="welcome-content">
          <h1>Welcome back, {user?.full_name}! 👋</h1>
          <p>
            Here's what's happening with your Tarento Copilot workspace today.
          </p>
        </div>
        <div className="welcome-badge">
          <span className="badge-icon">⭐</span>
          <span className="badge-text">Pro Account</span>
        </div>
      </section>

      {/* Quick Stats */}
      <section className="stats-section">
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📄</div>
            <div className="stat-content">
              <h3>Documents</h3>
              <p className="stat-value">{loading ? '...' : stats.documents}</p>
              <span className="stat-label">in workspace</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">💬</div>
            <div className="stat-content">
              <h3>Conversations</h3>
              <p className="stat-value">
                {loading ? '...' : stats.conversations}
              </p>
              <span className="stat-label">active chats</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🤖</div>
            <div className="stat-content">
              <h3>Agents</h3>
              <p className="stat-value">{loading ? '...' : stats.agents}</p>
              <span className="stat-label">configured</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⚡</div>
            <div className="stat-content">
              <h3>Last Activity</h3>
              <p className="stat-value" style={{ fontSize: '14px' }}>
                {stats.lastActivity}
              </p>
              <span className="stat-label">today</span>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="quick-actions-section">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <button
            className="action-card"
            onClick={() => handleQuickAction('new-conversation')}
          >
            <div className="action-icon">💬</div>
            <h3>New Conversation</h3>
            <p>Start a chat with the AI assistant</p>
          </button>

          <button
            className="action-card"
            onClick={() => handleQuickAction('upload-document')}
          >
            <div className="action-icon">📄</div>
            <h3>Upload Document</h3>
            <p>Add a document to your workspace</p>
          </button>

          <button
            className="action-card"
            onClick={() => handleQuickAction('create-agent')}
          >
            <div className="action-icon">🤖</div>
            <h3>Create Agent</h3>
            <p>Configure a new AI agent</p>
          </button>

          <button
            className="action-card"
            onClick={() => handleQuickAction('search')}
          >
            <div className="action-icon">🔍</div>
            <h3>Search</h3>
            <p>Find documents and conversations</p>
          </button>
        </div>
      </section>

      {/* Recent Activity */}
      <section className="recent-activity-section">
        <h2>Recent Activity</h2>
        <div className="activity-list">
          <div className="activity-item">
            <div className="activity-icon">📄</div>
            <div className="activity-content">
              <h4>Document uploaded</h4>
              <p>You uploaded "Q4 Report.pdf"</p>
              <span className="activity-time">2 hours ago</span>
            </div>
          </div>

          <div className="activity-item">
            <div className="activity-icon">💬</div>
            <div className="activity-content">
              <h4>Conversation started</h4>
              <p>You started a new conversation with AI Assistant</p>
              <span className="activity-time">5 hours ago</span>
            </div>
          </div>

          <div className="activity-item">
            <div className="activity-icon">🤖</div>
            <div className="activity-content">
              <h4>Agent executed</h4>
              <p>Your "Analysis Agent" executed successfully</p>
              <span className="activity-time">1 day ago</span>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="features-section">
        <h2>Featured Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3>AI-Powered Search</h3>
            <p>
              Semantic search across all your documents using advanced AI models
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Document Analysis</h3>
            <p>
              Get insights and summaries from your documents automatically
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔗</div>
            <h3>RAG Pipeline</h3>
            <p>
              Retrieval-Augmented Generation for enhanced AI responses
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Dashboard
