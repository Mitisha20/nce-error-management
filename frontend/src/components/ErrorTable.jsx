import React from 'react'

const table = { width: '100%', borderCollapse: 'collapse', marginTop: 10 }
const cell = { border: '1px solid #ddd', padding: 8, textAlign: 'left', verticalAlign: 'top' }
const th = { ...cell, background: '#eee', fontWeight: 'bold' }

const btn = { padding: '6px 10px', border: 0, borderRadius: 4, cursor: 'pointer', fontWeight: 'bold', marginRight: 6 }
const editBtn = { ...btn, background: '#ffc107', color: '#333' }
const delBtn = { ...btn, background: '#dc3545', color: '#fff' }

const pagWrap = { display: 'flex', justifyContent: 'center', alignItems: 'center', marginTop: 14, flexWrap: 'wrap' }
const pgBtn = { padding: '6px 10px', margin: 4, border: '1px solid #ddd', borderRadius: 4, background: '#f8f8f8', cursor: 'pointer' }
const pgBtnActive = { ...pgBtn, background: '#007bff', color: '#fff', fontWeight: 'bold' }

export default function ErrorTable({ items, page, limit, total, goToPage, handleEdit, handleDelete }) {
  const totalPages = Math.max(1, Math.ceil(total / limit))
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1)

  return (
    <>
      <h2 style={{ textAlign: 'center', marginBottom: 10 }}>Existing Error Records</h2>

      <table style={table}>
        <thead>
          <tr>
            <th style={th}>ID</th>
            <th style={th}>Description</th>
            <th style={th}>Category</th>
            <th style={th}>Type</th>
            <th style={th}>Date</th>
            <th style={th}>Count</th>
            <th style={th}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map(row => (
            <tr key={row.error_id}>
              <td style={cell}>{row.error_id}</td>
              <td style={cell}>{row.error_description}</td>
              <td style={cell}>{row.category}</td>
              <td style={cell}>{row.customer_overview_type}</td>
              <td style={cell}>{String(row.error_date).slice(0,10)}</td>
              <td style={cell}>{row.error_count}</td>
              <td style={cell}>
                <button style={editBtn} onClick={() => handleEdit(row)}>Edit</button>
                <button style={delBtn} onClick={() => handleDelete(row.error_id)}>Delete</button>
              </td>
            </tr>
          ))}
          {items.length === 0 && (
            <tr><td colSpan="7" style={{ ...cell, textAlign: 'center' }}>No records</td></tr>
          )}
        </tbody>
      </table>

      <div style={pagWrap}>
        <button style={pgBtn} onClick={() => goToPage(page - 1)} disabled={page <= 1}>Previous</button>
        {pages.map(n => (
          <button key={n} style={n === page ? pgBtnActive : pgBtn} onClick={() => goToPage(n)}>{n}</button>
        ))}
        <button style={pgBtn} onClick={() => goToPage(page + 1)} disabled={page >= totalPages}>Next</button>
        <span style={{ marginLeft: 8 }}>Page {page} of {totalPages} (Total: {total})</span>
      </div>
    </>
  )
}
