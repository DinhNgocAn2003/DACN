import React from 'react'

const Toast = ({ toast, onClose }) => {
  const { type = 'info', message } = toast

  return (
    <div className={`toast toast-${type}`} role="status">
      <div className="toast-message">{message}</div>
      <button className="toast-close" onClick={onClose} aria-label="close">×</button>
    </div>
  )
}

export default Toast
