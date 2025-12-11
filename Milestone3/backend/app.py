from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register blueprints for each task area
from routes.search import bp as search_bp  # noqa: E402
from routes.loans import bp as loans_bp  # noqa: E402
from routes.borrowers import bp as borrowers_bp  # noqa: E402
from routes.fines import bp as fines_bp  # noqa: E402

app.register_blueprint(search_bp)
app.register_blueprint(loans_bp)
app.register_blueprint(borrowers_bp)
app.register_blueprint(fines_bp)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Run with: python app.py
    # Add debug=True for development if desired.
    app.run(host="127.0.0.1", port=5000)

