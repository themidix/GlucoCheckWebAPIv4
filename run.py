#run.py
from app import create_app, db
from dotenv import load_dotenv
import os

app = create_app()

print(os.getenv("DB_URL"))

load_dotenv()
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)
