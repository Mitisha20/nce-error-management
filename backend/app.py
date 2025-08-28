from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
import os

DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
CORS(app)

DB_NAME = "nce_errors"
DB_USER = "nce_errors_user"
DB_PASSWORD = "PASTE_RENDERS_PASSWORD"
DB_HOST = "dpg-xxxx.oregon-postgres.render.com"
DB_PORT = "5432"

# ---------- accept multiple date formats ----------
def parse_date_any(s: str) -> date:
    s = str(s).strip()[:10]
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError("bad date format")

# ---------- short db error text ----------
def _db_err(e):
    return getattr(getattr(e, "diag", None), "message_primary", None) or str(e)

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def required_fields_present(d):
    required = ["error_description", "category", "customer_overview_type", "error_date", "error_count"]
    return all(k in d and d[k] not in (None, "") for k in required)

@app.route("/")
def health():
    return jsonify({"ok": True, "service": "NCE Error Management API"})

# -------- GET (list with pagination) --------
@app.route("/api/errors", methods=["GET"])
def list_errors():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    offset = (page - 1) * limit

    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
      
        cur.execute('SELECT COUNT(*) AS cnt FROM public."Sheet1_errors";')
        total = cur.fetchone()["cnt"]

        
        cur.execute(
            '''
            SELECT error_id, error_description, category, customer_overview_type, error_date, error_count
            FROM public."Sheet1_errors"
            ORDER BY error_id desc
            LIMIT %s OFFSET %s;
            ''',
            (limit, offset),
        )
        items = cur.fetchall()

    for r in items:
        if r["error_date"]:
            r["error_date"] = r["error_date"].isoformat()

    return jsonify({"items": items, "total": total, "page": page, "limit": limit})

# -------- GET (single) --------
@app.route("/api/errors/<int:error_id>", methods=["GET"])
def get_error(error_id):
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        
        cur.execute(
            '''
            SELECT error_id, error_description, category, customer_overview_type, error_date, error_count
            FROM public."Sheet1_errors"
            WHERE error_id = %s;
            ''',
            (error_id,),
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error": "Not found"}), 404

    if row["error_date"]:
        row["error_date"] = row["error_date"].isoformat()
    return jsonify(row)

# -------- CREATE --------
@app.route("/api/errors", methods=["POST"])
def create_error():
    data = request.get_json(silent=True) or {}
    if not required_fields_present(data):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        dt = parse_date_any(data["error_date"])
    except ValueError:
        return jsonify({"error": "error_date must be one of: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY"}), 400

    try:
        count = int(data["error_count"])
    except (TypeError, ValueError):
        return jsonify({"error": "error_count must be an integer"}), 400

    try:
        with get_conn() as conn, conn.cursor() as cur:
            
            cur.execute(
                '''
                INSERT INTO public."Sheet1_errors"
                (error_description, category, customer_overview_type, error_date, error_count)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING error_id;
                ''',
                (data["error_description"].strip(),
                 data["category"].strip(),
                 data["customer_overview_type"].strip(),
                 dt,
                 count),
            )
            new_id = cur.fetchone()[0]
            conn.commit()
        return jsonify({"message": "Created", "error_id": new_id}), 201
    except psycopg2.Error as e:
        return jsonify({"error": f"database error: {_db_err(e)}"}), 500

# -------- UPDATE --------
@app.route("/api/errors/<int:error_id>", methods=["PUT"])
def update_error(error_id):
    data = request.get_json(silent=True) or {}
    if not required_fields_present(data):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        dt = parse_date_any(data["error_date"])
    except ValueError:
        return jsonify({"error": "error_date must be one of: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY"}), 400

    try:
        count = int(data["error_count"])
    except (TypeError, ValueError):
        return jsonify({"error": "error_count must be an integer"}), 400

    try:
        with get_conn() as conn, conn.cursor() as cur:
            
            cur.execute(
                '''
                UPDATE public."Sheet1_errors"
                SET error_description = %s,
                    category = %s,
                    customer_overview_type = %s,
                    error_date = %s,
                    error_count = %s
                WHERE error_id = %s;
                ''',
                (data["error_description"].strip(),
                 data["category"].strip(),
                 data["customer_overview_type"].strip(),
                 dt,
                 count,
                 error_id),
            )
            rows = cur.rowcount
            conn.commit()
        if rows == 0:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Updated"})
    except psycopg2.Error as e:
        return jsonify({"error": f"database error: {_db_err(e)}"}), 500

# -------- DELETE --------
@app.route("/api/errors/<int:error_id>", methods=["DELETE"])
def delete_error(error_id):
    try:
        with get_conn() as conn, conn.cursor() as cur:
           
            cur.execute('DELETE FROM public."Sheet1_errors" WHERE error_id = %s;', (error_id,))
            rows = cur.rowcount
            conn.commit()
        if rows == 0:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Deleted"})
    except psycopg2.Error as e:
        return jsonify({"error": f"database error: {_db_err(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
