import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI } from '../../services/api'
import { setCurrentUser } from '../../services/auth'

const Login = ({ setUser }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [usernameFocused, setUsernameFocused] = useState(false)
  const [passwordFocused, setPasswordFocused] = useState(false)
  const navigate = useNavigate()

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authAPI.login(formData)
      const { user, token } = response.data
      
      setCurrentUser(user, token)
      setUser(user)
      navigate('/')
    } catch (error) {
      setError(error.response?.data?.detail || 'Đăng nhập thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-form">
        <h2>Đăng nhập</h2>
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} autoComplete="off" spellCheck="false">
          {/* dummy fields to discourage browser autofill */}
          <input type="text" name="__hidden_username" autoComplete="username" style={{ display: 'none' }} />
          <input type="password" name="__hidden_password" autoComplete="new-password" style={{ display: 'none' }} />
          <div className="form-group">
            <label>Tên người dùng:</label>
            <input
              type="text"
              name="username"
              placeholder="Nhập tên người dùng"
              value={formData.username}
              onChange={handleChange}
              autoComplete="off"
              readOnly={!usernameFocused}
              onFocus={() => setUsernameFocused(true)}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Mật khẩu:</label>
            <input
              type="password"
              name="password"
              placeholder="Nhập mật khẩu"
              value={formData.password}
              onChange={handleChange}
              autoComplete="new-password"
              readOnly={!passwordFocused}
              onFocus={() => setPasswordFocused(true)}
              required
            />
          </div>
          
          <button type="submit" disabled={loading}>
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>
        </form>
        
        <p>
          Chưa có tài khoản? <Link to="/register">Đăng ký</Link>
        </p>
      </div>
    </div>
  )
}

export default Login