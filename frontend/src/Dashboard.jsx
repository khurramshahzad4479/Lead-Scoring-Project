import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = 'https://lead-scoring-pro.onrender.com'

const INITIAL_FORM = {
  name: '', email: '',
  'Lead Origin': 'Landing Page Submission',
  'Lead Source': 'Organic Search',
  TotalVisits: 0,
  'Total Time Spent on Website': 0,
  'Page Views Per Visit': 0,
  'What is your current occupation': 'Unemployed'
}

function PieChart({ hot, cold }) {
  const total = hot + cold || 1
  const hotPercent = (hot / total) * 100
  const coldPercent = (cold / total) * 100
  
  return (
    <svg width="100" height="100" viewBox="0 0 36 36">
      <circle cx="18" cy="18" r="15.9" fill="none" stroke="#334155" strokeWidth="3" />
      <circle cx="18" cy="18" r="15.9" fill="none" stroke="#ef4444" strokeWidth="3"
        strokeDasharray={`${hotPercent} ${100 - hotPercent}`} strokeDashoffset="25" strokeLinecap="round" />
      <circle cx="18" cy="18" r="15.9" fill="none" stroke="#22c55e" strokeWidth="3"
        strokeDasharray={`${coldPercent} ${100 - coldPercent}`} strokeDashoffset={`${25 - hotPercent}`} strokeLinecap="round" />
      <text x="18" y="17" textAnchor="middle" fill="white" fontSize="6" fontWeight="bold">{hot + cold}</text>
      <text x="18" y="23" textAnchor="middle" fill="#94a3b8" fontSize="3.5">leads</text>
    </svg>
  )
}

function Dashboard({ token, username, onLogout }) {
  const [leads, setLeads] = useState([])
  const [msg, setMsg] = useState('')
  const [msgType, setMsgType] = useState('info')
  const [form, setForm] = useState(INITIAL_FORM)
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  useEffect(() => { if (token) fetchLeads() }, [token])

  const fetchLeads = async () => {
    setFetching(true)
    try {
      const res = await axios.get(`${API_BASE}/leads/`, { headers: { 'Authorization': `Bearer ${token}` } })
      setLeads((res.data.data || []).reverse())
    } catch (err) {
      if (err.response?.status === 401) { onLogout(); return }
      setMsg('Failed to fetch leads')
      setMsgType('error')
    } finally { setFetching(false) }
  }

  const showMsg = (text, type = 'info') => {
    setMsg(String(text))
    setMsgType(type)
    setTimeout(() => setMsg(''), 5000)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await axios.post(`${API_BASE}/predict-lead`, form, { headers: { 'Authorization': `Bearer ${token}` } })
      showMsg(res.data.message, 'success')
      setForm(INITIAL_FORM)
      fetchLeads()
    } catch (err) {
      showMsg(err.response?.data?.detail || err.message || 'Error', 'error')
    } finally { setLoading(false) }
  }

  const hotCount = leads.filter(l => l.is_converted).length
  const coldCount = leads.length - hotCount

  const s = {
    container: { minHeight: '100vh', background: '#0f172a', color: '#e2e8f0', padding: '24px', maxWidth: '1280px', margin: '0 auto', fontFamily: 'system-ui, sans-serif' },
    nav: { background: '#1e293b', padding: '16px 24px', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', border: '1px solid #334155' },
    card: { background: '#1e293b', padding: '24px', borderRadius: '12px', border: '1px solid #334155' },
    input: { width: '100%', padding: '10px 12px', background: '#334155', border: '1px solid #475569', borderRadius: '8px', color: 'white', fontSize: '14px', outline: 'none', boxSizing: 'border-box' },
    btn: { width: '100%', padding: '12px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', cursor: 'pointer', fontWeight: '500' },
    label: { display: 'block', color: '#94a3b8', fontSize: '13px', marginBottom: '6px' },
    th: { padding: '12px', textAlign: 'left', color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', background: '#334155' },
    td: { padding: '12px', borderBottom: '1px solid #334155', fontSize: '14px' },
    badge: { padding: '6px 16px', borderRadius: '20px', fontSize: '12px', fontWeight: '600', display: 'inline-block', minWidth: '90px', textAlign: 'center' }
  }

  const msgColors = {
    success: { background: '#052e16', color: '#86efac', border: '1px solid #166534' },
    error: { background: '#450a0a', color: '#fca5a5', border: '1px solid #991b1b' },
    info: { background: '#172554', color: '#93c5fd', border: '1px solid #1e40af' }
  }

  return (
    <div style={s.container}>
      <nav style={s.nav}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <img src="/logo.png" alt="Logo" style={{ height: '32px' }} />
          <h1 style={{ fontSize: '20px', fontWeight: 'bold', color: '#facc15', margin: 0 }}>Lead Scoring Pro</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <span style={{ color: '#94a3b8', fontSize: '14px' }}> {username}</span>
          <button onClick={onLogout} style={{ padding: '8px 16px', background: 'transparent', border: '1px solid #475569', color: '#94a3b8', borderRadius: '8px', cursor: 'pointer' }}> Logout</button>
        </div>
      </nav>

      {msg && <div style={{ ...msgColors[msgType], padding: '16px', borderRadius: '8px', marginBottom: '24px' }}>{msg}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '24px' }}>
        <div style={{ ...s.card, borderLeft: '4px solid #3b82f6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <p style={{ color: '#94a3b8', fontSize: '14px', margin: '0 0 8px 0' }}> Total Leads</p>
            <h2 style={{ fontSize: '32px', fontWeight: 'bold', margin: 0 }}>{leads.length}</h2>
          </div>
          <PieChart hot={hotCount} cold={coldCount} />
        </div>
        <div style={{ ...s.card, borderLeft: '4px solid #ef4444' }}>
          <p style={{ color: '#94a3b8', fontSize: '14px', margin: '0 0 8px 0' }}>🔥 Hot Leads</p>
          <h2 style={{ fontSize: '32px', fontWeight: 'bold', margin: 0, color: '#ef4444' }}>{hotCount}</h2>
        </div>
        <div style={{ ...s.card, borderLeft: '4px solid #22c55e' }}>
          <p style={{ color: '#94a3b8', fontSize: '14px', margin: '0 0 8px 0' }}>❄️ Cold Leads</p>
          <h2 style={{ fontSize: '32px', fontWeight: 'bold', margin: 0, color: '#22c55e' }}>{coldCount}</h2>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
        <div style={s.card}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '20px', borderBottom: '1px solid #334155', paddingBottom: '12px' }}> Add New Lead</h3>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={s.label}>Name *</label>
              <input style={s.input} value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
            </div>
            <div>
              <label style={s.label}>Email *</label>
              <input style={s.input} type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
            </div>
            <div>
              <label style={s.label}>Lead Origin</label>
              <select style={s.input} value={form['Lead Origin']} onChange={e => setForm({...form, 'Lead Origin': e.target.value})}>
                <option>Landing Page Submission</option><option>API</option><option>Lead Add Form</option>
              </select>
            </div>
            <div>
              <label style={s.label}>Lead Source</label>
              <select style={s.input} value={form['Lead Source']} onChange={e => setForm({...form, 'Lead Source': e.target.value})}>
                <option>Organic Search</option><option>Direct Traffic</option><option>Google</option><option>Olark Chat</option>
              </select>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={s.label}>Visits</label>
                <input style={s.input} type="number" value={form.TotalVisits} onChange={e => setForm({...form, TotalVisits: e.target.value})} />
              </div>
              <div>
                <label style={s.label}>Time (Sec)</label>
                <input style={s.input} type="number" value={form['Total Time Spent on Website']} onChange={e => setForm({...form, 'Total Time Spent on Website': e.target.value})} />
              </div>
            </div>
            <div>
              <label style={s.label}>Occupation</label>
              <select style={s.input} value={form['What is your current occupation']} onChange={e => setForm({...form, 'What is your current occupation': e.target.value})}>
                <option>Unemployed</option><option>Working Professional</option><option>Student</option><option>Businessman</option>
              </select>
            </div>
            <button type="submit" disabled={loading} style={{ ...s.btn, opacity: loading ? 0.6 : 1 }}>
              {loading ? ' Predicting...' : ' Predict Lead (ML)'}
            </button>
          </form>
        </div>

        <div style={s.card}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '20px', borderBottom: '1px solid #334155', paddingBottom: '12px' }}> Recent Leads</h3>
          {fetching ? (
            <div style={{ textAlign: 'center', padding: '48px 0', color: '#64748b' }}> Loading...</div>
          ) : leads.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '48px 0', color: '#64748b' }}>
              <p style={{ fontSize: '18px' }}>📭 No leads yet</p>
              <p style={{ fontSize: '14px', marginTop: '8px' }}>Add your first lead</p>
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ ...s.th, width: '60px' }}>ID</th>
                  <th style={s.th}>Name</th>
                  <th style={s.th}>Email</th>
                  <th style={{ ...s.th, width: '110px' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {leads.map(l => (
                  <tr key={l.id}>
                    <td style={{ ...s.td, color: '#e2e7ee' }}>{l.id}</td>
                    <td style={{ ...s.td, fontWeight: '500', color: '#e2e8f0' }}>{l.name}</td>
                    <td style={{ ...s.td, color: '#e8ebef' }}>{l.email}</td>
                    <td style={s.td}>
                      <span style={{
                        ...s.badge,
                        background: l.is_converted ? 'rgba(240, 54, 54, 0.15)' : 'rgba(34,197,94,0.15)',
                        color: l.is_converted ? '#ef4444' : '#22c55e'
                      }}>
                        {l.is_converted ? ' Hot' : ' Cold'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard