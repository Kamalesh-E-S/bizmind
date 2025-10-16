from app import create_app
from app import init_db  # Ensure database module is imported to register functions

app = create_app()

with app.app_context():
    init_db()
    print("Database initialized!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)