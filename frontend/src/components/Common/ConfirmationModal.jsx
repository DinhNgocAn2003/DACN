import React from 'react'

const ConfirmationModal = ({ isOpen, title = 'Xác nhận', message, onConfirm, onCancel, confirmLabel = 'Xác nhận', cancelLabel = 'Hủy' }) => {
  if (!isOpen) return null

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="close-btn" onClick={onCancel} aria-label="close">×</button>
        </div>
        <div className="modal-body">
          <p>{message}</p>
        </div>
        <div className="form-actions">
          <button className="btn-secondary" onClick={onCancel}>{cancelLabel}</button>
          <button className="btn-primary" onClick={onConfirm}>{confirmLabel}</button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmationModal
