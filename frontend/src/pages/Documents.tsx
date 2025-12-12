import type { FC } from 'react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../services/apiClient'
import { API_ENDPOINTS } from '../config'
import { logger } from '../utils/logger'
import type { Document, ListResponse } from '../types/api'
import './Documents.css'

interface DocumentsState {
  documents: Document[]
  total: number
  loading: boolean
  error: string | null
  searchTerm: string
  filterType: string
  sortBy: 'date' | 'title'
  sortOrder: 'asc' | 'desc'
}

export const Documents: FC = () => {
  const navigate = useNavigate()
  const [state, setState] = useState<DocumentsState>({
    documents: [],
    total: 0,
    loading: true,
    error: null,
    searchTerm: '',
    filterType: 'all',
    sortBy: 'date',
    sortOrder: 'desc',
  })

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [pagination, setPagination] = useState({ skip: 0, limit: 10 })

  // Fetch documents
  useEffect(() => {
    fetchDocuments()
  }, [pagination.skip, state.filterType, state.sortBy, state.sortOrder])

  const fetchDocuments = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }))
      
      const response = await apiClient.get<ListResponse<Document>>(
        API_ENDPOINTS.documents.list,
        {
          params: {
            skip: pagination.skip,
            limit: pagination.limit,
            search: state.searchTerm || undefined,
            document_type: state.filterType !== 'all' ? state.filterType : undefined,
          },
        }
      )

      setState(prev => ({
        ...prev,
        documents: response.data.data || [],
        total: response.data.total || 0,
        loading: false,
      }))

      logger.info('Documents fetched successfully')
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to fetch documents'
      setState(prev => ({ ...prev, error: errorMsg, loading: false }))
      logger.error('Failed to fetch documents', error)
    }
  }

  const handleSearch = (term: string) => {
    setState(prev => ({ ...prev, searchTerm: term }))
    setPagination({ skip: 0, limit: 10 })
  }

  const handleFilterChange = (type: string) => {
    setState(prev => ({ ...prev, filterType: type }))
    setPagination({ skip: 0, limit: 10 })
  }

  const handleSort = (sortBy: 'date' | 'title') => {
    if (state.sortBy === sortBy) {
      setState(prev => ({
        ...prev,
        sortOrder: prev.sortOrder === 'asc' ? 'desc' : 'asc',
      }))
    } else {
      setState(prev => ({
        ...prev,
        sortBy,
        sortOrder: 'desc',
      }))
    }
  }

  const handleDocumentClick = (docId: string) => {
    navigate(`/documents/${docId}`)
  }

  const handleDeleteDocument = async (docId: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return

    try {
      await apiClient.delete(API_ENDPOINTS.documents.delete(docId))
      logger.info('Document deleted successfully')
      fetchDocuments()
    } catch (error) {
      logger.error('Failed to delete document', error)
      setState(prev => ({ ...prev, error: 'Failed to delete document' }))
    }
  }

  const sortedDocuments = [...state.documents].sort((a, b) => {
    const compareValue = state.sortBy === 'title' 
      ? a.title.localeCompare(b.title)
      : new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    
    return state.sortOrder === 'asc' ? compareValue : -compareValue
  })

  const totalPages = Math.ceil(state.total / pagination.limit)
  const currentPage = Math.floor(pagination.skip / pagination.limit) + 1

  return (
    <div className="documents-page">
      {/* Header */}
      <div className="documents-header">
        <div className="documents-title">
          <h1>📄 Documents</h1>
          <p>Manage and search your documents</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            className="btn-primary"
            onClick={() => {
              setPagination({ skip: 0, limit: 10 })
              fetchDocuments()
            }}
            style={{ opacity: state.loading ? 0.6 : 1, cursor: state.loading ? 'not-allowed' : 'pointer' }}
            disabled={state.loading}
            title="Refresh documents list"
          >
            🔄 Refresh
          </button>
          <button 
            className="btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            + New Document
          </button>
        </div>
      </div>

      {/* Search & Filter Section */}
      <div className="documents-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search documents..."
            value={state.searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>

        <div className="filter-group">
          <select
            value={state.filterType}
            onChange={(e) => handleFilterChange(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Types</option>
            <option value="pdf">PDF</option>
            <option value="text">Text</option>
            <option value="markdown">Markdown</option>
            <option value="code">Code</option>
          </select>
        </div>
      </div>

      {/* Error Message */}
      {state.error && (
        <div className="error-banner">
          <span>⚠️</span>
          <span>{state.error}</span>
          <button onClick={() => setState(prev => ({ ...prev, error: null }))}>✕</button>
        </div>
      )}

      {/* Documents Table */}
      {state.loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading documents...</p>
        </div>
      ) : state.documents.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h3>No documents found</h3>
          <p>Create your first document to get started</p>
          <button 
            className="btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            Create Document
          </button>
        </div>
      ) : (
        <>
          <div className="documents-table-wrapper">
            <table className="documents-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('title')} className="sortable">
                    Title {state.sortBy === 'title' && (state.sortOrder === 'asc' ? '↑' : '↓')}
                  </th>
                  <th>Summary</th>
                  <th>Tags</th>
                  <th onClick={() => handleSort('date')} className="sortable">
                    Created {state.sortBy === 'date' && (state.sortOrder === 'asc' ? '↑' : '↓')}
                  </th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedDocuments.map((doc) => (
                  <tr key={doc.id} className="table-row">
                    <td className="cell-title">
                      <div 
                        className="title-link"
                        onClick={() => handleDocumentClick(doc.id)}
                      >
                        <span className="doc-icon">📋</span>
                        <span className="title-text">{doc.title}</span>
                      </div>
                    </td>
                    <td className="cell-summary">
                      <span className="summary-text">
                        {doc.summary ? doc.summary.substring(0, 60) + '...' : 'No summary'}
                      </span>
                    </td>
                    <td className="cell-tags">
                      <div className="tags-container">
                        {doc.tags && doc.tags.length > 0 ? (
                          doc.tags.slice(0, 2).map((tag, idx) => (
                            <span key={idx} className="tag">{tag}</span>
                          ))
                        ) : (
                          <span className="no-tags">—</span>
                        )}
                        {doc.tags && doc.tags.length > 2 && (
                          <span className="tag-more">+{doc.tags.length - 2}</span>
                        )}
                      </div>
                    </td>
                    <td className="cell-date">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="cell-actions">
                      <button
                        className="btn-action btn-view"
                        onClick={() => handleDocumentClick(doc.id)}
                        title="View"
                      >
                        👁️
                      </button>
                      <button
                        className="btn-action btn-edit"
                        onClick={() => navigate(`/documents/${doc.id}/edit`)}
                        title="Edit"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-action btn-delete"
                        onClick={() => handleDeleteDocument(doc.id)}
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="pagination">
            <button
              disabled={currentPage === 1}
              onClick={() => setPagination({ ...pagination, skip: pagination.skip - pagination.limit })}
              className="pagination-btn"
            >
              ← Previous
            </button>
            <span className="pagination-info">
              Page {currentPage} of {totalPages} ({state.total} total)
            </span>
            <button
              disabled={currentPage === totalPages}
              onClick={() => setPagination({ ...pagination, skip: pagination.skip + pagination.limit })}
              className="pagination-btn"
            >
              Next →
            </button>
          </div>
        </>
      )}

      {/* Create Document Modal */}
      {showCreateModal && (
        <CreateDocumentModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            // Reset pagination and refresh
            setPagination({ skip: 0, limit: 10 })
            setState(prev => ({ ...prev, documents: [], total: 0 }))
            setTimeout(() => fetchDocuments(), 100)
          }}
        />
      )}
    </div>
  )
}

// Create Document Modal Component
interface CreateDocumentModalProps {
  onClose: () => void
  onSuccess: () => void
}

const CreateDocumentModal: FC<CreateDocumentModalProps> = ({ onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    content: '',
    document_type: 'text',
    tags: '',
    is_public: false,
  })

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as any
    const newValue = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    setFormData(prev => ({ ...prev, [name]: newValue }))
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      // Auto-fill document type based on file extension
      const ext = selectedFile.name.split('.').pop()?.toLowerCase() || ''
      const typeMap: Record<string, string> = {
        'pdf': 'pdf',
        'txt': 'text',
        'md': 'markdown',
        'py': 'code',
        'js': 'code',
        'ts': 'code',
        'jsx': 'code',
        'tsx': 'code',
        'json': 'code',
        'yaml': 'code',
        'yml': 'code',
        'html': 'code',
        'css': 'code',
        'docx': 'docx',
        'doc': 'docx',
      }
      const detectedType = typeMap[ext] || 'text'
      setFormData(prev => ({ ...prev, document_type: detectedType }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (!formData.title.trim()) {
        setError('Title is required')
        setLoading(false)
        return
      }

      // Use file upload endpoint if file is selected
      if (file) {
        const formDataToSend = new FormData()
        formDataToSend.append('title', formData.title.trim())
        formDataToSend.append('description', formData.description.trim() || '')
        formDataToSend.append('file', file)
        formDataToSend.append('is_public', String(formData.is_public))
        
        if (formData.tags.trim()) {
          formDataToSend.append('tags', formData.tags)
        }

        logger.info('Uploading document with file:', file.name)
        const response = await apiClient.post(API_ENDPOINTS.documents.upload, formDataToSend)
        logger.info('Document uploaded successfully', response.data)
      } else {
        // Use regular create endpoint for text-only documents
        let content = formData.content.trim()

        if (!content) {
          setError('Please enter content or upload a file')
          setLoading(false)
          return
        }

        const payload = {
          title: formData.title.trim(),
          description: formData.description.trim() || undefined,
          content: content,
          document_type: formData.document_type,
          is_public: formData.is_public,
          tags: formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(t => t) : [],
          doc_metadata: {
            source_type: 'manual_entry',
          },
        }

        logger.info('Creating document with text content')
        const response = await apiClient.post(API_ENDPOINTS.documents.create, payload)
        logger.info('Document created successfully', response.data)
      }

      onSuccess()
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to create document'
      setError(errorMsg)
      logger.error('Failed to create document', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Document</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-form">
          {error && <div className="form-error">{error}</div>}

          <div className="form-group">
            <label>Title *</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="Document title"
              required
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Brief description or summary"
              rows={2}
            ></textarea>
          </div>

          <div className="form-group">
            <label>Document Type *</label>
            <select
              name="document_type"
              value={formData.document_type}
              onChange={handleInputChange}
            >
              <option value="text">Text</option>
              <option value="pdf">PDF</option>
              <option value="docx">Word Document</option>
              <option value="markdown">Markdown</option>
              <option value="code">Code</option>
              <option value="url">URL</option>
            </select>
          </div>

          <div className="form-group">
            <label>Upload File (Optional)</label>
            <div className="file-input-wrapper">
              <input
                type="file"
                onChange={handleFileChange}
                accept=".txt,.pdf,.md,.py,.js,.ts,.jsx,.tsx,.json,.yaml,.yml,.html,.css,.docx,.doc"
                disabled={loading}
              />
              {file && (
                <div className="file-info">
                  <span className="file-icon">📎</span>
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">({(file.size / 1024).toFixed(2)} KB)</span>
                </div>
              )}
            </div>
          </div>

          <div className="form-group">
            <label>Content {file ? '(Optional - file will be used)' : '*'}</label>
            <textarea
              name="content"
              value={formData.content}
              onChange={handleInputChange}
              placeholder="Document content (or upload a file above)"
              rows={6}
            ></textarea>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>Tags (comma-separated)</label>
              <input
                type="text"
                name="tags"
                value={formData.tags}
                onChange={handleInputChange}
                placeholder="e.g., api, documentation, research"
              />
            </div>

            <div className="form-group flex-1">
              <label>Visibility</label>
              <div className="checkbox-group">
                <input
                  type="checkbox"
                  name="is_public"
                  checked={formData.is_public}
                  onChange={handleInputChange}
                  id="is_public"
                />
                <label htmlFor="is_public">Make Public</label>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Document'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Documents
