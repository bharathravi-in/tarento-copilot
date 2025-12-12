import { useEffect, useState, useRef } from 'react'
import type { FC } from 'react'
import * as pdfjsLib from 'pdfjs-dist'
import workerSrc from 'pdfjs-dist/build/pdf.worker.min.mjs?url'
import '../styles/PDFViewer.css'

// Set up PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = workerSrc

interface PDFViewerProps {
  filePath: string
  fileName?: string
}

export const PDFViewer: FC<PDFViewerProps> = ({ filePath, fileName }) => {
  const [numPages, setNumPages] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [pdf, setPdf] = useState<any>(null)

  useEffect(() => {
    const loadPDF = async () => {
      try {
        setLoading(true)
        setError(null)
        const pdfDoc = await pdfjsLib.getDocument(filePath).promise
        setPdf(pdfDoc)
        setNumPages(pdfDoc.numPages)
        setCurrentPage(1)
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to load PDF'
        setError(errorMsg)
        console.error('PDF loading error:', err)
      } finally {
        setLoading(false)
      }
    }

    if (filePath) {
      loadPDF()
    }
  }, [filePath])

  useEffect(() => {
    const renderPage = async () => {
      if (!pdf || !canvasRef.current) return

      try {
        const page = await pdf.getPage(currentPage)
        const viewport = page.getViewport({ scale: 1.5 })
        const canvas = canvasRef.current
        const context = canvas.getContext('2d')
        if (!context) return

        canvas.width = viewport.width
        canvas.height = viewport.height

        const renderContext = {
          canvasContext: context,
          viewport: viewport,
        }

        await page.render(renderContext).promise
      } catch (err) {
        console.error('Error rendering page:', err)
      }
    }

    if (pdf && currentPage >= 1 && currentPage <= numPages) {
      renderPage()
    }
  }, [pdf, currentPage, numPages])

  if (loading) {
    return (
      <div className="pdf-viewer">
        <div className="pdf-loading">
          <div className="spinner"></div>
          <p>Loading PDF...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="pdf-viewer">
        <div className="pdf-error">
          <div className="error-icon">⚠️</div>
          <h3>Error Loading PDF</h3>
          <p>{error}</p>
          {fileName && <p className="file-name">File: {fileName}</p>}
        </div>
      </div>
    )
  }

  if (numPages === 0) {
    return (
      <div className="pdf-viewer">
        <div className="pdf-error">
          <p>No pages found in PDF</p>
        </div>
      </div>
    )
  }

  return (
    <div className="pdf-viewer">
      <div className="pdf-controls">
        <button
          className="pdf-btn"
          onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
        >
          ← Previous
        </button>
        <span className="pdf-page-info">
          Page {currentPage} of {numPages}
        </span>
        <button
          className="pdf-btn"
          onClick={() => setCurrentPage(Math.min(numPages, currentPage + 1))}
          disabled={currentPage === numPages}
        >
          Next →
        </button>
      </div>
      <div className="pdf-container">
        <canvas ref={canvasRef} className="pdf-canvas" />
      </div>
    </div>
  )
}
