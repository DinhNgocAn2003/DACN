export const getCurrentUser = () => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

export const setCurrentUser = (user, token) => {
  localStorage.setItem('user', JSON.stringify(user))
  localStorage.setItem('token', token)

}

export const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
}