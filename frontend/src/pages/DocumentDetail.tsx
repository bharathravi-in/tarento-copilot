import { useEffect, useState } from 'react'
import type { FC } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiClient } from '../services/apiClient'
import { API_ENDPOINTS } from '../config'
import { logger } from '../utils/logger'
import type { Document } from '../types/api'
import { PDFViewer } from '../components/PDFViewer'
import './DocumentDetail.css'

// Helper to check if content is a file reference (not actual content)
const isFileReference = (content: string): boolean => {
  return content.trim().startsWith('[') && (
    content.includes('File:') || 
    content.includes('Binary file:')
  )
}

// Helper to check if document is a PDF
const isPDF = (documentType: string, mimeType?: string): boolean => {
  return documentType.toLowerCase() === 'pdf' || 
         (mimeType?.toLowerCase().includes('pdf') ?? false)
}

// Helper to determine if content should be rendered as markdown
const isMarkdown = (documentType: string): boolean => {
  return documentType.toLowerCase().includes('md') || 
         documentType.toLowerCase().includes('markdown')
}

// Helper to render markdown as HTML
const renderMarkdown = (content: string): string => {
  let html = content
    // Headers
    .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
    .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
    .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/_(.*?)_/g, '<em>$1</em>')
    // Code blocks
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // Inline code
    .replace(/`(.*?)`/g, '<code>$1</code>')
    // Links
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')

  return `<div class="markdown-content"><p>${html}</p></div>`
}

export const DocumentDetail: FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [document, setDocument] = useState<Document | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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
      logger.info('Document fetched successfully', { docType: response.data.document_type })
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to fetch document'
      setError(errorMsg)
      logger.error('Failed to fetch document', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="document-detail-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading document...</p>
        </div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="document-detail-page">
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <h3>Document Not Found</h3>
          <p>{error || 'The document you are looking for does not exist'}</p>
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
    <div className="document-detail-page">
      <div className="detail-header">
        <button 
          className="btn-back"
          onClick={() => navigate('/documents')}
          title="Back to documents"
        >
          ← Back
        </button>
        <div className="header-content">
          <h1>{document.title}</h1>
          <p className="meta-info">
            <span>Created: {new Date(document.created_at).toLocaleDateString()}</span>
            <span>Updated: {new Date(document.updated_at).toLocaleDateString()}</span>
            {document.document_type && (
              <span className="doc-type-badge">{document.document_type.toUpperCase()}</span>
            )}
          </p>
        </div>
        <button 
          className="btn-primary"
          onClick={() => navigate(`/documents/${document.id}/edit`)}
        >
          ✏️ Edit
        </button>
      </div>

      <div className="detail-content">
        {document.summary && (
          <section className="summary-section">
            <h2>Summary</h2>
            <p className="summary-text">{document.summary}</p>
          </section>
        )}

        {document.tags && document.tags.length > 0 && (
          <section className="tags-section">
            <h3>Tags</h3>
            <div className="tags-list">
              {document.tags.map((tag, idx) => (
                <span key={idx} className="tag">{tag}</span>
              ))}
            </div>
          </section>
        )}

        {document.source && (
          <section className="source-section">
            <h3>Source</h3>
            <p className="source-text">{document.source}</p>
          </section>
        )}

        {document.content && (
          <section className="content-section">
            <h2>
              Document Content
              {document.file_name && <span className="file-name">({document.file_name})</span>}
            </h2>
            {isPDF(document.document_type, document.mime_type) ? (
              <div className="pdf-viewer-section">
                <PDFViewer 
                  filePath={API_ENDPOINTS.documents.download(document.id)}
                  fileName={document.file_name}
                />
              </div>
            ) : isFileReference(document.content) ? (
              <div className="binary-file-notice">
                <div className="file-icon">📄</div>
                <h3>Binary File - Not Displayable as Text</h3>
                <p>
                  This is a <strong>{document.document_type?.toUpperCase() || 'binary'}</strong> file.
                </p>
                <div className="file-info">
                  <p><strong>File Name:</strong> {document.file_name || 'Unknown'}</p>
                  {document.mime_type && <p><strong>File Type:</strong> {document.mime_type}</p>}
                  {document.file_path && <p><strong>Location:</strong> {document.file_path}</p>}
                </div>
                <p className="file-hint">
                  The file has been uploaded and indexed for search. Use the summary above for an overview of the document content.
                </p>
              </div>
            ) : isMarkdown(document.document_type) ? (
              <div 
                className="content-text markdown-render"
                dangerouslySetInnerHTML={{ __html: renderMarkdown(document.content) }}
              />
            ) : (
              <div className="content-text">
                {document.content}
              </div>
            )}
          </section>
        )}

        {!document.content && !document.summary && (
          <div className="empty-content">
            <p>No content available for this document</p>
          </div>
        )}
      </div>
    </div>
  )
}
