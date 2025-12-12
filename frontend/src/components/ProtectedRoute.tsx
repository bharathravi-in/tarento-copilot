import { FC, ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { authService } from '../services/authService'

interface ProtectedRouteProps {
  children: ReactNode
}

/**
 * ProtectedRoute component that ensures user is authenticated
 * before accessing the route. Redirects to login if not authenticated.
 */
export const ProtectedRoute: FC<ProtectedRouteProps> = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

export default ProtectedRoute
