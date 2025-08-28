from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
from datetime import date

# ----- Database config -----
DB_NAME = os.getenv("DB_NAME", "internship_data")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mitisha1")  
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
PORT = int(os.getenv("PORT", "5000"))

app = Flask(__name__)
CORS(app)  

# connect to DB
def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )

# convert rows → dicts
def rows_to_dicts(cur):
    cols = [c[0] for c in cur.description]
    results = []
    for row in cur.fetchall():
        d = dict(zip(cols, row))
        if isinstance(d.get("error_date"), date):
            d["error_date"] = d["error_date"].isoformat()
        results.append(d)
    return results

# -------- GET (with pagination) --------
@app.get("/api/errors")
def list_errors():
    page = max(int(request.args.get("page", 1)), 1)
    limit = max(int(request.args.get("limit", 20)), 1)
    offset = (page - 1) * limit

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sheet1_errors;")
        total = cur.fetchone()[0]

        cur.execute("""
            SELECT error_id, error_description, category, customer_overview_type, error_date, error_count
            FROM sheet1_errors
            ORDER BY error_id DESC
            LIMIT %s OFFSET %s;
        """, (limit, offset))
        items = rows_to_dicts(cur)

        cur.close()
        conn.close()
        return jsonify({"items": items, "total": total, "page": page, "limit": limit}), 200
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

# -------- CREATE --------
@app.post("/api/errors")
def create_error():
    data = request.get_json() or {}
    required = ["error_description", "category", "customer_overview_type", "error_date", "error_count"]
    if not all(k in data and data[k] not in ("", None) for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sheet1_errors (error_description, category, customer_overview_type, error_date, error_count)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING error_id;
        """, (
            data["error_description"],
            data["category"],
            data["customer_overview_type"],
            data["error_date"],
            int(data["error_count"])
        ))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "created", "error_id": new_id}), 201
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500

# -------- UPDATE --------
@app.put("/api/errors/<int:error_id>")
def update_error(error_id):
    data = request.get_json() or {}
    required = ["error_description", "category", "customer_overview_type", "error_date", "error_count"]
    if not all(k in data and data[k] not in ("", None) for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE sheet1_errors
            SET error_description=%s, category=%s, customer_overview_type=%s, error_date=%s, error_count=%s
            WHERE error_id=%s;
        """, (
            data["error_description"],
            data["category"],
            data["customer_overview_type"],
            data["error_date"],
            int(data["error_count"]),
            error_id
        ))
        changed = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        if changed:
            return jsonify({"message": "updated"}), 200
        return jsonify({"message": "not found"}), 404
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500

# -------- DELETE --------
@app.delete("/api/errors/<int:error_id>")
def delete_error(error_id):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM sheet1_errors WHERE error_id=%s;", (error_id,))
        changed = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        if changed:
            return jsonify({"message": "deleted"}), 200
        return jsonify({"message": "not found"}), 404
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=True)
