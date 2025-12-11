from flask import Flask, send_from_directory, send_file
from pathlib import Path

app = Flask(__name__)

# Register blueprints for each task area first
from routes.search import bp as search_bp  # noqa: E402
from routes.loans import bp as loans_bp  # noqa: E402
from routes.borrowers import bp as borrowers_bp  # noqa: E402
from routes.fines import bp as fines_bp  # noqa: E402

app.register_blueprint(search_bp)
app.register_blueprint(loans_bp)
app.register_blueprint(borrowers_bp)
app.register_blueprint(fines_bp)

# Serve frontend files to avoid CORS issues (register after API routes)
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

@app.route("/")
def serve_index():
    try:
        file_path = FRONTEND_DIR / "landingpage.html"
        if not file_path.exists():
            return f"File not found: {file_path}", 404
        return send_file(str(file_path))
    except Exception as e:
        return f"Error serving file: {str(e)}", 500

@app.route("/search")
@app.route("/loans")
@app.route("/borrower")
@app.route("/fines")
def serve_pages():
    from flask import request
    page = request.path.strip("/")
    if not page:
        page = "landingpage"
    return send_file(str(FRONTEND_DIR / f"{page}.html"))

@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(str(FRONTEND_DIR / "css"), filename)

@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(str(FRONTEND_DIR / "js"), filename)

@app.route("/<path:path>")
def serve_frontend(path):
    # Don't serve frontend for API routes
    if path.startswith("api"):
        return {"error": "Not found"}, 404
    
    # Serve HTML files directly
    if path.endswith(".html"):
        return send_file(str(FRONTEND_DIR / path))
    
    # Try to serve as HTML page
    html_path = FRONTEND_DIR / f"{path}.html"
    if html_path.exists():
        return send_file(str(html_path))
    
    # Default to landing page
    return send_file(str(FRONTEND_DIR / "landingpage.html"))


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Run with: python app.py
    # Add debug=True for development if desired.
    app.run(host="127.0.0.1", port=5000)

