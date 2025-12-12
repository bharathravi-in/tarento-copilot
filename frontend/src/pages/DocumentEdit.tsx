import { useEffect, useState } from 'react'
import type { FC } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiClient } from '../services/apiClient'
import { API_ENDPOINTS } from '../config'
import { logger } from '../utils/logger'
import type { Document } from '../types/api'
import './DocumentEdit.css'

interface EditFormData {
  title: string
  summary: string
  content: string
  tags: string
}

export const DocumentEdit: FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [document, setDocument] = useState<Document | null>(null)
  const [formData, setFormData] = useState<EditFormData>({
    title: '',
    summary: '',
    content: '',
    tags: '',
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    if (!id) {
      navigate('/documents')
      return
    }
    
    fetchDocument()
  }, [id, navigate])

  const fetchDocument = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await apiClient.get<Document>(
        API_ENDPOINTS.documents.get(id!)
      )
      
      setDocument(response.data)
      setFormData({
        title: response.data.title || '',
        summary: response.data.summary || '',
        content: response.data.content || '',
        tags: (response.data.tags || []).join(', '),
      })
      logger.info('Document fetched successfully')
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to fetch document'
      setError(errorMsg)
      logger.error('Failed to fetch document', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)
      setSuccess(null)

      if (!formData.title.trim()) {
        setError('Title is required')
        return
      }

      const updatePayload = {
        title: formData.title.trim(),
        summary: formData.summary.trim(),
        content: formData.content.trim(),
        tags: formData.tags
          .split(',')
          .map(tag => tag.trim())
          .filter(tag => tag.length > 0),
      }

      await apiClient.put(
        API_ENDPOINTS.documents.update(id!),
        updatePayload
      )

      setSuccess('Document updated successfully!')
      logger.info('Document updated successfully')
      
      // Refresh document
      await fetchDocument()
      
      // Redirect after success
      setTimeout(() => {
        navigate(`/documents/${id}`)
      }, 1500)
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to update document'
      setError(errorMsg)
      logger.error('Failed to update document', error)
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="document-edit-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading document...</p>
        </div>
      </div>
    )
  }

  if (!document) {
    return (
      <div className="document-edit-page">
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <h3>Document Not Found</h3>
          <p>The document you are trying to edit does not exist</p>
          <button 
            className="btn-primary"
            onClick={() => navigate('/documents')}
          >
            ← Back to Documents
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="document-edit-page">
      <div className="edit-header">
        <button 
          className="btn-back"
          onClick={() => navigate(`/documents/${id}`)}
          title="Back to document"
        >
          ← Back
        </button>
        <h1>Edit Document</h1>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {success && (
        <div className="success-banner">
          <span>✅</span>
          <span>{success}</span>
        </div>
      )}

      <form className="edit-form">
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            id="title"
            type="text"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            placeholder="Enter document title"
            disabled={saving}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="summary">Summary</label>
          <textarea
            id="summary"
            name="summary"
            value={formData.summary}
            onChange={handleInputChange}
            placeholder="Enter a brief summary"
            rows={3}
            disabled={saving}
          />
        </div>

        <div className="form-group">
          <label htmlFor="content">Content</label>
          <textarea
            id="content"
            name="content"
            value={formData.content}
            onChange={handleInputChange}
            placeholder="Enter document content"
            rows={10}
            disabled={saving}
          />
        </div>

        <div className="form-group">
          <label htmlFor="tags">Tags (comma-separated)</label>
          <input
            id="tags"
            type="text"
            name="tags"
            value={formData.tags}
            onChange={handleInputChange}
            placeholder="e.g., important, review, archived"
            disabled={saving}
          />
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={() => navigate(`/documents/${id}`)}
            disabled={saving}
          >
            Cancel
          </button>
          <button
            type="button"
            className="btn-primary"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? '💾 Saving...' : '💾 Save Changes'}
          </button>
        </div>
      </form>
    </div>
  )
}
