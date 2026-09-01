import { useState } from 'react'
import axios from 'axios'

const API_BASE = 'https://lead-scoring-pro.onrender.com'

function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isRegister) {
        await axios.post(`${API_BASE}/register`, { username, password })
      }

      const res = await axios.post(`${API_BASE}/login`, { username, password })
      onLogin(res.data.access_token, username)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{minHeight:'100vh',background:'#0f172a',display:'flex',alignItems:'center',justifyContent:'center',padding:'20px'}}>
      <div style={{background:'#1e293b',padding:'40px',borderRadius:'16px',width:'100%',maxWidth:'400px',border:'1px solid #334155'}}>
        <div style={{textAlign:'center',marginBottom:'30px'}}>
  <img src="/logo.png" alt="Logo" style={{ height: '48px', marginBottom: '12px' }} />
  <h1 style={{color:'#facc15',fontSize:'24px',margin:0}}>Lead Scoring Pro</h1>
</div>
        
        {error && <div style={{background:'#450a0a',color:'#fca5a5',padding:'12px',borderRadius:'8px',marginBottom:'20px',fontSize:'14px'}}>{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div style={{marginBottom:'16px'}}>
            <label style={{color:'#94a3b8',display:'block',marginBottom:'6px',fontSize:'14px'}}>Username</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)} required
              style={{width:'100%',padding:'12px',background:'#334155',border:'1px solid #475569',borderRadius:'8px',color:'white',fontSize:'14px',outline:'none'}} />
          </div>
          
          <div style={{marginBottom:'20px'}}>
            <label style={{color:'#94a3b8',display:'block',marginBottom:'6px',fontSize:'14px'}}>Password</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required
              style={{width:'100%',padding:'12px',background:'#334155',border:'1px solid #475569',borderRadius:'8px',color:'white',fontSize:'14px',outline:'none'}} />
          </div>
          
          <button type="submit" disabled={loading}
            style={{width:'100%',padding:'12px',background:'#2563eb',color:'white',border:'none',borderRadius:'8px',fontSize:'16px',cursor:'pointer'}}>
            {loading ? 'Please wait...' : isRegister ? 'Register & Login' : 'Login'}
          </button>
        </form>
        
        <div style={{textAlign:'center',marginTop:'20px'}}>
          <button onClick={() => {setIsRegister(!isRegister);setError('')}}
            style={{background:'none',border:'none',color:'#60a5fa',cursor:'pointer',fontSize:'14px'}}>
            {isRegister ? 'Already have account? Login' : "Don't have account? Register"}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Login