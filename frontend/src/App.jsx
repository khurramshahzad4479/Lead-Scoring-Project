import { useState, useEffect } from 'react'
import Login from './Login'
import Dashboard from './Dashboard'

function App() {
  const [token, setToken] = useState(null)
  const [username, setUsername] = useState(null)

  useEffect(() => {
    const t = localStorage.getItem('lead_token')
    const u = localStorage.getItem('lead_username')
    if (t && u) { setToken(t); setUsername(u) }
  }, [])

  const handleLogin = (token, username) => {
    localStorage.setItem('lead_token', token)
    localStorage.setItem('lead_username', username)
    setToken(token)
    setUsername(username)
  }

  const handleLogout = () => {
    localStorage.removeItem('lead_token')
    localStorage.removeItem('lead_username')
    setToken(null)
    setUsername(null)
  }

  if (!token) return <Login onLogin={handleLogin} />
  return <Dashboard token={token} username={username} onLogout={handleLogout} />
}

export default App