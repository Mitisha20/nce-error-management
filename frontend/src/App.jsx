import React, { useEffect, useState } from 'react'
import ErrorForm from './components/ErrorForm.jsx'
import ErrorTable from './components/ErrorTable.jsx'


const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'

const appStyles = { fontFamily: 'Arial, sans-serif', padding: 20, background: '#f4f4f4', minHeight: '100vh' }
const headerStyles = { color: '#333', textAlign: 'center', marginBottom: 20 }
const card = { background: '#fff', padding: 20, borderRadius: 8, boxShadow: '0 2px 4px rgba(0,0,0,0.1)', marginBottom: 20 }
const errorText = { color: 'red', textAlign: 'center', fontWeight: 'bold' }

export default function App() {
  // data + ui state
  const [items, setItems] = useState([])              
  const [total, setTotal] = useState(0)               
  const [page, setPage] = useState(1)                 
  const [limit] = useState(20)                        
  const [loading, setLoading] = useState(true)
  const [errMsg, setErrMsg] = useState('')

  // form state
  const [formData, setFormData] = useState({
    error_description: '',
    category: '',
    customer_overview_type: '',
    error_date: '',
    error_count: ''
  })
  const [editingId, setEditingId] = useState(null)

  async function fetchErrors(p = page) {
    try {
      setLoading(true)
      setErrMsg('')
      const res = await fetch(`${API_BASE}/api/errors?page=${p}&limit=${limit}`)
      if (!res.ok) {
        const e = await res.json().catch(() => ({}))
        throw new Error(e.error || `HTTP ${res.status}`)
      }
      const data = await res.json()
    
      setItems(data.items || [])
      setTotal(Number(data.total || 0))
      setPage(Number(data.page || p))
    } catch (err) {
      console.error('fetchErrors failed:', err)
      setErrMsg(`Failed to load data: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchErrors(1) }, []) 

  function handleChange(e) {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setErrMsg('')
    try {
      const isEdit = Boolean(editingId)
      const url = isEdit
        ? `${API_BASE}/api/errors/${editingId}`
        : `${API_BASE}/api/errors`
      const method = isEdit ? 'PUT' : 'POST'

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      if (!res.ok) {
        const e = await res.json().catch(() => ({}))
        throw new Error(e.error || `HTTP ${res.status}`)
      }

      // reset form
      setFormData({
        error_description: '',
        category: '',
        customer_overview_type: '',
        error_date: '',
        error_count: ''
      })
      setEditingId(null)

      // refresh current page 
      fetchErrors(page)
    } catch (err) {
      console.error('submit failed:', err)
      setErrMsg(`Submit failed: ${err.message}`)
    }
  }

  function handleEdit(row) {
    setEditingId(row.error_id)
    const formattedDate = row.error_date ? String(row.error_date).slice(0, 10) : ''
    setFormData({
      error_description: row.error_description || '',
      category: row.category || '',
      customer_overview_type: row.customer_overview_type || '',
      error_date: formattedDate,
      error_count: String(row.error_count ?? '')
    })
  }

  async function handleDelete(id) {
    if (!confirm('Delete this record?')) return
    try {
      const res = await fetch(`${API_BASE}/api/errors/${id}`, { method: 'DELETE' })
      if (!res.ok) {
        const e = await res.json().catch(() => ({}))
        throw new Error(e.error || `HTTP ${res.status}`)
      }
      // If we deleted the last item on the last page, move left one page
      const totalAfter = total - 1
      const lastPageAfter = Math.max(1, Math.ceil(totalAfter / limit))
      const nextPage = Math.min(page, lastPageAfter)
      await fetchErrors(nextPage)
    } catch (err) {
      console.error('delete failed:', err)
      setErrMsg(`Delete failed: ${err.message}`)
    }
  }

  async function goToPage(p) {
    if (p < 1) return
    const last = Math.max(1, Math.ceil(total / limit))
    if (p > last) return
    await fetchErrors(p)
  }

  return (
    <div style={appStyles}>
      <h1 style={headerStyles}>NCE Error Management</h1>

      {errMsg && <div style={errorText}>{errMsg}</div>}
      {loading && <div style={{ textAlign: 'center', marginBottom: 10 }}>Loading…</div>}

      <div style={card}>
        <ErrorForm
          formData={formData}
          handleChange={handleChange}
          handleSubmit={handleSubmit}
          editingId={editingId}
          setEditingId={setEditingId}
          setFormData={setFormData}
        />
      </div>

      <div style={card}>
        <ErrorTable
          items={items}          
          page={page}
          limit={limit}
          total={total}
          goToPage={goToPage}
          handleEdit={handleEdit}
          handleDelete={handleDelete}
        />
      </div>
    </div>
  )
}
