from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
# CHANGED (Line ~5): import `date` as well
from datetime import datetime, date
import os

DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
CORS(app)

# (These are not used now, safe to keep or delete)
DB_NAME = "nce_errors"
DB_USER = "nce_errors_user"
DB_PASSWORD = "PASTE_RENDERS_PASSWORD"
DB_HOST = "dpg-xxxx.oregon-postgres.render.com"
DB_PORT = "5432"


def parse_date_any(s: str) -> date:
    """Try YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY; raise ValueError if none match."""
    s = str(s).strip()[:10]  
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError("bad date format")

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
    """
    Query params:
      - page  (default 1)
      - limit (default 20)
    Response:
      { "items": [...], "total": 123, "page": 1, "limit": 20 }
    """
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    offset = (page - 1) * limit

    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM public.sheet1_errors;")
        total = cur.fetchone()["cnt"]

        cur.execute("""
            SELECT error_id, error_description, category, customer_overview_type, error_date, error_count
            FROM public.sheet1_errors
            ORDER BY error_id
            LIMIT %s OFFSET %s;
        """, (limit, offset))
        items = cur.fetchall()

    # Convert date to ISO for JSON
    for r in items:
        if r["error_date"]:
            r["error_date"] = r["error_date"].isoformat()

    return jsonify({"items": items, "total": total, "page": page, "limit": limit})

# -------- GET --------
@app.route("/api/errors/<int:error_id>", methods=["GET"])
def get_error(error_id):
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT error_id, error_description, category, customer_overview_type, error_date, error_count
            FROM public.sheet1_errors
            WHERE error_id = %s;
        """, (error_id,))
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

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO public.sheet1_errors
            (error_description, category, customer_overview_type, error_date, error_count)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING error_id;
        """, (data["error_description"], data["category"], data["customer_overview_type"], dt, count))
        new_id = cur.fetchone()[0]
        conn.commit()

    return jsonify({"message": "Created", "error_id": new_id}), 201

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

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            UPDATE public.sheet1_errors
            SET error_description = %s,
                category = %s,
                customer_overview_type = %s,
                error_date = %s,
                error_count = %s
            WHERE error_id = %s;
        """, (data["error_description"], data["category"], data["customer_overview_type"], dt, count, error_id))
        rows = cur.rowcount
        conn.commit()

    if rows == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Updated"})

# -------- DELETE --------
@app.route("/api/errors/<int:error_id>", methods=["DELETE"])
def delete_error(error_id):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM public.sheet1_errors WHERE error_id = %s;", (error_id,))
        rows = cur.rowcount
        conn.commit()

    if rows == 0:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"})

if __name__ == "__main__":
    # Local run for testing
    app.run(host="0.0.0.0", port=5000, debug=True)
