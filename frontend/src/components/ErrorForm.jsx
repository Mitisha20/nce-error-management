import React from 'react'

const grid = { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 15 }
const col = { display: 'flex', flexDirection: 'column' }
const lbl = { marginBottom: 6, fontWeight: 'bold' }
const inp = { padding: 8, borderRadius: 4, border: '1px solid #ddd' }
const btn = { padding: '10px 14px', border: 0, borderRadius: 6, cursor: 'pointer', fontWeight: 'bold', marginRight: 10 }
const primary = { ...btn, background: '#007bff', color: '#fff' }
const muted = { ...btn, background: '#6c757d', color: '#fff' }

export default function ErrorForm({ formData, handleChange, handleSubmit, editingId, setEditingId, setFormData }) {
  function cancelEdit() {
    setEditingId(null)
    setFormData({
      error_description: '',
      category: '',
      customer_overview_type: '',
      error_date: '',
      error_count: ''
    })
  }

  return (
    <>
      <h2 style={{ textAlign: 'center', marginBottom: 10 }}>{editingId ? 'Edit Record' : 'Add New Record'}</h2>
      <form onSubmit={handleSubmit} style={grid}>
        <div style={col}>
          <label style={lbl} htmlFor="error_description">Error Description</label>
          <input style={inp} id="error_description" name="error_description" value={formData.error_description} onChange={handleChange} required />
        </div>

        <div style={col}>
          <label style={lbl} htmlFor="category">Category</label>
          <input style={inp} id="category" name="category" value={formData.category} onChange={handleChange} required />
        </div>

        <div style={col}>
          <label style={lbl} htmlFor="customer_overview_type">Customer Overview Type</label>
          <input style={inp} id="customer_overview_type" name="customer_overview_type" value={formData.customer_overview_type} onChange={handleChange} required />
        </div>

        <div style={col}>
          <label style={lbl} htmlFor="error_date">Error Date</label>
          <input style={inp} type="date" id="error_date" name="error_date" value={formData.error_date} onChange={handleChange} required />
        </div>

        <div style={col}>
          <label style={lbl} htmlFor="error_count">Error Count</label>
          <input style={inp} type="number" id="error_count" name="error_count" value={formData.error_count} onChange={handleChange} required />
        </div>

        <div style={{ gridColumn: '1 / -1', textAlign: 'center' }}>
          <button type="submit" style={primary}>{editingId ? 'Update' : 'Add'}</button>
          {editingId && <button type="button" style={muted} onClick={cancelEdit}>Cancel</button>}
        </div>
      </form>
    </>
  )
}
