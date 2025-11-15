import React, { createContext, useContext, useState, useCallback } from 'react'
import Toast from './Toast'

const ToastContext = createContext()

export const useToast = () => useContext(ToastContext)

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([])

  const showToast = useCallback((toast) => {
    const id = Date.now() + Math.random()
    const t = { id, ...toast }
    setToasts((s) => [t, ...s])
    if (!toast.persist) {
      setTimeout(() => {
        setToasts((s) => s.filter((x) => x.id !== id))
      }, toast.duration || 4000)
    }
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((s) => s.filter((x) => x.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ showToast, removeToast }}>
      {children}
      <div className="toast-container">
        {toasts.map((t) => (
          <Toast key={t.id} toast={t} onClose={() => removeToast(t.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export default ToastContext
