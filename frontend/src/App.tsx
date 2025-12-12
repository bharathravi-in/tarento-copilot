import { useEffect, useState } from 'react'
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from 'react-router-dom'
import './App.css'
import { authService } from './services/authService'
import { logger } from './utils/logger'
import { config } from './config'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Layout } from './components/Layout'
import Dashboard from './pages/Dashboard'
import { Documents } from './pages/Documents'
import { DocumentDetail } from './pages/DocumentDetail'
import { DocumentEdit } from './pages/DocumentEdit'
import {
  Conversations,
  Agents,
  Search,
  Profile,
  Organization,
} from './pages'

// Initialize logger
logger.setLogLevel(config.app.logLevel)

function App() {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is already authenticated
    const currentUser = authService.getCurrentUser()
    if (currentUser && authService.isAuthenticated()) {
      logger.info('User session restored', { userId: currentUser.id })
    }
    setIsLoading(false)
  }, [])

  if (isLoading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <Router>
      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected Routes with Layout */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/conversations" element={<Conversations />} />
                  <Route path="/documents" element={<Documents />} />
                  <Route path="/documents/:id" element={<DocumentDetail />} />
                  <Route path="/documents/:id/edit" element={<DocumentEdit />} />
                  <Route path="/agents" element={<Agents />} />
                  <Route path="/search" element={<Search />} />
                  <Route path="/profile" element={<Profile />} />
                  <Route path="/organization" element={<Organization />} />
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  )
}

// Login Page Component
function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await authService.login({ username, password })
      navigate('/dashboard')
      logger.info('Login successful')
    } catch (err) {
      setError('Login failed. Please check your credentials.')
      logger.error('Login error', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      {/* Left Side - Branding & Info */}
      <div className="login-left">
        <div className="login-branding">
          <div className="logo-large">TC</div>
          <h1>Tarento Copilot</h1>
          <p>AI-Powered Knowledge Assistant</p>
        </div>
        
        <div className="login-features">
          <div className="feature-item">
            <span className="feature-icon">🚀</span>
            <div>
              <h3>Instant Search</h3>
              <p>Find answers across all documents instantly</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🤖</span>
            <div>
              <h3>AI Agents</h3>
              <p>Deploy intelligent agents for automation</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">💬</span>
            <div>
              <h3>Smart Conversations</h3>
              <p>Context-aware chat powered by RAG</p>
            </div>
          </div>
        </div>

        <div className="login-footer-info">
          <p>© 2024 Tarento. All rights reserved.</p>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="login-right">
        <div className="login-card">
          <div className="login-header">
            <h2>Welcome Back</h2>
            <p>Sign in to your account to continue</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {/* Username Field */}
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <div className="input-wrapper">
                <span className="input-icon">👤</span>
                <input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="input-wrapper">
                <span className="input-icon">🔐</span>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="show-password-btn"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading}
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? '👁️' : '👁️‍🗨️'}
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                <span>{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              className="login-button"
              disabled={isLoading || !username || !password}
            >
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default App

