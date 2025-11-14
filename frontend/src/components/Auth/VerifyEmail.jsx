import React, { useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { authAPI } from '../../services/api'

const VerifyEmail = () => {
  const location = useLocation()
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  
  const email = location.state?.email || ''

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await authAPI.verifyEmail({ email, code })
      setSuccess('Xác thực email thành công! Bạn có thể đăng nhập.')
    } catch (error) {
      setError(error.response?.data?.detail || 'Xác thực thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Xác thực Email</h2>
        <p>Nhập mã OTP đã gửi đến: {email}</p>
        
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Mã OTP:</label>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              required
              placeholder="Nhập mã xác thực"
            />
          </div>
          
          <button type="submit" disabled={loading}>
            {loading ? 'Đang xác thực...' : 'Xác thực'}
          </button>
        </form>
        
        <p>
          <Link to="/login">Quay lại đăng nhập</Link>
        </p>
      </div>
    </div>
  )
}

export default VerifyEmail