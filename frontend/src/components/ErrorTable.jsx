import React from 'react'

const tableWrap = { overflowX: 'auto' }
const table = { width: '100%', borderCollapse: 'collapse', marginTop: 10, border: '1px solid #dcdcdc' }
const th = { padding: '10px 8px', border: '1px solid #d0d0d0', background: '#f1f1f1', textAlign: 'left' }
const td = { padding: '10px 8px', border: '1px solid #e1e1e1', verticalAlign: 'top' }

const btn = {
  padding: '8px 12px',
  borderRadius: 6,
  border: '1px solid #d0d0d0',
  background: '#fafafa',
  cursor: 'pointer',
  marginRight: 8
}
const btnWarn = { ...btn, background: '#ffe9b0' }
const btnDanger = { ...btn, background: '#ffd2d2' }

const pagerWrap = { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginTop: 14, flexWrap: 'wrap' }
const pageBtn = { ...btn, padding: '6px 10px' }
const pageBtnActive = { ...pageBtn, background: '#007bff', color: '#fff', borderColor: '#007bff' }

export default function ErrorTable({ items, page, limit, total, goToPage, handleEdit, handleDelete }) {
  const totalPages = Math.max(1, Math.ceil((total || 0) / (limit || 10)))

  
  const nums = []
  const start = Math.max(1, page - 2)
  const end = Math.min(totalPages, page + 2)
  for (let i = start; i <= end; i++) nums.push(i)

  return (
    <>
      <h2 style={{ textAlign: 'center', marginBottom: 10 }}>Existing Error Records</h2>

      <div style={tableWrap}>
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
            {items.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ ...td, textAlign: 'center' }}>No records</td>
              </tr>
            ) : (
              items.map(row => (
                <tr key={row.error_id}>
                  <td style={td}>{row.error_id}</td>
                  <td style={td}>{row.error_description}</td>
                  <td style={td}>{row.category}</td>
                  <td style={td}>{row.customer_overview_type}</td>
                  <td style={td}>{row.error_date}</td>
                  <td style={td}>{row.error_count}</td>
                  <td style={td}>
                    <button style={btnWarn} onClick={() => handleEdit(row)}>Edit</button>
                    <button style={btnDanger} onClick={() => handleDelete(row.error_id)}>Delete</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination controls */}
      <div style={pagerWrap}>
        <button
          style={btn}
          onClick={() => goToPage(page - 1)}
          disabled={page <= 1}
          title="Previous page"
        >
          ◀ Previous
        </button>

        {nums.map(n => (
          <button
            key={n}
            style={n === page ? pageBtnActive : pageBtn}
            onClick={() => goToPage(n)}
          >
            {n}
          </button>
        ))}

        <button
          style={btn}
          onClick={() => goToPage(page + 1)}
          disabled={page >= totalPages}
          title="Next page"
        >
          Next ▶
        </button>

        <span style={{ marginLeft: 8, fontSize: 13, color: '#555' }}>
          Page {page} of {totalPages} &nbsp;|&nbsp; {limit} per page &nbsp;|&nbsp; Total {total}
        </span>
      </div>
    </>
  )
}
