import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { FiUploadCloud, FiX, FiFile, FiCheck } from 'react-icons/fi'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

function FileUploadModal({ onClose, onSuccess, notebookId }) {
  const [files, setFiles] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadComplete, setUploadComplete] = useState(false)

  const onDrop = useCallback((acceptedFiles) => {
    const pdfFiles = acceptedFiles.filter(file => file.type === 'application/pdf')
    setFiles(prev => [...prev, ...pdfFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  })

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setIsUploading(true)

    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })

      await axios.post(`${API_URL}/upload-pdfs/${notebookId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setUploadComplete(true)
      setTimeout(() => {
        onSuccess()
      }, 1000)
    } catch (error) {
      console.error('Error uploading files:', error)
      alert('Error uploading files. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Upload PDF Documents</h2>
        </div>

        <div className="modal-body">
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <div className="dropzone-icon">
              <FiUploadCloud />
            </div>
            {isDragActive ? (
              <p>Drop the PDFs here...</p>
            ) : (
              <>
                <p>
                  <span className="highlight">Click to upload</span> or drag and drop
                </p>
                <p style={{ fontSize: '12px', marginTop: '4px' }}>
                  PDF files only
                </p>
              </>
            )}
          </div>

          {files.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px' }}>
                Selected Files ({files.length})
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {files.map((file, index) => (
                  <div
                    key={index}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px',
                      backgroundColor: 'var(--bg-secondary)',
                      borderRadius: '8px',
                      fontSize: '13px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <FiFile />
                      <span>{file.name}</span>
                      <span style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    {!isUploading && !uploadComplete && (
                      <button
                        onClick={() => removeFile(index)}
                        style={{
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: 'var(--error)',
                          padding: '4px',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        <FiX />
                      </button>
                    )}
                    {uploadComplete && (
                      <FiCheck style={{ color: 'var(--success)' }} />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button
            className="cancel-button"
            onClick={onClose}
            disabled={isUploading}
          >
            Cancel
          </button>
          <button
            className="confirm-button"
            onClick={handleUpload}
            disabled={files.length === 0 || isUploading || uploadComplete}
          >
            {isUploading ? 'Uploading...' : uploadComplete ? 'Complete!' : `Upload ${files.length} file${files.length !== 1 ? 's' : ''}`}
          </button>
        </div>
      </div>
    </div>
  )
}

export default FileUploadModal
